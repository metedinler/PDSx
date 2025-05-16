
import re
import logging
import struct as py_struct
from collections import namedtuple

# 1. Temel veri yapıları ve sınıflar
# (StructInstance, UnionInstance, ArrayInstance, Pointer, ClassInstance)
# (Bu kısım burada yazılacak - kısaltıyorum şimdilik, çünkü zaten verdiğinle birebir olacak)
# ---------------
# (KOPYA: senin verdiğin tam StructInstance, UnionInstance, ArrayInstance, Pointer, ClassInstance sınıflarını koyacağız)
# ---------------

# 2. pdsXInterpreter güncellenmiş hali
class pdsXInterpreter:
    def __init__(self):
        self.program = []
        self.program_counter = 0
        self.global_vars = {}
        self.scopes = [{}]
        self.running = False
        self.modules = {}
        self.current_module = "main"
        self.types = {}
        self.classes = {}
        self.type_table = {
            "STRING": str, "INTEGER": int, "DOUBLE": float, "BYTE": int,
            "SHORT": int, "LONG": int, "SINGLE": float, "LIST": list, "ARRAY": list, "DICT": dict,
            "POINTER": lambda x: Pointer(None, x, self)
        }
        self.function_table = {}
        self.error_handler = None
        self.repl_mode = False
        self.expr_cache = {}
        self.memory_pool = {}
        self.next_address = 1000
        logging.basicConfig(level=logging.INFO)

    def parse_program(self, code, module_name="main"):
        # burada yeni parse programı yazılacak
        pass

    def current_scope(self):
        return self.scopes[-1]

    def execute_command(self, command, scope_name=None):
        # burada execute komutları güncellenecek
        pass

    def evaluate_expression(self, expr, scope_name=None):
        # burada expression evaluate edilecek
        pass

    def run(self, code=None):
        if code:
            self.parse_program(code)
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.program):
            command, scope_name = self.program[self.program_counter]
            self.execute_command(command, scope_name)
            self.program_counter += 1
            
import re
import logging

from collections import namedtuple
import struct as py_struct

class StructInstance:
    def __init__(self, fields, type_table, types):
        self.fields = {name: None for name, _ in fields}
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.types = types

    def set_field(self, field_name, value):
        if field_name not in self.fields:
            raise ValueError(f"Invalid field: {field_name}")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info['kind'] in ('STRUCT', 'CLASS'):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"Expected StructInstance or ClassInstance for {field_name}")
            elif type_info['kind'] == 'UNION':
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"Expected UnionInstance for {field_name}")
            self.fields[field_name] = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except Exception:
                    raise TypeError(f"Type mismatch for {field_name}: expected {expected_type.__name__}")
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.fields:
            raise ValueError(f"Invalid field: {field_name}")
        return self.fields[field_name]

class UnionInstance:
    def __init__(self, fields, type_table, types):
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.types = types
        self.active_field = None
        self.value = bytearray(8)

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Invalid field: {field_name}")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info['kind'] in ('STRUCT', 'CLASS'):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"Expected StructInstance or ClassInstance for {field_name}")
            elif type_info['kind'] == 'UNION':
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"Expected UnionInstance for {field_name}")
            self.active_field = field_name
            self.value = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except Exception:
                    raise TypeError(f"Type mismatch for {field_name}: expected {expected_type.__name__}")
            self.active_field = field_name
            fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
                   "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(field_type, "8s")
            if fmt == "8s":
                value = str(value).encode('utf-8')[:8].ljust(8, b'\0')
            else:
                value = py_struct.pack(fmt, value)
            self.value[:len(value)] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Invalid field: {field_name}")
        if self.active_field != field_name:
            raise ValueError(f"Field {field_name} not active")
        return self.value

class ArrayInstance:
    def __init__(self, dimensions, element_type, type_table, types):
        self.dimensions = dimensions
        self.element_type = element_type.upper()
        self.type_table = type_table
        self.types = types
        total_size = 1
        for dim in dimensions:
            total_size *= dim
        self.elements = [None] * total_size

    def set_element(self, indices, value):
        index = self._flatten_index(indices)
        self.elements[index] = value

    def get_element(self, indices):
        index = self._flatten_index(indices)
        return self.elements[index]

    def _flatten_index(self, indices):
        index = 0
        multiplier = 1
        for size, idx in zip(reversed(self.dimensions), reversed(indices)):
            index += idx * multiplier
            multiplier *= size
        return index

class ClassInstance:
    def __init__(self, class_info, type_table, types, interpreter):
        self.class_info = class_info
        self.type_table = type_table
        self.types = types
        self.interpreter = interpreter
        self.fields = {name: None for name, _ in class_info["fields"] if class_info["access"].get(name, "PUBLIC") == "PUBLIC"}
        self.field_types = {name: type_name for name, type_name in class_info["fields"]}
        self.access = class_info["access"]
        self.methods = class_info["methods"]
        self.parent = class_info.get("parent")

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Invalid field: {field_name}")
        self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Invalid field: {field_name}")
        return self.fields[field_name]

    def call_method(self, method_name, args):
        if method_name not in self.methods:
            raise ValueError(f"Invalid method: {method_name}")
        method = self.methods[method_name]
        self.interpreter.current_class = self
        self.interpreter.scopes.append({"SELF": self})
        for param, arg in zip(method["params"], args):
            self.interpreter.current_scope()[param[0]] = arg
        for cmd in method["body"]:
            self.interpreter.execute_command(cmd)
        self.interpreter.scopes.pop()
        del self.interpreter.current_class

# Devam edecek: pdsXInterpreter tam modernize edilmiş haliyle (parse_program, execute_command, run, evaluate_expression)...
# Burada kaldigimiz yerden, pdsXInterpreter guncel ve gelismis haliyle devam ediyoruz

class pdsXInterpreter:
    def __init__(self):
        self.program = []
        self.program_counter = 0
        self.global_vars = {}
        self.scopes = [{}]
        self.running = False
        self.modules = {}
        self.current_module = "main"
        self.types = {}
        self.type_table = {
            "STRING": str, "INTEGER": int, "DOUBLE": float, "BYTE": int,
            "SHORT": int, "LONG": int, "SINGLE": float,
            "LIST": list, "ARRAY": list, "DICT": dict,
            "POINTER": lambda x: Pointer(None, x, self)
        }
        self.function_table = {}
        self.error_handler = None
        self.repl_mode = False
        self.expr_cache = {}
        self.memory_pool = {}
        self.next_address = 1000
        self.current_class = None
        logging.basicConfig(level=logging.INFO)

    def parse_program(self, code, module_name="main"):
        self.current_module = module_name
        self.modules[module_name] = {
            "program": [], "functions": {}, "subs": {}, "classes": {}, "types": {}, "labels": {}
        }
        current_type = None
        current_enum = None
        current_class = None
        current_sub = None
        type_fields = {}
        enum_values = {}
        class_info = {}
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            line_upper = line.upper()

            if line_upper.startswith("TYPE ") or line_upper.startswith("STRUCT "):
                type_name = line.split()[1]
                current_type = type_name
                type_fields[current_type] = []
            elif line_upper.startswith("END TYPE") or line_upper.startswith("END STRUCT"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[current_type]}
                current_type = None
            elif line_upper.startswith("UNION "):
                union_name = line.split()[1]
                current_type = union_name
                type_fields[current_type] = []
            elif line_upper.startswith("END UNION"):
                self.types[current_type] = {"kind": "UNION", "fields": type_fields[current_type]}
                current_type = None
            elif line_upper.startswith("ENUM "):
                enum_name = line.split()[1]
                current_enum = enum_name
                enum_values[current_enum] = {}
            elif line_upper.startswith("END ENUM"):
                self.types[current_enum] = {"kind": "ENUM", "values": enum_values[current_enum]}
                current_enum = None
            elif line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+(INHERITS|EXTENDS)\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, _, parent_name = match.groups()
                    current_class = class_name
                    class_info[current_class] = {"fields": [], "methods": {}, "access": {}, "parent": parent_name}
            elif line_upper.startswith("END CLASS"):
                self.types[current_class] = {"kind": "CLASS", **class_info[current_class]}
                current_class = None
            elif current_type:
                match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    field_name, field_type = match.groups()
                    type_fields[current_type].append((field_name, field_type))
            elif current_enum:
                match = re.match(r"(\w+)(?:\s*=\s*(\d+))?", line, re.IGNORECASE)
                if match:
                    name, value = match.groups()
                    value = int(value) if value else len(enum_values[current_enum])
                    enum_values[current_enum][name] = value
            elif current_class:
                access = "PUBLIC"
                if line_upper.startswith("PUBLIC "):
                    access = "PUBLIC"
                    line = line[len("PUBLIC "):].strip()
                elif line_upper.startswith("PRIVATE "):
                    access = "PRIVATE"
                    line = line[len("PRIVATE "):].strip()
                if line_upper.startswith("SUB "):
                    sub_name = line[4:].split("(")[0].strip()
                    params = []
                    if "(" in line and ")" in line:
                        param_str = line[line.index("(")+1:line.index(")")]
                        if param_str.strip():
                            for param in param_str.split(","):
                                param_name, param_type = [x.strip() for x in param.split("AS")]
                                params.append((param_name, param_type))
                    class_info[current_class]["methods"][sub_name] = {"params": params, "body": []}
                    current_sub = sub_name
                elif line_upper.startswith("END SUB"):
                    current_sub = None
                elif current_sub:
                    class_info[current_class]["methods"][current_sub]["body"].append(line)
                else:
                    match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                    if match:
                        field_name, field_type = match.groups()
                        class_info[current_class]["fields"].append((field_name, field_type))
                        class_info[current_class]["access"][field_name] = access
            else:
                self.program.append((line, None))
                self.modules[module_name]["program"].append((line, None))
            i += 1

# Burada ara veriyorum, birazdan devam edecegim:
# - execute_command
# - evaluate_expression
# - run
# - ileri seviye hata kontrolu
# - pointer, malloc, free, memset, memcpy gibi islemleri destekleyen
# Hepsi tam modern ve uyumlu sekilde yazilacak.

# Devam ettirmemi ister misin?

# Burada kaldigimiz yerden, pdsXInterpreter guncel ve gelismis haliyle devam ediyoruz

class pdsXInterpreter:
    def __init__(self):
        self.program = []
        self.program_counter = 0
        self.global_vars = {}
        self.scopes = [{}]
        self.running = False
        self.modules = {}
        self.current_module = "main"
        self.types = {}
        self.type_table = {
            "STRING": str, "INTEGER": int, "DOUBLE": float, "BYTE": int,
            "SHORT": int, "LONG": int, "SINGLE": float,
            "LIST": list, "ARRAY": list, "DICT": dict,
            "POINTER": lambda x: Pointer(None, x, self)
        }
        self.function_table = {}
        self.error_handler = None
        self.repl_mode = False
        self.expr_cache = {}
        self.memory_pool = {}
        self.next_address = 1000
        self.current_class = None
        logging.basicConfig(level=logging.INFO)

    def parse_program(self, code, module_name="main"):
        self.current_module = module_name
        self.modules[module_name] = {
            "program": [], "functions": {}, "subs": {}, "classes": {}, "types": {}, "labels": {}
        }
        current_type = None
        current_enum = None
        current_class = None
        current_sub = None
        type_fields = {}
        enum_values = {}
        class_info = {}
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            line_upper = line.upper()

            if line_upper.startswith("TYPE ") or line_upper.startswith("STRUCT "):
                type_name = line.split()[1]
                current_type = type_name
                type_fields[current_type] = []
            elif line_upper.startswith("END TYPE") or line_upper.startswith("END STRUCT"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[current_type]}
                current_type = None
            elif line_upper.startswith("UNION "):
                union_name = line.split()[1]
                current_type = union_name
                type_fields[current_type] = []
            elif line_upper.startswith("END UNION"):
                self.types[current_type] = {"kind": "UNION", "fields": type_fields[current_type]}
                current_type = None
            elif line_upper.startswith("ENUM "):
                enum_name = line.split()[1]
                current_enum = enum_name
                enum_values[current_enum] = {}
            elif line_upper.startswith("END ENUM"):
                self.types[current_enum] = {"kind": "ENUM", "values": enum_values[current_enum]}
                current_enum = None
            elif line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+(INHERITS|EXTENDS)\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, _, parent_name = match.groups()
                    current_class = class_name
                    class_info[current_class] = {"fields": [], "methods": {}, "access": {}, "parent": parent_name}
            elif line_upper.startswith("END CLASS"):
                self.types[current_class] = {"kind": "CLASS", **class_info[current_class]}
                current_class = None
            elif current_type:
                match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    field_name, field_type = match.groups()
                    type_fields[current_type].append((field_name, field_type))
            elif current_enum:
                match = re.match(r"(\w+)(?:\s*=\s*(\d+))?", line, re.IGNORECASE)
                if match:
                    name, value = match.groups()
                    value = int(value) if value else len(enum_values[current_enum])
                    enum_values[current_enum][name] = value
            elif current_class:
                access = "PUBLIC"
                if line_upper.startswith("PUBLIC "):
                    access = "PUBLIC"
                    line = line[len("PUBLIC "):].strip()
                elif line_upper.startswith("PRIVATE "):
                    access = "PRIVATE"
                    line = line[len("PRIVATE "):].strip()
                if line_upper.startswith("SUB "):
                    sub_name = line[4:].split("(")[0].strip()
                    params = []
                    if "(" in line and ")" in line:
                        param_str = line[line.index("(")+1:line.index(")")]
                        if param_str.strip():
                            for param in param_str.split(","):
                                param_name, param_type = [x.strip() for x in param.split("AS")]
                                params.append((param_name, param_type))
                    class_info[current_class]["methods"][sub_name] = {"params": params, "body": []}
                    current_sub = sub_name
                elif line_upper.startswith("END SUB"):
                    current_sub = None
                elif current_sub:
                    class_info[current_class]["methods"][current_sub]["body"].append(line)
                else:
                    match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                    if match:
                        field_name, field_type = match.groups()
                        class_info[current_class]["fields"].append((field_name, field_type))
                        class_info[current_class]["access"][field_name] = access
            else:
                self.program.append((line, None))
                self.modules[module_name]["program"].append((line, None))
            i += 1

# Burada ara veriyorum, birazdan devam edecegim:
# - execute_command
# - evaluate_expression
# - run
# - ileri seviye hata kontrolu
# - pointer, malloc, free, memset, memcpy gibi islemleri destekleyen
# Hepsi tam modern ve uyumlu sekilde yazilacak.

# Devam ettirmemi ister misin?
    def execute_command(self, command, scope_name=None):
        command = command.strip()
        if not command:
            return None
        command_upper = command.upper()

        try:
            # DIM (Değişken tanımı)
            if command_upper.startswith("DIM"):
                match = re.match(r"DIM\s+(\w+)(?:\(([\d, ]+)\))?\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, dim_str, var_type = match.groups()
                    if dim_str:  # Çok boyutlu dizi
                        dimensions = [int(d) for d in dim_str.replace(" ", "").split(",")]
                        self.current_scope()[var_name] = ArrayInstance(dimensions, var_type, self.type_table, self.types)
                    elif var_type.upper() in self.types:
                        type_info = self.types[var_type.upper()]
                        kind = type_info["kind"]
                        if kind == "STRUCT":
                            self.current_scope()[var_name] = StructInstance(type_info["fields"], self.type_table, self.types)
                        elif kind == "CLASS":
                            self.current_scope()[var_name] = ClassInstance(type_info, self.type_table, self.types, self)
                        elif kind == "UNION":
                            self.current_scope()[var_name] = UnionInstance(type_info["fields"], self.type_table, self.types)
                        elif kind == "ENUM":
                            self.current_scope()[var_name] = None  # ENUM başlangıçta None
                        else:
                            raise Exception(f"Desteklenmeyen tür: {var_type}")
                    elif var_type.upper() == "POINTER":
                        # Özel durum: DIM p AS POINTER TO Type
                        match_ptr = re.match(r"DIM\s+(\w+)\s+AS\s+POINTER\s+TO\s+(\w+)", command, re.IGNORECASE)
                        if match_ptr:
                            var_name, target_type = match_ptr.groups()
                            self.current_scope()[var_name] = Pointer(None, target_type, self)
                        else:
                            raise Exception("POINTER tanımı hatası")
                    else:
                        # Basit türler
                        self.current_scope()[var_name] = self.type_table.get(var_type.upper(), object)()
                    return None
                else:
                    raise Exception("DIM komutunda sözdizimi hatası")

            # LET (Değere atama)
            if command_upper.startswith("LET"):
                match = re.match(r"LET\s+(.+?)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    target, expr = match.groups()
                    value = self.evaluate_expression(expr, scope_name)

                    # Struct, Class veya Union iç alan erişimi
                    if "." in target:
                        parts = target.split(".")
                        instance = self.current_scope().get(parts[0])
                        for field in parts[1:-1]:
                            instance = instance.get_field(field)
                        field_name = parts[-1]
                        instance.set_field(field_name, value)

                    # Dizi erişimi
                    elif "(" in target and ")" in target:
                        match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
                        if match_array:
                            var_name, indices_str = match_array.groups()
                            indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                            array = self.current_scope().get(var_name)
                            if isinstance(array, ArrayInstance):
                                array.set_element(indices, value)
                            else:
                                raise Exception(f"{var_name} bir dizi değil")

                    # Pointer (işaretçi)
                    elif "*" in target:
                        ptr_name = target.replace("*", "").strip()
                        ptr = self.current_scope().get(ptr_name)
                        if isinstance(ptr, Pointer):
                            ptr.set(value)
                        else:
                            raise Exception(f"{ptr_name} bir işaretçi değil")

                    # Normal değişken ataması
                    else:
                        if target in self.current_scope():
                            self.current_scope()[target] = value
                        elif target in self.global_vars:
                            self.global_vars[target] = value
                        else:
                            raise Exception(f"Tanımlanmamış değişken: {target}")

                    return None
                else:
                    raise Exception("LET komutunda sözdizimi hatası")

            # CALL (Metod çağrısı)
            if command_upper.startswith("CALL"):
                match = re.match(r"CALL\s+(\w+)\.(\w+)\((.*)\)", command, re.IGNORECASE)
                if match:
                    obj_name, method_name, args_str = match.groups()
                    obj = self.current_scope().get(obj_name)
                    if isinstance(obj, ClassInstance):
                        args = []
                        if args_str.strip():
                            args = [self.evaluate_expression(arg.strip(), scope_name) for arg in args_str.split(",")]
                        obj.call_method(method_name, args)
                    else:
                        raise Exception(f"{obj_name} bir sınıf nesnesi değil")
                    return None

            # PRINT (Yazdırma)
            if command_upper.startswith("PRINT"):
                expr = command[5:].strip()
                value = self.evaluate_expression(expr, scope_name)
                print(value)
                return None

            # Pointer işlemleri (PTR_SET, MALLOC, FREE vs.)
            if command_upper.startswith("PTR_SET") or command_upper.startswith("MALLOC") or command_upper.startswith("FREE") or command_upper.startswith("MEMCPY") or command_upper.startswith("MEMSET"):
                # Zaten özel işaretçi fonksiyonları ayrı olarak yazılmıştı.
                return self.pointer_operations(command, scope_name)

            raise Exception(f"Bilinmeyen komut: {command}")

        except Exception as e:
            error_msg = f"PDSX Hatası: {str(e)}, Satır {self.program_counter + 1 if not self.repl_mode else 'REPL'}"
            print(error_msg)
            logging.error(error_msg)
            if self.error_handler == "RESUME":
                return None
            elif self.error_handler:
                self.program_counter = self.error_handler
            else:
                self.running = False
            return None
    def evaluate_expression(self, expr, scope_name=None):
        expr = expr.strip()

        # Struct / Class / Union alan erişimi
        if "." in expr:
            parts = expr.split(".")
            instance = self.current_scope().get(parts[0])
            for field in parts[1:]:
                if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                    instance = instance.get_field(field)
                else:
                    raise Exception(f"Geçersiz alan erişimi: {expr}")
            return instance

        # Dizi erişimi
        elif "(" in expr and ")" in expr:
            match_array = re.match(r"(\w+)\(([\d, ]+)\)", expr)
            if match_array:
                var_name, indices_str = match_array.groups()
                indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                array = self.current_scope().get(var_name)
                if isinstance(array, ArrayInstance):
                    return array.get_element(indices)
                else:
                    raise Exception(f"{var_name} bir dizi değil")
            else:
                raise Exception("Dizi sözdizimi hatası")

        # Pointer erişimi
        elif "*" in expr:
            ptr_name = expr.replace("*", "").strip()
            ptr = self.current_scope().get(ptr_name)
            if isinstance(ptr, Pointer):
                return ptr.dereference()
            else:
                raise Exception(f"{ptr_name} bir işaretçi değil")

        # ENUM değerleri
        elif expr in self.types and self.types[expr]["kind"] == "ENUM":
            return self.types[expr]["values"]

        # Normal değişken veya matematiksel ifade
        namespace = {}
        namespace.update(self.global_vars)
        namespace.update(self.current_scope())
        namespace.update(self.function_table)

        try:
            return eval(expr, namespace)
        except Exception as e:
            raise Exception(f"İfade değerlendirme hatası: {expr}, Hata: {str(e)}")
    def run(self, code=None):
        if code:
            self.parse_program(code)
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.program):
            command, scope_name = self.program[self.program_counter]
            self.execute_command(command, scope_name)
            self.program_counter += 1
    def pointer_operations(self, command, scope_name=None):
        command_upper = command.upper()

        if command_upper.startswith("PTR_SET"):
            match = re.match(r"PTR_SET\s+(\w+)\s+TO\s+(.+)", command, re.IGNORECASE)
            if match:
                ptr_name, expr = match.groups()
                ptr = self.current_scope().get(ptr_name)
                if not isinstance(ptr, Pointer):
                    raise Exception(f"{ptr_name} bir işaretçi değil")

                if expr.startswith("&"):
                    target = expr[1:].strip()
                    if "(" in target and ")" in target:
                        match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
                        if match_array:
                            var_name, indices_str = match_array.groups()
                            indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                            array = self.current_scope().get(var_name)
                            if isinstance(array, ArrayInstance):
                                addr = self.next_address
                                self.memory_pool[addr] = {
                                    "value": array.get_element(indices),
                                    "type": array.element_type,
                                    "refs": 1
                                }
                                self.next_address += array.element_size
                                ptr.address = addr
                                ptr.dimensions = array.dimensions
                            else:
                                raise Exception(f"{var_name} bir dizi değil")
                    else:
                        if target in self.current_scope():
                            addr = self.next_address
                            self.memory_pool[addr] = {
                                "value": self.current_scope()[target],
                                "type": ptr.target_type,
                                "refs": 1
                            }
                            self.next_address += 8
                            ptr.address = addr
                        else:
                            raise Exception(f"Değişken bulunamadı: {target}")
                else:
                    addr = self.evaluate_expression(expr, scope_name)
                    if addr in self.memory_pool:
                        ptr.address = addr
                    else:
                        raise Exception(f"Geçersiz adres: {addr}")
            return None

        elif command_upper.startswith("MALLOC"):
            match = re.match(r"MALLOC\s+(\w+)\s+SIZE\s+(\d+)\s+AS\s+(\w+)", command, re.IGNORECASE)
            if match:
                var_name, size, var_type = match.groups()
                size = int(size)
                addr = self.next_address
                self.memory_pool[addr] = {
                    "value": None,
                    "type": var_type,
                    "refs": 1,
                    "size": size
                }
                self.next_address += size
                self.current_scope()[var_name] = Pointer(addr, var_type, self)
            return None

        elif command_upper.startswith("FREE"):
            match = re.match(r"FREE\s+(\w+)", command, re.IGNORECASE)
            if match:
                ptr_name = match.group(1)
                ptr = self.current_scope().get(ptr_name)
                if isinstance(ptr, Pointer) and ptr.address in self.memory_pool:
                    self.memory_pool[ptr.address]["refs"] -= 1
                    if self.memory_pool[ptr.address]["refs"] <= 0:
                        del self.memory_pool[ptr.address]
                    ptr.address = None
                else:
                    raise Exception(f"Geçersiz işaretçi: {ptr_name}")
            return None

        elif command_upper.startswith("MEMCPY"):
            match = re.match(r"MEMCPY\s+(\w+)\s+FROM\s+(\w+)\s+SIZE\s+(\d+)", command, re.IGNORECASE)
            if match:
                dest_ptr_name, src_ptr_name, size = match.groups()
                size = int(size)
                dest_ptr = self.current_scope().get(dest_ptr_name)
                src_ptr = self.current_scope().get(src_ptr_name)
                if isinstance(dest_ptr, Pointer) and isinstance(src_ptr, Pointer):
                    if src_ptr.address in self.memory_pool and dest_ptr.address in self.memory_pool:
                        self.memory_pool[dest_ptr.address]["value"] = self.memory_pool[src_ptr.address]["value"]
                    else:
                        raise Exception("Geçersiz bellek adresi")
                else:
                    raise Exception("Geçersiz işaretçi")
            return None

        elif command_upper.startswith("MEMSET"):
            match = re.match(r"MEMSET\s+(\w+)\s+VALUE\s+(.+)\s+SIZE\s+(\d+)", command, re.IGNORECASE)
            if match:
                ptr_name, value_expr, size = match.groups()
                size = int(size)
                ptr = self.current_scope().get(ptr_name)
                value = self.evaluate_expression(value_expr, scope_name)
                if isinstance(ptr, Pointer) and ptr.address in self.memory_pool:
                    self.memory_pool[ptr.address]["value"] = value
                else:
                    raise Exception("Geçersiz işaretçi")
            return None

        else:
            raise Exception(f"Bilinmeyen pointer komutu: {command}")


#pdfs icin libX_core
import os
import glob
import json
import shutil
import zipfile
import re
import time
import datetime
import subprocess
import numpy as np
from types import SimpleNamespace
from threading import Thread
import ctypes

class Stack:
    """Yığın veri yapısı"""
    def __init__(self):
        self.items = []
    def push(self, item):
        self.items.append(item)
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        raise Exception("Yığın boş")
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        raise Exception("Yığın boş")
    def is_empty(self):
        return len(self.items) == 0
    def size(self):
        return len(self.items)

class Queue:
    """Kuyruk veri yapısı"""
    def __init__(self):
        self.items = []
    def enqueue(self, item):
        self.items.append(item)
    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        raise Exception("Kuyruk boş")
    def peek(self):
        if not self.is_empty():
            return self.items[0]
        raise Exception("Kuyruk boş")
    def is_empty(self):
        return len(self.items) == 0
    def size(self):
        return len(self.items)

class LibXCore:
    def __init__(self):
        self.default_encoding = "utf-8"
        self.dll_handles = {}
        self.modules = {}
        self.omega_global = None

    # Çekirdek İşlevler
    def set_encoding(self, encoding):
        """Varsayılan dosya kodlamasını ayarlar."""
        self.default_encoding = encoding

    def load(self, module_path):
        """Modül dosyalarını yükler (.hz, .hx, .libx, .basx)."""
        if not os.path.exists(module_path):
            raise Exception(f"Modül bulunamadı: {module_path}")
        valid_extensions = (".hz", ".hx", ".libx", ".basx")
        if not module_path.endswith(valid_extensions):
            raise Exception("Geçersiz dosya uzantısı")
        with open(module_path, "r", encoding=self.default_encoding) as f:
            self.modules[module_path] = f.read()
        return True

    def list_lib(self):
        """Yüklenen modülleri listeler."""
        return list(self.modules.keys())

    def load_dll(self, dll_name):
        """DLL dosyasını yükler."""
        dll = ctypes.WinDLL(dll_name)
        self.dll_handles[dll_name] = dll
        return SimpleNamespace(call=lambda func_name, *args: getattr(dll, func_name)(*args))

    # Omega ve Kontrol Yapıları
    def omega(self):
        """Global omega bağlamını döndürür veya ayarlar."""
        return self.omega_global

    def ifthen(self, condition, then_value, else_value=None):
        """Ternary benzeri koşullu ifade."""
        return then_value if condition else else_value

    # Koleksiyon İşlemleri
    def each(self, iterable, func):
        """Iterable üzerinde fonksiyon uygular."""
        return [func(x) for x in iterable]

    def select(self, iterable, condition):
        """Koşula uyan elemanları seçer."""
        return [x for x in iterable if condition(x)]

    def insert(self, collection, index, value):
        """Koleksiyona eleman ekler."""
        collection.insert(index, value)

    def remove(self, collection, value):
        """Koleksiyondan elemanı kaldırır."""
        collection.remove(value)

    def pop(self, collection, index=-1):
        """Koleksiyondan eleman çıkarır."""
        return collection.pop(index)

    def clear(self, collection):
        """Koleksiyonu temizler."""
        collection.clear()

    def slice(self, collection, start, end):
        """Koleksiyondan dilim alır."""
        return collection[start:end]

    def keys(self, dictionary):
        """Sözlüğün anahtarlarını döndürür."""
        return list(dictionary.keys())

    # Matematiksel ve İstatistiksel İşlevler
    def sum(self, iterable=None, *args):
        """Iterable'ın toplamını hesaplar."""
        if iterable is not None:
            return np.sum(iterable) if iterable else 0
        return np.sum(args) if args else 0

    def mean(self, iterable=None, *args):
        """Iterable'ın ortalamasını hesaplar."""
        if iterable is not None:
            return np.mean(iterable) if iterable else 0
        return np.mean(args) if args else 0

    def min(self, iterable=None, *args):
        """Minimum değeri bulur."""
        if iterable is not None:
            return min(iterable) if iterable else None
        return min(args) if args else None

    def max(self, iterable=None, *args):
        """Maksimum değeri bulur."""
        if iterable is not None:
            return max(iterable) if iterable else None
        return max(args) if args else None

    def median(self, iterable):
        """Ortanca değeri hesaplar."""
        return np.median(iterable)

    def std(self, iterable):
        """Standart sapmayı hesaplar."""
        return np.std(iterable)

    def correlation(self, x, y):
        """İki dizi arasındaki korelasyonu hesaplar."""
        return np.corrcoef(x, y)[0, 1]

    def floor(self, x):
        """Aşağı yuvarlar."""
        return int(x // 1)

    def ceil(self, x):
        """Yukarı yuvarlar."""
        return int(-(-x // 1))

    def round(self, x, digits=0):
        """Sayıyı yuvarlar."""
        return round(x, digits)

    def random_int(self, start, end):
        """Rastgele tamsayı üretir."""
        import random
        return random.randint(start, end)

    # String İşlemleri
    def split(self, s, delimiter):
        """String'i böler."""
        return s.split(delimiter)

    def join(self, items, delimiter):
        """String'leri birleştirir."""
        return delimiter.join(items)

    def trim(self, s):
        """Baştaki ve sondaki boşlukları kaldırır."""
        return s.strip()

    def replace(self, s, old, new):
        """String'de değiştirme yapar."""
        return s.replace(old, new)

    def format(self, s, *args):
        """String formatlama."""
        return s.format(*args)

    def match_regex(self, s, pattern):
        """Regex eşleşmesini kontrol eder."""
        return bool(re.match(pattern, s))

    def find_regex(self, s, pattern):
        """Regex ile eşleşenleri bulur."""
        return re.findall(pattern, s)

    def len(self, obj):
        """String veya koleksiyon uzunluğunu döndürür."""
        return len(obj)

    def val(self, s):
        """String'i sayıya çevirir."""
        try:
            return float(s) if s.replace(".", "").replace("-", "").isdigit() else 0
        except:
            return 0

    def str(self, value):
        """Değeri string'e çevirir."""
        return str(value)

    # Dosya Sistemi İşlemleri
    def open(self, path, mode):
        """Dosyayı açar."""
        return open(path, mode, encoding=self.default_encoding)

    def read(self, file):
        """Dosyadan okur."""
        return file.read()

    def write(self, file, data):
        """Dosyaya yazar."""
        file.write(data)

    def close(self, file):
        """Dosyayı kapatır."""
        file.close()

    def read_lines(self, path):
        """Dosyayı satır satır okur."""
        with open(path, "r", encoding=self.default_encoding) as f:
            return f.readlines()

    def write_json(self, obj, path):
        """Nesneyi JSON olarak dosyaya yazar."""
        with open(path, "w", encoding=self.default_encoding) as f:
            json.dump(obj, f)

    def read_json(self, path):
        """JSON dosyasını okur."""
        with open(path, "r", encoding=self.default_encoding) as f:
            return json.load(f)

    def list_dir(self, path):
        """Dizindeki dosyaları listeler."""
        return os.listdir(path)

    def exists(self, path):
        """Dosyanın varlığını kontrol eder."""
        return os.path.exists(path)

    def mkdir(self, path):
        """Dizin oluşturur."""
        os.makedirs(path, exist_ok=True)

    def join_path(self, *paths):
        """Dosya yollarını birleştirir."""
        return os.path.join(*paths)

    def copy_file(self, src, dst):
        """Dosyayı kopyalar."""
        shutil.copy2(src, dst)

    def move_file(self, src, dst):
        """Dosyayı taşır."""
        shutil.move(src, dst)

    def delete_file(self, path):
        """Dosyayı siler."""
        os.remove(path)

    def file_size(self, path):
        """Dosyanın bayt cinsinden boyutunu döndürür."""
        return os.path.getsize(path)

    def file_mtime(self, path):
        """Dosyanın son değiştirilme zamanını döndürür."""
        return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")

    def file_exists(self, path):
        """Dosyanın varlığını kontrol eder (exists alias'ı)."""
        return os.path.exists(path)

    def dir_copy(self, src, dst):
        """Dizini kopyalar."""
        shutil.copytree(src, dst, dirs_exist_ok=True)

    def dir_remove(self, path):
        """Dizini ve içeriğini siler."""
        shutil.rmtree(path)

    def compress_zip(self, files, output):
        """Dosyaları ZIP'e sıkıştırır."""
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in files:
                zf.write(file)

    def extract_zip(self, zip_file, output_dir):
        """ZIP dosyasını çıkarır."""
        with zipfile.ZipFile(zip_file, "r") as zf:
            zf.extractall(output_dir)

    def find_files(self, path, pattern):
        """Kalıpla eşleşen dosyaları bulur."""
        return glob.glob(os.path.join(path, pattern), recursive=True)

    # Ağ İşlemleri
    def download(self, url, path):
        """URL'den dosya indirir."""
        import requests
        response = requests.get(url)
        with open(path, "wb") as f:
            f.write(response.content)

    def ping(self, host):
        """Host'un erişilebilirliğini kontrol eder."""
        import socket
        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False

    # Zaman ve Tarih İşlemleri
    def time_now(self):
        """Geçerli saati döndürür."""
        return time.strftime("%H:%M:%S")

    def date_now(self):
        """Geçerli tarihi döndürür."""
        return time.strftime("%Y-%m-%d")

    def timer(self):
        """Geçerli zaman damgasını döndürür."""
        return time.time()

    def sleep(self, seconds):
        """Programı duraklatır."""
        time.sleep(seconds)

    def date_diff(self, date1, date2, unit="days"):
        """Tarihler arasındaki farkı hesaplar."""
        d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
        delta = d2 - d1
        if unit == "days":
            return delta.days
        elif unit == "seconds":
            return delta.total_seconds()
        raise Exception("Geçersiz birim")

    # Hata Yönetimi ve Debugging
    def assert(self, condition, message="Assertion failed"):
        """Koşulu kontrol eder, başarısızsa hata fırlatır."""
        if not condition:
            raise Exception(message)

    def log(self, message):
        """Mesajı loglar."""
        print(f"LOG: {message}")

    def trace(self):
        """Çalışma zamanı yığın izini döndürür."""
        import traceback
        return traceback.format_stack()

    def try_catch(self, block, handler):
        """Hata yakalama mekanizması."""
        try:
            return block()
        except Exception as e:
            return handler(str(e))

    # Asenkron İşlemler
    def run_async(self, func):
        """Fonksiyonu asenkron çalıştırır."""
        t = Thread(target=func)
        t.start()
        return t

    def wait(self, tasks):
        """Asenkron görevleri bekler."""
        for t in tasks:
            t.join()

    # Veri Yapısı İşlemleri
    def create_stack(self):
        """Yeni yığın oluşturur."""
        return Stack()

    def push(self, stack, item):
        """Yığına eleman ekler."""
        stack.push(item)

    def pop_stack(self, stack):
        """Yığından eleman çıkarır."""
        return stack.pop()

    def peek(self, stack):
        """Yığının en üstteki elemanını okur."""
        return stack.peek()

    def stack_is_empty(self, stack):
        """Yığının boş olup olmadığını kontrol eder."""
        return stack.is_empty()

    def stack_size(self, stack):
        """Yığındaki eleman sayısını döndürür."""
        return stack.size()

    def create_queue(self):
        """Yeni kuyruk oluşturur."""
        return Queue()

    def enqueue(self, queue, item):
        """Kuyruğa eleman ekler."""
        queue.enqueue(item)

    def dequeue(self, queue):
        """Kuyruktan eleman çıkarır."""
        return queue.dequeue()

    def queue_peek(self, queue):
        """Kuyruğun başındaki elemanı okur."""
        return queue.peek()

    def queue_is_empty(self, queue):
        """Kuyruğun boş olup olmadığını kontrol eder."""
        return queue.is_empty()

    def queue_size(self, queue):
        """Kuyruktaki eleman sayısını döndürür."""
        return queue.size()

    def merge(self, col1, col2):
        """Koleksiyonları birleştirir."""
        if isinstance(col1, list) and isinstance(col2, list):
            return col1 + col2
        elif isinstance(col1, dict) and isinstance(col2, dict):
            return {**col1, **col2}
        raise Exception("Geçersiz veri tipi")

    def sort(self, iterable, key=None):
        """Iterable'ı sıralar."""
        return sorted(iterable, key=key)

    def set_union(self, set1, set2):
        """Kümelerin birleşimini döndürür."""
        return set1 | set2

    def set_intersection(self, set1, set2):
        """Kümelerin kesişimini döndürür."""
        return set1 & set2

    def set_difference(self, set1, set2):
        """Kümelerin farkını döndürür."""
        return set1 - set2

    def set_add(self, set_obj, item):
        """Kümeye eleman ekler."""
        set_obj.add(item)

    def set_remove(self, set_obj, item):
        """Kümeden elemanı kaldırır."""
        set_obj.discard(item)

    # Sistem ve Performans İzleme
    def memory_usage(self):
        """Programın bellek kullanımını döndürür."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB cinsinden

    def cpu_count(self):
        """CPU çekirdek sayısını döndürür."""
        import multiprocessing
        return multiprocessing.cpu_count()

    def shell(self, cmd):
        """Sistem komutu çalıştırır."""
        return subprocess.getoutput(cmd)

    def get_cwd(self):
        """Geçerli çalışma dizinini döndürür."""
        return os.getcwd()

    # Yardımcı İşlevler
    def type_of(self, value):
        """Değişkenin tipini döndürür."""
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "FLOAT"
        elif isinstance(value, str):
            return "STRING"
        elif isinstance(value, list):
            return "LIST"
        elif isinstance(value, dict):
            return "DICT"
        elif isinstance(value, set):
            return "SET"
        elif isinstance(value, Stack):
            return "STACK"
        elif isinstance(value, Queue):
            return "QUEUE"
        return "UNKNOWN"

    def is_empty(self, collection):
        """Koleksiyonun boş olup olmadığını kontrol eder."""
        return len(collection) == 0

    def getenv(self, var):
        """Çevresel değişkeni döndürür."""
        return os.getenv(var, "")

    def exit(self, code=0):
        """Programı sonlandırır."""
        import sys
        sys.exit(code)
        
pdsx v10m interpreterimde asagida ekledigim kodun getirdigi ozelikller bulunuyormu?

import re
import logging
import struct as py_struct
from collections import namedtuple

# Sınıflar
class StructInstance:
    def __init__(self, fields, type_table, types):
        self.fields = {name: None for name, _ in fields}
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.types = types
        self.sizes = {name: self._get_size(type_name) for name, type_name in fields}
        self.offsets = {}
        offset = 0
        for name in self.fields:
            self.offsets[name] = offset
            offset += self.sizes[name]

    def set_field(self, field_name, value):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.fields[field_name] = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        return self.fields[field_name]

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class UnionInstance:
    def __init__(self, fields, type_table, types):
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.types = types
        self.active_field = None
        self.value = bytearray(8)
        self.sizes = {name: self._get_size(type_name) for name, type_name in fields}

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.active_field = field_name
            self.value = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.active_field = field_name
            fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
                   "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(field_type, "8s")
            if fmt == "8s":
                value = str(value).encode('utf-8')[:8].ljust(8, b'\0')
            else:
                value = py_struct.pack(fmt, value)
            self.value[:len(value)] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.active_field != field_name:
            raise ValueError(f"{field_name} alanı aktif değil")
        if self.field_types[field_name].upper() in self.types:
            return self.value
        fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
               "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(self.field_types[field_name].upper(), "8s")
        try:
            if fmt == "8s":
                return self.value.decode('utf-8').rstrip('\0')
            return py_struct.unpack(fmt, self.value[:self.sizes[field_name]])[0]
        except:
            raise ValueError(f"{field_name} alanından veri okunamadı")

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class ArrayInstance:
    def __init__(self, dimensions, element_type, type_table, types):
        self.dimensions = dimensions
        self.element_type = element_type.upper()
        self.type_table = type_table
        self.types = types
        self.element_size = self._get_size(element_type)
        total_size = 1
        for dim in dimensions:
            total_size *= dim
        self.elements = [None] * total_size
        self.strides = []
        stride = self.element_size
        for dim in reversed(dimensions):
            self.strides.insert(0, stride)
            stride *= dim

    def set_element(self, indices, value):
        index = self._get_index(indices)
        if self.element_type in self.types:
            type_info = self.types[self.element_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"Dizi elemanı için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"Dizi elemanı için UnionInstance bekleniyor")
            self.elements[index] = value
        else:
            expected_type = self.type_table.get(self.element_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"Dizi elemanı için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.elements[index] = value

    def get_element(self, indices):
        index = self._get_index(indices)
        return self.elements[index]

    def _get_index(self, indices):
        if len(indices) != len(self.dimensions):
            raise ValueError(f"Beklenen {len(self.dimensions)} indeks, ancak {len(indices)} alındı")
        for i, idx in enumerate(indices):
            if not 0 <= idx < self.dimensions[i]:
                raise ValueError(f"Geçersiz indeks: {idx}")
        index = 0
        for i, idx in enumerate(indices):
            index += idx * self.strides[i] // self.element_size
        return index

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class Pointer:
    def __init__(self, address, target_type, interpreter, dimensions=None):
        self.address = address
        self.target_type = target_type.upper()
        self.interpreter = interpreter
        self.dimensions = dimensions
        self.element_size = self._get_size(target_type)
        self.strides = None
        if dimensions:
            self.strides = []
            stride = self.element_size
            for dim in reversed(dimensions):
                self.strides.insert(0, stride)
                stride *= dim

    def dereference(self):
        if self.address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi adresi: {self.address}")
        value = self.interpreter.memory_pool[self.address]["value"]
        if self.target_type in self.interpreter.types:
            type_info = self.interpreter.types[self.target_type]
            if type_info["kind"] in ("STRUCT", "CLASS") and not isinstance(value, (StructInstance, ClassInstance)):
                raise TypeError(f"StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION" and not isinstance(value, UnionInstance):
                raise TypeError(f"UnionInstance bekleniyor")
        else:
            expected_type = self.interpreter.type_table.get(self.target_type, object)
            if not isinstance(value, expected_type):
                raise TypeError(f"Beklenen tip {expected_type.__name__}, ancak {type(value).__name__} bulundu")
        return value

    def set(self, value):
        if self.address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi adresi: {self.address}")
        if self.target_type in self.interpreter.types:
            type_info = self.interpreter.types[self.target_type]
            if type_info["kind"] in ("STRUCT", "CLASS") and not isinstance(value, (StructInstance, ClassInstance)):
                raise TypeError(f"StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION" and not isinstance(value, UnionInstance):
                raise TypeError(f"UnionInstance bekleniyor")
        else:
            expected_type = self.interpreter.type_table.get(self.target_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"Beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
        self.interpreter.memory_pool[self.address]["value"] = value

    def add_offset(self, offset):
        if self.dimensions and self.strides:
            new_address = self.address + offset * self.strides[-1]
        else:
            new_address = self.address + offset * self.element_size
        if new_address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi aritmetiği: {new_address}")
        return Pointer(new_address, self.target_type, self.interpreter, self.dimensions)

    def _get_size(self, type_name):
        if type_name.upper() in self.interpreter.types:
            type_info = self.interpreter.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class ClassInstance:
    def __init__(self, class_info, type_table, types, interpreter):
        self.class_info = class_info
        self.type_table = type_table
        self.types = types
        self.interpreter = interpreter
        self.fields = {name: None for name, _ in class_info["fields"] if class_info["access"].get(name, "PUBLIC") == "PUBLIC"}
        self.field_types = {name: type_name for name, type_name in class_info["fields"]}
        self.access = class_info["access"]
        self.methods = class_info["methods"]
        self.parent = class_info.get("parent")

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.access.get(field_name, "PUBLIC") == "PRIVATE" and not hasattr(self.interpreter, "current_class"):
            raise ValueError(f"{field_name} özel bir alan")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.fields[field_name] = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.access.get(field_name, "PUBLIC") == "PRIVATE" and not hasattr(self.interpreter, "current_class"):
            raise ValueError(f"{field_name} özel bir alan")
        return self.fields[field_name]

    def call_method(self, method_name, args):
        if method_name not in self.methods:
            raise ValueError(f"Geçersiz metod: {method_name}")
        method = self.methods[method_name]
        self.interpreter.current_class = self
        self.interpreter.scopes.append({"SELF": self})
        for param, arg in zip(method["params"], args):
            self.interpreter.current_scope()[param[0]] = arg
        for cmd in method["body"]:
            self.interpreter.execute_command(cmd)
        self.interpreter.scopes.pop()
        del self.interpreter.current_class

# pdsXInterpreter sınıfı
class pdsXInterpreter:
    def __init__(self):
        self.program = []
        self.program_counter = 0
        self.global_vars = {}
        self.scopes = [{}]
        self.running = False
        self.modules = {}
        self.current_module = "main"
        self.types = {}
        self.type_table = {
            "STRING": str, "INTEGER": int, "DOUBLE": float, "BYTE": int,
            "SHORT": int, "LONG": int, "SINGLE": float, "LIST": list, "ARRAY": list, "DICT": dict,
            "POINTER": lambda x: Pointer(None, x, self)
        }
        self.function_table = {}
        self.error_handler = None
        self.repl_mode = False
        self.expr_cache = {}
        self.memory_pool = {}
        self.next_address = 1000
        logging.basicConfig(level=logging.INFO)

    def parse_program(self, code, module_name="main"):
        self.current_module = module_name
        self.modules[module_name] = {
            "program": [], "functions": {}, "subs": {}, "classes": {}, "types": {}, "labels": {}
        }
        current_sub = None
        current_function = None
        current_type = None
        current_class = None
        current_enum = None
        type_fields = {}
        enum_values = {}
        class_info = {}
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            line_upper = line.upper()
            # TYPE
            if line_upper.startswith("TYPE "):
                type_name = line[5:].strip()
                current_type = type_name
                type_fields[type_name] = []
                i += 1
            elif line_upper.startswith("END TYPE"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[current_type]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # STRUCT
            elif line_upper.startswith("STRUCT "):
                struct_name = line[7:].strip()
                current_type = struct_name
                type_fields[struct_name] = []
                i += 1
            elif line_upper.startswith("END STRUCT"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[struct_name]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # UNION
            elif line_upper.startswith("UNION "):
                union_name = line[6:].strip()
                current_type = union_name
                type_fields[union_name] = []
                i += 1
            elif line_upper.startswith("END UNION"):
                self.types[current_type] = {"kind": "UNION", "fields": type_fields[union_name]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # ENUM
            elif line_upper.startswith("ENUM "):
                enum_name = line[5:].strip()
                current_enum = enum_name
                enum_values[enum_name] = {}
                i += 1
            elif line_upper.startswith("END ENUM"):
                self.types[current_enum] = {"kind": "ENUM", "values": enum_values[current_enum]}
                self.modules[module_name]["types"][current_enum] = self.types[current_enum]
                current_enum = None
                i += 1
            # CLASS
            elif line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+INHERITS\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_name = match.groups()
                    current_class = class_name
                    class_info[class_name] = {
                        "fields": [], "methods": {}, "access": {}, "parent": parent_name
                    }
                i += 1
            elif line_upper.startswith("END CLASS"):
                self.types[current_class] = {"kind": "CLASS", **class_info[current_class]}
                self.modules[module_name]["types"][current_class] = self.types[current_class]
                current_class = None
                i += 1
            elif current_type:
                match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    field_name, field_type = match.groups()
                    type_fields[current_type].append((field_name, field_type))
                else:
                    raise Exception(f"Tanım hatası: {line}")
                i += 1
            elif current_enum:
                match = re.match(r"(\w+)(?:\s*=\s*(\d+))?", line, re.IGNORECASE)
                if match:
                    name, value = match.groups()
                    value = int(value) if value else len(enum_values[current_enum])
                    enum_values[current_enum][name] = value
                else:
                    raise Exception(f"ENUM tanımı hatası: {line}")
                i += 1
            elif current_class:
                if line_upper.startswith(("PUBLIC ", "PRIVATE ")):
                    access = "PUBLIC" if line_upper.startswith("PUBLIC ") else "PRIVATE"
                    line = line[len(access):].strip()
                    line_upper = line.upper()
                else:
                    access = "PUBLIC"
                if line_upper.startswith("SUB "):
                    sub_name = line[4:].split("(")[0].strip()
                    params = []
                    if "(" in line and ")" in line:
                        param_str = line[line.index("(")+1:line.index(")")]
                        if param_str.strip():
                            for param in param_str.split(","):
                                param_name, param_type = [x.strip() for x in param.split("AS")]
                                params.append((param_name, param_type))
                    class_info[current_class]["methods"][sub_name] = {"params": params, "body": []}
                    current_sub = sub_name
                    i += 1
                elif line_upper.startswith("END SUB"):
                    current_sub = None
                    i += 1
                elif current_sub:
                    class_info[current_class]["methods"][current_sub]["body"].append(line)
                    i += 1
                else:
                    match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                    if match:
                        field_name, field_type = match.groups()
                        class_info[current_class]["fields"].append((field_name, field_type))
                        class_info[current_class]["access"][field_name] = access
                    else:
                        raise Exception(f"Sınıf tanımı hatası: {line}")
                    i += 1
            else:
                if current_sub or current_function:
                    self.program.append((line, current_sub or current_function))
                    self.modules[module_name]["program"].append((line, current_sub or current_function))
                else:
                    self.program.append((line, None))
                    self.modules[module_name]["program"].append((line, None))
                i += 1

    def current_scope(self):
        return self.scopes[-1]

    def execute_command(self, command, scope_name=None):
        command = command.strip()
        if not command:
            return None
        command_upper = command.upper()

        try:
            # DIM
            if command_upper.startswith("DIM"):
                match = re.match(r"DIM\s+(\w+)(?:\(([\d, ]+)\))?\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, dim_str, var_type = match.groups()
                    if dim_str:  # Dizi tanımlama
                        dimensions = [int(d) for d in dim_str.replace(" ", "").split(",")]
                        self.current_scope()[var_name] = ArrayInstance(dimensions, var_type, self.type_table, self.types)
                    elif var_type in self.types:
                        type_info = self.types[var_type]
                        if type_info["kind"] in ("STRUCT", "CLASS"):
                            self.current_scope()[var_name] = (
                                StructInstance(type_info["fields"], self.type_table, self.types)
                                if type_info["kind"] == "STRUCT"
                                else ClassInstance(type_info, self.type_table, self.types, self)
                            )
                        elif type_info["kind"] == "UNION":
                            self.current_scope()[var_name] = UnionInstance(type_info["fields"], self.type_table, self.types)
                        elif type_info["kind"] == "ENUM":
                            self.current_scope()[var_name] = None
                        else:
                            raise Exception(f"Tanımlanamayan veri tipi: {var_type}")
                    elif var_type == "POINTER":
                        match_ptr = re.match(r"DIM\s+(\w+)\s+AS\s+POINTER\s+TO\s+(\w+)", command, re.IGNORECASE)
                        if match_ptr:
                            var_name, target_type = match_ptr.groups()
                            self.current_scope()[var_name] = Pointer(None, target_type, self)
                        else:
                            raise Exception("POINTER tanımı hatası")
                    else:
                        self.current_scope()[var_name] = None
                    return None
                else:
                    raise Exception("DIM komutunda sözdizimi hatası")

            # LET
            if command_upper.startswith("LET"):
                match = re.match(r"LET\s+(.+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    target, expr = match.groups()
                    if "." in target:
                        parts = target.split(".")
                        instance = self.current_scope().get(parts[0])
                        for field in parts[1:-1]:
                            if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                                instance = instance.get_field(field)
                            else:
                                raise Exception(f"Geçersiz alan erişimi: {target}")
                        field_name = parts[-1]
                        if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                            value = self.evaluate_expression(expr, scope_name)
                            instance.set_field(field_name, value)
                        else:
                            raise Exception(f"{parts[0]} bir struct, union veya sınıf değil")
                    elif "*" in target:
                        ptr_name = target.replace("*", "").strip()
                        if ptr_name in self.current_scope():
                            ptr = self.current_scope()[ptr_name]
                            if isinstance(ptr, Pointer):
                                value = self.evaluate_expression(expr, scope_name)
                                ptr.set(value)
                            else:
                                raise Exception(f"{ptr_name} bir işaretçi değil")
                        else:
                            raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    elif "(" in target and ")" in target:
                        match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
                        if match_array:
                            var_name, indices_str = match_array.groups()
                            indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                            if var_name in self.current_scope():
                                array = self.current_scope()[var_name]
                                if isinstance(array, ArrayInstance):
                                    value = self.evaluate_expression(expr, scope_name)
                                    array.set_element(indices, value)
                                else:
                                    raise Exception(f"{var_name} bir dizi değil")
                            else:
                                raise Exception(f"Değişken bulunamadı: {var_name}")
                        else:
                            raise Exception("Dizi erişiminde sözdizimi hatası")
                    else:
                        value = self.evaluate_expression(expr, scope_name)
                        if target in self.types and self.types[target]["kind"] == "ENUM":
                            if value in self.types[target]["values"].values():
                                self.current_scope()[target] = value
                            else:
                                raise Exception(f"Geçersiz ENUM değeri: {value}")
                        else:
                            if target in self.global_vars:
                                self.global_vars[target] = value
                            elif target in self.current_scope():
                                self.current_scope()[target] = value
                            else:
                                raise Exception(f"Tanımlanmamış değişken: {target}")
                    return None
                else:
                    raise Exception("LET komutunda sözdizimi hatası")

            # CALL
            if command_upper.startswith("CALL"):
                match = re.match(r"CALL\s+(\w+)\.(\w+)\((.*)\)", command, re.IGNORECASE)
                if match:
                    obj_name, method_name, args_str = match.groups()
                    if obj_name in self.current_scope():
                        obj = self.current_scope()[obj_name]
                        if isinstance(obj, ClassInstance):
                            args = []
                            if args_str.strip():
                                args = [self.evaluate_expression(arg.strip(), scope_name) for arg in args_str.split(",")]
                            obj.call_method(method_name, args)
                        else:
                            raise Exception(f"{obj_name} bir sınıf nesnesi değil")
                    else:
                        raise Exception(f"Değişken bulunamadı: {obj_name}")
                    return None
                else:
                    raise Exception("CALL komutunda sözdizimi hatası")

            # PRINT
            if command_upper.startswith("PRINT"):
                print_str = command[5:].strip()
                parts = re.split(r'([;,])', print_str)
                output = ""
                for j in range(0, len(parts), 2):
                    arg = parts[j].strip()
                    if arg:
                        if "." in arg:
                            parts_arg = arg.split(".")
                            instance = self.current_scope().get(parts_arg[0])
                            for field in parts_arg[1:]:
                                if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                                    instance = instance.get_field(field)
                                else:
                                    raise Exception(f"Geçersiz alan erişimi: {arg}")
                            output += str(instance)
                        elif "*" in arg:
                            ptr_name = arg.replace("*", "").strip()
                            if ptr_name in self.current_scope():
                                ptr = self.current_scope()[ptr_name]
                                if isinstance(ptr, Pointer):
                                    output += str(ptr.dereference())
                                else:
                                    raise Exception(f"{ptr_name} bir işaretçi değil")
                            else:
                                raise Exception(f"Değişken bulunamadı: {ptr_name}")
                        elif "(" in arg and ")" in arg:
                            match_array = re.match(r"(\w+)\(([\d, ]+)\)", arg)
                            if match_array:
                                var_name, indices_str = match_array.groups()
                                indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                                if var_name in self.current_scope():
                                    array = self.current_scope()[var_name]
                                    if isinstance(array, ArrayInstance):
                                        output += str(array.get_element(indices))
                                    else:
                                        raise Exception(f"{var_name} bir dizi değil")
                                else:
                                    raise Exception(f"Değişken bulunamadı: {var_name}")
                            else:
                                raise Exception("Dizi erişiminde sözdizimi hatası")
                        else:
                            value = self.evaluate_expression(arg, scope_name)
                            output += str(value)
                    if j + 1 < len(parts) and parts[j+1] == ',':
                        output += " "
                if print_str.strip().endswith(';'):
                    print(output, end='')
                else:
                    print(output)
                return None

            # İşaretçi Operasyonları
            if command_upper.startswith("PTR_SET"):
                match = re.match(r"PTR_SET\s+(\w+)\s+TO\s+(.+)", command, re.IGNORECASE)
                if match:
                    ptr_name, expr = match.groups()
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer):
                            if expr.startswith("&"):
                                target = expr[1:].strip()
                                if "(" in target and ")" in target:
                                    match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
                                    if match_array:
                                        var_name, indices_str = match_array.groups()
                                        indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                                        if var_name in self.current_scope():
                                            array = self.current_scope()[var_name]
                                            if isinstance(array, ArrayInstance):
                                                addr = self.next_address
                                                self.memory_pool[addr] = {
                                                    "value": array.get_element(indices),
                                                    "type": array.element_type,
                                                    "refs": 1
                                                }
                                                self.next_address += array.element_size
                                                ptr.address = addr
                                                ptr.dimensions = array.dimensions
                                            else:
                                                raise Exception(f"{var_name} bir dizi değil")
                                        else:
                                            raise Exception(f"Değişken bulunamadı: {var_name}")
                                    else:
                                        raise Exception("Dizi erişiminde sözdizimi hatası")
                                else:
                                    if target in self.current_scope():
                                        addr = self.next_address
                                        self.memory_pool[addr] = {
                                            "value": self.current_scope()[target],
                                            "type": ptr.target_type,
                                            "refs": 1
                                        }
                                        self.next_address += 8
                                        ptr.address = addr
                                    else:
                                        raise Exception(f"Değişken bulunamadı: {target}")
                            else:
                                addr = self.evaluate_expression(expr, scope_name)
                                if addr in self.memory_pool:
                                    ptr.address = addr
                                else:
                                    raise Exception(f"Geçersiz adres: {addr}")
                        else:
                            raise Exception(f"{ptr_name} bir işaretçi değil")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("PTR_SET komutunda sözdizimi hatası")

            # Bellek Yönetimi
            if command_upper.startswith("MALLOC"):
                match = re.match(r"MALLOC\s+(\w+)\s+SIZE\s+(\d+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, size, var_type = match.groups()
                    size = int(size)
                    addr = self.next_address
                    self.memory_pool[addr] = {
                        "value": None,
                        "type": var_type,
                        "refs": 1,
                        "size": size
                    }
                    self.next_address += size
                    self.current_scope()[var_name] = Pointer(addr, var_type, self)
                    return None
                else:
                    raise Exception("MALLOC komutunda sözdizimi hatası")

            if command_upper.startswith("FREE"):
                match = re.match(r"FREE\s+(\w+)", command, re.IGNORECASE)
                if match:
                    ptr_name = match.group(1)
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer) and ptr.address in self.memory_pool:
                            self.memory_pool[ptr.address]["refs"] -= 1
                            if self.memory_pool[ptr.address]["refs"] <= 0:
                                del self.memory_pool[ptr.address]
                            ptr.address = None
                        else:
                            raise Exception(f"Geçersiz işaretçi: {ptr_name}")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("FREE komutunda sözdizimi hatası")

            if command_upper.startswith("MEMCPY"):
                match = re.match(r"MEMCPY\s+(\w+)\s+FROM\s+(\w+)\s+SIZE\s+(\d+)", command, re.IGNORECASE)
                if match:
                    dest_ptr, src_ptr, size = match.groups()
                    size = int(size)
                    if dest_ptr in self.current_scope() and src_ptr in self.current_scope():
                        dest = self.current_scope()[dest_ptr]
                        src = self.current_scope()[src_ptr]
                        if isinstance(dest, Pointer) and isinstance(src, Pointer):
                            if src.address in self.memory_pool and dest.address in self.memory_pool:
                                self.memory_pool[dest.address]["value"] = self.memory_pool[src.address]["value"]
                            else:
                                raise Exception("Geçersiz bellek adresi")
                        else:
                            raise Exception("Geçersiz işaretçi")
                    else:
                        raise Exception("Değişken bulunamadı")
                    return None
                else:
                    raise Exception("MEMCPY komutunda sözdizimi hatası")

            if command_upper.startswith("MEMSET"):
                match = re.match(r"MEMSET\s+(\w+)\s+VALUE\s+(.+)\s+SIZE\s+(\d+)", command, re.IGNORECASE)
                if match:
                    ptr_name, value_expr, size = match.groups()
                    size = int(size)
                    value = self.evaluate_expression(value_expr, scope_name)
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer) and ptr.address in self.memory_pool:
                            self.memory_pool[ptr.address]["value"] = value
                        else:
                            raise Exception("Geçersiz işaretçi")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("MEMSET komutunda sözdizimi hatası")

            raise Exception(f"Bilinmeyen komut: {command}")
        except Exception as e:
            error_msg = f"PDSX Hatası: {str(e)}, Satır {self.program_counter + 1 if not self.repl_mode else 'REPL'}"
            print(error_msg)
            logging.error(error_msg)
            if self.error_handler == "RESUME":
                return None
            elif self.error_handler:
                self.program_counter = self.error_handler
            else:
                self.running = False
            return None

    def evaluate_expression(self, expr, scope_name=None):
        expr = expr.strip()
        if "." in expr:
            parts = expr.split(".")
            instance = self.current_scope().get(parts[0])
            for field in parts[1:]:
                if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                    instance = instance.get_field(field)
                else:
                    raise Exception(f"Geçersiz alan erişimi: {expr}")
            return instance
        elif "*" in expr:
            ptr_name = expr.replace("*", "").strip()
            if ptr_name in self.current_scope():
                ptr = self.current_scope()[ptr_name]
                if isinstance(ptr, Pointer):
                    return ptr.dereference()
            raise Exception(f"Geçersiz işaretçi: {expr}")
        elif "(" in expr and ")" in expr:
            match_array = re.match(r"(\w+)\(([\d, ]+)\)", expr)
            if match_array:
                var_name, indices_str = match_array.groups()
                indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                if var_name in self.current_scope():
                    array = self.current_scope()[var_name]
                    if isinstance(array, ArrayInstance):
                        return array.get_element(indices)
                raise Exception(f"Geçersiz dizi erişimi: {expr}")
            else:
                raise Exception("Dizi erişiminde sözdizimi hatası")
        elif expr in self.types and self.types[expr]["kind"] == "ENUM":
            return self.types[expr]["values"]
        namespace = {}
        namespace.update(self.global_vars)
        namespace.update(self.current_scope())
        namespace.update(self.function_table)
        try:
            return eval(expr, namespace)
        except Exception as e:
            raise Exception(f"İfade değerlendirme hatası: {expr}, Hata: {str(e)}")

    def run(self, code=None):
        if code:
            self.parse_program(code)
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.program):
            command, scope_name = self.program[self.program_counter]
            self.execute_command(command, scope_name)
            self.program_counter += 1



Yeni Kodun Entegrasyonu:
Sınıf Tanımlama:
Orijinal CLASS ayrıştırmasını koruyarak, yeni kodun PUBLIC, PRIVATE, ve INHERITS desteğini ekleyin. Örneğin, parse_program içinde:
python

Kopyala
elif line_upper.startswith("CLASS "):
    match = re.match(r"CLASS\s+(\w+)(?:\s+INHERITS\s+(\w+))?", line, re.IGNORECASE)
    if match:
        class_name, parent_name = match.groups()
        current_class = class_name
        class_info[class_name] = {
            "fields": [], "methods": {}, "access": {}, "parent": parent_name
        }
Orijinal kodda CLASS içinde sadece alanlar varsa, yeni kodun metod desteğini (SUB) ekleyin.
Nesne Oluşturma:
Orijinal DIM obj AS ClassName mantığını koruyun, ancak ClassInstance sınıfını kullanacak şekilde güncelleyin:
python

Kopyala
if type_info["kind"] == "CLASS":
    self.current_scope()[var_name] = ClassInstance(type_info, self.type_table, self.types, self)
Metod Çağrıları:
Orijinal CALL komutunu koruyun, ancak yeni call_method mantığını entegre edin:
python

Kopyala
if command_upper.startswith("CALL"):
    match = re.match(r"CALL\s+(\w+)\.(\w+)\((.*)\)", command, re.IGNORECASE)
    if match:
        obj_name, method_name, args_str = match.groups()
        obj = self.current_scope()[obj_name]
        if isinstance(obj, ClassInstance):
            args = [self.evaluate_expression(arg.strip(), scope_name) for arg in args_str.split(",") if arg.strip()]
            obj.call_method(method_name, args)
Kalıtım ve Erişim Kontrolü:
Orijinal kodda INHERITS yoksa, yeni kodun kalıtım desteğini opsiyonel olarak ekleyin (kullanılmazsa hata vermez).
PUBLIC/PRIVATE için, orijinal kodda erişim kontrolü yoksa, varsayılan olarak tüm alanları PUBLIC kabul edin.
Geri Uyumluluk:
Orijinal CLASS sözdizimini desteklemek için, yeni kodun parse_program ve execute_command bölümlerinde orijinal sözdizimini tanıyacak koşullu mantık ekleyin:
python

Kopyala
if line_upper.startswith("CLASS ") and "INHERITS" not in line_upper:
    # Orijinal CLASS ayrıştırma mantığı
Orijinal nesne oluşturma ve metod çağrılarını bozmadan, yeni ClassInstance sınıfını kullanın.
Çok Boyutlu Dizilerle Uyumluluk:
Orijinal CLASS içinde dizi kullanımı varsa, yeni ArrayInstance sınıfını kullanarak çok boyutlu dizileri destekleyin:
basX

Kopyala
CLASS MyClass
    matrix AS ARRAY(10, 5) AS DOUBLE
END CLASS
3. Zotero ve Veri Bilimi Bağlamında Kullanım
Yeni CLASS komutu, Zotero ve veri bilimi senaryolarında orijinaline göre daha güçlü. Örnek:

basX

Kopyala
CLASS ZoteroAnalyzer
    PRIVATE docs AS ARRAY(100, 2) AS DOUBLE  ' Çok boyutlu dizi
    PUBLIC SUB LoadDocuments(path AS STRING)
        LET SELF.docs = ARRAY(PDF_EXTRACT_TABLES(path))  ' Zotero PDF'den tablo
    END SUB
    PUBLIC SUB Analyze()
        DIM ptr AS POINTER TO DOUBLE
        PTR_SET ptr TO &SELF.docs(0, 0)
        PRINT "First cell: "; *ptr
    END SUB
END CLASS

CLASS ExtendedAnalyzer INHERITS ZoteroAnalyzer
    PUBLIC meta AS DICT
    PUBLIC SUB AddMeta(key AS STRING, value AS STRING)
        LET SELF.meta = DICT(key, value)
    END SUB
END CLASS

DIM analyzer AS ExtendedAnalyzer
CALL analyzer.LoadDocuments("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
CALL analyzer.AddMeta("author", "Ali")
CALL analyzer.Analyze()
Faydalar:

Orijinalden Fark: Orijinal CLASS muhtemelen PRIVATE veya INHERITS desteklemiyordu, bu da modülerliği sınırlıyordu. Yeni sürüm, Zotero verilerini daha güvenli ve yeniden kullanılabilir şekilde organize eder.
Çok Boyutlu Diziler: Tablo verileri için docs(100, 2) gibi yapılar, işaretçi aritmetiğiyle (ptr + 1) kolayca işlenebilir.
4. Test ve Entegrasyon
Test Programı
Orijinal ve yeni CLASS özelliklerini test eden bir program:

basX

Kopyala
' Orijinal tarz CLASS
CLASS SimpleClass
    x AS INTEGER
    SUB PrintX()
        PRINT x
    END SUB
END CLASS

' Yeni tarz CLASS
CLASS ZoteroDocument
    PUBLIC baslik AS STRING
    PRIVATE tablo AS ARRAY(2, 3) AS DOUBLE
    SUB SetTable(i AS INTEGER, j AS INTEGER, value AS DOUBLE)
        LET SELF.tablo(i, j) = value
    END SUB
END CLASS

CLASS ExtendedDocument INHERITS ZoteroDocument
    PUBLIC SUB PrintTable()
        PRINT SELF.tablo(0, 0)
    END SUB
END CLASS

DIM simple AS SimpleClass
LET simple.x = 42
CALL simple.PrintX()

DIM doc AS ExtendedDocument
LET doc.baslik = "Test"
CALL doc.SetTable(0, 0, 1.23)
CALL doc.PrintTable()


Entegrasyon Önerileri
Orijinal PDSX kodunu bozmadan yeni CLASS ve çok boyutlu dizi desteğini entegre etmek için:

Yedek Alma:
pdsX.py dosyasını yedekleyin (pdsX_backup.py).
Yeni Sınıfları Ekleme:
ClassInstance, ArrayInstance, Pointer, StructInstance, UnionInstance sınıflarını dosyanın başına ekleyin.
CLASS Ayrıştırmasını Güncelleme:
parse_program içindeki CLASS bloğunu, hem orijinal (EXTENDS, STATIC) hem yeni (INHERITS, PUBLIC/PRIVATE) sözdizimini destekleyecek şekilde birleştirin:
python

Kopyala
elif line_upper.startswith("CLASS "):
    match = re.match(r"CLASS\s+(\w+)(?:\s+(EXTENDS|INHERITS)\s+(\w+))?", line, re.IGNORECASE)
    if match:
        class_name, inherit_keyword, parent_name = match.groups()
        current_class = class_name
        class_info[class_name] = {
            'fields': [], 'methods': {}, 'private_methods': {}, 'static_vars': {}, 'access': {}, 'parent': parent_name
        }
Alanlar için PUBLIC/PRIVATE ve DIM desteği:
python

Kopyala
elif current_class:
    if line_upper.startswith(("PUBLIC ", "PRIVATE ")):
        access = "PUBLIC" if line_upper.startswith("PUBLIC ") else "PRIVATE"
        line = line[len(access):].strip()
        line_upper = line.upper()
    else:
        access = "PUBLIC"
    if line_upper.startswith("DIM ") or re.match(r"\w+\s+AS\s+\w+", line_upper):
        match = re.match(r"(?:DIM\s+)?(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
        if match:
            field_name, field_type = match.groups()
            class_info[current_class]['fields'].append((field_name, field_type))
            class_info[current_class]['access'][field_name] = access
Statik değişkenler için:
python

Kopyala
elif line_upper.startswith("STATIC "):
    match = re.match(r"STATIC\s+(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
    if match:
        var_name, var_type = match.groups()
        class_info[current_class]['static_vars'][var_name] = self.type_table.get(var_type, None)()
Nesne Oluşturma ve Metod Çağrıları:
execute_command içindeki DIM ve CALL bölümlerini güncelleyin:
python

Kopyala
if command_upper.startswith("DIM"):
    match = re.match(r"DIM\s+(\w+)(?:\(([\d, ]+)\))?\s+AS\s+(\w+)", command, re.IGNORECASE)
    if match:
        var_name, dim_str, var_type = match.groups()
        if dim_str:  # Çok boyutlu dizi
            dimensions = [int(d) for d in dim_str.replace(" ", "").split(",")]
            self.current_scope()[var_name] = ArrayInstance(dimensions, var_type, self.type_table, self.types)
        elif var_type in self.classes:
            self.current_scope()[var_name] = ClassInstance(self.types[var_type], self.type_table, self.types, self)
python

Kopyala
if command_upper.startswith("CALL"):
    match = re.match(r"CALL\s+(\w+)(?:\.(\w+))?(?:\((.*)\))?", command, re.IGNORECASE)
    if match:
        target, method_name, args_str = match.groups()
        if method_name:
            obj = self.current_scope()[target]
            if isinstance(obj, ClassInstance):
                args = [self.evaluate_expression(arg.strip(), scope_name) for arg in args_str.split(",") if arg.strip()]
                obj.call_method(method_name, args)
            elif hasattr(obj, method_name):
                args = self.evaluate_expression(f"({args_str})", scope_name) if args_str else []
                args = args if isinstance(args, (list, tuple)) else [args]
                method = obj.__dict__.get(method_name) or obj.__dict__.get('private_methods', {}).get(method_name)
                method(obj, *args)
Çok Boyutlu Diziler:
ArrayInstance sınıfını ekleyin ve execute_command içinde dizi erişimini destekleyin:
python

Kopyala
elif "(" in target and ")" in target:
    match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
    if match_array:
        var_name, indices_str = match_array.groups()
        indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
        array = self.current_scope()[var_name]
        if isinstance(array, ArrayInstance):
            value = self.evaluate_expression(expr, scope_name)
            array.set_element(indices, value)
Veri Bilimi Fonksiyonlarını Taşıma:
Orijinal function_table içindeki veri bilimi fonksiyonlarını (MEAN, DESCRIBE, PIVOT_TABLE) yeni koda ekleyin:
python

Kopyala
self.function_table.update({
    "MEAN": np.mean, "DESCRIBE": lambda df: df.describe(), ...
})
Test Programı:
basX

Kopyala
CLASS ZoteroDoc
    PUBLIC title AS STRING
    PRIVATE data AS ARRAY(2, 3) AS DOUBLE
    SUB LoadData(path AS STRING)
        LET SELF.data(0, 0) = PDF_EXTRACT_TABLES(path)[0][0][0]
        LET SELF.title = "Test"
    END SUB
END CLASS
DIM doc AS ZoteroDoc
CALL doc.LoadData("belge.pdf")
PRINT doc.title; doc.data(0, 0)

pdsx v10m interpreterimde asagida ekledigim kodun getirdigi ozelikller bulunuyormu?

import re
import logging
import struct as py_struct
from collections import namedtuple

# Sınıflar
class StructInstance:
    def __init__(self, fields, type_table, types):
        self.fields = {name: None for name, _ in fields}
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.types = types
        self.sizes = {name: self._get_size(type_name) for name, type_name in fields}
        self.offsets = {}
        offset = 0
        for name in self.fields:
            self.offsets[name] = offset
            offset += self.sizes[name]

    def set_field(self, field_name, value):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.fields[field_name] = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        return self.fields[field_name]

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class UnionInstance:
    def __init__(self, fields, type_table, types):
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.types = types
        self.active_field = None
        self.value = bytearray(8)
        self.sizes = {name: self._get_size(type_name) for name, type_name in fields}

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.active_field = field_name
            self.value = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.active_field = field_name
            fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
                   "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(field_type, "8s")
            if fmt == "8s":
                value = str(value).encode('utf-8')[:8].ljust(8, b'\0')
            else:
                value = py_struct.pack(fmt, value)
            self.value[:len(value)] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.active_field != field_name:
            raise ValueError(f"{field_name} alanı aktif değil")
        if self.field_types[field_name].upper() in self.types:
            return self.value
        fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
               "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(self.field_types[field_name].upper(), "8s")
        try:
            if fmt == "8s":
                return self.value.decode('utf-8').rstrip('\0')
            return py_struct.unpack(fmt, self.value[:self.sizes[field_name]])[0]
        except:
            raise ValueError(f"{field_name} alanından veri okunamadı")

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class ArrayInstance:
    def __init__(self, dimensions, element_type, type_table, types):
        self.dimensions = dimensions
        self.element_type = element_type.upper()
        self.type_table = type_table
        self.types = types
        self.element_size = self._get_size(element_type)
        total_size = 1
        for dim in dimensions:
            total_size *= dim
        self.elements = [None] * total_size
        self.strides = []
        stride = self.element_size
        for dim in reversed(dimensions):
            self.strides.insert(0, stride)
            stride *= dim

    def set_element(self, indices, value):
        index = self._get_index(indices)
        if self.element_type in self.types:
            type_info = self.types[self.element_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"Dizi elemanı için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"Dizi elemanı için UnionInstance bekleniyor")
            self.elements[index] = value
        else:
            expected_type = self.type_table.get(self.element_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"Dizi elemanı için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.elements[index] = value

    def get_element(self, indices):
        index = self._get_index(indices)
        return self.elements[index]

    def _get_index(self, indices):
        if len(indices) != len(self.dimensions):
            raise ValueError(f"Beklenen {len(self.dimensions)} indeks, ancak {len(indices)} alındı")
        for i, idx in enumerate(indices):
            if not 0 <= idx < self.dimensions[i]:
                raise ValueError(f"Geçersiz indeks: {idx}")
        index = 0
        for i, idx in enumerate(indices):
            index += idx * self.strides[i] // self.element_size
        return index

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class Pointer:
    def __init__(self, address, target_type, interpreter, dimensions=None):
        self.address = address
        self.target_type = target_type.upper()
        self.interpreter = interpreter
        self.dimensions = dimensions
        self.element_size = self._get_size(target_type)
        self.strides = None
        if dimensions:
            self.strides = []
            stride = self.element_size
            for dim in reversed(dimensions):
                self.strides.insert(0, stride)
                stride *= dim

    def dereference(self):
        if self.address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi adresi: {self.address}")
        value = self.interpreter.memory_pool[self.address]["value"]
        if self.target_type in self.interpreter.types:
            type_info = self.interpreter.types[self.target_type]
            if type_info["kind"] in ("STRUCT", "CLASS") and not isinstance(value, (StructInstance, ClassInstance)):
                raise TypeError(f"StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION" and not isinstance(value, UnionInstance):
                raise TypeError(f"UnionInstance bekleniyor")
        else:
            expected_type = self.interpreter.type_table.get(self.target_type, object)
            if not isinstance(value, expected_type):
                raise TypeError(f"Beklenen tip {expected_type.__name__}, ancak {type(value).__name__} bulundu")
        return value

    def set(self, value):
        if self.address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi adresi: {self.address}")
        if self.target_type in self.interpreter.types:
            type_info = self.interpreter.types[self.target_type]
            if type_info["kind"] in ("STRUCT", "CLASS") and not isinstance(value, (StructInstance, ClassInstance)):
                raise TypeError(f"StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION" and not isinstance(value, UnionInstance):
                raise TypeError(f"UnionInstance bekleniyor")
        else:
            expected_type = self.interpreter.type_table.get(self.target_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"Beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
        self.interpreter.memory_pool[self.address]["value"] = value

    def add_offset(self, offset):
        if self.dimensions and self.strides:
            new_address = self.address + offset * self.strides[-1]
        else:
            new_address = self.address + offset * self.element_size
        if new_address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi aritmetiği: {new_address}")
        return Pointer(new_address, self.target_type, self.interpreter, self.dimensions)

    def _get_size(self, type_name):
        if type_name.upper() in self.interpreter.types:
            type_info = self.interpreter.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class ClassInstance:
    def __init__(self, class_info, type_table, types, interpreter):
        self.class_info = class_info
        self.type_table = type_table
        self.types = types
        self.interpreter = interpreter
        self.fields = {name: None for name, _ in class_info["fields"] if class_info["access"].get(name, "PUBLIC") == "PUBLIC"}
        self.field_types = {name: type_name for name, type_name in class_info["fields"]}
        self.access = class_info["access"]
        self.methods = class_info["methods"]
        self.parent = class_info.get("parent")

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.access.get(field_name, "PUBLIC") == "PRIVATE" and not hasattr(self.interpreter, "current_class"):
            raise ValueError(f"{field_name} özel bir alan")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.fields[field_name] = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.access.get(field_name, "PUBLIC") == "PRIVATE" and not hasattr(self.interpreter, "current_class"):
            raise ValueError(f"{field_name} özel bir alan")
        return self.fields[field_name]

    def call_method(self, method_name, args):
        if method_name not in self.methods:
            raise ValueError(f"Geçersiz metod: {method_name}")
        method = self.methods[method_name]
        self.interpreter.current_class = self
        self.interpreter.scopes.append({"SELF": self})
        for param, arg in zip(method["params"], args):
            self.interpreter.current_scope()[param[0]] = arg
        for cmd in method["body"]:
            self.interpreter.execute_command(cmd)
        self.interpreter.scopes.pop()
        del self.interpreter.current_class

# pdsXInterpreter sınıfı
class pdsXInterpreter:
    def __init__(self):
        self.program = []
        self.program_counter = 0
        self.global_vars = {}
        self.scopes = [{}]
        self.running = False
        self.modules = {}
        self.current_module = "main"
        self.types = {}
        self.type_table = {
            "STRING": str, "INTEGER": int, "DOUBLE": float, "BYTE": int,
            "SHORT": int, "LONG": int, "SINGLE": float, "LIST": list, "ARRAY": list, "DICT": dict,
            "POINTER": lambda x: Pointer(None, x, self)
        }
        self.function_table = {}
        self.error_handler = None
        self.repl_mode = False
        self.expr_cache = {}
        self.memory_pool = {}
        self.next_address = 1000
        logging.basicConfig(level=logging.INFO)

    def parse_program(self, code, module_name="main"):
        self.current_module = module_name
        self.modules[module_name] = {
            "program": [], "functions": {}, "subs": {}, "classes": {}, "types": {}, "labels": {}
        }
        current_sub = None
        current_function = None
        current_type = None
        current_class = None
        current_enum = None
        type_fields = {}
        enum_values = {}
        class_info = {}
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            line_upper = line.upper()
            # TYPE
            if line_upper.startswith("TYPE "):
                type_name = line[5:].strip()
                current_type = type_name
                type_fields[type_name] = []
                i += 1
            elif line_upper.startswith("END TYPE"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[current_type]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # STRUCT
            elif line_upper.startswith("STRUCT "):
                struct_name = line[7:].strip()
                current_type = struct_name
                type_fields[struct_name] = []
                i += 1
            elif line_upper.startswith("END STRUCT"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[struct_name]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # UNION
            elif line_upper.startswith("UNION "):
                union_name = line[6:].strip()
                current_type = union_name
                type_fields[union_name] = []
                i += 1
            elif line_upper.startswith("END UNION"):
                self.types[current_type] = {"kind": "UNION", "fields": type_fields[union_name]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # ENUM
            elif line_upper.startswith("ENUM "):
                enum_name = line[5:].strip()
                current_enum = enum_name
                enum_values[enum_name] = {}
                i += 1
            elif line_upper.startswith("END ENUM"):
                self.types[current_enum] = {"kind": "ENUM", "values": enum_values[current_enum]}
                self.modules[module_name]["types"][current_enum] = self.types[current_enum]
                current_enum = None
                i += 1
            # CLASS
            elif line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+INHERITS\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_name = match.groups()
                    current_class = class_name
                    class_info[class_name] = {
                        "fields": [], "methods": {}, "access": {}, "parent": parent_name
                    }
                i += 1
            elif line_upper.startswith("END CLASS"):
                self.types[current_class] = {"kind": "CLASS", **class_info[current_class]}
                self.modules[module_name]["types"][current_class] = self.types[current_class]
                current_class = None
                i += 1
            elif current_type:
                match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    field_name, field_type = match.groups()
                    type_fields[current_type].append((field_name, field_type))
                else:
                    raise Exception(f"Tanım hatası: {line}")
                i += 1
            elif current_enum:
                match = re.match(r"(\w+)(?:\s*=\s*(\d+))?", line, re.IGNORECASE)
                if match:
                    name, value = match.groups()
                    value = int(value) if value else len(enum_values[current_enum])
                    enum_values[current_enum][name] = value
                else:
                    raise Exception(f"ENUM tanımı hatası: {line}")
                i += 1
            elif current_class:
                if line_upper.startswith(("PUBLIC ", "PRIVATE ")):
                    access = "PUBLIC" if line_upper.startswith("PUBLIC ") else "PRIVATE"
                    line = line[len(access):].strip()
                    line_upper = line.upper()
                else:
                    access = "PUBLIC"
                if line_upper.startswith("SUB "):
                    sub_name = line[4:].split("(")[0].strip()
                    params = []
                    if "(" in line and ")" in line:
                        param_str = line[line.index("(")+1:line.index(")")]
                        if param_str.strip():
                            for param in param_str.split(","):
                                param_name, param_type = [x.strip() for x in param.split("AS")]
                                params.append((param_name, param_type))
                    class_info[current_class]["methods"][sub_name] = {"params": params, "body": []}
                    current_sub = sub_name
                    i += 1
                elif line_upper.startswith("END SUB"):
                    current_sub = None
                    i += 1
                elif current_sub:
                    class_info[current_class]["methods"][current_sub]["body"].append(line)
                    i += 1
                else:
                    match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                    if match:
                        field_name, field_type = match.groups()
                        class_info[current_class]["fields"].append((field_name, field_type))
                        class_info[current_class]["access"][field_name] = access
                    else:
                        raise Exception(f"Sınıf tanımı hatası: {line}")
                    i += 1
            else:
                if current_sub or current_function:
                    self.program.append((line, current_sub or current_function))
                    self.modules[module_name]["program"].append((line, current_sub or current_function))
                else:
                    self.program.append((line, None))
                    self.modules[module_name]["program"].append((line, None))
                i += 1

    def current_scope(self):
        return self.scopes[-1]

    def execute_command(self, command, scope_name=None):
        command = command.strip()
        if not command:
            return None
        command_upper = command.upper()

        try:
            # DIM
            if command_upper.startswith("DIM"):
                match = re.match(r"DIM\s+(\w+)(?:\(([\d, ]+)\))?\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, dim_str, var_type = match.groups()
                    if dim_str:  # Dizi tanımlama
                        dimensions = [int(d) for d in dim_str.replace(" ", "").split(",")]
                        self.current_scope()[var_name] = ArrayInstance(dimensions, var_type, self.type_table, self.types)
                    elif var_type in self.types:
                        type_info = self.types[var_type]
                        if type_info["kind"] in ("STRUCT", "CLASS"):
                            self.current_scope()[var_name] = (
                                StructInstance(type_info["fields"], self.type_table, self.types)
                                if type_info["kind"] == "STRUCT"
                                else ClassInstance(type_info, self.type_table, self.types, self)
                            )
                        elif type_info["kind"] == "UNION":
                            self.current_scope()[var_name] = UnionInstance(type_info["fields"], self.type_table, self.types)
                        elif type_info["kind"] == "ENUM":
                            self.current_scope()[var_name] = None
                        else:
                            raise Exception(f"Tanımlanamayan veri tipi: {var_type}")
                    elif var_type == "POINTER":
                        match_ptr = re.match(r"DIM\s+(\w+)\s+AS\s+POINTER\s+TO\s+(\w+)", command, re.IGNORECASE)
                        if match_ptr:
                            var_name, target_type = match_ptr.groups()
                            self.current_scope()[var_name] = Pointer(None, target_type, self)
                        else:
                            raise Exception("POINTER tanımı hatası")
                    else:
                        self.current_scope()[var_name] = None
                    return None
                else:
                    raise Exception("DIM komutunda sözdizimi hatası")

            # LET
            if command_upper.startswith("LET"):
                match = re.match(r"LET\s+(.+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    target, expr = match.groups()
                    if "." in target:
                        parts = target.split(".")
                        instance = self.current_scope().get(parts[0])
                        for field in parts[1:-1]:
                            if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                                instance = instance.get_field(field)
                            else:
                                raise Exception(f"Geçersiz alan erişimi: {target}")
                        field_name = parts[-1]
                        if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                            value = self.evaluate_expression(expr, scope_name)
                            instance.set_field(field_name, value)
                        else:
                            raise Exception(f"{parts[0]} bir struct, union veya sınıf değil")
                    elif "*" in target:
                        ptr_name = target.replace("*", "").strip()
                        if ptr_name in self.current_scope():
                            ptr = self.current_scope()[ptr_name]
                            if isinstance(ptr, Pointer):
                                value = self.evaluate_expression(expr, scope_name)
                                ptr.set(value)
                            else:
                                raise Exception(f"{ptr_name} bir işaretçi değil")
                        else:
                            raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    elif "(" in target and ")" in target:
                        match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
                        if match_array:
                            var_name, indices_str = match_array.groups()
                            indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                            if var_name in self.current_scope():
                                array = self.current_scope()[var_name]
                                if isinstance(array, ArrayInstance):
                                    value = self.evaluate_expression(expr, scope_name)
                                    array.set_element(indices, value)
                                else:
                                    raise Exception(f"{var_name} bir dizi değil")
                            else:
                                raise Exception(f"Değişken bulunamadı: {var_name}")
                        else:
                            raise Exception("Dizi erişiminde sözdizimi hatası")
                    else:
                        value = self.evaluate_expression(expr, scope_name)
                        if target in self.types and self.types[target]["kind"] == "ENUM":
                            if value in self.types[target]["values"].values():
                                self.current_scope()[target] = value
                            else:
                                raise Exception(f"Geçersiz ENUM değeri: {value}")
                        else:
                            if target in self.global_vars:
                                self.global_vars[target] = value
                            elif target in self.current_scope():
                                self.current_scope()[target] = value
                            else:
                                raise Exception(f"Tanımlanmamış değişken: {target}")
                    return None
                else:
                    raise Exception("LET komutunda sözdizimi hatası")

            # CALL
            if command_upper.startswith("CALL"):
                match = re.match(r"CALL\s+(\w+)\.(\w+)\((.*)\)", command, re.IGNORECASE)
                if match:
                    obj_name, method_name, args_str = match.groups()
                    if obj_name in self.current_scope():
                        obj = self.current_scope()[obj_name]
                        if isinstance(obj, ClassInstance):
                            args = []
                            if args_str.strip():
                                args = [self.evaluate_expression(arg.strip(), scope_name) for arg in args_str.split(",")]
                            obj.call_method(method_name, args)
                        else:
                            raise Exception(f"{obj_name} bir sınıf nesnesi değil")
                    else:
                        raise Exception(f"Değişken bulunamadı: {obj_name}")
                    return None
                else:
                    raise Exception("CALL komutunda sözdizimi hatası")

            # PRINT
            if command_upper.startswith("PRINT"):
                print_str = command[5:].strip()
                parts = re.split(r'([;,])', print_str)
                output = ""
                for j in range(0, len(parts), 2):
                    arg = parts[j].strip()
                    if arg:
                        if "." in arg:
                            parts_arg = arg.split(".")
                            instance = self.current_scope().get(parts_arg[0])
                            for field in parts_arg[1:]:
                                if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                                    instance = instance.get_field(field)
                                else:
                                    raise Exception(f"Geçersiz alan erişimi: {arg}")
                            output += str(instance)
                        elif "*" in arg:
                            ptr_name = arg.replace("*", "").strip()
                            if ptr_name in self.current_scope():
                                ptr = self.current_scope()[ptr_name]
                                if isinstance(ptr, Pointer):
                                    output += str(ptr.dereference())
                                else:
                                    raise Exception(f"{ptr_name} bir işaretçi değil")
                            else:
                                raise Exception(f"Değişken bulunamadı: {ptr_name}")
                        elif "(" in arg and ")" in arg:
                            match_array = re.match(r"(\w+)\(([\d, ]+)\)", arg)
                            if match_array:
                                var_name, indices_str = match_array.groups()
                                indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                                if var_name in self.current_scope():
                                    array = self.current_scope()[var_name]
                                    if isinstance(array, ArrayInstance):
                                        output += str(array.get_element(indices))
                                    else:
                                        raise Exception(f"{var_name} bir dizi değil")
                                else:
                                    raise Exception(f"Değişken bulunamadı: {var_name}")
                            else:
                                raise Exception("Dizi erişiminde sözdizimi hatası")
                        else:
                            value = self.evaluate_expression(arg, scope_name)
                            output += str(value)
                    if j + 1 < len(parts) and parts[j+1] == ',':
                        output += " "
                if print_str.strip().endswith(';'):
                    print(output, end='')
                else:
                    print(output)
                return None

            # İşaretçi Operasyonları
            if command_upper.startswith("PTR_SET"):
                match = re.match(r"PTR_SET\s+(\w+)\s+TO\s+(.+)", command, re.IGNORECASE)
                if match:
                    ptr_name, expr = match.groups()
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer):
                            if expr.startswith("&"):
                                target = expr[1:].strip()
                                if "(" in target and ")" in target:
                                    match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
                                    if match_array:
                                        var_name, indices_str = match_array.groups()
                                        indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                                        if var_name in self.current_scope():
                                            array = self.current_scope()[var_name]
                                            if isinstance(array, ArrayInstance):
                                                addr = self.next_address
                                                self.memory_pool[addr] = {
                                                    "value": array.get_element(indices),
                                                    "type": array.element_type,
                                                    "refs": 1
                                                }
                                                self.next_address += array.element_size
                                                ptr.address = addr
                                                ptr.dimensions = array.dimensions
                                            else:
                                                raise Exception(f"{var_name} bir dizi değil")
                                        else:
                                            raise Exception(f"Değişken bulunamadı: {var_name}")
                                    else:
                                        raise Exception("Dizi erişiminde sözdizimi hatası")
                                else:
                                    if target in self.current_scope():
                                        addr = self.next_address
                                        self.memory_pool[addr] = {
                                            "value": self.current_scope()[target],
                                            "type": ptr.target_type,
                                            "refs": 1
                                        }
                                        self.next_address += 8
                                        ptr.address = addr
                                    else:
                                        raise Exception(f"Değişken bulunamadı: {target}")
                            else:
                                addr = self.evaluate_expression(expr, scope_name)
                                if addr in self.memory_pool:
                                    ptr.address = addr
                                else:
                                    raise Exception(f"Geçersiz adres: {addr}")
                        else:
                            raise Exception(f"{ptr_name} bir işaretçi değil")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("PTR_SET komutunda sözdizimi hatası")

            # Bellek Yönetimi
            if command_upper.startswith("MALLOC"):
                match = re.match(r"MALLOC\s+(\w+)\s+SIZE\s+(\d+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, size, var_type = match.groups()
                    size = int(size)
                    addr = self.next_address
                    self.memory_pool[addr] = {
                        "value": None,
                        "type": var_type,
                        "refs": 1,
                        "size": size
                    }
                    self.next_address += size
                    self.current_scope()[var_name] = Pointer(addr, var_type, self)
                    return None
                else:
                    raise Exception("MALLOC komutunda sözdizimi hatası")

            if command_upper.startswith("FREE"):
                match = re.match(r"FREE\s+(\w+)", command, re.IGNORECASE)
                if match:
                    ptr_name = match.group(1)
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer) and ptr.address in self.memory_pool:
                            self.memory_pool[ptr.address]["refs"] -= 1
                            if self.memory_pool[ptr.address]["refs"] <= 0:
                                del self.memory_pool[ptr.address]
                            ptr.address = None
                        else:
                            raise Exception(f"Geçersiz işaretçi: {ptr_name}")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("FREE komutunda sözdizimi hatası")

            if command_upper.startswith("MEMCPY"):
                match = re.match(r"MEMCPY\s+(\w+)\s+FROM\s+(\w+)\s+SIZE\s+(\d+)", command, re.IGNORECASE)
                if match:
                    dest_ptr, src_ptr, size = match.groups()
                    size = int(size)
                    if dest_ptr in self.current_scope() and src_ptr in self.current_scope():
                        dest = self.current_scope()[dest_ptr]
                        src = self.current_scope()[src_ptr]
                        if isinstance(dest, Pointer) and isinstance(src, Pointer):
                            if src.address in self.memory_pool and dest.address in self.memory_pool:
                                self.memory_pool[dest.address]["value"] = self.memory_pool[src.address]["value"]
                            else:
                                raise Exception("Geçersiz bellek adresi")
                        else:
                            raise Exception("Geçersiz işaretçi")
                    else:
                        raise Exception("Değişken bulunamadı")
                    return None
                else:
                    raise Exception("MEMCPY komutunda sözdizimi hatası")

            if command_upper.startswith("MEMSET"):
                match = re.match(r"MEMSET\s+(\w+)\s+VALUE\s+(.+)\s+SIZE\s+(\d+)", command, re.IGNORECASE)
                if match:
                    ptr_name, value_expr, size = match.groups()
                    size = int(size)
                    value = self.evaluate_expression(value_expr, scope_name)
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer) and ptr.address in self.memory_pool:
                            self.memory_pool[ptr.address]["value"] = value
                        else:
                            raise Exception("Geçersiz işaretçi")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("MEMSET komutunda sözdizimi hatası")

            raise Exception(f"Bilinmeyen komut: {command}")
        except Exception as e:
            error_msg = f"PDSX Hatası: {str(e)}, Satır {self.program_counter + 1 if not self.repl_mode else 'REPL'}"
            print(error_msg)
            logging.error(error_msg)
            if self.error_handler == "RESUME":
                return None
            elif self.error_handler:
                self.program_counter = self.error_handler
            else:
                self.running = False
            return None

    def evaluate_expression(self, expr, scope_name=None):
        expr = expr.strip()
        if "." in expr:
            parts = expr.split(".")
            instance = self.current_scope().get(parts[0])
            for field in parts[1:]:
                if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                    instance = instance.get_field(field)
                else:
                    raise Exception(f"Geçersiz alan erişimi: {expr}")
            return instance
        elif "*" in expr:
            ptr_name = expr.replace("*", "").strip()
            if ptr_name in self.current_scope():
                ptr = self.current_scope()[ptr_name]
                if isinstance(ptr, Pointer):
                    return ptr.dereference()
            raise Exception(f"Geçersiz işaretçi: {expr}")
        elif "(" in expr and ")" in expr:
            match_array = re.match(r"(\w+)\(([\d, ]+)\)", expr)
            if match_array:
                var_name, indices_str = match_array.groups()
                indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                if var_name in self.current_scope():
                    array = self.current_scope()[var_name]
                    if isinstance(array, ArrayInstance):
                        return array.get_element(indices)
                raise Exception(f"Geçersiz dizi erişimi: {expr}")
            else:
                raise Exception("Dizi erişiminde sözdizimi hatası")
        elif expr in self.types and self.types[expr]["kind"] == "ENUM":
            return self.types[expr]["values"]
        namespace = {}
        namespace.update(self.global_vars)
        namespace.update(self.current_scope())
        namespace.update(self.function_table)
        try:
            return eval(expr, namespace)
        except Exception as e:
            raise Exception(f"İfade değerlendirme hatası: {expr}, Hata: {str(e)}")

    def run(self, code=None):
        if code:
            self.parse_program(code)
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.program):
            command, scope_name = self.program[self.program_counter]
            self.execute_command(command, scope_name)
            self.program_counter += 1
            
            pdsx v10m interpreterimde asagida ekledigim kodun getirdigi ozelikller bulunuyormu?

import re
import logging
import struct as py_struct
from collections import namedtuple

# Sınıflar
class StructInstance:
    def __init__(self, fields, type_table, types):
        self.fields = {name: None for name, _ in fields}
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.types = types
        self.sizes = {name: self._get_size(type_name) for name, type_name in fields}
        self.offsets = {}
        offset = 0
        for name in self.fields:
            self.offsets[name] = offset
            offset += self.sizes[name]

    def set_field(self, field_name, value):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.fields[field_name] = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        return self.fields[field_name]

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class UnionInstance:
    def __init__(self, fields, type_table, types):
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.types = types
        self.active_field = None
        self.value = bytearray(8)
        self.sizes = {name: self._get_size(type_name) for name, type_name in fields}

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.active_field = field_name
            self.value = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.active_field = field_name
            fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
                   "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(field_type, "8s")
            if fmt == "8s":
                value = str(value).encode('utf-8')[:8].ljust(8, b'\0')
            else:
                value = py_struct.pack(fmt, value)
            self.value[:len(value)] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.active_field != field_name:
            raise ValueError(f"{field_name} alanı aktif değil")
        if self.field_types[field_name].upper() in self.types:
            return self.value
        fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
               "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(self.field_types[field_name].upper(), "8s")
        try:
            if fmt == "8s":
                return self.value.decode('utf-8').rstrip('\0')
            return py_struct.unpack(fmt, self.value[:self.sizes[field_name]])[0]
        except:
            raise ValueError(f"{field_name} alanından veri okunamadı")

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class ArrayInstance:
    def __init__(self, dimensions, element_type, type_table, types):
        self.dimensions = dimensions
        self.element_type = element_type.upper()
        self.type_table = type_table
        self.types = types
        self.element_size = self._get_size(element_type)
        total_size = 1
        for dim in dimensions:
            total_size *= dim
        self.elements = [None] * total_size
        self.strides = []
        stride = self.element_size
        for dim in reversed(dimensions):
            self.strides.insert(0, stride)
            stride *= dim

    def set_element(self, indices, value):
        index = self._get_index(indices)
        if self.element_type in self.types:
            type_info = self.types[self.element_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"Dizi elemanı için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"Dizi elemanı için UnionInstance bekleniyor")
            self.elements[index] = value
        else:
            expected_type = self.type_table.get(self.element_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"Dizi elemanı için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.elements[index] = value

    def get_element(self, indices):
        index = self._get_index(indices)
        return self.elements[index]

    def _get_index(self, indices):
        if len(indices) != len(self.dimensions):
            raise ValueError(f"Beklenen {len(self.dimensions)} indeks, ancak {len(indices)} alındı")
        for i, idx in enumerate(indices):
            if not 0 <= idx < self.dimensions[i]:
                raise ValueError(f"Geçersiz indeks: {idx}")
        index = 0
        for i, idx in enumerate(indices):
            index += idx * self.strides[i] // self.element_size
        return index

    def _get_size(self, type_name):
        if type_name.upper() in self.types:
            type_info = self.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class Pointer:
    def __init__(self, address, target_type, interpreter, dimensions=None):
        self.address = address
        self.target_type = target_type.upper()
        self.interpreter = interpreter
        self.dimensions = dimensions
        self.element_size = self._get_size(target_type)
        self.strides = None
        if dimensions:
            self.strides = []
            stride = self.element_size
            for dim in reversed(dimensions):
                self.strides.insert(0, stride)
                stride *= dim

    def dereference(self):
        if self.address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi adresi: {self.address}")
        value = self.interpreter.memory_pool[self.address]["value"]
        if self.target_type in self.interpreter.types:
            type_info = self.interpreter.types[self.target_type]
            if type_info["kind"] in ("STRUCT", "CLASS") and not isinstance(value, (StructInstance, ClassInstance)):
                raise TypeError(f"StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION" and not isinstance(value, UnionInstance):
                raise TypeError(f"UnionInstance bekleniyor")
        else:
            expected_type = self.interpreter.type_table.get(self.target_type, object)
            if not isinstance(value, expected_type):
                raise TypeError(f"Beklenen tip {expected_type.__name__}, ancak {type(value).__name__} bulundu")
        return value

    def set(self, value):
        if self.address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi adresi: {self.address}")
        if self.target_type in self.interpreter.types:
            type_info = self.interpreter.types[self.target_type]
            if type_info["kind"] in ("STRUCT", "CLASS") and not isinstance(value, (StructInstance, ClassInstance)):
                raise TypeError(f"StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION" and not isinstance(value, UnionInstance):
                raise TypeError(f"UnionInstance bekleniyor")
        else:
            expected_type = self.interpreter.type_table.get(self.target_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"Beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
        self.interpreter.memory_pool[self.address]["value"] = value

    def add_offset(self, offset):
        if self.dimensions and self.strides:
            new_address = self.address + offset * self.strides[-1]
        else:
            new_address = self.address + offset * self.element_size
        if new_address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi aritmetiği: {new_address}")
        return Pointer(new_address, self.target_type, self.interpreter, self.dimensions)

    def _get_size(self, type_name):
        if type_name.upper() in self.interpreter.types:
            type_info = self.interpreter.types[type_name.upper()]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                return sum(self._get_size(f[1]) for f in type_info["fields"])
            elif type_info["kind"] == "UNION":
                return max(self._get_size(f[1]) for f in type_info["fields"])
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class ClassInstance:
    def __init__(self, class_info, type_table, types, interpreter):
        self.class_info = class_info
        self.type_table = type_table
        self.types = types
        self.interpreter = interpreter
        self.fields = {name: None for name, _ in class_info["fields"] if class_info["access"].get(name, "PUBLIC") == "PUBLIC"}
        self.field_types = {name: type_name for name, type_name in class_info["fields"]}
        self.access = class_info["access"]
        self.methods = class_info["methods"]
        self.parent = class_info.get("parent")

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.access.get(field_name, "PUBLIC") == "PRIVATE" and not hasattr(self.interpreter, "current_class"):
            raise ValueError(f"{field_name} özel bir alan")
        field_type = self.field_types[field_name].upper()
        if field_type in self.types:
            type_info = self.types[field_type]
            if type_info["kind"] in ("STRUCT", "CLASS"):
                if not isinstance(value, (StructInstance, ClassInstance)):
                    raise TypeError(f"{field_name} için StructInstance veya ClassInstance bekleniyor")
            elif type_info["kind"] == "UNION":
                if not isinstance(value, UnionInstance):
                    raise TypeError(f"{field_name} için UnionInstance bekleniyor")
            self.fields[field_name] = value
        else:
            expected_type = self.type_table.get(field_type, object)
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except:
                    raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
            self.fields[field_name] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.access.get(field_name, "PUBLIC") == "PRIVATE" and not hasattr(self.interpreter, "current_class"):
            raise ValueError(f"{field_name} özel bir alan")
        return self.fields[field_name]

    def call_method(self, method_name, args):
        if method_name not in self.methods:
            raise ValueError(f"Geçersiz metod: {method_name}")
        method = self.methods[method_name]
        self.interpreter.current_class = self
        self.interpreter.scopes.append({"SELF": self})
        for param, arg in zip(method["params"], args):
            self.interpreter.current_scope()[param[0]] = arg
        for cmd in method["body"]:
            self.interpreter.execute_command(cmd)
        self.interpreter.scopes.pop()
        del self.interpreter.current_class

# pdsXInterpreter sınıfı
class pdsXInterpreter:
    def __init__(self):
        self.program = []
        self.program_counter = 0
        self.global_vars = {}
        self.scopes = [{}]
        self.running = False
        self.modules = {}
        self.current_module = "main"
        self.types = {}
        self.type_table = {
            "STRING": str, "INTEGER": int, "DOUBLE": float, "BYTE": int,
            "SHORT": int, "LONG": int, "SINGLE": float, "LIST": list, "ARRAY": list, "DICT": dict,
            "POINTER": lambda x: Pointer(None, x, self)
        }
        self.function_table = {}
        self.error_handler = None
        self.repl_mode = False
        self.expr_cache = {}
        self.memory_pool = {}
        self.next_address = 1000
        logging.basicConfig(level=logging.INFO)

    def parse_program(self, code, module_name="main"):
        self.current_module = module_name
        self.modules[module_name] = {
            "program": [], "functions": {}, "subs": {}, "classes": {}, "types": {}, "labels": {}
        }
        current_sub = None
        current_function = None
        current_type = None
        current_class = None
        current_enum = None
        type_fields = {}
        enum_values = {}
        class_info = {}
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            line_upper = line.upper()
            # TYPE
            if line_upper.startswith("TYPE "):
                type_name = line[5:].strip()
                current_type = type_name
                type_fields[type_name] = []
                i += 1
            elif line_upper.startswith("END TYPE"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[current_type]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # STRUCT
            elif line_upper.startswith("STRUCT "):
                struct_name = line[7:].strip()
                current_type = struct_name
                type_fields[struct_name] = []
                i += 1
            elif line_upper.startswith("END STRUCT"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[struct_name]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # UNION
            elif line_upper.startswith("UNION "):
                union_name = line[6:].strip()
                current_type = union_name
                type_fields[union_name] = []
                i += 1
            elif line_upper.startswith("END UNION"):
                self.types[current_type] = {"kind": "UNION", "fields": type_fields[union_name]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            # ENUM
            elif line_upper.startswith("ENUM "):
                enum_name = line[5:].strip()
                current_enum = enum_name
                enum_values[enum_name] = {}
                i += 1
            elif line_upper.startswith("END ENUM"):
                self.types[current_enum] = {"kind": "ENUM", "values": enum_values[current_enum]}
                self.modules[module_name]["types"][current_enum] = self.types[current_enum]
                current_enum = None
                i += 1
            # CLASS
            elif line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+INHERITS\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_name = match.groups()
                    current_class = class_name
                    class_info[class_name] = {
                        "fields": [], "methods": {}, "access": {}, "parent": parent_name
                    }
                i += 1
            elif line_upper.startswith("END CLASS"):
                self.types[current_class] = {"kind": "CLASS", **class_info[current_class]}
                self.modules[module_name]["types"][current_class] = self.types[current_class]
                current_class = None
                i += 1
            elif current_type:
                match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    field_name, field_type = match.groups()
                    type_fields[current_type].append((field_name, field_type))
                else:
                    raise Exception(f"Tanım hatası: {line}")
                i += 1
            elif current_enum:
                match = re.match(r"(\w+)(?:\s*=\s*(\d+))?", line, re.IGNORECASE)
                if match:
                    name, value = match.groups()
                    value = int(value) if value else len(enum_values[current_enum])
                    enum_values[current_enum][name] = value
                else:
                    raise Exception(f"ENUM tanımı hatası: {line}")
                i += 1
            elif current_class:
                if line_upper.startswith(("PUBLIC ", "PRIVATE ")):
                    access = "PUBLIC" if line_upper.startswith("PUBLIC ") else "PRIVATE"
                    line = line[len(access):].strip()
                    line_upper = line.upper()
                else:
                    access = "PUBLIC"
                if line_upper.startswith("SUB "):
                    sub_name = line[4:].split("(")[0].strip()
                    params = []
                    if "(" in line and ")" in line:
                        param_str = line[line.index("(")+1:line.index(")")]
                        if param_str.strip():
                            for param in param_str.split(","):
                                param_name, param_type = [x.strip() for x in param.split("AS")]
                                params.append((param_name, param_type))
                    class_info[current_class]["methods"][sub_name] = {"params": params, "body": []}
                    current_sub = sub_name
                    i += 1
                elif line_upper.startswith("END SUB"):
                    current_sub = None
                    i += 1
                elif current_sub:
                    class_info[current_class]["methods"][current_sub]["body"].append(line)
                    i += 1
                else:
                    match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                    if match:
                        field_name, field_type = match.groups()
                        class_info[current_class]["fields"].append((field_name, field_type))
                        class_info[current_class]["access"][field_name] = access
                    else:
                        raise Exception(f"Sınıf tanımı hatası: {line}")
                    i += 1
            else:
                if current_sub or current_function:
                    self.program.append((line, current_sub or current_function))
                    self.modules[module_name]["program"].append((line, current_sub or current_function))
                else:
                    self.program.append((line, None))
                    self.modules[module_name]["program"].append((line, None))
                i += 1

    def current_scope(self):
        return self.scopes[-1]

    def execute_command(self, command, scope_name=None):
        command = command.strip()
        if not command:
            return None
        command_upper = command.upper()

        try:
            # DIM
            if command_upper.startswith("DIM"):
                match = re.match(r"DIM\s+(\w+)(?:\(([\d, ]+)\))?\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, dim_str, var_type = match.groups()
                    if dim_str:  # Dizi tanımlama
                        dimensions = [int(d) for d in dim_str.replace(" ", "").split(",")]
                        self.current_scope()[var_name] = ArrayInstance(dimensions, var_type, self.type_table, self.types)
                    elif var_type in self.types:
                        type_info = self.types[var_type]
                        if type_info["kind"] in ("STRUCT", "CLASS"):
                            self.current_scope()[var_name] = (
                                StructInstance(type_info["fields"], self.type_table, self.types)
                                if type_info["kind"] == "STRUCT"
                                else ClassInstance(type_info, self.type_table, self.types, self)
                            )
                        elif type_info["kind"] == "UNION":
                            self.current_scope()[var_name] = UnionInstance(type_info["fields"], self.type_table, self.types)
                        elif type_info["kind"] == "ENUM":
                            self.current_scope()[var_name] = None
                        else:
                            raise Exception(f"Tanımlanamayan veri tipi: {var_type}")
                    elif var_type == "POINTER":
                        match_ptr = re.match(r"DIM\s+(\w+)\s+AS\s+POINTER\s+TO\s+(\w+)", command, re.IGNORECASE)
                        if match_ptr:
                            var_name, target_type = match_ptr.groups()
                            self.current_scope()[var_name] = Pointer(None, target_type, self)
                        else:
                            raise Exception("POINTER tanımı hatası")
                    else:
                        self.current_scope()[var_name] = None
                    return None
                else:
                    raise Exception("DIM komutunda sözdizimi hatası")

            # LET
            if command_upper.startswith("LET"):
                match = re.match(r"LET\s+(.+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    target, expr = match.groups()
                    if "." in target:
                        parts = target.split(".")
                        instance = self.current_scope().get(parts[0])
                        for field in parts[1:-1]:
                            if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                                instance = instance.get_field(field)
                            else:
                                raise Exception(f"Geçersiz alan erişimi: {target}")
                        field_name = parts[-1]
                        if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                            value = self.evaluate_expression(expr, scope_name)
                            instance.set_field(field_name, value)
                        else:
                            raise Exception(f"{parts[0]} bir struct, union veya sınıf değil")
                    elif "*" in target:
                        ptr_name = target.replace("*", "").strip()
                        if ptr_name in self.current_scope():
                            ptr = self.current_scope()[ptr_name]
                            if isinstance(ptr, Pointer):
                                value = self.evaluate_expression(expr, scope_name)
                                ptr.set(value)
                            else:
                                raise Exception(f"{ptr_name} bir işaretçi değil")
                        else:
                            raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    elif "(" in target and ")" in target:
                        match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
                        if match_array:
                            var_name, indices_str = match_array.groups()
                            indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                            if var_name in self.current_scope():
                                array = self.current_scope()[var_name]
                                if isinstance(array, ArrayInstance):
                                    value = self.evaluate_expression(expr, scope_name)
                                    array.set_element(indices, value)
                                else:
                                    raise Exception(f"{var_name} bir dizi değil")
                            else:
                                raise Exception(f"Değişken bulunamadı: {var_name}")
                        else:
                            raise Exception("Dizi erişiminde sözdizimi hatası")
                    else:
                        value = self.evaluate_expression(expr, scope_name)
                        if target in self.types and self.types[target]["kind"] == "ENUM":
                            if value in self.types[target]["values"].values():
                                self.current_scope()[target] = value
                            else:
                                raise Exception(f"Geçersiz ENUM değeri: {value}")
                        else:
                            if target in self.global_vars:
                                self.global_vars[target] = value
                            elif target in self.current_scope():
                                self.current_scope()[target] = value
                            else:
                                raise Exception(f"Tanımlanmamış değişken: {target}")
                    return None
                else:
                    raise Exception("LET komutunda sözdizimi hatası")

            # CALL
            if command_upper.startswith("CALL"):
                match = re.match(r"CALL\s+(\w+)\.(\w+)\((.*)\)", command, re.IGNORECASE)
                if match:
                    obj_name, method_name, args_str = match.groups()
                    if obj_name in self.current_scope():
                        obj = self.current_scope()[obj_name]
                        if isinstance(obj, ClassInstance):
                            args = []
                            if args_str.strip():
                                args = [self.evaluate_expression(arg.strip(), scope_name) for arg in args_str.split(",")]
                            obj.call_method(method_name, args)
                        else:
                            raise Exception(f"{obj_name} bir sınıf nesnesi değil")
                    else:
                        raise Exception(f"Değişken bulunamadı: {obj_name}")
                    return None
                else:
                    raise Exception("CALL komutunda sözdizimi hatası")

            # PRINT
            if command_upper.startswith("PRINT"):
                print_str = command[5:].strip()
                parts = re.split(r'([;,])', print_str)
                output = ""
                for j in range(0, len(parts), 2):
                    arg = parts[j].strip()
                    if arg:
                        if "." in arg:
                            parts_arg = arg.split(".")
                            instance = self.current_scope().get(parts_arg[0])
                            for field in parts_arg[1:]:
                                if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                                    instance = instance.get_field(field)
                                else:
                                    raise Exception(f"Geçersiz alan erişimi: {arg}")
                            output += str(instance)
                        elif "*" in arg:
                            ptr_name = arg.replace("*", "").strip()
                            if ptr_name in self.current_scope():
                                ptr = self.current_scope()[ptr_name]
                                if isinstance(ptr, Pointer):
                                    output += str(ptr.dereference())
                                else:
                                    raise Exception(f"{ptr_name} bir işaretçi değil")
                            else:
                                raise Exception(f"Değişken bulunamadı: {ptr_name}")
                        elif "(" in arg and ")" in arg:
                            match_array = re.match(r"(\w+)\(([\d, ]+)\)", arg)
                            if match_array:
                                var_name, indices_str = match_array.groups()
                                indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                                if var_name in self.current_scope():
                                    array = self.current_scope()[var_name]
                                    if isinstance(array, ArrayInstance):
                                        output += str(array.get_element(indices))
                                    else:
                                        raise Exception(f"{var_name} bir dizi değil")
                                else:
                                    raise Exception(f"Değişken bulunamadı: {var_name}")
                            else:
                                raise Exception("Dizi erişiminde sözdizimi hatası")
                        else:
                            value = self.evaluate_expression(arg, scope_name)
                            output += str(value)
                    if j + 1 < len(parts) and parts[j+1] == ',':
                        output += " "
                if print_str.strip().endswith(';'):
                    print(output, end='')
                else:
                    print(output)
                return None

            # İşaretçi Operasyonları
            if command_upper.startswith("PTR_SET"):
                match = re.match(r"PTR_SET\s+(\w+)\s+TO\s+(.+)", command, re.IGNORECASE)
                if match:
                    ptr_name, expr = match.groups()
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer):
                            if expr.startswith("&"):
                                target = expr[1:].strip()
                                if "(" in target and ")" in target:
                                    match_array = re.match(r"(\w+)\(([\d, ]+)\)", target)
                                    if match_array:
                                        var_name, indices_str = match_array.groups()
                                        indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                                        if var_name in self.current_scope():
                                            array = self.current_scope()[var_name]
                                            if isinstance(array, ArrayInstance):
                                                addr = self.next_address
                                                self.memory_pool[addr] = {
                                                    "value": array.get_element(indices),
                                                    "type": array.element_type,
                                                    "refs": 1
                                                }
                                                self.next_address += array.element_size
                                                ptr.address = addr
                                                ptr.dimensions = array.dimensions
                                            else:
                                                raise Exception(f"{var_name} bir dizi değil")
                                        else:
                                            raise Exception(f"Değişken bulunamadı: {var_name}")
                                    else:
                                        raise Exception("Dizi erişiminde sözdizimi hatası")
                                else:
                                    if target in self.current_scope():
                                        addr = self.next_address
                                        self.memory_pool[addr] = {
                                            "value": self.current_scope()[target],
                                            "type": ptr.target_type,
                                            "refs": 1
                                        }
                                        self.next_address += 8
                                        ptr.address = addr
                                    else:
                                        raise Exception(f"Değişken bulunamadı: {target}")
                            else:
                                addr = self.evaluate_expression(expr, scope_name)
                                if addr in self.memory_pool:
                                    ptr.address = addr
                                else:
                                    raise Exception(f"Geçersiz adres: {addr}")
                        else:
                            raise Exception(f"{ptr_name} bir işaretçi değil")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("PTR_SET komutunda sözdizimi hatası")

            # Bellek Yönetimi
            if command_upper.startswith("MALLOC"):
                match = re.match(r"MALLOC\s+(\w+)\s+SIZE\s+(\d+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, size, var_type = match.groups()
                    size = int(size)
                    addr = self.next_address
                    self.memory_pool[addr] = {
                        "value": None,
                        "type": var_type,
                        "refs": 1,
                        "size": size
                    }
                    self.next_address += size
                    self.current_scope()[var_name] = Pointer(addr, var_type, self)
                    return None
                else:
                    raise Exception("MALLOC komutunda sözdizimi hatası")

            if command_upper.startswith("FREE"):
                match = re.match(r"FREE\s+(\w+)", command, re.IGNORECASE)
                if match:
                    ptr_name = match.group(1)
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer) and ptr.address in self.memory_pool:
                            self.memory_pool[ptr.address]["refs"] -= 1
                            if self.memory_pool[ptr.address]["refs"] <= 0:
                                del self.memory_pool[ptr.address]
                            ptr.address = None
                        else:
                            raise Exception(f"Geçersiz işaretçi: {ptr_name}")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("FREE komutunda sözdizimi hatası")

            if command_upper.startswith("MEMCPY"):
                match = re.match(r"MEMCPY\s+(\w+)\s+FROM\s+(\w+)\s+SIZE\s+(\d+)", command, re.IGNORECASE)
                if match:
                    dest_ptr, src_ptr, size = match.groups()
                    size = int(size)
                    if dest_ptr in self.current_scope() and src_ptr in self.current_scope():
                        dest = self.current_scope()[dest_ptr]
                        src = self.current_scope()[src_ptr]
                        if isinstance(dest, Pointer) and isinstance(src, Pointer):
                            if src.address in self.memory_pool and dest.address in self.memory_pool:
                                self.memory_pool[dest.address]["value"] = self.memory_pool[src.address]["value"]
                            else:
                                raise Exception("Geçersiz bellek adresi")
                        else:
                            raise Exception("Geçersiz işaretçi")
                    else:
                        raise Exception("Değişken bulunamadı")
                    return None
                else:
                    raise Exception("MEMCPY komutunda sözdizimi hatası")

            if command_upper.startswith("MEMSET"):
                match = re.match(r"MEMSET\s+(\w+)\s+VALUE\s+(.+)\s+SIZE\s+(\d+)", command, re.IGNORECASE)
                if match:
                    ptr_name, value_expr, size = match.groups()
                    size = int(size)
                    value = self.evaluate_expression(value_expr, scope_name)
                    if ptr_name in self.current_scope():
                        ptr = self.current_scope()[ptr_name]
                        if isinstance(ptr, Pointer) and ptr.address in self.memory_pool:
                            self.memory_pool[ptr.address]["value"] = value
                        else:
                            raise Exception("Geçersiz işaretçi")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("MEMSET komutunda sözdizimi hatası")

            raise Exception(f"Bilinmeyen komut: {command}")
        except Exception as e:
            error_msg = f"PDSX Hatası: {str(e)}, Satır {self.program_counter + 1 if not self.repl_mode else 'REPL'}"
            print(error_msg)
            logging.error(error_msg)
            if self.error_handler == "RESUME":
                return None
            elif self.error_handler:
                self.program_counter = self.error_handler
            else:
                self.running = False
            return None

    def evaluate_expression(self, expr, scope_name=None):
        expr = expr.strip()
        if "." in expr:
            parts = expr.split(".")
            instance = self.current_scope().get(parts[0])
            for field in parts[1:]:
                if isinstance(instance, (StructInstance, UnionInstance, ClassInstance)):
                    instance = instance.get_field(field)
                else:
                    raise Exception(f"Geçersiz alan erişimi: {expr}")
            return instance
        elif "*" in expr:
            ptr_name = expr.replace("*", "").strip()
            if ptr_name in self.current_scope():
                ptr = self.current_scope()[ptr_name]
                if isinstance(ptr, Pointer):
                    return ptr.dereference()
            raise Exception(f"Geçersiz işaretçi: {expr}")
        elif "(" in expr and ")" in expr:
            match_array = re.match(r"(\w+)\(([\d, ]+)\)", expr)
            if match_array:
                var_name, indices_str = match_array.groups()
                indices = [int(i) for i in indices_str.replace(" ", "").split(",")]
                if var_name in self.current_scope():
                    array = self.current_scope()[var_name]
                    if isinstance(array, ArrayInstance):
                        return array.get_element(indices)
                raise Exception(f"Geçersiz dizi erişimi: {expr}")
            else:
                raise Exception("Dizi erişiminde sözdizimi hatası")
        elif expr in self.types and self.types[expr]["kind"] == "ENUM":
            return self.types[expr]["values"]
        namespace = {}
        namespace.update(self.global_vars)
        namespace.update(self.current_scope())
        namespace.update(self.function_table)
        try:
            return eval(expr, namespace)
        except Exception as e:
            raise Exception(f"İfade değerlendirme hatası: {expr}, Hata: {str(e)}")

    def run(self, code=None):
        if code:
            self.parse_program(code)
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.program):
            command, scope_name = self.program[self.program_counter]
            self.execute_command(command, scope_name)
            self.program_counter += 1
            
            