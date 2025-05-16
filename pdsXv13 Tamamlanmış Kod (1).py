```python
    def _get_size(self, type_name):
        return self.get_type_size(type_name)

class UnionInstance:
    def __init__(self, fields, type_table, get_type_size):
        self.field_types = {name: type_name for name, type_name, _ in fields}
        self.init_values = {name: init_value for name, _, init_value in fields}
        self.type_table = type_table
        self.get_type_size = get_type_size
        self.sizes = {name: get_type_size(type_name) for name, type_name, _ in fields}
        max_size = max(self.sizes.values()) if self.sizes else 8
        self.value = bytearray(max_size)
        self.active_field = None
        for name, init_value in self.init_values.items():
            if init_value.upper() == "NULL" and self.field_types[name].upper() != "VOID":
                self.value = None
                self.active_field = name
                break
            elif init_value.upper() == "NAN" and self.field_types[name].upper() in ("FLOAT", "DOUBLE", "SINGLE"):
                self.value = float('nan')
                self.active_field = name
                break
            elif init_value != "None":
                self.set_field(name, init_value)
                break

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        expected_type = self.type_table.get(self.field_types[field_name].upper(), object)
        if value == "NULL" and self.field_types[field_name].upper() != "VOID":
            self.value = None
            self.active_field = field_name
            return
        if value == "NAN" and self.field_types[field_name].upper() in ("FLOAT", "DOUBLE", "SINGLE"):
            self.value = float('nan')
            self.active_field = field_name
            return
        if not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except:
                raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
        self.active_field = field_name
        fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "s", "BYTE": "b",
               "SHORT": "h", "LONG": "q", "SINGLE": "f", "BOOLEAN": "?"}
        fmt = fmt.get(self.field_types[field_name].upper(), "s")
        if fmt == "s":
            value = str(value).encode('utf-8')[:self.sizes[field_name]].ljust(self.sizes[field_name], b'\0')
        else:
            value = struct.pack(fmt, value)
            if len(value) > self.sizes[field_name]:
                raise ValueError(f"Değer boyutu alan boyutunu aşıyor: {field_name}")
            value = value.ljust(self.sizes[field_name], b'\0')
        self.value[:len(value)] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.active_field != field_name:
            raise ValueError(f"{field_name} alanı aktif değil")
        if self.value is None:
            return None
        if isinstance(self.value, float) and math.isnan(self.value):
            return float('nan')
        fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "s", "BYTE": "b",
               "SHORT": "h", "LONG": "q", "SINGLE": "f", "BOOLEAN": "?"}
        fmt = fmt.get(self.field_types[field_name].upper(), "s")
        try:
            if fmt == "s":
                return self.value[:self.sizes[field_name]].decode('utf-8').rstrip('\0')
            return struct.unpack(fmt, self.value[:self.sizes[field_name]])[0]
        except:
            raise ValueError(f"{field_name} alanından veri okunamadı")

class Pointer:
    def __init__(self, address, target_type, interpreter):
        self.address = address
        self.target_type = target_type
        self.interpreter = interpreter

    def dereference(self):
        if self.address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi adresi: {self.address}")
        value = self.interpreter.memory_pool[self.address]["value"]
        expected_type = self.interpreter.type_table.get(self.target_type.upper(), object)
        if not isinstance(value, expected_type):
            raise TypeError(f"Beklenen tip {expected_type.__name__}, ancak {type(value).__name__} bulundu")
        return value

    def set(self, value):
        if self.address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi adresi: {self.address}")
        expected_type = self.interpreter.type_table.get(self.target_type.upper(), object)
        if value == "NULL" and self.target_type.upper() != "VOID":
            self.interpreter.memory_pool[self.address]["value"] = None
            return
        if value == "NAN" and self.target_type.upper() in ("FLOAT", "DOUBLE", "SINGLE"):
            self.interpreter.memory_pool[self.address]["value"] = float('nan')
            return
        if not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except:
                raise TypeError(f"Beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
        self.interpreter.memory_pool[self.address]["value"] = value

    def add_offset(self, offset):
        new_address = self.address + offset
        if new_address not in self.interpreter.memory_pool:
            raise ValueError(f"Geçersiz işaretçi aritmetiği: {new_address}")
        return Pointer(new_address, self.target_type, self.interpreter)

class ClassDef:
    def __init__(self, name, parents=None, abstract=False, interfaces=None):
        self.name = name
        self.parents = parents or []
        self.abstract = abstract
        self.interfaces = interfaces or []
        self.methods = {}
        self.constructor = None
        self.destructor = None
        self.static_vars = {}
        self.is_mixin = False
        self.operators = {}
        self.iterators = None
        self.type_param = None

class InterfaceDef:
    def __init__(self, name):
        self.name = name
        self.methods = []

class MethodDef:
    def __init__(self, name, body, params=None, private=False, static=False):
        self.name = name
        self.body = body or []
        self.params = params or []
        self.private = private
        self.static = static

class PipelineInstance:
    def __init__(self, commands, interpreter, alias=None, return_var=None):
        self.commands = commands
        self.interpreter = interpreter
        self.current_index = 0
        self.data = []
        self.active = False
        self.status = {"executed": [], "pending": commands.copy()}
        self.id = None
        self.priority = "NORMAL"
        self.alias = alias
        self.return_var = return_var
        self.labels = {}

    def add_command(self, command, step_no=None, position=None):
        if step_no is not None:
            self.commands.insert(int(step_no), command)
            self.status["pending"].insert(int(step_no), command)
        elif position == "START":
            self.commands.insert(0, command)
            self.status["pending"].insert(0, command)
        elif position == "END":
            self.commands.append(command)
            self.status["pending"].append(command)
        else:
            self.commands.append(command)
            self.status["pending"].append(command)

    def remove_command(self, step_no):
        if 0 <= step_no < len(self.commands):
            self.status["pending"].remove(self.commands[step_no])
            self.commands.pop(step_no)

    def execute(self):
        self.active = True
        for cmd in self.commands[self.current_index:]:
            self.interpreter.execute_command(cmd)
            self.current_index += 1
            self.status["executed"].append(cmd)
            self.status["pending"].remove(cmd)
        self.active = False
        if self.return_var:
            return self.interpreter.current_scope().get(self.return_var, None)

    def next(self):
        if self.current_index < len(self.commands):
            self.interpreter.execute_command(self.commands[self.current_index])
            self.status["executed"].append(self.commands[self.current_index])
            self.status["pending"].remove(self.commands[self.current_index])
            self.current_index += 1

    def set_label(self, label, step_no):
        if isinstance(label, (str, int)):
            self.labels[str(label)] = step_no.to_bytes(1, 'big')
        elif isinstance(label, bytes):
            self.labels[label.decode()] = label

    def get_label(self, label):
        return int.from_bytes(self.labels.get(str(label), b'\x00'), 'big')

    def get_status(self):
        return self.status

class LibXCore:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.default_encoding = "utf-8"
        self.supported_encodings = [
            "utf-8", "cp1254", "iso-8859-9", "ascii", "utf-16", "utf-32",
            "cp1252", "iso-8859-1", "windows-1250", "latin-9",
            "cp932", "gb2312", "gbk", "euc-kr", "cp1251", "iso-8859-5",
            "cp1256", "iso-8859-6", "cp874", "iso-8859-7", "cp1257", "iso-8859-8"
        ]
        self.metadata = {"libx_core": {"version": "1.0.0", "dependencies": []}}
        self.stacks = {}
        self.queues = {}
        self.active_pipes = 0
        self.active_threads = 0

    def omega(self, *args):
        params = args[:-1]
        expr = args[-1]
        return lambda *values: eval(expr, {p: v for p, v in zip(params, values)})

    def list_lib(self, lib_name):
        module = self.interpreter.modules.get(lib_name, {})
        return {"functions": list(module.get("functions", {}).keys()), "classes": list(module.get("classes", {}).keys())}

    def each(self, func, iterable):
        for item in iterable:
            func(item)

    def select(self, func, iterable):
        return [item for item in iterable if func(item)]

    def insert(self, collection, value, index=None, key=None):
        if isinstance(collection, list):
            if index is None:
                collection.append(value)
            else:
                collection.insert(index, value)
        elif isinstance(collection, dict):
            if key is None:
                raise PdsXException("DICT için anahtar gerekli")
            collection[key] = value
        else:
            raise PdsXException("Geçersiz veri tipi")

    def remove(self, collection, index=None, key=None):
        if isinstance(collection, list):
            if index is None:
                raise PdsXException("Liste için indeks gerekli")
            collection.pop(index)
        elif isinstance(collection, dict):
            if key is None:
                raise PdsXException("DICT için anahtar gerekli")
            collection.pop(key, None)
        else:
            raise PdsXException("Geçersiz veri tipi")

    def pop(self, collection):
        if isinstance(collection, list):
            return collection.pop()
        raise PdsXException("Yalnızca liste için geçerli")

    def clear(self, collection):
        if isinstance(collection, (list, dict)):
            collection.clear()
        else:
            raise PdsXException("Geçersiz veri tipi")

    def slice(self, iterable, start, end=None):
        return iterable[start:end]

    def keys(self, obj):
        if isinstance(obj, dict):
            return list(obj.keys())
        raise PdsXException("Yalnızca DICT için geçerli")

    def time_now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def date_now(self):
        return datetime.now().strftime("%Y-%m-%d")

    def timer(self):
        return time.time()

    def random_int(self, min_val, max_val):
        return random.randint(min_val, max_val)

    def assert_(self, condition, message):
        if not condition:
            raise PdsXException(f"Assert hatası: {message}")

    def log(self, message, level="INFO", target=None):
        log_message = f"[{level}] {message}"
        if target:
            with open(target, "a", encoding=self.default_encoding) as f:
                f.write(log_message + "\n")
        else:
            print(log_message)

    def ifthen(self, condition, value1, value2):
        return value1 if condition else value2

    def exists(self, path):
        return os.path.exists(path)

    def mkdir(self, path):
        os.makedirs(path, exist_ok=True)

    def getenv(self, name):
        return os.getenv(name)

    def exit(self, code):
        sys.exit(code)

    def join_path(self, *parts):
        return os.path.join(*parts)

    def copy_file(self, src, dst):
        shutil.copy(src, dst)

    def move_file(self, src, dst):
        shutil.move(src, dst)

    def delete_file(self, path):
        os.remove(path)

    def floor(self, x):
        return math.floor(x)

    def ceil(self, x):
        return math.ceil(x)

    def split(self, s, sep):
        return s.split(sep)

    def join(self, iterable, sep):
        return sep.join(iterable)

    def read_lines(self, path):
        with open(path, "r", encoding=self.default_encoding) as f:
            return f.readlines()

    def write_json(self, obj, path):
        with open(path, "w", encoding=self.default_encoding) as f:
            json.dump(obj, f)

    def read_json(self, path):
        with open(path, "r", encoding=self.default_encoding) as f:
            return json.load(f)

    def list_dir(self, path):
        return os.listdir(path)

    def ping(self, host):
        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False

    def sum(self, iterable):
        return sum(iterable)

    def mean(self, iterable):
        return sum(iterable) / len(iterable) if iterable else 0

    def min(self, iterable):
        return min(iterable) if iterable else None

    def max(self, iterable):
        return max(iterable) if iterable else None

    def round(self, x, digits=0):
        return round(x, digits)

    def trim(self, s):
        return s.strip()

    def replace(self, s, old, new):
        return s.replace(old, new)

    def format(self, s, *args):
        return s.format(*args)

    def trace(self):
        return traceback.format_stack()

    def try_catch(self, block, handler):
        try:
            return block()
        except Exception as e:
            return handler(str(e))

    def sleep(self, seconds):
        time.sleep(seconds)

    def date_diff(self, date1, date2, unit="days"):
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        delta = d2 - d1
        if unit == "days":
            return delta.days
        elif unit == "seconds":
            return delta.total_seconds()
        raise PdsXException("Geçersiz birim")

    async def run_async(self, func):
        return await asyncio.to_thread(func)

    def wait(self, tasks):
        for t in tasks:
            t.join()

    def merge(self, col1, col2):
        if isinstance(col1, list) and isinstance(col2, list):
            return col1 + col2
        elif isinstance(col1, dict) and isinstance(col2, dict):
            return {**col1, **col2}
        raise PdsXException("Geçersiz veri tipi")

    def sort(self, iterable, key=None):
        return sorted(iterable, key=key)

    def memory_usage(self):
        return psutil.Process().memory_info().rss / 1024 / 1024

    def cpu_count(self):
        return multiprocessing.cpu_count()

    def type_of(self, value):
        if value is None:
            return "NULL"
        if isinstance(value, float) and math.isnan(value):
            return "NAN"
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
        elif isinstance(value, bool):
            return "BOOLEAN"
        return "UNKNOWN"

    def is_empty(self, collection):
        return len(collection) == 0

    def len(self, obj):
        return len(obj)

    def val(self, s):
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                raise PdsXException(f"Geçersiz değer: {s}")

    def str(self, value):
        return str(value)

    def listfile(self, path, pattern="*"):
        files = glob.glob(os.path.join(path, pattern))
        return [{"name": f, "metadata": {"compressed": f.endswith(".hz")}} for f in files]

    def stack(self):
        stack_id = id([])
        self.stacks[stack_id] = []
        return stack_id

    def push(self, stack_id, item):
        if stack_id in self.stacks:
            self.stacks[stack_id].append(item)
        else:
            raise PdsXException("Geçersiz yığın")

    def pop(self, stack_id):
        if stack_id in self.stacks and self.stacks[stack_id]:
            return self.stacks[stack_id].pop()
        raise PdsXException("Yığın boş veya geçersiz")

    def queue(self):
        queue_id = id([])
        self.queues[queue_id] = []
        return queue_id

    def enqueue(self, queue_id, item):
        if queue_id in self.queues:
            self.queues[queue_id].append(item)
        else:
            raise PdsXException("Geçersiz kuyruk")

    def dequeue(self, queue_id):
        if queue_id in self.queues and self.queues[queue_id]:
            return self.queues[queue_id].pop(0)
        raise PdsXException("Kuyruk boş veya geçersiz")

    def map(self, func, iterable):
        return [func(x) for x in iterable]

    def filter(self, func, iterable):
        return [x for x in iterable if func(x)]

    def reduce(self, func, iterable, initial):
        result = initial
        for x in iterable:
            result = func(result, x)
        return result

    def load_hz(self, path):
        with open(path, "r", encoding=self.default_encoding) as f:
            return f.read()

    def open(self, file_path, mode, encoding="utf-8"):
        return open(file_path, mode, encoding=encoding)

    def load_dll(self, dll_name):
        try:
            return ctypes.WinDLL(dll_name)
        except Exception as e:
            logging.error(f"DLL yükleme hatası: {dll_name}, {e}")
            raise PdsXException(f"DLL yükleme hatası: {e}")

    def load_api(self, url):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise PdsXException(f"API yükleme hatası: {url}, Durum: {response.status_code}")
            return SimpleNamespace(
                ask=lambda query: requests.post(url, json={"query": query}).json().get("response", "")
            )
        except Exception as e:
            logging.error(f"API yükleme hatası: {url}, {e}")
            raise PdsXException(f"API yükleme hatası: {e}")

    def version(self, lib_name):
        return self.metadata.get(lib_name, {}).get("version", "unknown")

    def require_version(self, lib_name, required_version):
        current = self.version(lib_name)
        if not self._check_version(current, required_version):
            raise PdsXException(f"Versiyon uyumsuzluğu: {lib_name} {required_version} gerekli, {current} bulundu")

    def _check_version(self, current, required):
        return version.parse(current) >= version.parse(required)

    def set_encoding(self, encoding):
        if encoding in self.supported_encodings:
            self.default_encoding = encoding
        else:
            raise PdsXException(f"Desteklenmeyen encoding: {encoding}")

    async def async_wait(self, seconds):
        await asyncio.sleep(seconds)

    def pdf_read_text(self, file_path):
        if not os.path.exists(file_path):
            return "PDF bulunamadı"
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ''
        return text

    def pdf_extract_tables(self, file_path):
        if not os.path.exists(file_path):
            return []
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                tables.extend(page_tables)
        return tables

    def web_get(self, url):
        try:
            response = requests.get(url)
            return response.text
        except Exception as e:
            return f"Hata: {e}"

    def system(self, resource):
        process = psutil.Process()
        if resource == "ram":
            return psutil.virtual_memory().available / 1024 / 1024
        elif resource == "cpu":
            return {"cores": multiprocessing.cpu_count(), "usage": psutil.cpu_percent()}
        elif resource == "gpu":
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                gpu_info = []
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_info.append({
                        "memory_total": mem_info.total / 1024 / 1024,
                        "memory_used": mem_info.used / 1024 / 1024,
                        "utilization": util.gpu
                    })
                return gpu_info
            except ImportError:
                return "GPU izleme için pynvml gerekli"
        elif resource == "process":
            return len(psutil.pids())
        elif resource == "thread":
            return threading.active_count()
        elif resource == "pipe":
            return self.active_pipes
        else:
            raise PdsXException(f"Geçersiz kaynak: {resource}")

class PdsXv13:
    def __init__(self):
        self.global_vars = {}
        self.shared_vars = defaultdict(list)
        self.local_scopes = [{}]
        self.types = {}
        self.classes = {}
        self.functions = {}
        self.subs = {}
        self.labels = {}
        self.program = []
        self.program_counter = 0
        self.call_stack = []
        self.running = False
        self.db_connections = {}
        self.file_handles = {}
        self.error_handler = None
        self.gosub_handler = None
        self.error_sub = None
        self.debug_mode = False
        self.trace_mode = False
        self.loop_stack = []
        self.select_stack = []
        self.if_stack = []
        self.data_list = []
        self.data_pointer = 0
        self.transaction_active = {}
        self.modules = {"core": {"functions": {}, "classes": {}, "program": []}}
        self.current_module = "main"
        self.repl_mode = False
        self.language = "en"
        self.translations = self.load_translations("lang.json")
        self.memory_manager = MemoryManager()
        self.memory_pool = {}
        self.next_address = 1000
        self.expr_cache = {}
        self.variable_cache = {}
        self.bytecode = []
        self.core = LibXCore(self)
        self.async_tasks = []
        self.performance_metrics = {"start_time": time.time(), "memory_usage": 0}
        self.supported_encodings = [
            "utf-8", "cp1254", "iso-8859-9", "ascii", "utf-16", "utf-32",
            "cp1252", "iso-8859-1", "windows-1250", "latin-9",
            "cp932", "gb2312", "gbk", "euc-kr", "cp1251", "iso-8859-5",
            "cp1256", "iso-8859-6", "cp874", "iso-8859-7", "cp1257", "iso-8859-