class PdsXv13:
    def _get_size(self, type_name):
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8,
            "BITFIELD": 4, "ENUM": 4, "FLOAT128": 16, "FLOAT256": 32, "STRING8": 8, "STRING16": 16,
            "BOOLEAN": 1, "NULL": 8, "NAN": 8
        }
        return size_map.get(type_name.upper(), 8)

    # ... (önceki kodlar burada)

    def parse_program(self, code, module_name="main", lightweight=False, as_library=False):
        self.current_module = module_name
        self.modules[module_name] = {
            "program": [],
            "functions": {},
            "subs": {},
            "classes": {},
            "types": {},
            "labels": {}
        }
        current_sub = None
        current_function = None
        current_type = None
        current_class = None
        current_interface = None
        type_fields = {}
        class_info = {}
        interface_info = {}
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            line_upper = line.upper()
            if line_upper.startswith("'"):
                i += 1
                continue
            if ":" in line and not line_upper.startswith("PIPE("):
                parts = [p.strip() for p in line.split(":")]
                for part in parts:
                    self.program.append((part, None))
                i += 1
                continue
            if "/" in line and line_upper.startswith("FOR "):
                parts = [p.strip() for p in line.split("/")]
                for part in parts:
                    self.program.append((part, None))
                i += 1
                continue
            if "/" in line and line_upper.startswith("IF "):
                parts = [p.strip() for p in line.split("/")]
                for part in parts:
                    self.program.append((part, None))
                i += 1
                continue
            if line_upper.startswith("FUNC "):
                expr = line[5:].strip()
                self.function_table["_func"] = lambda *args: eval(expr, dict(zip(['x','y','z'], args)))
                i += 1
                continue
            if line_upper.startswith("GAMMA "):
                expr = line[6:].strip()
                self.function_table["_gamma"] = self.core.omega('x', 'y', expr)
                i += 1
                continue
            if line_upper.startswith("FACT "):
                self.prolog_engine.add_fact(line[5:].strip())
                i += 1
                continue
            if line_upper.startswith("RULE "):
                match = re.match(r"RULE\s+(\w+)\s*:-\s*(.+)", line, re.IGNORECASE)
                if match:
                    head, body = match.groups()
                    self.prolog_engine.add_rule(head, body.strip())
                i += 1
                continue
            if line_upper.startswith("QUERY "):
                self.prolog_engine.query(line[6:].strip())
                i += 1
                continue
            if line_upper.startswith("ASM"):
                asm_code = []
                j = i + 1
                while j < len(lines) and not lines[j].strip().upper().startswith("END ASM"):
                    asm_code.append(lines[j])
                    j += 1
                self.asm_blocks.append("\n".join(asm_code))
                i = j + 1
                continue
            if line_upper.startswith("INTERFACE "):
                match = re.match(r"INTERFACE\s+(\w+)", line, re.IGNORECASE)
                if match:
                    name = match.group(1)
                    current_interface = InterfaceDef(name)
                    interface_info[name] = current_interface
                    self.modules[module_name]["classes"][name] = current_interface
                    i += 1
                    continue
            if line_upper == "END INTERFACE":
                if current_interface:
                    self.classes[current_interface.name] = current_interface
                    current_interface = None
                    i += 1
                    continue
            if line_upper.startswith("ABSTRACT CLASS "):
                match = re.match(r"ABSTRACT CLASS\s+(\w+)(?:\s+EXTENDS\s+(.+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_names = match.groups()
                    parent_list = [p.strip() for p in parent_names.split(",")] if parent_names else []
                    current_class = ClassDef(class_name, parents=parent_list, abstract=True)
                    class_info[class_name] = current_class
                    self.modules[module_name]["classes"][class_name] = current_class
                    i += 1
                    continue
            if line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+EXTENDS\s+(.+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_names = match.groups()
                    parent_list = [p.strip() for p in parent_names.split(",")] if parent_names else []
                    current_class = ClassDef(class_name, parents=parent_list, abstract=False)
                    class_info[class_name] = current_class
                    self.modules[module_name]["classes"][class_name] = current_class
                    i += 1
                    continue
            if line_upper.startswith("END CLASS"):
                if current_class:
                    self.classes[current_class.name] = self.build_class(current_class)
                    current_class = None
                    i += 1
                    continue
            if current_class:
                if line_upper.startswith("MIXIN "):
                    current_class.is_mixin = True
                    i += 1
                    continue
                if line_upper.startswith(("SUB ", "PRIVATE SUB ", "FUNCTION ", "PRIVATE FUNCTION ")):
                    is_private = line_upper.startswith(("PRIVATE SUB ", "PRIVATE FUNCTION "))
                    prefix = "PRIVATE " if is_private else ""
                    method_type = "SUB" if line_upper.startswith((prefix + "SUB ")) else "FUNCTION"
                    match = re.match(rf"{prefix}{method_type}\s+(\w+)(?:\(.*\))?", line, re.IGNORECASE)
                    if match:
                        method_name = match.group(1)
                        method_body = []
                        j = i + 1
                        while j < len(lines) and lines[j].strip().upper() != f"END {method_type}":
                            method_body.append(lines[j].strip())
                            j += 1
                        params = re.search(r"\((.*?)\)", line, re.IGNORECASE)
                        params = params.group(1).split(",") if params else []
                        params = [p.strip() for p in params]
                        method_lambda = lambda self, *args, **kwargs: self.execute_method(method_name, method_body, params, args, scope_name=current_class)
                        if is_private:
                            class_info[current_class]['private_methods'][method_name] = method_lambda
                        else:
                            class_info[current_class]['methods'][method_name] = method_lambda
                        i = j + 1
                        continue
                if line_upper.startswith("STATIC "):
                    match = re.match(r"STATIC\s+(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                    if match:
                        var_name, var_type = match.groups()
                        class_info[current_class]['static_vars'][var_name] = self.type_table.get(var_type, None)()
                        i += 1
                        continue
            self.program.append((line, None))
            i += 1

    def execute_command(self, command, scope_name=None):
        command = command.strip()
        if not command:
            return None
        command_upper = command.upper()

        if self.trace_mode:
            print(f"TRACE: Satır {self.program_counter + 1}: {command}")

        try:
            if command_upper.startswith("IMPORT"):
                match = re.match(r"IMPORT\s+([^\s]+)(?:\s+AS\s+(\w+))?", command, re.IGNORECASE)
                if match:
                    file_name, alias = match.groups()
                    module_name = alias or os.path.splitext(os.path.basename(file_name))[0]
                    self.import_module(file_name, module_name)
                    return None
                else:
                    raise PdsXException("IMPORT komutunda sözdizimi hatası")

            if command_upper.startswith("ON ERROR GOTO"):
                match = re.match(r"ON ERROR GOTO\s+(\w+)", command, re.IGNORECASE)
                if match:
                    label = match.group(1)
                    if label in self.labels:
                        self.error_handler = self.labels[label]
                    else:
                        raise PdsXException(f"Etiket bulunamadı: {label}")
                    return None
                else:
                    raise PdsXException("ON ERROR GOTO komutunda sözdizimi hatası")

            if command_upper.startswith("ON ERROR GOSUB"):
                match = re.match(r"ON ERROR GOSUB\s+(\w+)", command, re.IGNORECASE)
                if match:
                    label = match.group(1)
                    if label in self.labels:
                        self.gosub_handler = self.labels[label]
                    else:
                        raise PdsXException(f"Etiket bulunamadı: {label}")
                    return None
                else:
                    raise PdsXException("ON ERROR GOSUB komutunda sözdizimi hatası")

            if command_upper.startswith("ON ERROR DO"):
                match = re.match(r"ON ERROR DO\s+(\w+)", command, re.IGNORECASE)
                if match:
                    sub_name = match.group(1)
                    if sub_name in self.subs:
                        self.error_sub = sub_name
                    else:
                        raise PdsXException(f"Altprogram bulunamadı: {sub_name}")
                    return None
                else:
                    raise PdsXException("ON ERROR DO komutunda sözdizimi hatası")

            if command_upper.startswith("ON SYSTEM EVENT"):
                match = re.match(r"ON SYSTEM EVENT\s+(\w+)\s+DO\s+(\w+)", command, re.IGNORECASE)
                if match:
                    event, handler = match.groups()
                    event_key = f"system.{event.lower()}"
                    if handler not in self.subs and handler not in self.functions:
                        raise PdsXException(f"Handler bulunamadı: {handler}")
                    self.event_handlers[event_key] = {"type": "DO", "handler": handler}
                    if event.lower() == "timer_elapsed":
                        timer = threading.Timer(1.0, lambda: self.handle_event(event_key))
                        timer.start()
                    elif event.lower() == "file_changed" and Observer:
                        class FileHandler(FileSystemEventHandler):
                            def on_modified(self, evt):
                                self.handle_event(event_key)
                        observer = Observer()
                        observer.schedule(FileHandler(), path=".", recursive=False)
                        observer.start()
                    elif event.lower() in ("mouse_clicked", "key_pressed"):
                        if self.gui:
                            self.gui.bind_system_event(event.lower(), lambda e: self.handle_event(event_key))
                    return None
                match = re.match(r"ON SYSTEM EVENT\s+(\w+)\s+(.+)", command, re.IGNORECASE)
                if match:
                    event, action = match.groups()
                    event_key = f"system.{event.lower()}"
                    self.event_handlers[event_key] = {"type": "CUSTOM", "action": action}
                    if event.lower() == "timer_elapsed":
                        timer = threading.Timer(1.0, lambda: self.handle_event(event_key))
                        timer.start()
                    elif event.lower() == "file_changed" and Observer:
                        class FileHandler(FileSystemEventHandler):
                            def on_modified(self, evt):
                                self.handle_event(event_key)
                        observer = Observer()
                        observer.schedule(FileHandler(), path=".", recursive=False)
                        observer.start()
                    elif event.lower() in ("mouse_clicked", "key_pressed"):
                        if self.gui:
                            self.gui.bind_system_event(event.lower(), lambda e: self.handle_event(event_key))
                    return None
                else:
                    raise PdsXException("ON SYSTEM EVENT komutunda sözdizimi hatası")

            if command_upper.startswith("ON EVENT"):
                match = re.match(r"ON EVENT\s+(\w+\.\w+)\s+WAIT\s+DO\s+(\w+)", command, re.IGNORECASE)
                if match:
                    event_key, handler = match.groups()
                    if handler not in self.subs and handler not in self.functions:
                        raise PdsXException(f"Handler bulunamadı: {handler}")
                    self.event_handlers[event_key.lower()] = {"type": "WAIT", "handler": handler}
                    return None
                else:
                    raise PdsXException("ON EVENT WAIT komutunda sözdizimi hatası")

            if command_upper.startswith("ON INTERRUPT"):
                match = re.match(r"ON INTERRUPT\s+(\w+)\s+DO\s+(\w+)", command, re.IGNORECASE)
                if match:
                    signal_name, handler = match.groups()
                    signal_map = {
                        "SIGINT": signal.SIGINT, "SIGTERM": signal.SIGTERM,
                        "SIGSEGV": signal.SIGSEGV, "SIGFPE": signal.SIGFPE,
                        "SIGILL": signal.SIGILL, "SIGABRT": signal.SIGABRT
                    }
                    if signal_name not in signal_map:
                        raise PdsXException(f"Geçersiz sinyal: {signal_name}")
                    if handler not in self.subs and handler not in self.functions:
                        raise PdsXException(f"Handler bulunamadı: {handler}")
                    def signal_handler(signum, frame):
                        self.execute_command(f"CALL {handler}", scope_name)
                    signal.signal(signal_map[signal_name], signal_handler)
                    return None
                else:
                    raise PdsXException("ON INTERRUPT komutunda sözdizimi hatası")

            if command_upper.startswith("DIM"):
                match = re.match(r"DIM\s+(\w+)\s+AS\s+(\w+)(?:\s*=\s*(.+))?", command, re.IGNORECASE)
                if match:
                    var_name, var_type, init_value = match.groups()
                    if var_type.upper() == "VOID":
                        raise PdsXException("VOID değişken tanımlamada kullanılamaz")
                    value = self.type_table.get(var_type.upper(), object)()
                    if init_value:
                        if init_value.upper() == "NULL" and var_type.upper() != "VOID":
                            value = None
                        elif init_value.upper() == "NAN" and var_type.upper() in ("FLOAT", "DOUBLE", "SINGLE"):
                            value = float('nan')
                        else:
                            try:
                                value = self.evaluate_expression(init_value, scope_name)
                            except:
                                raise PdsXException(f"Geçersiz başlangıç değeri: {init_value}")
                    self.current_scope()[var_name] = value
                    return None
                match = re.match(r"DIM\s+(\w+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    alias_name, original_name = match.groups()
                    if original_name.upper() in self.type_table or original_name in self.types:
                        self.type_table[alias_name.upper()] = self.type_table.get(original_name.upper(), original_name)
                    elif original_name in self.classes:
                        self.classes[alias_name] = self.classes[original_name]
                    elif original_name in self.functions:
                        self.functions[alias_name] = self.functions[original_name]
                    elif original_name in self.subs:
                        self.subs[alias_name] = self.subs[original_name]
                    else:
                        raise PdsXException(f"Geçersiz alias hedefi: {original_name}")
                    return None
                else:
                    raise PdsXException("DIM komutunda sözdizimi hatası")

            if command_upper.startswith("LET"):
                match = re.match(r"LET\s+(\w+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    var_name, expr = match.groups()
                    value = self.evaluate_expression(expr, scope_name)
                    self.current_scope()[var_name] = value
                    return None
                else:
                    raise PdsXException("LET komutunda sözdizimi hatası")

            if command_upper.startswith("~"):
                parts = [p.strip() for p in command[1:].split(";")]
                args = [self.evaluate_expression(p, scope_name) for p in parts]
                self.print_with_semicolon(*args)
                return None

            if command_upper.startswith("??"):
                prompt = command[2:].strip()
                result = input(prompt)
                self.current_scope()['_input'] = result
                return None

            if command_upper.startswith("GOTO"):
                label = command[5:].strip()
                if label in self.labels:
                    return self.labels[label]
                else:
                    raise PdsXException(f"Etiket bulunamadı: {label}")

            if command_upper.startswith("GOSUB"):
                label = command[6:].strip()
                if label in self.labels:
                    self.call_stack.append(self.program_counter + 1)
                    return self.labels[label]
                else:
                    raise PdsXException(f"Etiket bulunamadı: {label}")

            if command_upper == "RETURN":
                if self.call_stack:
                    return self.call_stack.pop()
                else:
                    raise PdsXException("RETURN için eşleşen GOSUB bulunamadı")

            if command_upper.startswith("CALL"):
                sub_name = command[5:].split("(")[0].strip()
                if sub_name in self.subs:
                    self.call_stack.append(self.program_counter + 1)
                    return self.subs[sub_name]
                elif sub_name in self.functions:
                    params = re.search(r"\((.*?)\)", command, re.IGNORECASE)
                    params = [self.evaluate_expression(p.strip(), scope_name) for p in params.group(1).split(",")] if params else []
                    result = self.functions[sub_name](*params)
                    self.current_scope()['RETURN'] = result
                    return None
                else:
                    raise PdsXException(f"Altprogram veya fonksiyon bulunamadı: {sub_name}")

            if command_upper.startswith("IF"):
                match = re.match(r"IF\s+(.+)\s+THEN\s+(.+)", command, re.IGNORECASE)
                if match:
                    condition, action = match.groups()
                    if self.evaluate_expression(condition, scope_name):
                        self.execute_command(action, scope_name)
                    return None
                else:
                    raise PdsXException("IF komutunda sözdizimi hatası")

            if command_upper.startswith("FOR"):
                match = re.match(r"FOR\s+(\w+)\s*=\s*(.+)\s+TO\s+(.+)(?:\s+STEP\s+(.+))?", command, re.IGNORECASE)
                if match:
                    var_name, start, end, step = match.groups()
                    start_val = self.evaluate_expression(start, scope_name)
                    end_val = self.evaluate_expression(end, scope_name)
                    step_val = self.evaluate_expression(step, scope_name) if step else 1
                    self.current_scope()[var_name] = start_val
                    self.loop_stack.append({
                        "start": self.program_counter,
                        "type": "FOR",
                        "var": var_name,
                        "end": end_val,
                        "step": step_val
                    })
                    return None
                else:
                    raise PdsXException("FOR komutunda sözdizimi hatası")

            if command_upper.startswith("EXIT FOR"):
                if self.loop_stack and self.loop_stack[-1]["type"] == "FOR":
                    while self.program_counter < len(self.program) and \
                          self.program[self.program_counter][0].upper() != "NEXT":
                        self.program_counter += 1
                    self.loop_stack.pop()
                    return None
                else:
                    raise PdsXException("EXIT FOR için eşleşen FOR bulunamadı")

            if command_upper.startswith("CONTINUE FOR"):
                if self.loop_stack and self.loop_stack[-1]["type"] == "FOR":
                    loop_info = self.loop_stack[-1]
                    var_name = loop_info["var"]
                    current_value = self.current_scope()[var_name]
                    current_value += loop_info["step"]
                    self.current_scope()[var_name] = current_value
                    return loop_info["start"]
                else:
                    raise PdsXException("CONTINUE FOR için eşleşen FOR bulunamadı")

            if command_upper.startswith("NEXT"):
                if self.loop_stack and self.loop_stack[-1]["type"] == "FOR":
                    loop_info = self.loop_stack[-1]
                    var_name = loop_info["var"]
                    current_value = self.current_scope()[var_name]
                    current_value += loop_info["step"]
                    self.current_scope()[var_name] = current_value
                    if (loop_info["step"] > 0 and current_value <= loop_info["end"]) or \
                       (loop_info["step"] < 0 and current_value >= loop_info["end"]):
                        return loop_info["start"]
                    else:
                        self.loop_stack.pop()
                    return None
                else:
                    raise PdsXException("NEXT için eşleşen FOR bulunamadı")

            if command_upper.startswith("WHILE"):
                match = re.match(r"WHILE\s+(.+)", command, re.IGNORECASE)
                if match:
                    condition = match.group(1)
                    self.loop_stack.append({
                        "start": self.program_counter,
                        "type": "WHILE",
                        "condition": condition
                    })
                    if not self.evaluate_expression(condition, scope_name):
                        while self.program_counter < len(self.program) and \
                              self.program[self.program_counter][0].upper() != "WEND":
                            self.program_counter += 1
                    return None
                else:
                    raise PdsXException("WHILE komutunda sözdizimi hatası")

            if command_upper == "WEND":
                if self.loop_stack and self.loop_stack[-1]["type"] == "WHILE":
                    loop_info = self.loop_stack[-1]
                    if self.evaluate_expression(loop_info["condition"], scope_name):
                        return loop_info["start"]
                    else:
                        self.loop_stack.pop()
                    return None
                else:
                    raise PdsXException("WEND için eşleşen WHILE bulunamadı")

            if command_upper.startswith("DO"):
                match = re.match(r"DO\s+(WHILE|UNTIL)?\s*(.+)?", command, re.IGNORECASE)
                if match:
                    loop_type, condition = match.groups()
                    self.loop_stack.append({
                        "start": self.program_counter,
                        "type": loop_type or "NONE",
                        "condition": condition or "True"
                    })
                    return None
                else:
                    raise PdsXException("DO komutunda sözdizimi hatası")

            if command_upper.startswith("EXIT DO"):
                if self.loop_stack and self.loop_stack[-1]["type"] in ("WHILE", "UNTIL", "NONE"):
                    while self.program_counter < len(self.program) and \
                          self.program[self.program_counter][0].upper() != "LOOP":
                        self.program_counter += 1
                    self.loop_stack.pop()
                    return None
                else:
                    raise PdsXException("EXIT DO için eşleşen DO bulunamadı")

            if command_upper.startswith("CONTINUE DO"):
                if self.loop_stack and self.loop_stack[-1]["type"] in ("WHILE", "UNTIL", "NONE"):
                    return self.loop_stack[-1]["start"]
                else:
                    raise PdsXException("CONTINUE DO için eşleşen DO bulunamadı")

            if command_upper.startswith("LOOP"):
                if self.loop_stack and self.loop_stack[-1]["type"] in ("WHILE", "UNTIL", "NONE"):
                    loop_info = self.loop_stack[-1]
                    condition = loop_info["condition"]
                    if loop_info["type"] == "WHILE" and not self.evaluate_expression(condition, scope_name):
                        self.loop_stack.pop()
                    elif loop_info["type"] == "UNTIL" and self.evaluate_expression(condition, scope_name):
                        self.loop_stack.pop()
                    elif loop_info["type"] == "NONE":
                        return loop_info["start"]
                    return None
                else:
                    raise PdsXException("LOOP için eşleşen DO bulunamadı")

            if command_upper.startswith("TRY"):
                match = re.match(r"TRY\s+(.+)\s+CATCH\s+(.+)", command, re.IGNORECASE)
                if match:
                    try_block, catch_block = match.groups()
                    try:
                        self.execute_command(try_block, scope_name)
                    except Exception as e:
                        self.current_scope()['_error'] = str(e)
                        self.execute_command(catch_block, scope_name)
                    return None
                else:
                    raise PdsXException("TRY CATCH komutunda sözdizimi hatası")

            if command_upper == "DEBUG ON":
                self.debug_mode = True
                return None
            if command_upper == "DEBUG OFF":
                self.debug_mode = False
                return None
            if command_upper == "TRACE ON":
                self.trace_mode = True
                return None
            if command_upper == "TRACE OFF":
                self.trace_mode = False
                return None
            if command_upper == "STEP DEBUG":
                self.debug_mode = True
                input(f"Satır {self.program_counter + 1}: {command}\nDevam için Enter...")
                return None

            if command_upper.startswith("PERFORMANCE"):
                process = psutil.Process()
                memory = process.memory_info().rss / 1024 / 1024
                cpu = psutil.cpu_percent()
                elapsed = time.time() - self.performance_metrics["start_time"]
                print(f"Performans: Bellek: {memory:.2f} MB, CPU: {cpu:.2f}%, Süre: {elapsed:.2f}s")
                return None

            if command_upper.startswith("SET LANGUAGE"):
                match = re.match(r"SET LANGUAGE\s+(\w+)", command, re.IGNORECASE)
                if match:
                    lang = match.group(1).lower()
                    if lang in self.translations:
                        self.language = lang
                    else:
                        raise PdsXException(f"Desteklenmeyen dil: {lang}")
                    return None
                else:
                    raise PdsXException("SET LANGUAGE komutunda sözdizimi hatası")

            if command_upper.startswith("CALL API::GET"):
                match = re.match(r"CALL API::GET\s+(.+)", command, re.IGNORECASE)
                if match:
                    url = match.group(1)
                    return requests.get(url).json()

            if command_upper.startswith("HELP"):
                match = re.match(r"HELP\s*(\w+)?", command, re.IGNORECASE)
                if match:
                    lib_name = match.group(1)
                    self.show_help(lib_name)
                    return None
                else:
                    raise PdsXException("HELP komutunda sözdizimi hatası")

            raise PdsXException(f"Bilinmeyen komut: {command}")

        except Exception as e:
            if self.error_sub:
                self.execute_command(f"CALL {self.error_sub}", scope_name)
            elif self.error_handler:
                return self.error_handler
            elif self.gosub_handler:
                self.call_stack.append(self.program_counter + 1)
                return self.gosub_handler
            else:
                logging.error(f"Hata: {str(e)}")
                raise PdsXException(f"Hata: {str(e)}")

    def show_help(self, lib_name=None):
        if lib_name:
            help_file = f"{lib_name}/{lib_name}_help.json"
            if os.path.exists(help_file):
                with open(help_file, "r", encoding="utf-8") as f:
                    help_data = json.load(f)
                for cmd in help_data.get(lib_name, {}).get("commands", []):
                    print(f"Komut: {cmd['name']}")
                    print(f"Kullanım: {cmd['usage']}")
                    print(f"Amaç: {cmd['purpose']}")
                    print(f"Örnek: {cmd['example']}")
                    print("-" * 50)
            else:
                print(f"Yardım dosyası bulunamadı: {lib_name}")
        else:
            print("Kullanım: HELP [kütüphane_adı]")
            print("Örnek: HELP libx_core")

    def run(self, code):
        self.parse_program(code)
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.program):
            command, scope = self.program[self.program_counter]
            if self.debug_mode:
                print(f"DEBUG: Satır {self.program_counter + 1}: {command}")
            next_pc = self.execute_command(command, scope)
            if next_pc is not None:
                self.program_counter = next_pc
            else:
                self.program_counter += 1
        self.running = False

    def repl(self):
        self.repl_mode = True
        print("pdsXv13 REPL. Çıkmak için EXIT yazın.")
        while self.repl_mode:
            try:
                command = input(">> ")
                if command.upper() == "EXIT":
                    self.repl_mode = False
                    break
                self.execute_command(command)
            except PdsXException as e:
                print(f"Hata: {e}")
            except Exception as e:
                print(f"Beklenmeyen hata: {e}")

if __name__ == "__main__":
    interpreter = PdsXv13()
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
        interpreter.run(code)
    else:
        interpreter.repl()