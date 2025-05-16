# grok yazdirdi. 27.nisan.2025 mete dinler.

import json
import os
import requests
import ctypes
import logging
import traceback
import time
from datetime import datetime
from types import SimpleNamespace
import threading
import psutil
import multiprocessing
from packaging import version
import random
import math
import shutil
import glob
import socket
import numpy as np
import pandas as pd
import scipy.stats as stats
import pdfplumber
from bs4 import BeautifulSoup
import sqlite3
import ast
import re
import struct
import asyncio
import argparse
from collections import defaultdict, namedtuple
from abc import ABC, abstractmethod
import sys
import subprocess
import importlib.metadata

# Bağımlılık Yönetimi
def install_missing_libraries():
    required = {
        'numpy': 'numpy', 'pandas': 'pandas', 'scipy': 'scipy', 'psutil': 'psutil',
        'pdfplumber': 'pdfplumber', 'bs4': 'beautifulsoup4', 'requests': 'requests',
        'packaging': 'packaging'
    }
    installed = {pkg.metadata['Name'].lower() for pkg in importlib.metadata.distributions()}
    missing = [lib for lib, pkg in required.items() if lib not in installed]
    if missing:
        print(f"Eksik kütüphaneler yükleniyor: {missing}")
        for lib in missing:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', required[lib]])
            except subprocess.CalledProcessError:
                print(f"Kütüphane yüklenemedi: {lib}")

install_missing_libraries()

# Loglama Ayarları
logging.basicConfig(filename='interpreter_errors.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Yardımcı Sınıflar
class MemoryManager:
    def __init__(self):
        self.heap = {}
        self.ref_counts = {}
        self.bitfields = {}

    def allocate(self, size: int):
        ptr = id(bytearray(size))
        self.heap[ptr] = bytearray(size)
        self.ref_counts[ptr] = 1
        return ptr

    def release(self, ptr: int):
        if ptr in self.ref_counts:
            self.ref_counts[ptr] -= 1
            if self.ref_counts[ptr] == 0:
                del self.heap[ptr]
                del self.ref_counts[ptr]
                self.bitfields.pop(ptr, None)

    def dereference(self, ptr: int):
        return self.heap.get(ptr, None)

    def set_value(self, ptr: int, value):
        if ptr in self.heap:
            if isinstance(value, (int, float)):
                self.heap[ptr][:] = struct.pack('d', float(value))
            elif isinstance(value, str):
                self.heap[ptr][:] = value.encode()
            elif isinstance(value, (list, np.ndarray)):
                self.heap[ptr][:] = value.tobytes() if hasattr(value, 'tobytes') else bytes(value)

    def sizeof(self, obj):
        if isinstance(obj, (int, float)):
            return 8
        elif isinstance(obj, str):
            return len(obj.encode())
        elif isinstance(obj, (list, np.ndarray)):
            return obj.nbytes if hasattr(obj, 'nbytes') else len(obj) * 8
        return sys.getsizeof(obj)

    def set_bitfield(self, ptr: int, field: str, value: int, bits: int):
        if ptr not in self.heap:
            raise ValueError(f"Geçersiz işaretçi: {ptr}")
        if bits not in (1, 2, 4, 8, 16, 32, 64):
            raise ValueError(f"Geçersiz bit uzunluğu: {bits}")
        self.bitfields.setdefault(ptr, {})[field] = (value, bits)

    def get_bitfield(self, ptr: int, field: str):
        if ptr not in self.bitfields or field not in self.bitfields[ptr]:
            raise ValueError(f"Geçersiz bit alanı: {ptr}.{field}")
        value, _ = self.bitfields[ptr][field]
        return value

class StructInstance:
    def __init__(self, fields, type_table):
        self.fields = {name: None for name, _ in fields}
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.sizes = {name: self._get_size(type_name) for name, type_name in fields}
        self.offsets = {}
        offset = 0
        for name in self.fields:
            self.offsets[name] = offset
            offset += self.sizes[name]

    def set_field(self, field_name, value):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        expected_type = self.type_table.get(self.field_types[field_name].upper(), object)
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
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8,
            "BITFIELD": 4, "ENUM": 4
        }
        return size_map.get(type_name.upper(), 8)

class UnionInstance:
    def __init__(self, fields, type_table):
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.active_field = None
        self.value = bytearray(max(self._get_size(t) for _, t in fields))
        self.sizes = {name: self._get_size(type_name) for name, type_name in fields}

    def set_field(self, field_name, value):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        expected_type = self.type_table.get(self.field_types[field_name].upper(), object)
        if not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except:
                raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
        self.active_field = field_name
        fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
               "SHORT": "h", "LONG": "q", "SINGLE": "f", "BITFIELD": "i", "ENUM": "i"}.get(
            self.field_types[field_name].upper(), "8s")
        if fmt == "8s":
            value = str(value).encode('utf-8')[:8].ljust(8, b'\0')
        else:
            value = struct.pack(fmt, value)
        self.value[:len(value)] = value

    def get_field(self, field_name):
        if field_name not in self.field_types:
            raise ValueError(f"Geçersiz alan: {field_name}")
        if self.active_field != field_name:
            raise ValueError(f"{field_name} alanı aktif değil")
        fmt = {"INTEGER": "i", "DOUBLE": "d", "STRING": "8s", "BYTE": "b",
               "SHORT": "h", "LONG": "q", "SINGLE": "f", "BITFIELD": "i", "ENUM": "i"}.get(
            self.field_types[field_name].upper(), "8s")
        try:
            if fmt == "8s":
                return self.value.decode('utf-8').rstrip('\0')
            return struct.unpack(fmt, self.value[:self.sizes[field_name]])[0]
        except:
            raise ValueError(f"{field_name} alanından veri okunamadı")

    def _get_size(self, type_name):
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8,
            "BITFIELD": 4, "ENUM": 4
        }
        return size_map.get(type_name.upper(), 8)

class EnumInstance:
    def __init__(self, values):
        self.values = values
        self.current = None

    def set_value(self, value):
        if value in self.values:
            self.current = value
        else:
            raise ValueError(f"Geçersiz ENUM değeri: {value}")

    def get_value(self):
        return self.current

    def get_index(self):
        return list(self.values.keys()).index(self.current) if self.current in self.values else -1

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

# LibXLowLevel Sınıfı
class LibXLowLevel:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.memory_manager = interpreter.memory_manager

    def alloc(self, size: int):
        return self.memory_manager.allocate(size)

    def free(self, ptr: int):
        self.memory_manager.release(ptr)

    def bitset(self, ptr: int, field: str, value: int, bits: int):
        self.memory_manager.set_bitfield(ptr, field, value, bits)

    def bitget(self, ptr: int, field: str):
        return self.memory_manager.get_bitfield(ptr, field)

    def memcpy(self, dest_ptr: int, src_ptr: int, size: int):
        if dest_ptr in self.memory_manager.heap and src_ptr in self.memory_manager.heap:
            self.memory_manager.heap[dest_ptr][:size] = self.memory_manager.heap[src_ptr][:size]
        else:
            raise ValueError("Geçersiz işaretçi")

    def memset(self, ptr: int, value: int, size: int):
        if ptr in self.memory_manager.heap:
            self.memory_manager.heap[ptr][:size] = bytes([value]) * size
        else:
            raise ValueError("Geçersiz işaretçi")

# LibXCore Sınıfı
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
                raise Exception("DICT için anahtar gerekli")
            collection[key] = value
        else:
            raise Exception("Geçersiz veri tipi")

    def remove(self, collection, index=None, key=None):
        if isinstance(collection, list):
            if index is None:
                raise Exception("Liste için indeks gerekli")
            collection.pop(index)
        elif isinstance(collection, dict):
            if key is None:
                raise Exception("DICT için anahtar gerekli")
            collection.pop(key, None)
        else:
            raise Exception("Geçersiz veri tipi")

    def pop(self, collection):
        if isinstance(collection, list):
            return collection.pop()
        raise Exception("Yalnızca liste için geçerli")

    def clear(self, collection):
        if isinstance(collection, (list, dict)):
            collection.clear()
        else:
            raise Exception("Geçersiz veri tipi")

    def slice(self, iterable, start, end=None):
        return iterable[start:end]

    def keys(self, obj):
        if isinstance(obj, dict):
            return list(obj.keys())
        raise Exception("Yalnızca DICT için geçerli")

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
            raise Exception(f"Assert hatası: {message}")

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
        raise Exception("Geçersiz birim")

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
        raise Exception("Geçersiz veri tipi")

    def sort(self, iterable, key=None):
        return sorted(iterable, key=key)

    def memory_usage(self):
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def cpu_count(self):
        return multiprocessing.cpu_count()

    def type_of(self, value):
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
        elif isinstance(value, np.ndarray):
            return "ARRAY"
        elif isinstance(value, pd.DataFrame):
            return "DATAFRAME"
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
                raise Exception(f"Geçersiz değer: {s}")

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
            raise Exception("Geçersiz yığın")

    def pop(self, stack_id):
        if stack_id in self.stacks and self.stacks[stack_id]:
            return self.stacks[stack_id].pop()
        raise Exception("Yığın boş veya geçersiz")

    def queue(self):
        queue_id = id([])
        self.queues[queue_id] = []
        return queue_id

    def enqueue(self, queue_id, item):
        if queue_id in self.queues:
            self.queues[queue_id].append(item)
        else:
            raise Exception("Geçersiz kuyruk")

    def dequeue(self, queue_id):
        if queue_id in self.queues and self.queues[queue_id]:
            return self.queues[queue_id].pop(0)
        raise Exception("Kuyruk boş veya geçersiz")

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
            raise Exception(f"DLL yükleme hatası: {e}")

    def load_api(self, url):
        return SimpleNamespace(
            ask=lambda query: requests.post(url, json={"query": query}).json().get("response", "")
        )

    def version(self, lib_name):
        return self.metadata.get(lib_name, {}).get("version", "unknown")

    def require_version(self, lib_name, required_version):
        current = self.version(lib_name)
        if not self._check_version(current, required_version):
            raise Exception(f"Versiyon uyumsuzluğu: {lib_name} {required_version} gerekli, {current} bulundu")

    def _check_version(self, current, required):
        return version.parse(current) >= version.parse(required)

    def set_encoding(self, encoding):
        if encoding in self.supported_encodings:
            self.default_encoding = encoding
        else:
            raise Exception(f"Desteklenmeyen encoding: {encoding}")

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

# Interpreter Çekirdeği
class pdsXv11:
    def __init__(self):
        self.global_vars = {}
        self.shared_vars = defaultdict(list)
        self.local_scopes = [{}]
        self.types = {}
        self.classes = {}
        self.interfaces = {}
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
        self.lowlevel = LibXLowLevel(self)
        self.async_tasks = []
        self.performance_metrics = {"start_time": time.time(), "memory_usage": 0, "cpu_usage": 0}
        self.supported_encodings = [
            "utf-8", "cp1254", "iso-8859-9", "ascii", "utf-16", "utf-32",
            "cp1252", "iso-8859-1", "windows-1250", "latin-9",
            "cp932", "gb2312", "gbk", "euc-kr", "cp1251", "iso-8859-5",
            "cp1256", "iso-8859-6", "cp874", "iso-8859-7", "cp1257", "iso-8859-8",
            "utf-8-sig", "utf-8-bom-less"
        ]

        self.type_table = {
            "STRING": str, "INTEGER": int, "LONG": int, "SINGLE": float, "DOUBLE": float,
            "BYTE": int, "SHORT": int, "UNSIGNED INTEGER": int, "CHAR": str,
            "LIST": list, "DICT": dict, "SET": set, "TUPLE": tuple,
            "ARRAY": np.array, "DATAFRAME": pd.DataFrame, "POINTER": None,
            "STRUCT": dict, "UNION": None, "ENUM": dict, "VOID": None, "BITFIELD": int
        }

        self.function_table = {
            "MID$": lambda s, start, length: s[start-1:start-1+length],
            "LEN": len, "RND": random.random, "ABS": abs, "INT": int,
            "LEFT$": lambda s, n: s[:n], "RIGHT$": lambda s, n: s[-n:],
            "LTRIM$": lambda s: s.lstrip(), "RTRIM$": lambda s: s.rstrip(),
            "STRING$": lambda n, c: c * n, "SPACE$": lambda n: " " * n,
            "INSTR": lambda start, s, sub: s.find(sub, start-1) + 1,
            "UCASE$": lambda s: s.upper(), "LCASE$": lambda s: s.lower(),
            "STR$": lambda n: str(n), "SQR": np.sqrt, "SIN": np.sin,
            "COS": np.cos, "TAN": np.tan, "LOG": np.log, "EXP": np.exp,
            "ATN": np.arctan, "FIX": lambda x: int(x), "ROUND": lambda x, n=0: round(x, n),
            "SGN": lambda x: -1 if x < 0 else (1 if x > 0 else 0),
            "MOD": lambda x, y: x % y, "MIN": lambda *args: min(args),
            "MAX": lambda *args: max(args), "TIMER": lambda: time.time(),
            "DATE$": lambda: time.strftime("%m-%d-%Y"),
            "TIME$": lambda: time.strftime("%H:%M:%S"),
            "INKEY$": lambda: input()[:1], "ENVIRON$": lambda var: os.environ.get(var, ""),
            "COMMAND$": lambda: " ".join(sys.argv[1:]),
            "CSRLIN": lambda: 1, "POS": lambda x: 1, "VAL": lambda s: float(s) if s.replace(".", "").isdigit() else 0,
            "ASC": lambda c: ord(c[0]),
            "MEAN": np.mean, "MEDIAN": np.median, "MODE": lambda x: stats.mode(x)[0][0],
            "STD": np.std, "VAR": np.var, "SUM": np.sum, "PROD": np.prod,
            "PERCENTILE": np.percentile, "QUANTILE": np.quantile,
            "CORR": lambda x, y: np.corrcoef(x, y)[0, 1], "COV": np.cov,
            "DESCRIBE": lambda df: df.describe(), "GROUPBY": lambda df, col: df.groupby(col),
            "FILTER": lambda df, cond: df.query(cond), "SORT": lambda df, col: df.sort_values(col),
            "HEAD": lambda df, n=5: df.head(n), "TAIL": lambda df, n=5: df.tail(n),
            "MERGE": lambda df1, df2, on: pd.merge(df1, df2, on=on),
            "TTEST": lambda sample1, sample2: stats.ttest_ind(sample1, sample2),
            "CHISQUARE": lambda observed: stats.chisquare(observed),
            "ANOVA": lambda *groups: stats.f_oneway(*groups),
            "REGRESS": lambda x, y: stats.linregress(x, y),
            "CONCATENATE": np.concatenate, "STACK": np.stack, "VSTACK": np.vstack,
            "HSTACK": np.hstack, "DOT": np.dot, "CROSS": np.cross,
            "NORM": np.linalg.norm, "INV": np.linalg.inv, "SOLVE": np.linalg.solve,
            "LINSPACE": np.linspace, "ARANGE": np.arange, "ZEROS": np.zeros,
            "ONES": np.ones, "FULL": np.full, "EYE": np.eye, "DIAG": np.diag,
            "RESHAPE": np.reshape, "TRANSPOSE": np.transpose, "FLIP": np.flip,
            "ROLL": np.roll,
            "PIVOT_TABLE": lambda df, **kwargs: df.pivot_table(**kwargs),
            "CROSSTAB": pd.crosstab, "FILLNA": lambda df, value: df.fillna(value),
            "DROPNA": lambda df, **kwargs: df.dropna(**kwargs),
            "ASTYPE": lambda df, dtype: df.astype(dtype),
            "MELT": lambda df, **kwargs: pd.melt(df, **kwargs),
            "CUT": pd.cut, "QCUT": pd.qcut, "TO_DATETIME": pd.to_datetime,
            "RESAMPLE": lambda df, rule, **kwargs: df.resample(rule, **kwargs),
            "ROLLING": lambda df, window: df.rolling(window),
            "EWMA": lambda df, **kwargs: df.ewm(**kwargs).mean(),
            "SHIFT": lambda df, periods: df.shift(periods),
            "DIFF": lambda df, periods=1: df.diff(periods),
            "PCT_CHANGE": lambda df: df.pct_change(),
            "EOF": lambda n: self.file_handles[n].eof() if hasattr(self.file_handles[n], 'eof') else False,
            "LOC": lambda n: self.file_handles[n].tell(),
            "LOF": lambda n: os.path.getsize(self.file_handles[n].name),
            "FREEFILE": lambda: min(set(range(1, 100)) - set(self.file_handles.keys())),
            "CHR$": lambda n: chr(n),
            "INPUT$": lambda n, f: self.file_handles[f].read(n),
            "MKI$": lambda n: struct.pack("i", n).decode('latin1'),
            "MKS$": lambda n: struct.pack("f", n).decode('latin1'),
            "MKD$": lambda n: struct.pack("d", n).decode('latin1'),
            "DIR$": lambda path: os.listdir(path),
            "ISDIR": lambda path: os.path.isdir(path),
            "PDF_READ_TEXT": self.core.pdf_read_text,
            "PDF_EXTRACT_TABLES": self.core.pdf_extract_tables,
            "WEB_GET": self.core.web_get,
            "SINH": math.sinh, "COSH": math.cosh, "TANH": math.tanh,
            "ASINH": math.asinh, "ACOSH": math.acosh, "ATANH": math.atanh,
            "SIND": lambda x: math.sin(math.radians(x)),
            "COSD": lambda x: math.cos(math.radians(x)),
            "TAND": lambda x: math.tan(math.radians(x)),
            "PI": math.pi, "E": math.e,
            "BIN": bin, "HEX": hex, "OCT": oct,
            "ADDR": lambda x: id(x),
            "SIZEOF": lambda x: self.memory_manager.sizeof(x),
            "NEW": self.memory_manager.allocate,
            "DELETE": self.memory_manager.release,
            "ASYNC_WAIT": self.core.async_wait,
            "THREAD_COUNT": threading.active_count,
            "CURRENT_THREAD": threading.get_ident,
            "MAP": self.core.map,
            "FILTER": self.core.filter,
            "REDUCE": self.core.reduce,
            "OMEGA": self.core.omega,
            "LIST_LIB": self.core.list_lib,
            "EACH": self.core.each,
            "SELECT": self.core.select,
            "INSERT": self.core.insert,
            "REMOVE": self.core.remove,
            "POP": self.core.pop,
            "CLEAR": self.core.clear,
            "SLICE": self.core.slice,
            "KEYS": self.core.keys,
            "TIME_NOW": self.core.time_now,
            "DATE_NOW": self.core.date_now,
            "TIMER": self.core.timer,
            "RANDOM_INT": self.core.random_int,
            "ASSERT": self.core.assert_,
            "LOG": self.core.log,
            "IFTHEN": self.core.ifthen,
            "EXISTS": self.core.exists,
            "MKDIR": self.core.mkdir,
            "GETENV": self.core.getenv,
            "EXIT": self.core.exit,
            "JOIN_PATH": self.core.join_path,
            "COPY_FILE": self.core.copy_file,
            "MOVE_FILE": self.core.move_file,
            "DELETE_FILE": self.core.delete_file,
            "FLOOR": self.core.floor,
            "CEIL": self.core.ceil,
            "SPLIT": self.core.split,
            "JOIN": self.core.join,
            "READ_LINES": self.core.read_lines,
            "WRITE_JSON": self.core.write_json,
            "READ_JSON": self.core.read_json,
            "LIST_DIR": self.core.list_dir,
            "PING": self.core.ping,
            "SUM": self.core.sum,
            "MEAN": self.core.mean,
            "MIN": self.core.min,
            "MAX": self.core.max,
            "ROUND": self.core.round,
            "TRIM": self.core.trim,
            "REPLACE": self.core.replace,
            "FORMAT": self.core.format,
            "TRACE": self.core.trace,
            "TRY_CATCH": self.core.try_catch,
            "SLEEP": self.core.sleep,
            "DATE_DIFF": self.core.date_diff,
            "RUN_ASYNC": self.core.run_async,
            "WAIT": self.core.wait,
            "MERGE": self.core.merge,
            "SORT": self.core.sort,
            "MEMORY_USAGE": self.core.memory_usage,
            "CPU_COUNT": self.core.cpu_count,
            "TYPE_OF": self.core.type_of,
            "IS_EMPTY": self.core.is_empty,
            "LEN": self.core.len,
            "VAL": self.core.val,
            "STR": self.core.str,
            "LISTFILE": self.core.listfile,
            "STACK": self.core.stack,
            "PUSH": self.core.push,
            "POP": self.core.pop,
            "QUEUE": self.core.queue,
            "ENQUEUE": self.core.enqueue,
            "DEQUEUE": self.core.dequeue,
            "LOAD_HZ": self.core.load_hz,
            "OPEN": self.core.open,
            "LOAD_DLL": self.core.load_dll,
            "LOAD_API": self.core.load_api,
            "VERSION": self.core.version,
            "REQUIRE_VERSION": self.core.require_version,
            "SET_ENCODING": self.core.set_encoding,
            "PDF_READ_TEXT": self.core.pdf_read_text,
            "PDF_EXTRACT_TABLES": self.core.pdf_extract_tables,
            "WEB_GET": self.core.web_get
        }

        self.operator_table = {
            '++': lambda x: x + 1,
            '--': lambda x: x - 1,
            '<<': lambda x, y: x << y,
            '>>': lambda x, y: x >> y,
            '&': lambda x, y: x & y,
            '|': lambda x, y: x | y,
            '^': lambda x, y: x ^ y,
            '~': lambda x: ~x,
            'AND': lambda x, y: x and y,
            'OR': lambda x, y: x or y,
            'XOR': lambda x, y: bool(x) != bool(y),
            'NOT': lambda x: not x,
            '+=': lambda x, y: x + y,
            '-=': lambda x, y: x - y,
            '*=': lambda x, y: x * y,
            '/=': lambda x, y: x / y,
            '%=': lambda x, y: x % y,
            '&=': lambda x, y: x & y,
            '|=': lambda x, y: x | y,
            '^=': lambda x, y: x ^ y,
            '<<=': lambda x, y: x << y,
            '>>=': lambda x, y: x >> y
        }

    def load_translations(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Dil dosyası bulunamadı. Varsayılan İngilizce kullanılacak.")
            return {
                "en": {"PRINT": "Print", "ERROR": "Error", "LET": "Let", "DIM": "Dim"},
                "tr": {"PRINT": "Yaz", "ERROR": "Hata", "LET": "Atama", "DIM": "Tanımla"}
            }

    def translate(self, key):
        return self.translations.get(self.language, {}).get(key, key)

    def current_scope(self):
        return self.local_scopes[-1]

    def parse_program(self, code, module_name="main", lightweight=False, as_library=False):
        self.current_module = module_name
        self.modules[module_name] = {
            "program": [],
            "functions": {},
            "subs": {},
            "classes": {},
            "interfaces": {},
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
        enum_values = {}
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            line_upper = line.upper()
            if line_upper.startswith("SUB "):
                match = re.match(r"SUB\s+(\w+)(?:\((.*)\))?", line, re.IGNORECASE)
                if match:
                    sub_name, params = match.groups()
                    params = [p.strip() for p in params.split(",")] if params else []
                    self.subs[sub_name] = {"line": i + 1, "params": params}
                    self.modules[module_name]["subs"][sub_name] = i + 1
                    current_sub = sub_name
                    i += 1
                else:
                    raise Exception("SUB komutunda sözdizimi hatası")
            elif line_upper.startswith("FUNCTION "):
                match = re.match(r"FUNCTION\s+(\w+)(?:\((.*)\))?", line, re.IGNORECASE)
                if match:
                    func_name, params = match.groups()
                    params = [p.strip() for p in params.split(",")] if params else []
                    self.functions[func_name] = {"line": i + 1, "params": params}
                    self.modules[module_name]["functions"][func_name] = i + 1
                    current_function = func_name
                    i += 1
                else:
                    raise Exception("FUNCTION komutunda sözdizimi hatası")
            elif line_upper.startswith("TYPE "):
                type_name = line[5:].strip()
                current_type = type_name
                type_fields[type_name] = []
                i += 1
            elif line_upper.startswith("END TYPE"):
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[current_type]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            elif line_upper.startswith("UNION "):
                union_name = line[6:].strip()
                current_type = union_name
                type_fields[union_name] = []
                i += 1
            elif line_upper.startswith("END UNION"):
                self.types[current_type] = {"kind": "UNION", "fields": type_fields[current_type]}
                self.modules[module_name]["types"][current_type] = self.types[current_type]
                current_type = None
                i += 1
            elif line_upper.startswith("ENUM "):
                enum_name = line[5:].strip()
                current_type = enum_name
                enum_values[enum_name] = {}
                value_index = 0
                i += 1
                while i < len(lines) and not lines[i].strip().upper().startswith("END ENUM"):
                    value_name = lines[i].strip()
                    if value_name:
                        enum_values[enum_name][value_name] = value_index
                        value_index += 1
                    i += 1
                self.types[enum_name] = {"kind": "ENUM", "values": enum_values[enum_name]}
                self.modules[module_name]["types"][enum_name] = self.types[enum_name]
                current_type = None
                i += 1
                continue
            elif line_upper.startswith("STRUCT "):
                struct_name = line[7:].strip()
                current_type = struct_name
                type_fields[struct_name] = []
                i += 1
                while i < len(lines) and not lines[i].strip().upper().startswith("END STRUCT"):
                    field_line = lines[i].strip()
                    if field_line:
                        match = re.match(r"(\w+)\s+AS\s+(\w+)", field_line, re.IGNORECASE)
                        if match:
                            field_name, field_type = match.groups()
                            type_fields[struct_name].append((field_name, field_type))
                        else:
                            raise Exception(f"STRUCT tanımı hatası: {field_line}")
                    i += 1
                self.types[struct_name] = {"kind": "STRUCT", "fields": type_fields[struct_name]}
                self.modules[module_name]["types"][struct_name] = self.types[struct_name]
                current_type = None
                i += 1
                continue
            elif line_upper.startswith("ABSTRACT CLASS "):
                match = re.match(r"ABSTRACT CLASS\s+(\w+)(?:\s+EXTENDS\s+(\w+))?(?:\s+IMPLEMENTS\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_name, interface_name = match.groups()
                    current_class = class_name
                    class_info[class_name] = {
                        'methods': {},
                        'private_methods': {},
                        'static_vars': {},
                        'parent': parent_name,
                        'interfaces': [interface_name] if interface_name else [],
                        'abstract': True
                    }
                    i += 1
                else:
                    raise Exception("ABSTRACT CLASS komutunda sözdizimi hatası")
            elif line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+EXTENDS\s+(\w+))?(?:\s+IMPLEMENTS\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_name, interface_name = match.groups()
                    current_class = class_name
                    class_info[class_name] = {
                        'methods': {},
                        'private_methods': {},
                        'static_vars': {},
                        'parent': parent_name,
                        'interfaces': [interface_name] if interface_name else [],
                        'abstract': False
                    }
                    i += 1
                else:
                    raise Exception("CLASS komutunda sözdizimi hatası")
            elif line_upper.startswith("INTERFACE "):
                interface_name = line[10:].strip()
                current_interface = interface_name
                interface_info[interface_name] = {'methods': {}}
                i += 1
            elif line_upper.startswith("END INTERFACE"):
                self.interfaces[current_interface] = interface_info[current_interface]
                self.modules[module_name]["interfaces"][current_interface] = interface_info[current_interface]
                current_interface = None
                i += 1
            elif current_interface and line_upper.startswith("DECLARE "):
                match = re.match(r"DECLARE\s+(SUB|FUNCTION)\s+(\w+)(?:\((.*)\))?", line, re.IGNORECASE)
                if match:
                    method_type, method_name, params = match.groups()
                    params = [p.strip() for p in params.split(",")] if params else []
                    interface_info[current_interface]['methods'][method_name] = {
                        'type': method_type,
                        'params': params
                    }
                    i += 1
                else:
                    raise Exception("INTERFACE DECLARE komutunda sözdizimi hatası")
            elif line_upper.startswith("END CLASS"):
                parent_class = class_info[current_class]['parent']
                parent_methods = self.classes.get(parent_class, type('', (), {'_vars': {}})()).__dict__ if parent_class else {}
                parent_static_vars = class_info.get(parent_class, {}).get('static_vars', {})
                interfaces = class_info[current_class]['interfaces']
                for iface in interfaces:
                    if iface in self.interfaces:
                        for method_name, method_info in self.interfaces[iface]['methods'].items():
                            if method_name not in class_info[current_class]['methods'] and \
                               method_name not in class_info[current_class]['private_methods']:
                                raise Exception(f"{current_class} sınıfı {iface} arayüzündeki {method_name} metodunu uygulamıyor")
                if class_info[current_class]['abstract']:
                    class_def = type(current_class, (ABC, self.classes.get(parent_class, object)), {
                        '_vars': {},
                        '_static_vars': {**parent_static_vars, **class_info[current_class]['static_vars']},
                        '__init__': lambda self: None,
                        'private_methods': class_info[current_class]['private_methods'],
                        **{k: abstractmethod(v) if k.startswith('_') else v for k, v in class_info[current_class]['methods'].items()},
                        **{k: v for k, v in parent_methods.items() if k not in class_info[current_class]['methods'] and k != 'private_methods'}
                    })
                else:
                    class_def = type(current_class, (self.classes.get(parent_class, object),), {
                        '_vars': {},
                        '_static_vars': {**parent_static_vars, **class_info[current_class]['static_vars']},
                        '__init__': lambda self: None,
                        'private_methods': class_info[current_class]['private_methods'],
                        **{k: v for k, v in class_info[current_class]['methods'].items()},
                        **{k: v for k, v in parent_methods.items() if k not in class_info[current_class]['methods'] and k != 'private_methods'}
                    })
                self.classes[current_class] = class_def
                self.modules[module_name]["classes"][current_class] = class_def
                current_class = None
                i += 1
            elif current_class and line_upper.startswith(("SUB ", "PRIVATE SUB ", "FUNCTION ", "PRIVATE FUNCTION ")):
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
                else:
                    raise Exception(f"{method_type} tanımı hatası: {line}")
            elif current_class and line_upper.startswith("STATIC "):
                match = re.match(r"STATIC\s+(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    var_name, var_type = match.groups()
                    class_info[current_class]['static_vars'][var_name] = self.type_table.get(var_type.upper(), None)()
                    i += 1
                else:
                    raise Exception("STATIC komutunda sözdizimi hatası")
            elif current_class and line_upper.startswith("DIM "):
                match = re.match(r"DIM\s+(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    var_name, var_type = match.groups()
                    class_info[current_class]['methods']['__init__'] = lambda self: self._vars.update({var_name: self.type_table.get(var_type.upper(), None)()})
                    i += 1
                else:
                    raise Exception("DIM komutunda sözdizimi hatası")
            elif line_upper == "END SUB" or line_upper == "END FUNCTION":
                current_sub = None
                current_function = None
                i += 1
            elif line_upper.startswith("LABEL "):
                label_name = line[6:].strip()
                self.labels[label_name] = i
                self.modules[module_name]["labels"][label_name] = i
                i += 1
            elif line_upper.startswith("DATA "):
                data_items = line[5:].split(",")
                self.data_list.extend([item.strip() for item in data_items])
                i += 1
            elif line_upper.startswith("COMPILE"):
                self.bytecode = self.compile_to_bytecode(code)
                return None
            else:
                if current_sub or current_function:
                    self.program.append((line, current_sub or current_function))
                    self.modules[module_name]["program"].append((line, current_sub or current_function))
                else:
                    self.program.append((line, None))
                    self.modules[module_name]["program"].append((line, None))
                i += 1

    def import_module(self, file_name, module_name=None):
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in (".basx", ".libx", ".hx", ".hz"):
            for try_ext in [".hz", ".hx", ".libx", ".basx"]:
                if os.path.exists(file_name + try_ext):
                    file_name = file_name + try_ext
                    ext = try_ext
                    break
            else:
                raise Exception("Desteklenmeyen dosya uzantısı. Uzantı .basX, .libX, .hX veya .hz olmalı")
        if not os.path.exists(file_name):
            raise Exception(f"Dosya bulunamadı: {file_name}")
        module_name = module_name or os.path.splitext(os.path.basename(file_name))[0]
        if module_name in self.modules:
            raise Exception(f"Modül zaten yüklü: {module_name}")
        with open(file_name, 'r', encoding='utf-8') as f:
            code = f.read()
        old_program = self.program
        old_functions = self.functions.copy()
        old_subs = self.subs.copy()
        old_classes = self.classes.copy()
        old_interfaces = self.interfaces.copy()
        old_types = self.types.copy()
        old_labels = self.labels.copy()
        old_module = self.current_module
        self.program = []
        self.functions.clear()
        self.subs.clear()
        self.classes.clear()
        self.interfaces.clear()
        self.types.clear()
        self.labels.clear()
        if ext == ".hz":
            self.parse_program(code, module_name, lightweight=True)
        elif ext == ".hx":
            self.parse_definitions(code, module_name)
        elif ext == ".libx":
            self.parse_program(code, module_name, as_library=True)
        else:
            self.parse_program(code, module_name)
        self.program = old_program
        self.functions.update(old_functions)
        self.subs.update(old_subs)
        self.classes.update(old_classes)
        self.interfaces.update(old_interfaces)
        self.types.update(old_types)
        self.labels.update(old_labels)
        self.current_module = old_module

    def parse_definitions(self, code, module_name):
        lines = code.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            line_upper = line.upper()
            if line_upper.startswith("DECLARE FUNCTION"):
                match = re.match(r"DECLARE FUNCTION\s+(\w+)(?:\((.*)\))?", line, re.IGNORECASE)
                if match:
                    func_name, params = match.groups()
                    params = [p.strip() for p in params.split(",")] if params else []
                    self.functions[func_name] = {"line": None, "params": params}
                    self.modules[module_name]["functions"][func_name] = None
            elif line_upper.startswith("DECLARE SUB"):
                match = re.match(r"DECLARE SUB\s+(\w+)(?:\((.*)\))?", line, re.IGNORECASE)
                if match:
                    sub_name, params = match.groups()
                    params = [p.strip() for p in params.split(",")] if params else []
                    self.subs[sub_name] = {"line": None, "params": params}
                    self.modules[module_name]["subs"][sub_name] = None

    def execute_method(self, method_name, method_body, params, args, scope_name):
        if len(args) != len(params):
            raise Exception(f"Parametre uyuşmazlığı: {method_name}")
        local_scope = {p: a for p, a in zip(params, args)}
        self.local_scopes.append(local_scope)
        for line in method_body:
            self.execute_command(line, scope_name)
        self.local_scopes.pop()
        return local_scope.get('RETURN', None)

    def evaluate_expression(self, expr, scope_name=None):
        cache_key = (expr, scope_name)
        if cache_key not in self.expr_cache:
            try:
                tree = ast.parse(expr, mode='eval')
                self.expr_cache[cache_key] = compile(tree, '<string>', 'eval')
            except SyntaxError:
                raise Exception(f"Geçersiz ifade: {expr}")
        namespace = {}
        namespace.update(self.global_vars)
        namespace.update(self.current_scope())
        namespace.update(self.function_table)
        try:
            return eval(self.expr_cache[cache_key], namespace)
        except Exception as e:
            raise Exception(f"İfade değerlendirme hatası: {expr}, {str(e)}")

    async def run_async(self, code):
        self.parse_program(code)
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.program):
            command, scope = self.program[self.program_counter]
            if self.debug_mode:
                print(f"DEBUG: Satır {self.program_counter + 1}: {command}")
                await asyncio.sleep(0)
            next_pc = self.execute_command(command, scope)
            if next_pc is not None:
                self.program_counter = next_pc
            else:
                self.program_counter += 1
        self.running = False

    def execute_command(self, command, scope_name=None):
        command = command.strip()
        if not command:
            return None
        command_upper = command.upper()

        if self.trace_mode:
            logging.debug(f"TRACE: Satır {self.program_counter + 1}: {command}")

        try:
            if command_upper == "CLS":
                os.system('cls' if os.name == 'nt' else 'clear')
                return None

            if command_upper.startswith("BEEP"):
                print("\a")
                return None

            if command_upper.startswith("REM ") or command_upper.startswith("'"):
                return None

            if command_upper == "END":
                self.running = False
                return None

            if command_upper.startswith("STOP"):
                self.running = False
                return None

            if command_upper.startswith("SYSTEM"):
                match = re.match(r"SYSTEM\s+(.+)", command, re.IGNORECASE)
                if match:
                    cmd = match.group(1).strip()
                    os.system(cmd)
                    return None
                else:
                    raise Exception("SYSTEM komutunda sözdizimi hatası")

            if command_upper.startswith("OPEN"):
                match = re.match(r"OPEN\s+\"([^\"]+)\"\s+FOR\s+(\w+)\s+AS\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    file_path, mode, file_number = match.groups()
                    file_number = int(file_number)
                    mode_map = {
                        "INPUT": "r", "OUTPUT": "w", "APPEND": "a", "BINARY": "rb",
                        "RANDOM": "r+b"
                    }
                    if mode.upper() not in mode_map:
                        raise Exception(f"Geçersiz dosya modu: {mode}")
                    self.file_handles[file_number] = open(file_path, mode_map[mode.upper()], encoding='utf-8' if mode.upper() != "BINARY" else None)
                    return None
                else:
                    raise Exception("OPEN komutunda sözdizimi hatası")

            if command_upper.startswith("CLOSE"):
                match = re.match(r"CLOSE\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    file_number = int(match.group(1))
                    if file_number in self.file_handles:
                        self.file_handles[file_number].close()
                        del self.file_handles[file_number]
                    return None
                else:
                    raise Exception("CLOSE komutunda sözdizimi hatası")

            if command_upper.startswith("WRITE #"):
                match = re.match(r"WRITE\s+#(\d+),\s*(.+)", command, re.IGNORECASE)
                if match:
                    file_number, data = match.groups()
                    file_number = int(file_number)
                    if file_number in self.file_handles:
                        data_value = self.evaluate_expression(data, scope_name)
                        self.file_handles[file_number].write(str(data_value) + "\n")
                        self.file_handles[file_number].flush()
                    return None
                else:
                    raise Exception("WRITE # komutunda sözdizimi hatası")

            if command_upper.startswith("INPUT #"):
                match = re.match(r"INPUT\s+#(\d+),\s*(\w+)", command, re.IGNORECASE)
                if match:
                    file_number, var_name = match.groups()
                    file_number = int(file_number)
                    if file_number in self.file_handles:
                        line = self.file_handles[file_number].readline().strip()
                        self.current_scope()[var_name] = line
                    return None
                else:
                    raise Exception("INPUT # komutunda sözdizimi hatası")

            if command_upper.startswith("SEEK"):
                match = re.match(r"SEEK\s+#(\d+),\s*(.+)", command, re.IGNORECASE)
                if match:
                    file_number, position = match.groups()
                    file_number = int(file_number)
                    position = self.evaluate_expression(position, scope_name)
                    if file_number in self.file_handles:
                        self.file_handles[file_number].seek(position)
                    return None
                else:
                    raise Exception("SEEK komutunda sözdizimi hatası")

            if command_upper.startswith("GET"):
                match = re.match(r"GET\s+#(\d+),\s*(\w+)", command, re.IGNORECASE)
                if match:
                    file_number, var_name = match.groups()
                    file_number = int(file_number)
                    if file_number in self.file_handles:
                        data = self.file_handles[file_number].read(8)
                        self.current_scope()[var_name] = struct.unpack('d', data)[0]
                    return None
                else:
                    raise Exception("GET komutunda sözdizimi hatası")

            if command_upper.startswith("PUT"):
                match = re.match(r"PUT\s+#(\d+),\s*(.+)", command, re.IGNORECASE)
                if match:
                    file_number, value = match.groups()
                    file_number = int(file_number)
                    value = self.evaluate_expression(value, scope_name)
                    if file_number in self.file_handles:
                        self.file_handles[file_number].write(struct.pack('d', float(value)))
                        self.file_handles[file_number].flush()
                    return None
                else:
                    raise Exception("PUT komutunda sözdizimi hatası")

            if command_upper.startswith("LINE INPUT"):
                match = re.match(r"LINE INPUT\s+\"([^\"]+)\",\s*(\w+)", command, re.IGNORECASE)
                if match:
                    prompt, var_name = match.groups()
                    value = input(prompt)
                    self.current_scope()[var_name] = value
                    return None
                else:
                    raise Exception("LINE INPUT komutunda sözdizimi hatası")

            if command_upper.startswith("READ"):
                match = re.match(r"READ\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    if self.data_pointer < len(self.data_list):
                        self.current_scope()[var_name] = self.data_list[self.data_pointer]
                        self.data_pointer += 1
                    else:
                        raise Exception("Veri listesi sonuna ulaşıldı")
                    return None
                else:
                    raise Exception("READ komutunda sözdizimi hatası")

            if command_upper.startswith("RESTORE"):
                self.data_pointer = 0
                return None

            if command_upper.startswith("SWAP"):
                match = re.match(r"SWAP\s+(\w+),\s*(\w+)", command, re.IGNORECASE)
                if match:
                    var1, var2 = match.groups()
                    scope = self.current_scope()
                    if var1 in scope and var2 in scope:
                        scope[var1], scope[var2] = scope[var2], scope[var1]
                    else:
                        raise Exception(f"Değişkenler bulunamadı: {var1}, {var2}")
                    return None
                else:
                    raise Exception("SWAP komutunda sözdizimi hatası")

            if command_upper.startswith("KILL"):
                match = re.match(r"KILL\s+\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    file_path = match.group(1)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    else:
                        raise Exception(f"Dosya bulunamadı: {file_path}")
                    return None
                else:
                    raise Exception("KILL komutunda sözdizimi hatası")

            if command_upper.startswith("NAME"):
                match = re.match(r"NAME\s+\"([^\"]+)\"\s+AS\s+\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    old_name, new_name = match.groups()
                    if os.path.exists(old_name):
                        os.rename(old_name, new_name)
                    else:
                        raise Exception(f"Dosya bulunamadı: {old_name}")
                    return None
                else:
                    raise Exception("NAME komutunda sözdizimi hatası")

            if command_upper.startswith("MKDIR"):
                match = re.match(r"MKDIR\s+\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    os.makedirs(path, exist_ok=True)
                    return None
                else:
                    raise Exception("MKDIR komutunda sözdizimi hatası")

            if command_upper.startswith("RMDIR"):
                match = re.match(r"RMDIR\s+\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    if os.path.exists(path):
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        raise Exception(f"Dizin bulunamadı: {path}")
                    return None
                else:
                    raise Exception("RMDIR komutunda sözdizimi hatası")

            if command_upper.startswith("CHDIR"):
                match = re.match(r"CHDIR\s+\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    if os.path.exists(path):
                        os.chdir(path)
                    else:
                        raise Exception(f"Dizin bulunamadı: {path}")
                    return None
                else:
                    raise Exception("CHDIR komutunda sözdizimi hatası")

            if command_upper.startswith("FILES"):
                match = re.match(r"FILES\s+\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    if os.path.exists(path):
                        print("\n".join(os.listdir(path)))
                    else:
                        raise Exception(f"Dizin bulunamadı: {path}")
                    return None
                else:
                    raise Exception("FILES komutunda sözdizimi hatası")

            if command_upper.startswith("CHAIN"):
                match = re.match(r"CHAIN\s+\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    file_path = match.group(1)
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code = f.read()
                        self.run(code)
                        self.running = False
                    else:
                        raise Exception(f"Dosya bulunamadı: {file_path}")
                    return None
                else:
                    raise Exception("CHAIN komutunda sözdizimi hatası")

            if command_upper.startswith("COMMON"):
                match = re.match(r"COMMON\s+(.+)", command, re.IGNORECASE)
                if match:
                    var_names = [v.strip() for v in match.group(1).split(",")]
                    for var in var_names:
                        if var in self.current_scope():
                            self.shared_vars[var].append(self.current_scope()[var])
                        else:
                            raise Exception(f"Değişken bulunamadı: {var}")
                    return None
                else:
                    raise Exception("COMMON komutunda sözdizimi hatası")

            if command_upper.startswith("DECLARE"):
                match = re.match(r"DECLARE\s+(FUNCTION|SUB)\s+(\w+)(?:\((.*)\))?", command, re.IGNORECASE)
                if match:
                    decl_type, name, params = match.groups()
                    params = [p.strip() for p in params.split(",")] if params else []
                    if decl_type.upper() == "FUNCTION":
                        self.functions[name] = {"line": None, "params": params}
                    else:
                        self.subs[name] = {"line": None, "params": params}
                    return None
                else:
                    raise Exception("DECLARE komutunda sözdizimi hatası")

            if command_upper.startswith("DEF"):
                match = re.match(r"DEF\s+(\w+)\((.*)\)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    func_name, params, expr = match.groups()
                    params = [p.strip() for p in params.split(",") if p.strip()]
                    self.functions[func_name] = {
                        "line": None,
                        "params": params,
                        "expr": expr
                    }
                    return None
                else:
                    raise Exception("DEF komutunda sözdizimi hatası")

            if command_upper.startswith("REDIM"):
                match = re.match(r"REDIM\s+(\w+)\s*\((.+)\)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, dims, var_type = match.groups()
                    dims = [self.evaluate_expression(d.strip(), scope_name) for d in dims.split(",")]
                    if var_type.upper() in self.type_table:
                        self.current_scope()[var_name] = np.zeros(dims, dtype=self.type_table[var_type.upper()])
                    else:
                        raise Exception(f"Geçersiz veri tipi: {var_type}")
                    return None
                else:
                    raise Exception("REDIM komutunda sözdizimi hatası")

            if command_upper.startswith("ERASE"):
                match = re.match(r"ERASE\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    if var_name in self.current_scope():
                        del self.current_scope()[var_name]
                    else:
                        raise Exception(f"Değişken bulunamadı: {var_name}")
                    return None
                else:
                    raise Exception("ERASE komutunda sözdizimi hatası")

            if command_upper.startswith("SQLITE CONNECT"):
                match = re.match(r"SQLITE CONNECT\s+\"([^\"]+)\"\s+AS\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    db_path, db_number = match.groups()
                    db_number = int(db_number)
                    self.db_connections[db_number] = sqlite3.connect(db_path)
                    return None
                else:
                    raise Exception("SQLITE CONNECT komutunda sözdizimi hatası")

            if command_upper.startswith("SQLITE EXECUTE"):
                match = re.match(r"SQLITE EXECUTE\s+#(\d+),\s*\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    db_number, query = match.groups()
                    db_number = int(db_number)
                    if db_number in self.db_connections:
                        cursor = self.db_connections[db_number].cursor()
                        cursor.execute(query)
                        self.db_connections[db_number].commit()
                    else:
                        raise Exception(f"Veritabanı bağlantısı bulunamadı: #{db_number}")
                    return None
                else:
                    raise Exception("SQLITE EXECUTE komutunda sözdizimi hatası")

            if command_upper.startswith("SQLITE QUERY"):
                match = re.match(r"SQLITE QUERY\s+#(\d+),\s*\"([^\"]+)\",\s*(\w+)", command, re.IGNORECASE)
                if match:
                    db_number, query, var_name = match.groups()
                    db_number = int(db_number)
                    if db_number in self.db_connections:
                        cursor = self.db_connections[db_number].cursor()
                        cursor.execute(query)
                        results = cursor.fetchall()
                        self.current_scope()[var_name] = results
                    else:
                        raise Exception(f"Veritabanı bağlantısı bulunamadı: #{db_number}")
                    return None
                else:
                    raise Exception("SQLITE QUERY komutunda sözdizimi hatası")

            if command_upper.startswith("SQLITE CLOSE"):
                match = re.match(r"SQLITE CLOSE\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    db_number = int(match.group(1))
                    if db_number in self.db_connections:
                        self.db_connections[db_number].close()
                        del self.db_connections[db_number]
                    return None
                else:
                    raise Exception("SQLITE CLOSE komutunda sözdizimi hatası")

            if command_upper.startswith("BEGIN TRANSACTION"):
                match = re.match(r"BEGIN TRANSACTION\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    db_number = int(match.group(1))
                    if db_number in self.db_connections:
                        self.transaction_active[db_number] = True
                        cursor = self.db_connections[db_number].cursor()
                        cursor.execute("BEGIN TRANSACTION")
                    else:
                        raise Exception(f"Veritabanı bağlantısı bulunamadı: #{db_number}")
                    return None
                else:
                    raise Exception("BEGIN TRANSACTION komutunda sözdizimi hatası")

            if command_upper.startswith("COMMIT"):
                match = re.match(r"COMMIT\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    db_number = int(match.group(1))
                    if db_number in self.db_connections and self.transaction_active.get(db_number, False):
                        self.db_connections[db_number].commit()
                        self.transaction_active[db_number] = False
                    else:
                        raise Exception(f"Aktif işlem yok veya bağlantı bulunamadı: #{db_number}")
                    return None
                else:
                    raise Exception("COMMIT komutunda sözdizimi hatası")

            if command_upper.startswith("ROLLBACK"):
                match = re.match(r"ROLLBACK\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    db_number = int(match.group(1))
                    if db_number in self.db_connections and self.transaction_active.get(db_number, False):
                        self.db_connections[db_number].rollback()
                        self.transaction_active[db_number] = False
                    else:
                        raise Exception(f"Aktif işlem yok veya bağlantı bulunamadı: #{db_number}")
                    return None
                else:
                    raise Exception("ROLLBACK komutunda sözdizimi hatası")

            if command_upper.startswith("PRINT"):
                match = re.match(r"PRINT\s*(.+)?", command, re.IGNORECASE)
                if match:
                    expr = match.group(1)
                    if expr:
                        parts = [part.strip() for part in expr.split(";")]
                        output = []
                        for part in parts:
                            if part:
                                result = self.evaluate_expression(part, scope_name)
                                output.append(str(result))
                            else:
                                output.append(" ")
                        print("".join(output), end="")
                    else:
                        print()
                    return None
                else:
                    raise Exception("PRINT komutunda sözdizimi hatası")

            if command_upper.startswith("LET"):
                match = re.match(r"LET\s+(\w+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    var_name, expr = match.groups()
                    value = self.evaluate_expression(expr, scope_name)
                    self.current_scope()[var_name] = value
                    return None
                else:
                    raise Exception("LET komutunda sözdizimi hatası")

            if command_upper.startswith("DIM"):
                match = re.match(r"DIM\s+(\w+)\s*(?:\((.+)\))?\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, dims, var_type = match.groups()
                    if dims:
                        dims = [self.evaluate_expression(d.strip(), scope_name) for d in dims.split(",")]
                        if var_type.upper() in self.type_table:
                            self.current_scope()[var_name] = np.zeros(dims, dtype=self.type_table[var_type.upper()])
                        elif var_type.upper() in self.types:
                            type_info = self.types[var_type.upper()]
                            if type_info["kind"] == "STRUCT":
                                self.current_scope()[var_name] = StructInstance(type_info["fields"], self.type_table)
                            elif type_info["kind"] == "UNION":
                                self.current_scope()[var_name] = UnionInstance(type_info["fields"], self.type_table)
                            elif type_info["kind"] == "ENUM":
                                self.current_scope()[var_name] = EnumInstance(type_info["values"])
                        else:
                            raise Exception(f"Geçersiz veri tipi: {var_type}")
                    else:
                        if var_type.upper() in self.type_table:
                            self.current_scope()[var_name] = self.type_table[var_type.upper()]()
                        elif var_type.upper() in self.types:
                            type_info = self.types[var_type.upper()]
                            if type_info["kind"] == "STRUCT":
                                self.current_scope()[var_name] = StructInstance(type_info["fields"], self.type_table)
                            elif type_info["kind"] == "UNION":
                                self.current_scope()[var_name] = UnionInstance(type_info["fields"], self.type_table)
                            elif type_info["kind"] == "ENUM":
                                self.current_scope()[var_name] = EnumInstance(type_info["values"])
                        else:
                            raise Exception(f"Geçersiz veri tipi: {var_type}")
                    return None
                else:
                    raise Exception("DIM komutunda sözdizimi hatası")

            if command_upper.startswith("IF"):
                match = re.match(r"IF\s+(.+)\s+THEN\s*(.+)?", command, re.IGNORECASE)
                if match:
                    condition, then_clause = match.groups()
                    condition_result = self.evaluate_expression(condition, scope_name)
                    self.if_stack.append({"condition": condition_result, "else": False})
                    if condition_result:
                        if then_clause:
                            return self.execute_command(then_clause, scope_name)
                    else:
                        return self.find_else_or_endif()
                    return None
                else:
                    raise Exception("IF komutunda sözdizimi hatası")

            if command_upper == "ELSE":
                if self.if_stack and not self.if_stack[-1]["else"]:
                    self.if_stack[-1]["else"] = True
                    if self.if_stack[-1]["condition"]:
                        return self.find_endif()
                    return None
                else:
                    raise Exception("ELSE komutu eşleşen IF olmadan kullanıldı")

            if command_upper == "ENDIF":
                if self.if_stack:
                    self.if_stack.pop()
                    return None
                else:
                    raise Exception("ENDIF komutu eşleşen IF olmadan kullanıldı")

            if command_upper.startswith("WHILE"):
                match = re.match(r"WHILE\s+(.+)", command, re.IGNORECASE)
                if match:
                    condition = match.group(1)
                    condition_result = self.evaluate_expression(condition, scope_name)
                    if condition_result:
                        self.loop_stack.append({"type": "WHILE", "start": self.program_counter, "condition": condition})
                    else:
                        return self.find_wend()
                    return None
                else:
                    raise Exception("WHILE komutunda sözdizimi hatası")

            if command_upper == "WEND":
                if self.loop_stack and self.loop_stack[-1]["type"] == "WHILE":
                    condition = self.loop_stack[-1]["condition"]
                    condition_result = self.evaluate_expression(condition, scope_name)
                    if condition_result:
                        return self.loop_stack[-1]["start"]
                    else:
                        self.loop_stack.pop()
                    return None
                else:
                    raise Exception("WEND komutu eşleşen WHILE olmadan kullanıldı")

            if command_upper.startswith("FOR"):
                match = re.match(r"FOR\s+(\w+)\s*=\s*(.+)\s+TO\s+(.+)(?:\s+STEP\s+(.+))?", command, re.IGNORECASE)
                if match:
                    var_name, start, end, step = match.groups()
                    start_val = self.evaluate_expression(start, scope_name)
                    end_val = self.evaluate_expression(end, scope_name)
                    step_val = self.evaluate_expression(step, scope_name) if step else 1
                    self.current_scope()[var_name] = start_val
                    self.loop_stack.append({
                        "type": "FOR",
                        "var": var_name,
                        "end": end_val,
                        "step": step_val,
                        "start_line": self.program_counter
                    })
                    if step_val > 0 and start_val > end_val or step_val < 0 and start_val < end_val:
                        return self.find_next()
                    return None
                else:
                    raise Exception("FOR komutunda sözdizimi hatası")

            if command_upper == "NEXT":
                if self.loop_stack and self.loop_stack[-1]["type"] == "FOR":
                    loop = self.loop_stack[-1]
                    var_name = loop["var"]
                    current_val = self.current_scope()[var_name]
                    step = loop["step"]
                    end = loop["end"]
                    current_val += step
                    self.current_scope()[var_name] = current_val
                    if step > 0 and current_val <= end or step < 0 and current_val >= end:
                        return loop["start_line"]
                    else:
                        self.loop_stack.pop()
                    return None
                else:
                    raise Exception("NEXT komutu eşleşen FOR olmadan kullanıldı")

            if command_upper.startswith("DO"):
                match = re.match(r"DO(?:\s+(.+))?", command, re.IGNORECASE)
                if match:
                    condition = match.group(1)
                    if condition and condition.upper().startswith("WHILE"):
                        condition = condition[5:].strip()
                        condition_result = self.evaluate_expression(condition, scope_name)
                        if not condition_result:
                            return self.find_loop()
                        self.loop_stack.append({"type": "DO_WHILE", "start": self.program_counter, "condition": condition})
                    elif condition and condition.upper().startswith("UNTIL"):
                        condition = condition[5:].strip()
                        condition_result = self.evaluate_expression(condition, scope_name)
                        if condition_result:
                            return self.find_loop()
                        self.loop_stack.append({"type": "DO_UNTIL", "start": self.program_counter, "condition": condition})
                    else:
                        self.loop_stack.append({"type": "DO", "start": self.program_counter})
                    return None
                else:
                    raise Exception("DO komutunda sözdizimi hatası")

            if command_upper.startswith("LOOP"):
                match = re.match(r"LOOP(?:\s+(.+))?", command, re.IGNORECASE)
                if match and self.loop_stack:
                    loop = self.loop_stack[-1]
                    condition = match.group(1)
                    if loop["type"] == "DO":
                        return loop["start"]
                    elif loop["type"] == "DO_WHILE" and (not condition or condition.upper().startswith("WHILE")):
                        loop_condition = loop["condition"]
                        condition_result = self.evaluate_expression(loop_condition, scope_name)
                        if condition_result:
                            return loop["start"]
                        else:
                            self.loop_stack.pop()
                    elif loop["type"] == "DO_UNTIL" and (not condition or condition.upper().startswith("UNTIL")):
                        loop_condition = loop["condition"]
                        condition_result = self.evaluate_expression(loop_condition, scope_name)
                        if not condition_result:
                            return loop["start"]
                        else:
                            self.loop_stack.pop()
                    return None
                else:
                    raise Exception("LOOP komutu eşleşen DO olmadan kullanıldı")

            if command_upper.startswith("GOTO"):
                match = re.match(r"GOTO\s+(\w+)", command, re.IGNORECASE)
                if match:
                    label = match.group(1)
                    if label in self.labels:
                        return self.labels[label]
                    else:
                        raise Exception(f"Etiket bulunamadı: {label}")
                else:
                    raise Exception("GOTO komutunda sözdizimi hatası")

            if command_upper.startswith("GOSUB"):
                match = re.match(r"GOSUB\s+(\w+)", command, re.IGNORECASE)
                if match:
                    label = match.group(1)
                    if label in self.labels:
                        self.call_stack.append(self.program_counter + 1)
                        return self.labels[label]
                    else:
                        raise Exception(f"Etiket bulunamadı: {label}")
                else:
                    raise Exception("GOSUB komutunda sözdizimi hatası")

            if command_upper == "RETURN":
                if self.call_stack:
                    return self.call_stack.pop()
                elif scope_name in self.subs or scope_name in self.functions:
                    return None
                else:
                    raise Exception("RETURN komutu eşleşen GOSUB olmadan kullanıldı")

            if command_upper.startswith("ON ERROR GOTO"):
                match = re.match(r"ON ERROR GOTO\s+(\w+)", command, re.IGNORECASE)
                if match:
                    label = match.group(1)
                    if label in self.labels:
                        self.error_handler = self.labels[label]
                    else:
                        raise Exception(f"Etiket bulunamadı: {label}")
                    return None
                else:
                    raise Exception("ON ERROR GOTO komutunda sözdizimi hatası")

            if command_upper == "RESUME":
                if self.error_handler is not None:
                    return self.error_handler
                else:
                    raise Exception("RESUME komutu ON ERROR GOTO olmadan kullanıldı")

            if command_upper.startswith("SELECT CASE"):
                match = re.match(r"SELECT CASE\s+(.+)", command, re.IGNORECASE)
                if match:
                    expr = match.group(1)
                    value = self.evaluate_expression(expr, scope_name)
                    self.select_stack.append({"value": value, "matched": False})
                    return None
                else:
                    raise Exception("SELECT CASE komutunda sözdizimi hatası")

            if command_upper.startswith("CASE"):
                if self.select_stack:
                    match = re.match(r"CASE\s+(.+)", command, re.IGNORECASE)
                    if match:
                        case_expr = match.group(1)
                        if case_expr.upper() == "ELSE":
                            if not self.select_stack[-1]["matched"]:
                                self.select_stack[-1]["matched"] = True
                            else:
                                return self.find_end_select()
                        else:
                            case_value = self.evaluate_expression(case_expr, scope_name)
                            if self.select_stack[-1]["value"] == case_value and not self.select_stack[-1]["matched"]:
                                self.select_stack[-1]["matched"] = True
                            else:
                                return self.find_next_case_or_end()
                        return None
                    else:
                        raise Exception("CASE komutunda sözdizimi hatası")
                else:
                    raise Exception("CASE komutu eşleşen SELECT CASE olmadan kullanıldı")

            if command_upper == "END SELECT":
                if self.select_stack:
                    self.select_stack.pop()
                    return None
                else:
                    raise Exception("END SELECT komutu eşleşen SELECT CASE olmadan kullanıldı")

            if command_upper.startswith("CALL"):
                match = re.match(r"CALL\s+(\w+)(?:\((.*)\))?", command, re.IGNORECASE)
                if match:
                    sub_name, params = match.groups()
                    params = [self.evaluate_expression(p.strip(), scope_name) for p in params.split(",")] if params else []
                    if sub_name in self.subs:
                        sub_info = self.subs[sub_name]
                        if len(params) != len(sub_info["params"]):
                            raise Exception(f"Parametre uyuşmazlığı: {sub_name}")
                        self.local_scopes.append({p: v for p, v in zip(sub_info["params"], params)})
                        self.call_stack.append(self.program_counter + 1)
                        return sub_info["line"]
                    else:
                        raise Exception(f"Alt program bulunamadı: {sub_name}")
                else:
                    raise Exception("CALL komutunda sözdizimi hatası")

            if command_upper.startswith("FUNCTION"):
                match = re.match(r"FUNCTION\s+(\w+)(?:\((.*)\))?", command, re.IGNORECASE)
                if match:
                    func_name, params = match.groups()
                    params = [p.strip() for p in params.split(",")] if params else []
                    self.functions[func_name] = {"line": self.program_counter + 1, "params": params}
                    return self.find_end_function()
                else:
                    raise Exception("FUNCTION komutunda sözdizimi hatası")

            if command_upper.startswith("SUB"):
                match = re.match(r"SUB\s+(\w+)(?:\((.*)\))?", command, re.IGNORECASE)
                if match:
                    sub_name, params = match.groups()
                    params = [p.strip() for p in params.split(",")] if params else []
                    self.subs[sub_name] = {"line": self.program_counter + 1, "params": params}
                    return self.find_end_sub()
                else:
                    raise Exception("SUB komutunda sözdizimi hatası")

            if command_upper.startswith("EXIT"):
                match = re.match(r"EXIT\s+(SUB|FUNCTION|FOR|WHILE|DO)", command, re.IGNORECASE)
                if match:
                    exit_type = match.group(1).upper()
                    if exit_type == "SUB" and scope_name in self.subs:
                        return None
                    elif exit_type == "FUNCTION" and scope_name in self.functions:
                        return None
                    elif exit_type == "FOR" and self.loop_stack and self.loop_stack[-1]["type"] == "FOR":
                        self.loop_stack.pop()
                        return self.find_next()
                    elif exit_type == "WHILE" and self.loop_stack and self.loop_stack[-1]["type"] == "WHILE":
                        self.loop_stack.pop()
                        return self.find_wend()
                    elif exit_type == "DO" and self.loop_stack and self.loop_stack[-1]["type"].startswith("DO"):
                        self.loop_stack.pop()
                        return self.find_loop()
                    else:
                        raise Exception(f"EXIT {exit_type} için uygun bağlam bulunamadı")
                else:
                    raise Exception("EXIT komutunda sözdizimi hatası")

            if command_upper.startswith("TYPE"):
                match = re.match(r"TYPE\s+(\w+)", command, re.IGNORECASE)
                if match:
                    type_name = match.group(1)
                    fields = []
                    i = self.program_counter + 1
                    while i < len(self.program) and not self.program[i][0].strip().upper().startswith("END TYPE"):
                        field_line = self.program[i][0].strip()
                        if field_line:
                            field_match = re.match(r"(\w+)\s+AS\s+(\w+)", field_line, re.IGNORECASE)
                            if field_match:
                                fields.append(field_match.groups())
                            else:
                                raise Exception(f"TYPE tanımında hata: {field_line}")
                        i += 1
                    self.types[type_name] = {"kind": "STRUCT", "fields": fields}
                    return i
                else:
                    raise Exception("TYPE komutunda sözdizimi hatası")

            if command_upper.startswith("STRUCT"):
                match = re.match(r"STRUCT\s+(\w+)", command, re.IGNORECASE)
                if match:
                    struct_name = match.group(1)
                    fields = []
                    i = self.program_counter + 1
                    while i < len(self.program) and not self.program[i][0].strip().upper().startswith("END STRUCT"):
                        field_line = self.program[i][0].strip()
                        if field_line:
                            field_match = re.match(r"(\w+)\s+AS\s+(\w+)", field_line, re.IGNORECASE)
                            if field_match:
                                fields.append(field_match.groups())
                            else:
                                raise Exception(f"STRUCT tanımında hata: {field_line}")
                        i += 1
                    self.types[struct_name] = {"kind": "STRUCT", "fields": fields}
                    return i
                else:
                    raise Exception("STRUCT komutunda sözdizimi hatası")

            if command_upper.startswith("UNION"):
                match = re.match(r"UNION\s+(\w+)", command, re.IGNORECASE)
                if match:
                    union_name = match.group(1)
                    fields = []
                    i = self.program_counter + 1
                    while i < len(self.program) and not self.program[i][0].strip().upper().startswith("END UNION"):
                        field_line = self.program[i][0].strip()
                        if field_line:
                            field_match = re.match(r"(\w+)\s+AS\s+(\w+)", field_line, re.IGNORECASE)
                            if field_match:
                                fields.append(field_match.groups())
                            else:
                                raise Exception(f"UNION tanımında hata: {field_line}")
                        i += 1
                    self.types[union_name] = {"kind": "UNION", "fields": fields}
                    return i
                else:
                    raise Exception("UNION komutunda sözdizimi hatası")

            if command_upper.startswith("ENUM"):
                match = re.match(r"ENUM\s+(\w+)", command, re.IGNORECASE)
                if match:
                    enum_name = match.group(1)
                    values = {}
                    value_index = 0
                    i = self.program_counter + 1
                    while i < len(self.program) and not self.program[i][0].strip().upper().startswith("END ENUM"):
                        value_name = self.program[i][0].strip()
                        if value_name:
                            values[value_name] = value_index
                            value_index += 1
                        i += 1
                    self.types[enum_name] = {"kind": "ENUM", "values": values}
                    return i
                else:
                    raise Exception("ENUM komutunda sözdizimi hatası")

            if command_upper.startswith("NEW"):
                match = re.match(r"NEW\s+(\w+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, type_name = match.groups()
                    if type_name.upper() in self.types:
                        type_info = self.types[type_name.upper()]
                        if type_info["kind"] == "STRUCT":
                            self.current_scope()[var_name] = StructInstance(type_info["fields"], self.type_table)
                        elif type_info["kind"] == "UNION":
                            self.current_scope()[var_name] = UnionInstance(type_info["fields"], self.type_table)
                        elif type_info["kind"] == "ENUM":
                            self.current_scope()[var_name] = EnumInstance(type_info["values"])
                    elif type_name.upper() in self.classes:
                        self.current_scope()[var_name] = self.classes[type_name.upper()]()
                    else:
                        raise Exception(f"Geçersiz tip: {type_name}")
                    return None
                else:
                    raise Exception("NEW komutunda sözdizimi hatası")

            if command_upper.startswith("SET"):
                match = re.match(r"SET\s+(\w+)\.(\w+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    var_name, field_name, value_expr = match.groups()
                    value = self.evaluate_expression(value_expr, scope_name)
                    if var_name in self.current_scope():
                        instance = self.current_scope()[var_name]
                        if isinstance(instance, (StructInstance, UnionInstance)):
                            instance.set_field(field_name, value)
                        elif isinstance(instance, EnumInstance):
                            instance.set_value(value)
                        elif hasattr(instance, field_name):
                            setattr(instance, field_name, value)
                        else:
                            raise Exception(f"Geçersiz alan: {field_name}")
                    else:
                        raise Exception(f"Değişken bulunamadı: {var_name}")
                    return None
                else:
                    raise Exception("SET komutunda sözdizimi hatası")

            if command_upper.startswith("GET"):
                match = re.match(r"GET\s+(\w+)\.(\w+)\s*,\s*(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, field_name, target_var = match.groups()
                    if var_name in self.current_scope():
                        instance = self.current_scope()[var_name]
                        if isinstance(instance, (StructInstance, UnionInstance)):
                            self.current_scope()[target_var] = instance.get_field(field_name)
                        elif isinstance(instance, EnumInstance):
                            self.current_scope()[target_var] = instance.get_value()
                        elif hasattr(instance, field_name):
                            self.current_scope()[target_var] = getattr(instance, field_name)
                        else:
                            raise Exception(f"Geçersiz alan: {field_name}")
                    else:
                        raise Exception(f"Değişken bulunamadı: {var_name}")
                    return None
                else:
                    raise Exception("GET komutunda sözdizimi hatası")

            if command_upper.startswith("CONST"):
                match = re.match(r"CONST\s+(\w+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    const_name, value_expr = match.groups()
                    if const_name in self.global_vars:
                        raise Exception(f"Sabit zaten tanımlı: {const_name}")
                    value = self.evaluate_expression(value_expr, scope_name)
                    self.global_vars[const_name] = value
                    return None
                else:
                    raise Exception("CONST komutunda sözdizimi hatası")

            if command_upper.startswith("INCLUDE"):
                match = re.match(r"INCLUDE\s+\"([^\"]+)\"", command, re.IGNORECASE)
                if match:
                    file_path = match.group(1)
                    self.import_module(file_path)
                    return None
                else:
                    raise Exception("INCLUDE komutunda sözdizimi hatası")

            if command_upper.startswith("IMPORT"):
                match = re.match(r"IMPORT\s+\"([^\"]+)\"\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    file_path, module_name = match.groups()
                    self.import_module(file_path, module_name)
                    return None
                else:
                    raise Exception("IMPORT komutunda sözdizimi hatası")

            if command_upper.startswith("TRACE"):
                self.trace_mode = command_upper == "TRACE ON"
                return None

            if command_upper.startswith("DEBUG"):
                self.debug_mode = command_upper == "DEBUG ON"
                return None

            if command_upper.startswith("OPTION"):
                match = re.match(r"OPTION\s+(\w+)\s+(\w+)", command, re.IGNORECASE)
                if match:
                    option, value = match.groups()
                    if option.upper() == "ENCODING":
                        if value.lower() in self.supported_encodings:
                            self.core.set_encoding(value.lower())
                        else:
                            raise Exception(f"Desteklenmeyen kodlama: {value}")
                    elif option.upper() == "LANGUAGE":
                        if value.lower() in self.translations:
                            self.language = value.lower()
                        else:
                            raise Exception(f"Desteklenmeyen dil: {value}")
                    else:
                        raise Exception(f"Geçersiz seçenek: {option}")
                    return None
                else:
                    raise Exception("OPTION komutunda sözdizimi hatası")

            if command_upper.startswith("LOCK"):
                match = re.match(r"LOCK\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    file_number = int(match.group(1))
                    if file_number in self.file_handles:
                        self.file_handles[file_number].flush()
                        os.fsync(self.file_handles[file_number].fileno())
                    else:
                        raise Exception(f"Dosya bulunamadı: #{file_number}")
                    return None
                else:
                    raise Exception("LOCK komutunda sözdizimi hatası")

            if command_upper.startswith("UNLOCK"):
                match = re.match(r"UNLOCK\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    file_number = int(match.group(1))
                    if file_number in self.file_handles:
                        # Dosya kilidi serbest bırakma (işletim sistemine bağlı)
                        pass
                    else:
                        raise Exception(f"Dosya bulunamadı: #{file_number}")
                    return None
                else:
                    raise Exception("UNLOCK komutunda sözdizimi hatası")

            if command_upper.startswith("THREAD"):
                match = re.match(r"THREAD\s+(\w+)\s*,\s*(.+)", command, re.IGNORECASE)
                if match:
                    thread_name, sub_name = match.groups()
                    if sub_name in self.subs:
                        sub_info = self.subs[sub_name]
                        thread = threading.Thread(target=self.execute_sub, args=(sub_name, []))
                        self.async_tasks.append(thread)
                        thread.start()
                        self.current_scope()[thread_name] = thread.ident
                    else:
                        raise Exception(f"Alt program bulunamadı: {sub_name}")
                    return None
                else:
                    raise Exception("THREAD komutunda sözdizimi hatası")

            if command_upper.startswith("ASYNC"):
                match = re.match(r"ASYNC\s+(\w+)\s*,\s*(.+)", command, re.IGNORECASE)
                if match:
                    task_name, sub_name = match.groups()
                    if sub_name in self.subs:
                        task = asyncio.create_task(self.execute_sub_async(sub_name, []))
                        self.async_tasks.append(task)
                        self.current_scope()[task_name] = id(task)
                    else:
                        raise Exception(f"Alt program bulunamadı: {sub_name}")
                    return None
                else:
                    raise Exception("ASYNC komutunda sözdizimi hatası")

            if command_upper.startswith("WAIT"):
                match = re.match(r"WAIT\s+(\w+)", command, re.IGNORECASE)
                if match:
                    task_name = match.group(1)
                    if task_name in self.current_scope():
                        task_id = self.current_scope()[task_name]
                        for task in self.async_tasks:
                            if id(task) == task_id or task.ident == task_id:
                                if isinstance(task, threading.Thread):
                                    task.join()
                                elif isinstance(task, asyncio.Task):
                                    asyncio.run(task)
                                break
                    else:
                        raise Exception(f"Görev bulunamadı: {task_name}")
                    return None
                else:
                    raise Exception("WAIT komutunda sözdizimi hatası")

            if command_upper.startswith("BITSET"):
                match = re.match(r"BITSET\s+(\d+)\s*,\s*(\w+)\s*,\s*(\d+)\s*,\s*(\d+)", command, re.IGNORECASE)
                if match:
                    ptr, field, value, bits = map(int, match.groups())
                    self.lowlevel.bitset(ptr, field, value, bits)
                    return None
                else:
                    raise Exception("BITSET komutunda sözdizimi hatası")

            if command_upper.startswith("BITGET"):
                match = re.match(r"BITGET\s+(\d+)\s*,\s*(\w+)\s*,\s*(\w+)", command, re.IGNORECASE)
                if match:
                    ptr, field, var_name = match.groups()
                    ptr = int(ptr)
                    self.current_scope()[var_name] = self.lowlevel.bitget(ptr, field)
                    return None
                else:
                    raise Exception("BITGET komutunda sözdizimi hatası")

            if command_upper.startswith("MEMCPY"):
                match = re.match(r"MEMCPY\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", command, re.IGNORECASE)
                if match:
                    dest_ptr, src_ptr, size = map(int, match.groups())
                    self.lowlevel.memcpy(dest_ptr, src_ptr, size)
                    return None
                else:
                    raise Exception("MEMCPY komutunda sözdizimi hatası")

            if command_upper.startswith("MEMSET"):
                match = re.match(r"MEMSET\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", command, re.IGNORECASE)
                if match:
                    ptr, value, size = map(int, match.groups())
                    self.lowlevel.memset(ptr, value, size)
                    return None
                else:
                    raise Exception("MEMSET komutunda sözdizimi hatası")

            if command_upper.startswith("PTR"):
                match = re.match(r"PTR\s+(\w+)\s+AS\s+(\w+)\s+TO\s+(.+)", command, re.IGNORECASE)
                if match:
                    var_name, type_name, target = match.groups()
                    target_value = self.evaluate_expression(target, scope_name)
                    address = self.memory_manager.allocate(self.memory_manager.sizeof(target_value))
                    self.memory_manager.set_value(address, target_value)
                    self.current_scope()[var_name] = Pointer(address, type_name, self)
                    return None
                else:
                    raise Exception("PTR komutunda sözdizimi hatası")

            if command_upper.startswith("DEREF"):
                match = re.match(r"DEREF\s+(\w+)\s*,\s*(\w+)", command, re.IGNORECASE)
                if match:
                    ptr_name, var_name = match.groups()
                    if ptr_name in self.current_scope():
                        pointer = self.current_scope()[ptr_name]
                        if isinstance(pointer, Pointer):
                            self.current_scope()[var_name] = pointer.dereference()
                        else:
                            raise Exception(f"Geçersiz işaretçi: {ptr_name}")
                    else:
                        raise Exception(f"Değişken bulunamadı: {ptr_name}")
                    return None
                else:
                    raise Exception("DEREF komutunda sözdizimi hatası")

            # Fonksiyon çağrıları ve değişken atamaları
            match = re.match(r"(\w+)\s*=\s*(.+)", command, re.IGNORECASE)
            if match:
                var_name, expr = match.groups()
                if var_name.upper() in self.functions:
                    raise Exception(f"{var_name} bir fonksiyon adı, değişken olarak kullanılamaz")
                value = self.evaluate_expression(expr, scope_name)
                self.current_scope()[var_name] = value
                return None

            # Fonksiyon veya alt program çağrısı
            match = re.match(r"(\w+)(?:\((.*)\))?", command, re.IGNORECASE)
            if match:
                name, params = match.groups()
                params = [self.evaluate_expression(p.strip(), scope_name) for p in params.split(",")] if params else []
                if name.upper() in self.functions:
                    func_info = self.functions[name.upper()]
                    if func_info.get("expr"):
                        namespace = {p: v for p, v in zip(func_info["params"], params)}
                        return self.evaluate_expression(func_info["expr"], scope_name)
                    if len(params) != len(func_info["params"]):
                        raise Exception(f"Parametre uyuşmazlığı: {name}")
                    self.local_scopes.append({p: v for p, v in zip(func_info["params"], params)})
                    self.call_stack.append(self.program_counter + 1)
                    return func_info["line"]
                elif name.upper() in self.subs:
                    sub_info = self.subs[name.upper()]
                    if len(params) != len(sub_info["params"]):
                        raise Exception(f"Parametre uyuşmazlığı: {name}")
                    self.local_scopes.append({p: v for p, v in zip(sub_info["params"], params)})
                    self.call_stack.append(self.program_counter + 1)
                    return sub_info["line"]
                else:
                    raise Exception(f"Bilinmeyen komut veya fonksiyon: {name}")
            else:
                raise Exception(f"Geçersiz komut: {command}")

        except Exception as e:
            if self.error_handler is not None:
                self.current_scope()["ERR"] = str(e)
                return self.error_handler
            else:
                raise Exception(f"Hata: {str(e)}")

    def execute_sub(self, sub_name, params):
        if sub_name in self.subs:
            sub_info = self.subs[sub_name]
            if len(params) != len(sub_info["params"]):
                raise Exception(f"Parametre uyuşmazlığı: {sub_name}")
            self.local_scopes.append({p: v for p, v in zip(sub_info["params"], params)})
            self.program_counter = sub_info["line"]
            while self.program_counter < len(self.program):
                command, scope = self.program[self.program_counter]
                if command.strip().upper() == "END SUB":
                    break
                next_pc = self.execute_command(command, sub_name)
                if next_pc is not None:
                    self.program_counter = next_pc
                else:
                    self.program_counter += 1
            self.local_scopes.pop()
        else:
            raise Exception(f"Alt program bulunamadı: {sub_name}")

    async def execute_sub_async(self, sub_name, params):
        return self.execute_sub(sub_name, params)

    def find_else_or_endif(self):
        i = self.program_counter + 1
        nesting = 0
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd.startswith("IF"):
                nesting += 1
            elif cmd == "ENDIF":
                if nesting == 0:
                    return i
                nesting -= 1
            elif cmd == "ELSE" and nesting == 0:
                return i
            i += 1
        raise Exception("Eşleşen ELSE veya ENDIF bulunamadı")

    def find_endif(self):
        i = self.program_counter + 1
        nesting = 0
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd.startswith("IF"):
                nesting += 1
            elif cmd == "ENDIF":
                if nesting == 0:
                    return i
                nesting -= 1
            i += 1
        raise Exception("Eşleşen ENDIF bulunamadı")

    def find_wend(self):
        i = self.program_counter + 1
        nesting = 0
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd.startswith("WHILE"):
                nesting += 1
            elif cmd == "WEND":
                if nesting == 0:
                    return i
                nesting -= 1
            i += 1
        raise Exception("Eşleşen WEND bulunamadı")

    def find_next(self):
        i = self.program_counter + 1
        nesting = 0
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd.startswith("FOR"):
                nesting += 1
            elif cmd == "NEXT":
                if nesting == 0:
                    return i
                nesting -= 1
            i += 1
        raise Exception("Eşleşen NEXT bulunamadı")

    def find_loop(self):
        i = self.program_counter + 1
        nesting = 0
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd.startswith("DO"):
                nesting += 1
            elif cmd.startswith("LOOP"):
                if nesting == 0:
                    return i
                nesting -= 1
            i += 1
        raise Exception("Eşleşen LOOP bulunamadı")

    def find_end_select(self):
        i = self.program_counter + 1
        nesting = 0
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd.startswith("SELECT CASE"):
                nesting += 1
            elif cmd == "END SELECT":
                if nesting == 0:
                    return i
                nesting -= 1
            i += 1
        raise Exception("Eşleşen END SELECT bulunamadı")

    def find_next_case_or_end(self):
        i = self.program_counter + 1
        nesting = 0
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd.startswith("SELECT CASE"):
                nesting += 1
            elif cmd == "END SELECT":
                if nesting == 0:
                    return i
                nesting -= 1
            elif cmd.startswith("CASE") and nesting == 0:
                return i
            i += 1
        raise Exception("Eşleşen CASE veya END SELECT bulunamadı")

    def find_end_function(self):
        i = self.program_counter + 1
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd == "END FUNCTION":
                return i
            i += 1
        raise Exception("Eşleşen END FUNCTION bulunamadı")

    def find_end_sub(self):
        i = self.program_counter + 1
        while i < len(self.program):
            cmd = self.program[i][0].strip().upper()
            if cmd == "END SUB":
                return i
            i += 1
        raise Exception("Eşleşen END SUB bulunamadı")

    def compile_to_bytecode(self, code):
        bytecode = []
        lines = code.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            bytecode.append(("EXEC", line))
        return bytecode

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
        print("pdsXv11 REPL - Çıkmak için EXIT yazın")
        while self.repl_mode:
            try:
                command = input(">>> ")
                if command.strip().upper() == "EXIT":
                    self.repl_mode = False
                    break
                self.execute_command(command)
            except Exception as e:
                print(f"Hata: {e}")
        self.repl_mode = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pdsXv11 Interpreter")
    parser.add_argument("file", nargs="?", help="Çalıştırılacak BASIC dosyası")
    parser.add_argument("--repl", action="store_true", help="REPL modunda çalıştır")
    args = parser.parse_args()

    interpreter = pdsXv11()
    if args.repl:
        interpreter.repl()
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
        interpreter.run(code)
    else:
        print("Lütfen bir dosya belirtin veya --repl ile REPL modunu kullanın")