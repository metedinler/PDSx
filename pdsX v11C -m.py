import json
import os
import requests
import ctypes
import logging
import traceback
import time
from datetime import datetime
from types import SimpleNamespace
from threading import Thread
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
logging.basicConfig(filename='interpreter_errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

# Yardımcı Sınıflar
class MemoryManager:
    def __init__(self):
        self.heap = {}
        self.ref_counts = {}

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

    def dereference(self, ptr: int):
        return self.heap.get(ptr, None)

    def set_value(self, ptr: int, value):
        if ptr in self.heap:
            if isinstance(value, (int, float)):
                self.heap[ptr][:] = struct.pack('d', float(value))
            elif isinstance(value, str):
                self.heap[ptr][:] = value.encode()

    def sizeof(self, obj):
        if isinstance(obj, (int, float)):
            return 8
        elif isinstance(obj, str):
            return len(obj.encode())
        elif isinstance(obj, (list, np.ndarray)):
            return obj.nbytes if hasattr(obj, 'nbytes') else len(obj) * 8
        return 0

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
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

class UnionInstance:
    def __init__(self, fields, type_table):
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table
        self.active_field = None
        self.value = bytearray(8)
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
               "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(self.field_types[field_name].upper(), "8s")
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
               "SHORT": "h", "LONG": "q", "SINGLE": "f"}.get(self.field_types[field_name].upper(), "8s")
        try:
            if fmt == "8s":
                return self.value.decode('utf-8').rstrip('\0')
            return struct.unpack(fmt, self.value[:self.sizes[field_name]])[0]
        except:
            raise ValueError(f"{field_name} alanından veri okunamadı")

    def _get_size(self, type_name):
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8
        }
        return size_map.get(type_name.upper(), 8)

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
        self.async_tasks = []
        self.performance_metrics = {"start_time": time.time(), "memory_usage": 0}
        self.supported_encodings = [
            "utf-8", "cp1254", "iso-8859-9", "ascii", "utf-16", "utf-32",
            "cp1252", "iso-8859-1", "windows-1250", "latin-9",
            "cp932", "gb2312", "gbk", "euc-kr", "cp1251", "iso-8859-5",
            "cp1256", "iso-8859-6", "cp874", "iso-8859-7", "cp1257", "iso-8859-8"
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
            "SINH": math.sinh,
            "COSH": math.cosh,
            "TANH": math.tanh,
            "ASINH": math.asinh,
            "ACOSH": math.acosh,
            "ATANH": math.atanh,
            "SIND": lambda x: math.sin(math.radians(x)),
            "COSD": lambda x: math.cos(math.radians(x)),
            "TAND": lambda x: math.tan(math.radians(x)),
            "PI": math.pi,
            "E": math.e,
            "BIN": bin,
            "HEX": hex,
            "OCT": oct,
            "ADDR": lambda x: id(x),
            "SIZEOF": lambda x: self.memory_manager.sizeof(x),
            "NEW": self.memory_manager.allocate,
            "DELETE": self.memory_manager.release,
            "ASYNC_WAIT": self.core.async_wait,
            "THREAD_COUNT": lambda: threading.active_count(),
            "CURRENT_THREAD": lambda: threading.get_ident(),
            "MAP": self.core.map,
            "FILTER": self.core.filter,
            "REDUCE": self.core.reduce
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
            return {"en": {"PRINT": "Print", "ERROR": "Error"}}

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
            "types": {},
            "labels": {}
        }
        current_sub = None
        current_function = None
        current_type = None
        current_class = None
        type_fields = {}
        class_info = {}
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
                sub_name = line[4:].split("(")[0].strip()
                self.subs[sub_name] = i + 1
                self.modules[module_name]["subs"][sub_name] = i + 1
                current_sub = sub_name
                i += 1
            elif line_upper.startswith("FUNCTION "):
                func_name = line[8:].split("(")[0].strip()
                self.functions[func_name] = i + 1
                self.modules[module_name]["functions"][func_name] = i + 1
                current_function = func_name
                i += 1
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
                current_enum = enum_name
                enum_values[enum_name] = {}
                i += 1
            elif line_upper.startswith("END ENUM"):
                self.types[current_enum] = {"kind": "ENUM", "values": enum_values[current_enum]}
                self.modules[module_name]["types"][current_enum] = self.types[current_enum]
                current_enum = None
                i += 1
            elif current_type:
                match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    field_name, field_type = match.groups()
                    type_fields[current_type].append((field_name, field_type))
                else:
                    raise Exception(f"TYPE tanımı hatası: {line}")
                i += 1
            elif line_upper.startswith("ABSTRACT CLASS "):
                match = re.match(r"ABSTRACT CLASS\s+(\w+)(?:\s+EXTENDS\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_name = match.groups()
                    current_class = class_name
                    class_info[class_name] = {
                        'methods': {},
                        'private_methods': {},
                        'static_vars': {},
                        'parent': parent_name,
                        'abstract': True
                    }
                    i += 1
                else:
                    raise Exception("ABSTRACT CLASS komutunda sözdizimi hatası")
            elif line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+EXTENDS\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_name = match.groups()
                    current_class = class_name
                    class_info[class_name] = {
                        'methods': {},
                        'private_methods': {},
                        'static_vars': {},
                        'parent': parent_name,
                        'abstract': False
                    }
                    i += 1
                else:
                    raise Exception("CLASS komutunda sözdizimi hatası")
            elif line_upper.startswith("END CLASS"):
                parent_class = class_info[current_class]['parent']
                parent_methods = self.classes.get(parent_class, type('', (), {'_vars': {}})()).__dict__ if parent_class else {}
                parent_static_vars = class_info.get(parent_class, {}).get('static_vars', {})
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
                    class_info[current_class]['static_vars'][var_name] = self.type_table.get(var_type, None)()
                    i += 1
                else:
                    raise Exception("STATIC komutunda sözdizimi hatası")
            elif current_class and line_upper.startswith("DIM "):
                match = re.match(r"DIM\s+(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
                if match:
                    var_name, var_type = match.groups()
                    class_info[current_class]['methods']['__init__'] = lambda self: self._vars.update({var_name: self.type_table.get(var_type, None)()})
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
            elif line_upper.startswith("STRUCT "):
                struct_name = line[7:].strip()
                current_type = struct_name
                type_fields[struct_name] = []
                i += 1
                while i < len(lines) and not lines[i].strip().upper().startswith("END STRUCT"):
                    field_line = lines[i].strip()
                    if field_line:
                        field_name, field_type = [x.strip() for x in field_line.split("AS")]
                        type_fields[struct_name].append((field_name, field_type))
                    i += 1
                self.types[current_type] = {"kind": "STRUCT", "fields": type_fields[current_type]}
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
            for try_ext in [".hz", ".hx"]:
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
        old_types = self.types.copy()
        old_labels = self.labels.copy()
        old_module = self.current_module
        self.program = []
        self.functions.clear()
        self.subs.clear()
        self.classes.clear()
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
        self.types.update(old_types)
        self.labels.update(old_labels)
        self.current_module = old_module

    def parse_definitions(self, code, module_name):
        pass

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
            tree = ast.parse(expr, mode='eval')
            self.expr_cache[cache_key] = compile(tree, '<string>', 'eval')
        namespace = {}
        namespace.update(self.global_vars)
        namespace.update(self.current_scope())
        namespace.update(self.function_table)
        return eval(self.expr_cache[cache_key], namespace)

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
                    raise Exception("IMPORT komutunda sözdizimi hatası")

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

            if command_upper.startswith("ON GOSUB"):
                match = re.match(r"ON GOSUB\s+(\w+)", command, re.IGNORECASE)
                if match:
                    label = match.group(1)
                    if label in self.labels:
                        self.gosub_handler = self.labels[label]
                    else:
                        raise Exception(f"Etiket bulunamadı: {label}")
                    return None
                else:
                    raise Exception("ON GOSUB komutunda sözdizimi hatası")

            if command_upper.startswith("PRINT"):
                parts = command[5:].strip().split()
                args = [self.evaluate_expression(arg, scope_name) for arg in parts]
                print(*args)
                return None

            if command_upper.startswith("INPUT"):
                match = re.match(r"INPUT\s+\"([^\"]+)\",\s*(\w+)", command, re.IGNORECASE)
                if match:
                    prompt, var_name = match.groups()
                    value = input(prompt)
                    self.current_scope()[var_name] = value
                    return None
                else:
                    raise Exception("INPUT komutunda sözdizimi hatası")

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
                match = re.match(r"DIM\s+(\w+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, var_type = match.groups()
                    if var_type.upper() == "STRUCT":
                        self.current_scope()[var_name] = StructInstance([], self.type_table)
                    elif var_type.upper() == "UNION":
                        self.current_scope()[var_name] = UnionInstance([], self.type_table)
                    else:
                        self.current_scope()[var_name] = self.type_table.get(var_type.upper(), object)()
                    return None
                else:
                    raise Exception("DIM komutunda sözdizimi hatası")

            if command_upper.startswith("IF"):
                match = re.match(r"IF\s+(.+)\s+THEN\s+(.+)", command, re.IGNORECASE)
                if match:
                    condition, then_cmd = match.groups()
                    if self.evaluate_expression(condition, scope_name):
                        return self.execute_command(then_cmd, scope_name)
                    return None
                else:
                    raise Exception("IF komutunda sözdizimi hatası")

            if command_upper.startswith("FOR"):
                match = re.match(r"FOR\s+(\w+)\s*=\s*(.+)\s+TO\s+(.+)(?:\s+STEP\s+(.+))?", command, re.IGNORECASE)
                if match:
                    var_name, start_expr, end_expr, step_expr = match.groups()
                    start = self.evaluate_expression(start_expr, scope_name)
                    end = self.evaluate_expression(end_expr, scope_name)
                    step = self.evaluate_expression(step_expr, scope_name) if step_expr else 1
                    self.current_scope()[var_name] = start
                    self.loop_stack.append({
                        "start": self.program_counter,
                        "type": "FOR",
                        "var": var_name,
                        "end": end,
                        "step": step
                    })
                    return None
                else:
                    raise Exception("FOR komutunda sözdizimi hatası")

            if command_upper.startswith("EXIT FOR"):
                if self.loop_stack and self.loop_stack[-1]["type"] == "FOR":
                    while self.program_counter < len(self.program) and \
                          self.program[self.program_counter][0].upper() != "NEXT":
                        self.program_counter += 1
                    self.loop_stack.pop()
                    return None
                else:
                    raise Exception("EXIT FOR için eşleşen FOR bulunamadı")

            if command_upper.startswith("CONTINUE FOR"):
                if self.loop_stack and self.loop_stack[-1]["type"] == "FOR":
                    loop_info = self.loop_stack[-1]
                    var_name = loop_info["var"]
                    current_value = self.current_scope()[var_name]
                    current_value += loop_info["step"]
                    self.current_scope()[var_name] = current_value
                    return loop_info["start"]
                else:
                    raise Exception("CONTINUE FOR için eşleşen FOR bulunamadı")

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
                    raise Exception("NEXT için eşleşen FOR bulunamadı")

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
                    raise Exception("WHILE komutunda sözdizimi hatası")

            if command_upper == "WEND":
                if self.loop_stack and self.loop_stack[-1]["type"] == "WHILE":
                    loop_info = self.loop_stack[-1]
                    if self.evaluate_expression(loop_info["condition"], scope_name):
                        return loop_info["start"]
                    else:
                        self.loop_stack.pop()
                    return None
                else:
                    raise Exception("WEND için eşleşen WHILE bulunamadı")

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
                    raise Exception("DO komutunda sözdizimi hatası")

            if command_upper.startswith("EXIT DO"):
                if self.loop_stack and self.loop_stack[-1]["type"] in ("WHILE", "UNTIL", "NONE"):
                    while self.program_counter < len(self.program) and \
                          self.program[self.program_counter][0].upper() != "LOOP":
                        self.program_counter += 1
                    self.loop_stack.pop()
                    return None
                else:
                    raise Exception("EXIT DO için eşleşen DO bulunamadı")

            if command_upper.startswith("CONTINUE DO"):
                if self.loop_stack and self.loop_stack[-1]["type"] in ("WHILE", "UNTIL", "NONE"):
                    return self.loop_stack[-1]["start"]
                else:
                    raise Exception("CONTINUE DO için eşleşen DO bulunamadı")

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
                    raise Exception("LOOP için eşleşen DO bulunamadı")

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
                else:
                    raise Exception("RETURN için eşleşen GOSUB bulunamadı")

            if command_upper.startswith("TRY"):
                match = re.match(r"TRY\s+(.+)\s+CATCH\s+(\w+)\s+DO\s+(.+)", command, re.IGNORECASE)
                if match:
                    try_block, error_var, catch_block = match.groups()
                    try:
                        self.execute_command(try_block, scope_name)
                    except Exception as e:
                        self.current_scope()[error_var] = str(e)
                        self.execute_command(catch_block, scope_name)
                    return None
                else:
                    raise Exception("TRY...CATCH komutunda sözdizimi hatası")

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
                        raise Exception(f"Desteklenmeyen dil: {lang}")
                    return None
                else:
                    raise Exception("SET LANGUAGE komutunda sözdizimi hatası")

            if command_upper.startswith("CALL"):
                if command_upper.startswith("CALL API::GET"):
                    match = re.match(r"CALL API::GET\s+(.+)", command, re.IGNORECASE)
                    if match:
                        url = match.group(1)
                        return requests.get(url).json()
                elif command_upper.startswith("CALL"):
                    match = re.match(r"CALL\s+(\w+)::(\w+)\((.*)\)", command, re.IGNORECASE)
                    if match:
                        dll_name, func_name, args = match.groups()
                        dll = self.core.load_dll(dll_name)
                        func = getattr(dll, func_name)
                        arg_list = [self.evaluate_expression(arg.strip(), scope_name) for arg in args.split(",") if arg.strip()]
                        return func(*arg_list)
                raise Exception("CALL komutunda sözdizimi hatası")

            if command_upper.startswith("HELP"):
                match = re.match(r"HELP\s*(\w+)?", command, re.IGNORECASE)
                if match:
                    lib_name = match.group(1)
                    self.show_help(lib_name)
                    return None
                else:
                    raise Exception("HELP komutunda sözdizimi hatası")

            if command_upper.startswith("CORE."):
                func_name = command_upper.split(".")[1]
                args = re.match(r"CORE\.(\w+)\((.*)\)", command, re.IGNORECASE)
                if args:
                    _, arg_str = args.groups()
                    arg_list = [self.evaluate_expression(arg.strip(), scope_name) for arg in arg_str.split(",") if arg.strip()]
                    return getattr(self.core, func_name.lower())(*arg_list)
                else:
                    return getattr(self.core, func_name.lower())()

            raise Exception(f"Bilinmeyen komut: {command}")

        except Exception as e:
            logging.error(f"Hata: {str(e)}\n{''.join(traceback.format_stack())}")
            if self.error_handler:
                return self.error_handler
            elif self.gosub_handler:
                return self.gosub_handler
            else:
                raise e

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
        self.program = []
        self.parse_program(code)
        self.running = True
        self.program_counter = 0
        try:
            while self.running and self.program_counter < len(self.program):
                cmd, scope = self.program[self.program_counter]
                next_pc = self.execute_command(cmd, scope)
                self.program_counter = next_pc if next_pc is not None else self.program_counter + 1
        except Exception as e:
            if self.error_handler:
                self.program_counter = self.error_handler
            elif self.gosub_handler:
                self.program_counter = self.gosub_handler
            else:
                raise e
        self.running = False

    def repl(self):
        self.repl_mode = True
        print("pdsXv11 REPL - Çıkış için 'EXIT'")
        while True:
            try:
                cmd = input("> ")
                if cmd.upper() == "EXIT":
                    break
                self.execute_command(cmd)
            except Exception as e:
                print(f"Hata: {e}")
        self.repl_mode = False

    def compile_to_bytecode(self, code):
        self.bytecode = []
        lines = code.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            tokens = line.split(maxsplit=1)
            opcode = tokens[0].upper()
            operands = tokens[1] if len(tokens) > 1 else ""
            self.bytecode.append({"opcode": opcode, "operands": operands, "line": i + 1})
        return self.bytecode

    def execute_bytecode(self):
        self.running = True
        pc = 0
        while self.running and pc < len(self.bytecode):
            instruction = self.bytecode[pc]
            opcode = instruction["opcode"]
            operands = instruction["operands"]
            try:
                if opcode == "PRINT":
                    print(self.evaluate_expression(operands))
                elif opcode == "LET":
                    var, val = operands.split("=", 1)
                    self.current_scope()[var.strip()] = self.evaluate_expression(val.strip())
                elif opcode == "DIM":
                    var_name, var_type = operands.split("AS")
                    self.current_scope()[var_name.strip()] = self.type_table.get(var_type.strip().upper(), object)()
                elif opcode == "IF":
                    condition, then_cmd = operands.split("THEN")
                    if self.evaluate_expression(condition.strip()):
                        self.execute_command(then_cmd.strip())
                elif opcode == "GOTO":
                    label = operands.strip()
                    for i, instr in enumerate(self.bytecode):
                        if instr["opcode"] == "LABEL" and instr["operands"] == label:
                            pc = i
                            break
                pc += 1
            except Exception as e:
                logging.error(f"Bayt kodu hatası: Satır {instruction['line']}, {str(e)}")
                if self.error_handler:
                    pc = self.error_handler
                else:
                    raise e
        self.running = False

def main():
    parser = argparse.ArgumentParser(description='pdsXv11 Interpreter')
    parser.add_argument('file', nargs='?', help='Çalıştırılacak dosya')
    parser.add_argument('-i', '--interactive', action='store_true', help='Etkileşimli mod')
    args = parser.parse_args()

    interpreter = pdsXv11()
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
        interpreter.run(code)
    if args.interactive or not args.file:
        interpreter.repl()

if __name__ == "__main__":
    main()