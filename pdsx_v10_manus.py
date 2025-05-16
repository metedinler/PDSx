import sys
import subprocess
import importlib.metadata
import platform
import json  # Çoklu dil desteği için gerekli
import threading  # Paralel programlama için gerekli
import asyncio  # Asenkron programlama için gerekli
import ast  # AST modülü ifadeleri önbelleğe almak için kullanılacak
import math  # Matematiksel fonksiyonlar için gerekli
import re
import logging
import struct as py_struct
from collections import namedtuple

def install_missing_libraries():
    """Gerekli kütüphaneleri kontrol eder ve eksik olanları yükler."""
    required_libraries = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'scipy': 'scipy',
        'pdfplumber': 'pdfplumber',
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'readline': 'pyreadline3' if platform.system() == 'Windows' else 'readline'
    }
    installed = {pkg.metadata['Name'].lower() for pkg in importlib.metadata.distributions()}
    missing = [lib for lib, pkg_name in required_libraries.items() if lib not in installed]

    if missing:
        print(f"Eksik kütüphaneler tespit edildi: {missing}")
        print("Yükleniyor...")
        for lib in missing:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', required_libraries[lib]])
                print(f"{lib} başarıyla yüklendi.")
            except subprocess.CalledProcessError:
                print(f"Hata: {lib} yüklenemedi. Lütfen manuel olarak yükleyin.")
                sys.exit(1)
    else:
        print("Tüm gerekli kütüphaneler zaten yüklü.")

# Kütüphaneleri kontrol et ve yükle
install_missing_libraries()
try:
    if platform.system() == 'Windows':
        import pyreadline3 as readline
    else:
        import readline
except ImportError:
    print("Uyarı: readline kütüphanesi bulunamadı. Komut geçmişi devre dışı.")
    readline = None
import re
import random
import sqlite3
import numpy as np
import pandas as pd
import scipy.stats as stats
from collections import defaultdict, namedtuple
from types import SimpleNamespace
import os
import logging
import time
import sys
import argparse
import struct
import pdfplumber
import requests
from bs4 import BeautifulSoup
from collections import Counter
import readline  # Komut geçmişi için
import time  # Performans ölçümü için gerekli
import struct as py_struct
from collections import namedtuple
# Hata loglama için logging ayarı
logging.basicConfig(filename='interpreter_errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')
logging.basicConfig(filename='interpreter_errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

class MemoryManager:
    """Bellek yönetimi ve işaretçi aritmetiği"""
    def __init__(self):
        self.heap = {}
        self.ref_counts = {}

    def allocate(self, size: int):
        """Bellek ayırma"""
        ptr = id(bytearray(size))
        self.heap[ptr] = bytearray(size)
        self.ref_counts[ptr] = 1
        return ptr

    def release(self, ptr: int):
        """Bellek serbest bırakma"""
        if ptr in self.ref_counts:
            self.ref_counts[ptr] -= 1
            if self.ref_counts[ptr] == 0:
                del self.heap[ptr]
                del self.ref_counts[ptr]

    def dereference(self, ptr: int):
        """İşaretçi dereferansı"""
        return self.heap.get(ptr, None)

    def set_value(self, ptr: int, value):
        """İşaretçi konumuna değer yaz"""
        if ptr in self.heap:
            if isinstance(value, (int, float)):
                self.heap[ptr][:] = struct.pack('d', float(value))
            elif isinstance(value, str):
                self.heap[ptr][:] = value.encode()

    def sizeof(self, obj):
        """Nesne boyutunu byte cinsinden döndür"""
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
        self.value = bytearray(8)  # Maksimum alan boyutu
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
            value = py_struct.pack(fmt, value)
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
            return py_struct.unpack(fmt, self.value[:self.sizes[field_name]])[0]
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

class pdsXInterpreter:
    def __init__(self):
        self.global_vars = {}  # GLOBAL değişkenler
        self.shared_vars = defaultdict(list)  # DIM SHARED değişkenler
        self.local_scopes = [{}]  # Yerel kapsam yığını
        self.types = {}  # TYPE tanımları
        self.classes = {}  # CLASS tanımları
        self.functions = {}  # FUNCTION tanımları
        self.subs = {}  # SUB tanımları
        self.labels = {}  # Etiketler
        self.program = []  # Program satırları
        self.program_counter = 0
        self.call_stack = []  # GOSUB, SUB, FUNCTION için yığın
        self.running = False
        self.db_connections = {}  # Veritabanı bağlantıları
        self.file_handles = {}  # Dosya kolları
        self.error_handler = None  # ON ERROR GOTO için
        self.debug_mode = False  # DEBUG modu
        self.trace_mode = False  # TRACE ON/OFF için
        self.loop_stack = []  # DO...LOOP, FOR...NEXT için yığın
        self.select_stack = []  # SELECT CASE için yığın
        self.if_stack = []  # IF...THEN...ELSE için yığın
        self.data_list = []  # DATA komutları için liste
        self.data_pointer = 0  # READ komutu için işaretçi
        self.transaction_active = {}  # Transaction durumları
        self.modules = {}  # İçe aktarılmış modüller
        self.current_module = "main"  # Aktif modül adı
        self.repl_mode = False  # REPL modu aktif mi
        self.type_table = {
            "STRING": str, "INTEGER": int, "LONG": int, "SINGLE": float, "DOUBLE": float,
            "BYTE": int, "SHORT": int, "UNSIGNED INTEGER": int, "CHAR": str,
            "LIST": list, "DICT": dict, "SET": set, "TUPLE": tuple,
            "ARRAY": np.array, "DATAFRAME": pd.DataFrame, "POINTER": None,
            "STRUCT": dict, "UNION": None, "ENUM": dict, "VOID": None, "BITFIELD": int
        }
        self.function_table = {
            # PDS Fonksiyonları
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
            # Veri Bilimi Fonksiyonları
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
            # NumPy Fonksiyonları
            "CONCATENATE": np.concatenate, "STACK": np.stack, "VSTACK": np.vstack,
            "HSTACK": np.hstack, "DOT": np.dot, "CROSS": np.cross,
            "NORM": np.linalg.norm, "INV": np.linalg.inv, "SOLVE": np.linalg.solve,
            "LINSPACE": np.linspace, "ARANGE": np.arange, "ZEROS": np.zeros,
            "ONES": np.ones, "FULL": np.full, "EYE": np.eye, "DIAG": np.diag,
            "RESHAPE": np.reshape, "TRANSPOSE": np.transpose, "FLIP": np.flip,
            "ROLL": np.roll,
            # Pandas Fonksiyonları
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
            # Dosya ve Sistem İşlemleri
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
            # PDF ve Web Fonksiyonları
            "PDF_READ_TEXT": self.pdf_read_text,
            "PDF_EXTRACT_TABLES": self.pdf_extract_tables,
            "PDF_SEARCH_KEYWORD": self.pdf_search_keyword,
            "TXT_SEARCH": self.txt_search,
            "TXT_ANALYZE": self.txt_analyze,
            "WEB_GET": self.web_get,
            "WEB_POST": self.web_post,
            "SCRAPE_LINKS": self.scrape_links,
            "SCRAPE_TEXT": self.scrape_text
        }
        self.memory_manager = MemoryManager()
        self.operator_table = self._init_operator_table()
        self.function_table = self._init_function_table()
        self.memory_pool = {}  # Sanal bellek havuzu
        self.next_address = 1000  # Başlangıç adresi
        self.expr_cache = {}  # İfade önbelleği
        self.variable_cache = {}  # Değişken erişim önbelleği
        self.language = "en"  # Varsayılan dil
        self.translations = self.load_translations("lang.json")
        self.bytecode = []  # Bayt kodu depolamak için

    def load_translations(self, file_path):
        """Dil dosyasını yükler."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Dil dosyası bulunamadı. Varsayılan İngilizce kullanılacak.")
            return {}

    def translate(self, key):
        """Anahtar kelimeleri ve mesajları çevirir."""
        return self.translations.get(self.language, {}).get(key, key)

    def _init_operator_table(self):
        """C tarzı operatörleri içeren tablo"""
        return {
            '++': self._increment,
            '--': self._decrement,
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

    def _init_function_table(self):
        """Matematiksel ve diğer fonksiyonlar"""
        funcs = {
            'SINH': math.sinh,
            'COSH': math.cosh,
            'TANH': math.tanh,
            'ASINH': math.asinh,
            'ACOSH': math.acosh,
            'ATANH': math.atanh,
            'SIND': lambda x: math.sin(math.radians(x)),
            'COSD': lambda x: math.cos(math.radians(x)),
            'TAND': lambda x: math.tan(math.radians(x)),
            'PI': math.pi,
            'E': math.e,
            'BIN': bin,
            'HEX': hex,
            'OCT': oct,
            'ADDR': lambda x: id(x),
            'SIZEOF': lambda x: self.memory_manager.sizeof(x),
            'NEW': self.memory_manager.allocate,
            'DELETE': self.memory_manager.release
        }
        for name in ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'ceil', 'floor']:
            funcs[name.upper()] = getattr(math, name)
        return funcs

    def _increment(self, x):
        """Bir değeri bir artırır."""
        if isinstance(x, (int, float)):
            return x + 1
        raise TypeError("_increment sadece sayısal değerler için geçerlidir.")

    def _decrement(self, x):
        """Bir değeri bir azaltır."""
        if isinstance(x, (int, float)):
            return x - 1
        raise TypeError("_decrement sadece sayısal değerler için geçerlidir.")

    # PDF ve Web İşlemleri için Yardımcı Fonksiyonlar
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

    def pdf_search_keyword(self, file_path, keyword):
        if not os.path.exists(file_path):
            return []
        results = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and keyword.lower() in text.lower():
                    results.append((i + 1, text))
        return results

    def txt_search(self, file_path, keyword):
        if not os.path.exists(file_path):
            return []
        results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if keyword.lower() in line.lower():
                    results.append((i, line.strip()))
        return results

    def txt_analyze(self, file_path):
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        words = re.findall(r'\b\w+\b', content.lower())
        return Counter(words).most_common(20)

    def web_get(self, url):
        try:
            response = requests.get(url)
            return response.text
        except Exception as e:
            return f"Hata: {e}"

    def web_post(self, url, data):
        try:
            response = requests.post(url, data=data)
            return response.text
        except Exception as e:
            return f"Hata: {e}"

    def scrape_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True)]

    def scrape_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(separator='\n')

    def current_scope(self):
        return self.local_scopes[-1]

    def parse_program(self, code, module_name="main"):
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
            elif line_upper.startswith("CLASS "):
                match = re.match(r"CLASS\s+(\w+)(?:\s+EXTENDS\s+(\w+))?", line, re.IGNORECASE)
                if match:
                    class_name, parent_name = match.groups()
                    current_class = class_name
                    class_info[class_name] = {
                        'methods': {},
                        'private_methods': {},
                        'static_vars': {},
                        'parent': parent_name
                    }
                    i += 1
                else:
                    raise Exception("CLASS komutunda sözdizimi hatası")
            elif line_upper.startswith("END CLASS"):
                parent_class = class_info[current_class]['parent']
                parent_methods = self.classes.get(parent_class, type('', (), {'_vars': {}})()).__dict__ if parent_class else {}
                parent_static_vars = class_info.get(parent_class, {}).get('static_vars', {})
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
                match = re.match(rf"{prefix}{method_type}\s+(\w+)(?:\((.*)\))?", line, re.IGNORECASE)
                if match:
                    method_name, params = match.groups()
                    method_body = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip().upper() != f"END {method_type}":
                        method_body.append(lines[j].strip())
                        j += 1
                    params = params.split(",") if params else []
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
        if not file_name.endswith(('.basX', '.libX', '.hX')):
            raise Exception("Desteklenmeyen dosya uzantısı. Uzantı .basX, .libX veya .hX olmalı")
        if not os.path.exists(file_name):
            raise Exception(f"Dosya bulunamadı: {file_name}")
        module_name = module_name or os.path.splitext(os.path.basename(file_name))[0]
        with open(file_name, 'r', encoding='utf-8') as f:
            code = f.read()
        # Mevcut durumları yedekle
        old_program = self.program
        old_functions = self.functions.copy()
        old_subs = self.subs.copy()
        old_classes = self.classes.copy()
        old_types = self.types.copy()
        old_labels = self.labels.copy()
        old_module = self.current_module
        # Yeni modülü ayrıştır
        self.program = []
        self.functions.clear()
        self.subs.clear()
        self.classes.clear()
        self.types.clear()
        self.labels.clear()
        self.parse_program(code, module_name)
        # Yedekleri geri yükle
        self.program = old_program
        self.functions.update(old_functions)
        self.subs.update(old_subs)
        self.classes.update(old_classes)
        self.types.update(old_types)
        self.labels.update(old_labels)
        self.current_module = old_module

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
        """İfadeleri AST ile önbelleğe alarak değerlendirir."""
        cache_key = (expr, scope_name)
        if cache_key not in self.expr_cache:
            tree = ast.parse(expr, mode='eval')
            self.expr_cache[cache_key] = compile(tree, '<string>', 'eval')
        # Değişken erişimlerini optimize etmek için mevcut kapsamı önbelleğe al
        namespace = {}
        namespace.update(self.global_vars)
        namespace.update(self.current_scope())
        namespace.update(self.function_table)
        return eval(self.expr_cache[cache_key], namespace)

    def execute_command(self, command, scope_name=None):
        command = command.strip()
        if not command:
            return None
        command_upper = command.upper()

        if self.trace_mode:
            print(f"TRACE: Satır {self.program_counter + 1}: {command}")

        try:
            # IMPORT Komutu
            if command_upper.startswith("IMPORT"):
                match = re.match(r"IMPORT\s+\"(.+)\"(?:\s+AS\s+(\w+))?", command, re.IGNORECASE)
                if match:
                    file_name, alias = match.groups()
                    module_name = alias or os.path.splitext(os.path.basename(file_name))[0]
                    self.import_module(file_name, module_name)
                    return None
                else:
                    raise Exception("IMPORT komutunda sözdizimi hatası")

            # Hata Yönetimi
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

            if command_upper.startswith("ON ERROR RESUME"):
                self.error_handler = "RESUME"
                return None

            if command_upper == "RESUME":
                if self.error_handler and self.error_handler != "RESUME":
                    return self.error_handler
                elif self.error_handler == "RESUME":
                    return None
                else:
                    raise Exception("RESUME için hata işleyicisi tanımlı değil")

            if command_upper == "RESUME NEXT":
                return self.program_counter + 1

            if command_upper.startswith("RESUME LABEL"):
                match = re.match(r"RESUME LABEL\s+(\w+)", command, re.IGNORECASE)
                if match:
                    label = match.group(1)
                    if label in self.labels:
                        return self.labels[label]
                    else:
                        raise Exception(f"Etiket bulunamadı: {label}")
                else:
                    raise Exception("RESUME LABEL komutunda sözdizimi hatası")

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

            # WHILE...WEND Desteği
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

            # FOR...NEXT Desteği
            if command_upper.startswith("FOR"):
                match = re.match(r"FOR\s+(\w+)\s*=\s*(.+)\s+TO\s+(.+)(?:\s+STEP\s+(.+))?", command, re.IGNORECASE)
                if match:
                    var_name, start_expr, end_expr, step_expr = match.groups()
                    start = self.evaluate_expression(start_expr, scope_name)
                    end = self.evaluate_expression(end_expr, scope_name)
                    step = self.evaluate_expression(step_expr, scope_name) if step_expr else 1
                    if var_name in self.global_vars:
                        self.global_vars[var_name] = start
                    else:
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
                    current_value = self.global_vars.get(var_name, self.current_scope().get(var_name))
                    current_value += loop_info["step"]
                    if var_name in self.global_vars:
                        self.global_vars[var_name] = current_value
                    else:
                        self.current_scope()[var_name] = current_value
                    return loop_info["start"]
                else:
                    raise Exception("CONTINUE FOR için eşleşen FOR bulunamadı")

            if command_upper.startswith("NEXT"):
                if self.loop_stack and self.loop_stack[-1]["type"] == "FOR":
                    loop_info = self.loop_stack[-1]
                    var_name = loop_info["var"]
                    current_value = self.global_vars.get(var_name, self.current_scope().get(var_name))
                    current_value += loop_info["step"]
                    if var_name in self.global_vars:
                        self.global_vars[var_name] = current_value
                    else:
                        self.current_scope()[var_name] = current_value
                    if (loop_info["step"] > 0 and current_value <= loop_info["end"]) or \
                       (loop_info["step"] < 0 and current_value >= loop_info["end"]):
                        return loop_info["start"]
                    else:
                        self.loop_stack.pop()
                    return None
                else:
                    raise Exception("NEXT için eşleşen FOR bulunamadı")

            # DO...LOOP Desteği
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
                match = re.match(r"LOOP\s+(WHILE|UNTIL)?\s*(.+)?", command, re.IGNORECASE)
                if match and self.loop_stack:
                    loop_type, condition = match.groups()
                    loop_info = self.loop_stack[-1]
                    if loop_type and condition:
                        cond_result = self.evaluate_expression(condition, scope_name)
                        if (loop_type == "WHILE" and cond_result) or (loop_type == "UNTIL" and not cond_result):
                            return loop_info["start"]
                        else:
                            self.loop_stack.pop()
                    elif loop_info["type"] == "WHILE":
                        if self.evaluate_expression(loop_info["condition"], scope_name):
                            return loop_info["start"]
                        else:
                            self.loop_stack.pop()
                    elif loop_info["type"] == "UNTIL":
                        if not self.evaluate_expression(loop_info["condition"], scope_name):
                            return loop_info["start"]
                        else:
                            self.loop_stack.pop()
                    else:
                        return loop_info["start"]
                    return None
                else:
                    raise Exception("LOOP için eşleşen DO bulunamadı")

            # SELECT CASE Desteği
            if command_upper.startswith("SELECT CASE"):
                match = re.match(r"SELECT CASE\s+(.+)", command, re.IGNORECASE)
                if match:
                    expr = match.group(1)
                    value = self.evaluate_expression(expr, scope_name)
                    self.select_stack.append({"value": value, "matched": False, "start": self.program_counter})
                    return None
                else:
                    raise Exception("SELECT CASE komutunda sözdizimi hatası")

            if command_upper.startswith("CASE"):
                if not self.select_stack:
                    raise Exception("CASE için eşleşen SELECT CASE bulunamadı")
                select_info = self.select_stack[-1]
                match = re.match(r"CASE\s+(.+)", command, re.IGNORECASE)
                if match:
                    case_expr = match.group(1)
                    if case_expr.upper() == "ELSE":
                        if not select_info["matched"]:
                            select_info["matched"] = True
                        else:
                            while self.program_counter < len(self.program) and \
                                  self.program[self.program_counter][0].upper() != "END SELECT":
                                self.program_counter += 1
                    else:
                        case_value = self.evaluate_expression(case_expr, scope_name)
                        if select_info["value"] == case_value and not select_info["matched"]:
                            select_info["matched"] = True
                        else:
                            while self.program_counter < len(self.program) and \
                                  self.program[self.program_counter][0].upper() not in ("CASE", "END SELECT"):
                                self.program_counter += 1
                    return None
                else:
                    raise Exception("CASE komutunda sözdizimi hatası")

            if command_upper == "END SELECT":
                if self.select_stack:
                    self.select_stack.pop()
                    return None
                else:
                    raise Exception("END SELECT için eşleşen SELECT CASE bulunamadı")

            # IF...THEN...ELSE...END IF Desteği
            if command_upper.startswith("IF"):
                match = re.match(r"IF\s+(.+)\s+THEN", command, re.IGNORECASE)
                if match:
                    condition = match.group(1)
                    cond_result = self.evaluate_expression(condition, scope_name)
                    self.if_stack.append({"condition": cond_result, "start": self.program_counter, "else_found": False})
                    if not cond_result:
                        while self.program_counter < len(self.program) and \
                              self.program[self.program_counter][0].upper() not in ("ELSE", "END IF"):
                            self.program_counter += 1
                    return None
                else:
                    raise Exception("IF komutunda sözdizimi hatası")

            if command_upper == "ELSE":
                if not self.if_stack:
                    raise Exception("ELSE için eşleşen IF bulunamadı")
                if_info = self.if_stack[-1]
                if if_info["condition"] or if_info["else_found"]:
                    while self.program_counter < len(self.program) and \
                          self.program[self.program_counter][0].upper() != "END IF":
                        self.program_counter += 1
                if_info["else_found"] = True
                return None

            if command_upper == "END IF":
                if self.if_stack:
                    self.if_stack.pop()
                    return None
                else:
                    raise Exception("END IF için eşleşen IF bulunamadı")

            # Test Desteği
            if command_upper.startswith("ASSERT"):
                match = re.match(r"ASSERT\s+(.+)", command, re.IGNORECASE)
                if match:
                    condition = match.group(1)
                    if not self.evaluate_expression(condition, scope_name):
                        raise Exception(f"ASSERT başarısız: {condition}")
                    return None
                else:
                    raise Exception("ASSERT komutunda sözdizimi hatası")

            # Değişken ve Veri Yönetimi
            if command_upper.startswith("DEFINT"):
                match = re.match(r"DEFINT\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    self.current_scope()[var_name] = 0
                    return None
                else:
                    raise Exception("DEFINT komutunda sözdizimi hatası")

            if command_upper.startswith("DEFSNG"):
                match = re.match(r"DEFSNG\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    self.current_scope()[var_name] = 0.0
                    return None
                else:
                    raise Exception("DEFSNG komutunda sözdizimi hatası")

            if command_upper.startswith("DEFDBL"):
                match = re.match(r"DEFDBL\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    self.current_scope()[var_name] = 0.0
                    return None
                else:
                    raise Exception("DEFDBL komutunda sözdizimi hatası")

            if command_upper.startswith("DEFSTR"):
                match = re.match(r"DEFSTR\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    self.current_scope()[var_name] = ""
                    return None
                else:
                    raise Exception("DEFSTR komutunda sözdizimi hatası")

            if command_upper.startswith("GLOBAL"):
                match = re.match(r"GLOBAL\s+(\w+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, var_type = match.groups()
                    self.global_vars[var_name] = self.type_table.get(var_type, None)()
                    return None
                else:
                    raise Exception("GLOBAL komutunda sözdizimi hatası")

            if command_upper.startswith("DIM SHARED"):
                match = re.match(r"DIM SHARED\s+(.+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    scopes, var_type = match.groups()
                    var_name = scopes.split(",")[-1].strip()
                    scope_list = [s.strip() for s in scopes.split(",")[:-1]]
                    self.shared_vars[var_name] = scope_list
                    return None
                else:
                    raise Exception("DIM SHARED komutunda sözdizimi hatası")

            if command_upper.startswith("DIM"):
                match = re.match(r"DIM\s+(\w+)\s+AS\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name, var_type = match.groups()
                    if var_type in self.types and self.types[var_type]["kind"] == "STRUCT":
                        self.current_scope()[var_name] = StructInstance(self.types[var_type]["fields"], self.type_table)
                    elif var_type in self.types:
                        type_info = self.types[var_type]
                        if type_info["kind"] == "STRUCT":
                            self.current_scope()[var_name] = StructInstance(type_info["fields"], self.type_table)
                        elif type_info["kind"] == "UNION":
                            self.current_scope()[var_name] = UnionInstance(type_info["fields"], self.type_table)
                        elif type_info["kind"] == "ENUM":
                            self.current_scope()[var_name] = None
                    elif var_type == "POINTER":
                        match_ptr = re.match(r"DIM\s+(\w+)\s+AS\s+POINTER\s+TO\s+(\w+)", command, re.IGNORECASE)
                        if match_ptr:
                            var_name, target_type = match_ptr.groups()
                            self.current_scope()[var_name] = Pointer(None, target_type, self)
                    elif var_type == "ARRAY":
                        self.current_scope()[var_name] = np.array([])
                    elif var_type == "DATAFRAME":
                        self.current_scope()[var_name] = pd.DataFrame()
                    elif var_type == "STRING":
                        self.current_scope()[var_name] = ""
                    elif var_type in ("INTEGER", "LONG"):
                        self.current_scope()[var_name] = 0
                    elif var_type in ("SINGLE", "DOUBLE"):
                        self.current_scope()[var_name] = 0.0
                    elif var_type == "BYTE":
                        self.current_scope()[var_name] = 0
                    elif var_type == "SHORT":
                        self.current_scope()[var_name] = 0
                    elif var_type == "UNSIGNED INTEGER":
                        self.current_scope()[var_name] = 0
                    elif var_type == "CHAR":
                        self.current_scope()[var_name] = ''
                    elif var_type == "LIST":
                        self.current_scope()[var_name] = []
                    elif var_type == "DICT":
                        self.current_scope()[var_name] = {}
                    elif var_type == "SET":
                        self.current_scope()[var_name] = set()
                    elif var_type == "TUPLE":
                        self.current_scope()[var_name] = ()
                    else:
                        raise Exception(f"Tanımlanamayan veri tipi: {var_type}")
                    return None
                else:
                    raise Exception("DIM komutunda sözdizimi hatası")

            if command_upper.startswith("LET"):
                match = re.match(r"LET\s+(\w+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    var_name, expr = match.groups()
                    value = self.evaluate_expression(expr, scope_name)
                    if var_name in self.global_vars:
                        self.global_vars[var_name] = value
                    elif var_name in self.shared_vars and (scope_name in self.shared_vars[var_name] or not self.shared_vars[var_name]):
                        self.shared_vars[var_name] = value
                    elif var_name in self.current_scope():
                        self.current_scope()[var_name] = value
                    else:
                        raise Exception(f"Tanımlanmamış değişken: {var_name}")
                    return None
                else:
                    raise Exception("LET komutunda sözdizimi hatası")

            # Girdi/Çıktı
            if command_upper.startswith("PRINT"):
                print_str = command[5:].strip()
                parts = re.split(r'([;,])', print_str)
                output = ""
                for j in range(0, len(parts), 2):
                    arg = parts[j].strip()
                    if arg:
                        value = self.evaluate_expression(arg, scope_name)
                        output += str(value)
                    if j + 1 < len(parts) and parts[j+1] == ',':
                        output += " "
                if print_str.strip().endswith(';'):
                    print(output, end='')
                else:
                    print(output)
                return None

            if command_upper.startswith("INPUT"):
                match = re.match(r"INPUT\s+\"(.+)\"?,\s*(\w+)", command, re.IGNORECASE)
                if match:
                    prompt, var_name = match.groups()
                    if prompt:
                        value = input(prompt + " ")
                    else:
                        value = input("> ")
                    self.current_scope()[var_name] = value
                    return None
                else:
                    raise Exception("INPUT komutunda sözdizimi hatası")

            if command_upper.startswith("LINE INPUT"):
                match = re.match(r"LINE INPUT\s+\"(.+)\"?,\s*(\w+)", command, re.IGNORECASE)
                if match:
                    prompt, var_name = match.groups()
                    if prompt:
                        value = input(prompt + " ")
                    else:
                        value = input("> ")
                    self.current_scope()[var_name] = value
                    return None
                else:
                    raise Exception("LINE INPUT komutunda sözdizimi hatası")

            if command_upper.startswith("WRITE"):
                match = re.match(r"WRITE\s+(.+)", command, re.IGNORECASE)
                if match:
                    expr = match.group(1)
                    value = self.evaluate_expression(expr, scope_name)
                    print(f'"{value}"' if isinstance(value, str) else value)
                    return None
                else:
                    raise Exception("WRITE komutunda sözdizimi hatası")

            # Atama
            if re.match(r"\w+\s*=\s*.+", command, re.IGNORECASE):
                match = re.match(r"(\w+)\s*=\s*(.+)", command, re.IGNORECASE)
                if match:
                    var_name, expr = match.groups()
                    value = self.evaluate_expression(expr, scope_name)
                    if var_name in self.global_vars:
                        self.global_vars[var_name] = value
                    elif var_name in self.shared_vars and (scope_name in self.shared_vars[var_name] or not self.shared_vars[var_name]):
                        self.shared_vars[var_name] = value
                    elif var_name in self.current_scope():
                        self.current_scope()[var_name] = value
                    else:
                        raise Exception(f"Tanımlanmamış değişken: {var_name}")
                    return None

            # Alt Programlar
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
                        self.call_stack.append(self.program_counter)
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

            if command_upper.startswith("CALL"):
                match = re.match(r"CALL\s+(\w+)(?:\.(\w+))?(?:\((.*)\))?", command, re.IGNORECASE)
                if match:
                    target, method_name, args_str = match.groups()
                    if method_name:  # Sınıf yöntemi çağrısı
                        if target in self.current_scope():
                            obj = self.current_scope()[target]
                            args = self.evaluate_expression(f"({args_str})", scope_name) if args_str else []
                            args = args if isinstance(args, (list, tuple)) else [args]
                            method = obj.__dict__.get(method_name) or obj.__dict__.get('private_methods', {}).get(method_name)
                            if method:
                                return method(obj, *args)
                            else:
                                raise Exception(f"Yöntem bulunamadı: {method_name}")
                        else:
                            raise Exception(f"Sınıf örneği bulunamadı: {target}")
                    elif target in self.subs:  # Alt program çağrısı
                        self.call_stack.append(self.program_counter)
                        self.local_scopes.append({})
                        return self.subs[target]
                    else:
                        raise Exception(f"Alt program bulunamadı: {target}")
                else:
                    raise Exception("CALL komutunda sözdizimi hatası")

            # Fonksiyon Çağrısı
            if re.match(r"\w+\s*\(.+\)", command, re.IGNORECASE):
                match = re.match(r"(\w+)\s*\((.+)\)", command, re.IGNORECASE)
                if match:
                    func_name, args_str = match.groups()
                    if func_name in self.functions:
                        self.call_stack.append(self.program_counter)
                        self.local_scopes.append({})
                        return self.functions[func_name]
                    elif func_name in self.function_table:
                        args_tuple = self.evaluate_expression(f"({args_str})", scope_name)
                        args_tuple = args_tuple if isinstance(args_tuple, (list, tuple)) else [args_tuple]
                        result = self.function_table[func_name](*args_tuple)
                        if self.repl_mode:
                            print(result)
                        return result
                    else:
                        raise Exception(f"Fonksiyon bulunamadı: {func_name}")
                else:
                    raise Exception("Fonksiyon çağrısında sözdizimi hatası")

            # Sınıf Meta Veri İnceleme
            if command_upper.startswith("DESCRIBE"):
                match = re.match(r"DESCRIBE\s+(\w+)", command, re.IGNORECASE)
                if match:
                    class_name = match.group(1)
                    if class_name in self.classes:
                        cls = self.classes[class_name]
                        attrs = cls._vars.keys()
                        methods = [k for k, v in cls.__dict__.items() if callable(v) and k != '__init__' and k != 'private_methods']
                        private_methods = cls.__dict__.get('private_methods', {}).keys()
                        static_vars = cls._static_vars.keys()
                        print(f"Sınıf: {class_name}")
                        print(f"Nitelikler: {', '.join(attrs) or 'Yok'}")
                        print(f"Yöntemler: {', '.join(methods) or 'Yok'}")
                        print(f"Özel Yöntemler: {', '.join(private_methods) or 'Yok'}")
                        print(f"Statik Değişkenler: {', '.join(static_vars) or 'Yok'}")
                    else:
                        raise Exception(f"Sınıf bulunamadı: {class_name}")
                    return None
                else:
                    raise Exception("DESCRIBE komutunda sözdizimi hatası")

            # Dosya İşlemleri
            if command_upper.startswith("OPEN"):
                if "FOR ISAM" not in command_upper:
                    match = re.match(r"OPEN\s+\"(.+)\"\s+FOR\s+(INPUT|OUTPUT|APPEND|BINARY)\s+AS\s+#(\d+)", command, re.IGNORECASE)
                    if match:
                        file_path, mode, file_num = match.groups()
                        mode_map = {"INPUT": "r", "OUTPUT": "w", "APPEND": "a", "BINARY": "rb+"}
                        self.file_handles[int(file_num)] = open(file_path, mode_map[mode])
                        return None
                    else:
                        raise Exception("OPEN komutunda sözdizimi hatası")

            if command_upper.startswith("WRITE #"):
                match = re.match(r"WRITE\s+#(\d+),\s*(.+)", command, re.IGNORECASE)
                if match:
                    file_num, data = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        file.write(str(self.evaluate_expression(data, scope_name)) + "\n")
                        file.flush()
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("WRITE # komutunda sözdizimi hatası")

            if command_upper.startswith("APPEND #"):
                match = re.match(r"APPEND\s+#(\d+),\s*(.+)", command, re.IGNORECASE)
                if match:
                    file_num, data = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        file.seek(0, 2)  # Dosya sonuna git
                        file.write(str(self.evaluate_expression(data, scope_name)) + "\n")
                        file.flush()
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("APPEND # komutunda sözdizimi hatası")

            if command_upper.startswith("READ #"):
                match = re.match(r"READ\s+#(\d+),\s*(\w+)", command, re.IGNORECASE)
                if match:
                    file_num, var_name = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        self.current_scope()[var_name] = file.readline().strip()
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("READ # komutunda sözdizimi hatası")

            if command_upper.startswith("LOCK"):
                match = re.match(r"LOCK\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    file_num = match.group(1)
                    if int(file_num) in self.file_handles:
                        # Basit kilit simülasyonu
                        self.file_handles[int(file_num)].write("\0")
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("LOCK komutunda sözdizimi hatası")

            if command_upper.startswith("UNLOCK"):
                match = re.match(r"UNLOCK\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    file_num = match.group(1)
                    if int(file_num) in self.file_handles:
                        # Kilit kaldırma simülasyonu
                        pass
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("UNLOCK komutunda sözdizimi hatası")

            if command_upper.startswith("PRINT #"):
                match = re.match(r"PRINT\s+#(\d+),\s*(.+)", command, re.IGNORECASE)
                if match:
                    file_num, data = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        file.write(str(self.evaluate_expression(data, scope_name)) + "\n")
                        file.flush()
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("PRINT # komutunda sözdizimi hatası")

            if command_upper.startswith("INPUT #"):
                match = re.match(r"INPUT\s+#(\d+),\s*(\w+)", command, re.IGNORECASE)
                if match:
                    file_num, var_name = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        self.current_scope()[var_name] = file.readline().strip()
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("INPUT # komutunda sözdizimi hatası")

            if command_upper.startswith("LINE INPUT #"):
                match = re.match(r"LINE INPUT\s+#(\d+),\s*(\w+)", command, re.IGNORECASE)
                if match:
                    file_num, var_name = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        self.current_scope()[var_name] = file.readline().strip()
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("LINE INPUT # komutunda sözdizimi hatası")

            if command_upper.startswith("SEEK"):
                match = re.match(r"SEEK\s+#(\d+),\s*(.+)", command, re.IGNORECASE)
                if match:
                    file_num, position = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        file.seek(self.evaluate_expression(position, scope_name))
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("SEEK komutunda sözdizimi hatası")

            if command_upper.startswith("GET #"):
                match = re.match(r"GET\s+#(\d+),\s*(.+),\s*(\w+)", command, re.IGNORECASE)
                if match:
                    file_num, position, var_name = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        file.seek(self.evaluate_expression(position, scope_name))
                        self.current_scope()[var_name] = file.read(1)  # Basit okuma
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("GET # komutunda sözdizimi hatası")

            if command_upper.startswith("PUT #"):
                match = re.match(r"PUT\s+#(\d+),\s*(.+),\s*(.+)", command, re.IGNORECASE)
                if match:
                    file_num, position, data = match.groups()
                    file = self.file_handles.get(int(file_num))
                    if file:
                        file.seek(self.evaluate_expression(position, scope_name))
                        file.write(str(self.evaluate_expression(data, scope_name)))
                    else:
                        raise Exception(f"Dosya #{file_num} açık değil")
                    return None
                else:
                    raise Exception("PUT # komutunda sözdizimi hatası")

            if command_upper.startswith("CLOSE"):
                match = re.match(r"CLOSE\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    file_num = match.group(1)
                    num = int(file_num)
                    if num in self.file_handles:
                        self.file_handles[num].close()
                        del self.file_handles[num]
                    elif num in self.db_connections:
                        self.db_connections[num].close()
                        del self.db_connections[num]
                    else:
                        raise Exception(f"Kapatılacak dosya #{file_num} bulunamadı")
                    return None
                else:
                    raise Exception("CLOSE komutunda sözdizimi hatası")

            if command_upper.startswith("KILL"):
                match = re.match(r"KILL\s+\"(.+)\"", command, re.IGNORECASE)
                if match:
                    file_name = match.group(1)
                    os.remove(file_name)
                    return None
                else:
                    raise Exception("KILL komutunda sözdizimi hatası")

            if command_upper.startswith("NAME"):
                match = re.match(r"NAME\s+\"(.+)\"\s+AS\s+\"(.+)\"", command, re.IGNORECASE)
                if match:
                    old_name, new_name = match.groups()
                    os.rename(old_name, new_name)
                    return None
                else:
                    raise Exception("NAME komutunda sözdizimi hatası")

            if command_upper.startswith("FILES"):
                match = re.match(r"FILES\s+\"(.+)\"", command, re.IGNORECASE)
                if match:
                    pattern = match.group(1)
                    print("\n".join(os.listdir(pattern)))
                    return None
                else:
                    raise Exception("FILES komutunda sözdizimi hatası")

            if command_upper.startswith("CHDIR"):
                match = re.match(r"CHDIR\s+\"(.+)\"", command, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    os.chdir(path)
                    return None
                else:
                    raise Exception("CHDIR komutunda sözdizimi hatası")

            if command_upper.startswith("MKDIR"):
                match = re.match(r"MKDIR\s+\"(.+)\"", command, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    os.mkdir(path)
                    return None
                else:
                    raise Exception("MKDIR komutunda sözdizimi hatası")

            if command_upper.startswith("RMDIR"):
                match = re.match(r"RMDIR\s+\"(.+)\"", command, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    os.rmdir(path)
                    return None
                else:
                    raise Exception("RMDIR komutunda sözdizimi hatası")

            # Veritabanı İşlemleri
            if command_upper.startswith("OPEN") and "FOR ISAM" in command_upper:
                match = re.match(r"OPEN\s+\"(.+)\"\s+FOR\s+ISAM\s+AS\s+#(\d+)", command, re.IGNORECASE)
                if match:
                    db_file, file_num = match.groups()
                    conn = sqlite3.connect(db_file)
                    self.db_connections[int(file_num)] = conn
                    self.transaction_active[int(file_num)] = False
                    return None
                else:
                    raise Exception("OPEN FOR ISAM komutunda sözdizimi hatası")

            # Komut bulunamadı
            raise Exception(f"Tanınmayan komut: {command}")

        except Exception as e:
            if self.error_handler:
                if self.error_handler == "RESUME":
                    print(f"Hata: {e}")
                    return None
                else:
                    print(f"Hata: {e}")
                    return self.error_handler
            else:
                raise

    def run(self, code=None):
        """Programı çalıştırır."""
        if code:
            self.parse_program(code)
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.program):
            command, scope = self.program[self.program_counter]
            if self.debug_mode:
                print(f"DEBUG: Satır {self.program_counter + 1}: {command}")
                input("Devam için Enter...")
            next_pc = self.execute_command(command, scope)
            if next_pc is not None:
                self.program_counter = next_pc
            else:
                self.program_counter += 1
        self.running = False

    def repl(self):
        """Etkileşimli yorumlayıcı."""
        self.repl_mode = True
        print("pdsX Etkileşimli Yorumlayıcı v1.0")
        print("Çıkış için 'EXIT' yazın.")
        while True:
            try:
                command = input("> ")
                if command.upper() == "EXIT":
                    break
                result = self.execute_command(command)
                if result is not None and result != self.program_counter + 1:
                    print(f"Sonuç: {result}")
            except Exception as e:
                print(f"Hata: {e}")
        self.repl_mode = False

    def compile_to_bytecode(self, code):
        """Kodu bayt koduna derler."""
        bytecode = []
        lines = code.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Basit bir bayt kodu oluşturma
            tokens = line.split()
            if tokens:
                opcode = tokens[0].upper()
                operands = tokens[1:] if len(tokens) > 1 else []
                bytecode.append((opcode, operands))
        return bytecode

    def execute_bytecode(self):
        """Bayt kodunu çalıştırır."""
        if not self.bytecode:
            raise Exception("Bayt kodu bulunamadı")
        self.running = True
        self.program_counter = 0
        while self.running and self.program_counter < len(self.bytecode):
            opcode, operands = self.bytecode[self.program_counter]
            # Bayt kodu işleme
            if opcode == "PRINT":
                print(" ".join(operands))
            elif opcode == "LET":
                var_name = operands[0]
                value = " ".join(operands[2:])
                self.current_scope()[var_name] = self.evaluate_expression(value)
            # Diğer opcode'lar...
            self.program_counter += 1
        self.running = False

def main():
    parser = argparse.ArgumentParser(description='pdsX Yorumlayıcı')
    parser.add_argument('file', nargs='?', help='Çalıştırılacak dosya')
    parser.add_argument('-i', '--interactive', action='store_true', help='Etkileşimli mod')
    parser.add_argument('-d', '--debug', action='store_true', help='Hata ayıklama modu')
    parser.add_argument('-t', '--trace', action='store_true', help='İzleme modu')
    parser.add_argument('-c', '--compile', action='store_true', help='Derleme modu')
    args = parser.parse_args()

    interpreter = pdsXInterpreter()
    
    if args.debug:
        interpreter.debug_mode = True
    
    if args.trace:
        interpreter.trace_mode = True
    
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
        if args.compile:
            interpreter.bytecode = interpreter.compile_to_bytecode(code)
            interpreter.execute_bytecode()
        else:
            interpreter.run(code)
    
    if args.interactive or not args.file:
        interpreter.repl()

if __name__ == "__main__":
    main()
