# pdsXv13u.py deneme3
# Ultimate Professional Development System Interpreter
# Version: 13u - Mete Dinler (Fikir) + v9 a kadar kodlayap grok, v10 metedinler, v11, v12, v13 kodlayan ChatGPT (Kodlama)
# v13 denemeleri bir kas tane bu 3. su her birinde birseyler eksik

import os
import sys
import time
import math
import glob
import json
import ast
import re
import shutil
import random
import socket
import struct
import logging
import ctypes
import threading
import asyncio
import sqlite3
import requests
import pdfplumber
import numpy as np
import pandas as pd
import psutil
from types import SimpleNamespace
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict, namedtuple
from packaging import version
from threading import Thread
import multiprocessing
import subprocess
import importlib.metadata
import argparse
from abc import ABC, abstractmethod

# Bağımlılık Yönetimi
def install_missing_libraries():
    """Gerekli bağımlılıkları kontrol eder ve eksik olanları yükler."""
    required = {
        'numpy': 'numpy', 'pandas': 'pandas', 'scipy': 'scipy',
        'psutil': 'psutil', 'pdfplumber': 'pdfplumber', 'bs4': 'beautifulsoup4',
        'requests': 'requests', 'packaging': 'packaging'
    }
    installed = {pkg.metadata['Name'].lower() for pkg in importlib.metadata.distributions()}
    missing = [lib for lib, pkg in required.items() if lib not in installed]
    if missing:
        print(f"Eksik kütüphaneler yükleniyor: {missing}")
        for lib in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", required[lib]])
                print(f"{lib} kuruldu.")
            except subprocess.CalledProcessError:
                print(f"Hata: {lib} yüklenemedi, elle kurun.")

install_missing_libraries()

# Loglama Ayarları
logging.basicConfig(filename='interpreter_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(message)s')

# Yardımcı Sınıflar
class ClassDef:
    def __init__(self, name, parent=None, abstract=False, interfaces=None):
        self.name = name
        self.parent = parent
        self.abstract = abstract
        self.interfaces = interfaces if interfaces else []
        self.constructor = None
        self.destructor = None
        self.methods = {}
        self.static_vars = {}
        self.is_mixin = False

class InterfaceDef:
    def __init__(self, name):
        self.name = name
        self.methods = []

class MethodDef:
    def __init__(self, name, body, params, private=False):
        self.name = name
        self.body = body
        self.params = params
        self.private = private

# Hafıza Yönetimi
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

# Yapılar (Struct ve Union)
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
# Pointer Sınıfı
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

# Temel Exception
class PdsXException(Exception):
    class PdsXException(Exception):
    """
    pdsXv13u yorumlayıcısı için özel hata sınıfı.
    Her türlü yorumlayıcı hatasını anlamlı ve kontrol edilebilir şekilde işler.
    """
    def __init__(self, message=None, code=None, context=None):
        """
        :param message: Hata mesajı (str)
        :param code: Hata kodu (int, opsiyonel)
        :param context: Hata sırasında ek bilgi veya nesne (opsiyonel)
        """
        super().__init__(message)
        self.message = message or "Bilinmeyen pdsX hatası"
        self.code = code
        self.context = context

    def __str__(self):
        info = f"PDSX HATASI"
        if self.code is not None:
            info += f" [Kod: {self.code}]"
        info += f" - {self.message}"
        if self.context:
            info += f" (Bağlam: {self.context})"
        return info

    def to_dict(self):
        """
        Hata bilgisini sözlük formatında döndürür.
        :return: dict
        """
        return {
            "error": True,
            "message": self.message,
            "code": self.code,
            "context": self.context
        }



# Basit Struct ve Veri Tipleri için Tip Tablosu
def create_type_table():
    return {
        "INTEGER": int,
        "FLOAT": float,
        "STRING": str,
        "LIST": list,
        "DICT": dict,
        "BOOL": bool,
        "ARRAY": list,
        "BYTE": int,
        "SHORT": int,
        "LONG": int,
        "DOUBLE": float,
        "SINGLE": float,
        "POINTER": Pointer,
        "STRUCT": StructInstance,
        "UNION": UnionInstance,
    }

# Utility Fonksiyonları
def safe_eval(expr, variables):
    try:
        return eval(expr, {}, variables)
    except Exception as e:
        return f"Eval Hatası: {e}"

def parse_params(params_str):
    if not params_str:
        return []
    return [param.strip() for param in params_str.split(",") if param.strip()]

def to_bool(val):
    if isinstance(val, str):
        val = val.strip().lower()
        return val in ["true", "1", "evet", "yes"]
    return bool(val)

def serialize_pipe(data, compress=False):
    if compress:
        import gzip
        out = gzip.compress(json.dumps(data).encode('utf-8'))
        return out
    return json.dumps(data).encode('utf-8')

def deserialize_pipe(data, compressed=False):
    if compressed:
        import gzip
        out = json.loads(gzip.decompress(data).decode('utf-8'))
        return out
    return json.loads(data.decode('utf-8'))

# Yardımcı Basit Fonksiyonlar
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def today():
    return datetime.now().strftime("%Y-%m-%d")

def timestamp():
    return time.time()

def cpu_count():
    return multiprocessing.cpu_count()

def ram_usage():
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def internet_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        return False

# Log fonksiyonu
def write_log(message, level="INFO"):
    log_line = f"{now()} [{level}] {message}"
    print(log_line)
    with open("interpreter.log", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

# Event Manager Sınıfı
class Event:
    def __init__(self, event_id, trigger, action, priority=0, enabled=True, delay=0):
        self.event_id = event_id
        self.trigger = trigger
        self.action = action
        self.priority = priority
        self.enabled = enabled
        self.delay = delay
        self.last_trigger_time = 0

class EventManager:
    def __init__(self):
        self.events = {}
        self.max_events = 64
        self.active_limit = 32

    def add_event(self, trigger, action, priority=0, delay=0):
        if len(self.events) >= self.max_events:
            raise Exception("Maksimum event sayısına ulaşıldı")
        event_id = len(self.events)
        event = Event(event_id, trigger, action, priority, enabled=True, delay=delay)
        self.events[event_id] = event
        return event_id

    def remove_event(self, event_id):
        if event_id in self.events:
            del self.events[event_id]

    def enable_event(self, event_id):
        if event_id in self.events:
            self.events[event_id].enabled = True

    def disable_event(self, event_id):
        if event_id in self.events:
            self.events[event_id].enabled = False

    def trigger_event(self, event_id):
        if event_id in self.events:
            event = self.events[event_id]
            if event.enabled:
                now_time = time.time()
                if now_time - event.last_trigger_time >= event.delay:
                    event.action()
                    event.last_trigger_time = now_time

    def process_events(self):
        active_events = [e for e in self.events.values() if e.enabled]
        active_events.sort(key=lambda e: e.priority)
        for event in active_events[:self.active_limit]:
            if event.trigger():
                self.trigger_event(event.event_id)

    def clear(self):
        self.events.clear()

# Tree Veri Yapısı
class TreeNode:
    def __init__(self, key, data=None):
        self.key = key
        self.data = data
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def find(self, key):
        if self.key == key:
            return self
        for child in self.children:
            result = child.find(key)
            if result:
                return result
        return None

    def to_dict(self):
        return {
            "key": self.key,
            "data": self.data,
            "children": [child.to_dict() for child in self.children]
        }

    def traverse(self):
        yield self
        for child in self.children:
            yield from child.traverse()

# Graph Veri Yapısı
class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, key, data=None):
        self.nodes[key] = data
        self.edges[key] = []

    def add_edge(self, src, dest):
        if src not in self.nodes or dest not in self.nodes:
            raise Exception("Geçersiz düğüm")
        self.edges[src].append(dest)

    def get_neighbors(self, node):
        return self.edges.get(node, [])

    def bfs(self, start):
        visited = set()
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                yield node
                visited.add(node)
                queue.extend(self.edges.get(node, []))

    def dfs(self, start):
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                yield node
                visited.add(node)
                stack.extend(reversed(self.edges.get(node, [])))

# Pipe İşlemleri
class PipeManager:
    def __init__(self):
        self.pipes = {}
        self.counter = 0

    def create_pipe(self):
        pipe_id = f"pipe_{self.counter}"
        self.pipes[pipe_id] = []
        self.counter += 1
        return pipe_id

    def add_to_pipe(self, pipe_id, item):
        if pipe_id in self.pipes:
            self.pipes[pipe_id].append(item)
        else:
            raise Exception("Boru hattı bulunamadı")

    def get_pipe(self, pipe_id):
        return self.pipes.get(pipe_id, [])

    def clear_pipe(self, pipe_id):
        if pipe_id in self.pipes:
            self.pipes[pipe_id] = []

    def delete_pipe(self, pipe_id):
        if pipe_id in self.pipes:
            del self.pipes[pipe_id]

# SQL Yönetimi
class SqlManager:
    def __init__(self):
        self.databases = {}
        self.auto_database = None

    def open_database(self, name, path=":memory:"):
        conn = sqlite3.connect(path)
        self.databases[name] = conn
        if self.auto_database is None:
            self.auto_database = name

    def close_database(self, name):
        if name in self.databases:
            self.databases[name].close()
            del self.databases[name]
            if self.auto_database == name:
                self.auto_database = None

    def exec_sql(self, sql, params=None, db=None):
        if db is None:
            db = self.auto_database
        if db not in self.databases:
            raise Exception(f"Veritabanı bulunamadı: {db}")
        cur = self.databases[db].cursor()
        cur.execute(sql, params or [])
        self.databases[db].commit()

    def query_sql(self, sql, params=None, db=None):
        if db is None:
            db = self.auto_database
        if db not in self.databases:
            raise Exception(f"Veritabanı bulunamadı: {db}")
        cur = self.databases[db].cursor()
        cur.execute(sql, params or [])
        return cur.fetchall()

    def sql_pipeline(self, sql, db=None, map_func=None, filter_func=None):
        rows = self.query_sql(sql, db=db)
        if map_func:
            rows = [map_func(row) for row in rows]
        if filter_func:
            rows = [row for row in rows if filter_func(row)]
        return rows

# Save/Load Program ve State
def save_program(filename, program_lines, compress=True):
    data = "\n".join(program_lines)
    if compress:
        import gzip
        with gzip.open(filename, "wt", encoding="utf-8") as f:
            f.write(data)
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)

def load_program(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".gz":
        import gzip
        with gzip.open(filename, "rt", encoding="utf-8") as f:
            data = f.read()
    else:
        with open(filename, "r", encoding="utf-8") as f:
            data = f.read()
    return data.splitlines()

def save_state(filename, state):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

def load_state(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# Basit Argparse Wrapper
def create_parser():
    parser = argparse.ArgumentParser(description="pdsXv13u Ultimate Interpreter")
    parser.add_argument('file', nargs='?', help='Çalıştırılacak dosya')
    parser.add_argument('-i', '--interactive', action='store_true', help='Etkileşimli mod')
    parser.add_argument('--save-state', action='store_true', help='Çıkışta state kaydet')
    parser.add_argument('--load-state', action='store_true', help='Başlarken state yükle')
    return parser

# Yardım Sistemi JSON Okuyucu
def load_help_file(language="en"):
    path = f"help_{language}.json"
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def print_help(command=None, language="en"):
    help_data = load_help_file(language)
    if command:
        desc = help_data.get(command.upper(), "Komut bulunamadı.")
        print(f"{command}: {desc}")
    else:
        for cmd, desc in help_data.items():
            print(f"{cmd}: {desc}")
# INLINE Sistemleri
class InlineHandler:
    def __init__(self):
        self.inline_blocks = {"ASM": {}, "C": {}, "REPLY": {}}
        self.current_block = None
        self.current_type = None

    def start_inline(self, inline_type, name):
        if inline_type not in self.inline_blocks:
            raise Exception(f"Desteklenmeyen INLINE tipi: {inline_type}")
        self.current_block = []
        self.current_type = inline_type
        self.current_name = name

    def end_inline(self):
        if not self.current_block or not self.current_type or not self.current_name:
            raise Exception("INLINE bloğu başlatılmadı")
        self.inline_blocks[self.current_type][self.current_name] = "\n".join(self.current_block)
        self.current_block = None
        self.current_type = None
        self.current_name = None

    def add_line(self, line):
        if self.current_block is not None:
            self.current_block.append(line)
        else:
            raise Exception("Aktif INLINE bloğu yok")

    def get_inline(self, inline_type, name):
        return self.inline_blocks.get(inline_type, {}).get(name, None)

    def list_inline(self, inline_type):
        return list(self.inline_blocks.get(inline_type, {}).keys())

    def save_inline(self, filename):
        data = {
            "ASM": self.inline_blocks["ASM"],
            "C": self.inline_blocks["C"],
            "REPLY": self.inline_blocks["REPLY"]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_inline(self, filename):
        if not os.path.exists(filename):
            raise Exception(f"INLINE dosyası bulunamadı: {filename}")
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.inline_blocks.update(data)

# Prolog V3 Mantıksal Motor
class PrologEngine:
    def __init__(self):
        self.facts = []
        self.rules = []
        self.variables = {}

    def add_fact(self, fact):
        self.facts.append(fact)

    def add_rule(self, head, body):
        self.rules.append((head, body))

    def query(self, goal):
        self.variables = {}
        result = self.match_goal(goal)
        return result

    def match_goal(self, goal):
        if isinstance(goal, tuple):
            op = goal[0].upper()
            if op == "PAND":
                return all(self.match_goal(sub) for sub in goal[1:])
            elif op == "POR":
                return any(self.match_goal(sub) for sub in goal[1:])
            elif op == "PNOT":
                return not self.match_goal(goal[1])
            elif op == "PXOR":
                return sum(self.match_goal(sub) for sub in goal[1:]) == 1
            elif op == "PIMP":
                return not self.match_goal(goal[1]) or self.match_goal(goal[2])
            elif op == "PBICOND":
                return self.match_goal(("PIMP", goal[1], goal[2])) and self.match_goal(("PIMP", goal[2], goal[1]))
            else:
                return self.unify_goal(goal)
        else:
            return self.unify_goal(goal)

    def unify_goal(self, goal):
        for fact in self.facts:
            self.variables = {}
            if self.unify(goal, fact, self.variables):
                return True
        for head, body in self.rules:
            self.variables = {}
            if self.unify(goal, head, self.variables):
                if all(self.match_goal(subgoal) for subgoal in body):
                    return True
        return False

    def unify(self, t1, t2, bindings):
        if isinstance(t1, str) and t1.startswith("#"):
            bindings[t1] = t2
            return True
        if isinstance(t2, str) and t2.startswith("#"):
            bindings[t2] = t1
            return True
        if isinstance(t1, str) and isinstance(t2, str):
            return t1 == t2
        if isinstance(t1, tuple) and isinstance(t2, tuple):
            if len(t1) != len(t2):
                return False
            return all(self.unify(a, b, bindings) for a, b in zip(t1, t2))
        return False

    def print_bindings(self):
        for var, val in self.variables.items():
            print(f"{var} = {val}")

    def clear(self):
        self.facts.clear()
        self.rules.clear()

    def remove_fact(self, fact):
        if fact in self.facts:
            self.facts.remove(fact)

    def remove_rule(self, rule):
        if rule in self.rules:
            self.rules.remove(rule)

    def dump_knowledge_base(self):
        print("--- FACTS ---")
        for f in self.facts:
            print(f)
        print("--- RULES ---")
        for h, b in self.rules:
            print(f"{h} :- {b}")

# Interpreter Ana Yapısı
class PDSXv13u:
    def __init__(self):
        self.program = []
        self.memory = MemoryManager()
        self.inline = InlineHandler()
        self.prolog = PrologEngine()
        self.pipe = PipeManager()
        self.sql = SqlManager()
        self.libx = LibXCore(self)
        self.global_scope = {}
        self.modules = {}
        self.running = False
        self.event_manager = EventManager()
        self.state_loaded = False

    def repl(self):
        while True:
            try:
                line = input(">>> ")
                if line.strip().lower() in ("exit", "quit"):
                    break
                self.execute_line(line)
            except Exception as e:
                print(f"Hata: {e}")

    def execute_line(self, line):
        # Komut çözümleyici burada olacak (bir sonraki bölümde)
        pass

    def run(self, code_lines):
        self.program = code_lines
        self.running = True
        for line in self.program:
            self.execute_line(line)

    def save_state(self, filename="pdsx13_state.json"):
        save_state(filename, {
            "globals": self.global_scope,
            "pipes": self.pipe.pipes,
            "events": self.event_manager.events,
        })

    def load_state(self, filename="pdsx13_state.json"):
        state = load_state(filename)
        self.global_scope.update(state.get("globals", {}))
        self.pipe.pipes.update(state.get("pipes", {}))
        # Eventler burada yeniden yüklenebilir (isteğe bağlı)

    def start(self, filepath=None):
        if filepath:
            code = load_program(filepath)
            self.run(code)
        else:
            self.repl()
# Yardımcı Fonksiyonlar
def save_state(filename, state_data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=4)

def load_state(filename):
    if not os.path.exists(filename):
        raise Exception(f"Durum dosyası bulunamadı: {filename}")
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def load_program(filepath):
    if not os.path.exists(filepath):
        raise Exception(f"Program dosyası bulunamadı: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

# PipeManager Yapısı
class PipeManager:
    def __init__(self):
        self.pipes = {}
        self.pipe_id_counter = 0

    def create_pipe(self):
        pid = self.pipe_id_counter
        self.pipes[pid] = []
        self.pipe_id_counter += 1
        return pid

    def save_pipe(self, pid, path, compressed=False):
        if pid not in self.pipes:
            raise Exception("Boru bulunamadı")
        data = self.pipes[pid]
        if compressed:
            import gzip
            with gzip.open(path, "wt", encoding="utf-8") as f:
                json.dump(data, f)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)

    def load_pipe(self, path, compressed=False):
        if compressed:
            import gzip
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        pid = self.pipe_id_counter
        self.pipes[pid] = data
        self.pipe_id_counter += 1
        return pid

# SqlManager Yapısı
class SqlManager:
    def __init__(self):
        self.connections = {}
        self.auto_db = None

    def open_db(self, name, path=":memory:"):
        conn = sqlite3.connect(path)
        self.connections[name] = conn
        if self.auto_db is None:
            self.auto_db = name

    def close_db(self, name):
        if name in self.connections:
            self.connections[name].close()
            del self.connections[name]
            if self.auto_db == name:
                self.auto_db = None

    def execute(self, sql, params=None, db=None):
        if db is None:
            db = self.auto_db
        if db not in self.connections:
            raise Exception(f"Veritabanı bulunamadı: {db}")
        cur = self.connections[db].cursor()
        cur.execute(sql, params or [])
        self.connections[db].commit()

    def query(self, sql, params=None, db=None):
        if db is None:
            db = self.auto_db
        if db not in self.connections:
            raise Exception(f"Veritabanı bulunamadı: {db}")
        cur = self.connections[db].cursor()
        cur.execute(sql, params or [])
        return cur.fetchall()

    def sql_pipeline(self, sql, db=None, map_func=None, filter_func=None):
        rows = self.query(sql, db=db)
        if map_func:
            rows = [map_func(r) for r in rows]
        if filter_func:
            rows = [r for r in rows if filter_func(r)]
        return rows

# EventManager yeniden
class Event:
    def __init__(self, event_id, trigger, action, priority=0, delay=0):
        self.event_id = event_id
        self.trigger = trigger
        self.action = action
        self.priority = priority
        self.delay = delay
        self.enabled = True
        self.last_trigger_time = 0

class EventManager:
    def __init__(self):
        self.events = {}
        self.max_events = 64
        self.active_limit = 32

    def add_event(self, trigger, action, priority=0, delay=0):
        if len(self.events) >= self.max_events:
            raise Exception("Maksimum event sayısına ulaşıldı")
        event_id = len(self.events)
        event = Event(event_id, trigger, action, priority, delay)
        self.events[event_id] = event
        return event_id

    def trigger_event(self, event_id):
        event = self.events.get(event_id)
        if event and event.enabled:
            now = time.time()
            if now - event.last_trigger_time >= event.delay:
                event.action()
                event.last_trigger_time = now

    def process_events(self):
        active = [e for e in self.events.values() if e.enabled]
        active.sort(key=lambda e: e.priority)
        for event in active[:self.active_limit]:
            if event.trigger():
                self.trigger_event(event.event_id)

    def clear(self):
        self.events.clear()
# PrologV3 - Gelişmiş Prolog Mantıksal Motor
class PrologV3:
    def __init__(self):
        self.facts = []
        self.rules = []
        self.variables = {}
        self.trace_enabled = False

    def add_fact(self, fact):
        self.facts.append(fact)

    def add_rule(self, head, body):
        self.rules.append((head, body))

    def query(self, goal):
        self.variables = {}
        result = self.match(goal)
        if result:
            if self.trace_enabled:
                self.print_variables()
            return True
        else:
            if self.trace_enabled:
                print(f"Başarısız: {goal}")
            return False

    def match(self, goal):
        if isinstance(goal, tuple) and goal[0] == "pAND":
            return all(self.match(sub) for sub in goal[1:])
        elif isinstance(goal, tuple) and goal[0] == "pOR":
            return any(self.match(sub) for sub in goal[1:])
        elif isinstance(goal, tuple) and goal[0] == "pNOT":
            return not self.match(goal[1])
        elif isinstance(goal, tuple) and goal[0] == "pXOR":
            return sum(self.match(sub) for sub in goal[1:]) == 1
        elif isinstance(goal, tuple) and goal[0] == "pIMP":
            return not self.match(goal[1]) or self.match(goal[2])
        elif isinstance(goal, tuple) and goal[0] == "pBICOND":
            return self.match(("pIMP", goal[1], goal[2])) and self.match(("pIMP", goal[2], goal[1]))
        else:
            return self.unify(goal)

    def unify(self, goal):
        for fact in self.facts:
            self.variables = {}
            if self.unify_terms(goal, fact):
                return True
        for head, body in self.rules:
            self.variables = {}
            if self.unify_terms(goal, head):
                if all(self.match(subgoal) for subgoal in body):
                    return True
        return False

    def unify_terms(self, term1, term2):
        if isinstance(term1, str) and term1.startswith("#"):
            self.variables[term1] = term2
            return True
        if isinstance(term2, str) and term2.startswith("#"):
            self.variables[term2] = term1
            return True
        if isinstance(term1, str) and isinstance(term2, str):
            return term1 == term2
        if isinstance(term1, tuple) and isinstance(term2, tuple):
            if len(term1) != len(term2):
                return False
            return all(self.unify_terms(t1, t2) for t1, t2 in zip(term1, term2))
        return False

    def print_variables(self):
        for var, val in self.variables.items():
            print(f"{var} = {val}")

    def clear(self):
        self.facts.clear()
        self.rules.clear()

    def backtrace(self):
        print("Backtrace: Bilgi tabanı sorgulama zinciri.")
        for idx, fact in enumerate(self.facts):
            print(f"FACT {idx}: {fact}")
        for idx, (head, body) in enumerate(self.rules):
            print(f"RULE {idx}: {head} :- {body}")

    def dump(self):
        return {"facts": self.facts, "rules": self.rules}

    def count(self, predicate):
        return sum(1 for fact in self.facts if fact[0] == predicate)

    def exists(self, predicate):
        return any(fact[0] == predicate for fact in self.facts)

    def forall(self, predicate):
        return all(fact[0] == predicate for fact in self.facts)
# PrologV3 ile pdsX Interpreter Entegrasyonu
class pdsXv13uPrologMixin:
    def __init__(self):
        self.prolog = PrologV3()

    def cmd_pfact(self, args):
        """pFACT predicate arguments"""
        if not args:
            print("Kullanım: pFACT predicate arguments")
            return
        pred = args[0]
        params = args[1:]
        self.prolog.add_fact((pred, *params))
        print(f"Fact eklendi: {pred} {params}")

    def cmd_prule(self, args):
        """pRULE head :- body"""
        if not args or ":-" not in args:
            print("Kullanım: pRULE head :- body")
            return
        split_idx = args.index(":-")
        head = tuple(args[:split_idx])
        body = [tuple(x.split(",")) for x in args[split_idx+1:]]
        self.prolog.add_rule(head, body)
        print(f"Rule eklendi: {head} :- {body}")

    def cmd_pquery(self, args):
        """pQUERY predicate arguments"""
        if not args:
            print("Kullanım: pQUERY predicate arguments")
            return
        goal = (args[0], *args[1:])
        result = self.prolog.query(goal)
        if result:
            print("Sorgu BAŞARILI")
        else:
            print("Sorgu BAŞARISIZ")

    def cmd_passert(self, args):
        """pASSERT predicate arguments"""
        self.cmd_pfact(args)

    def cmd_pretract(self, args):
        """pRETRACT predicate arguments"""
        if not args:
            print("Kullanım: pRETRACT predicate arguments")
            return
        pred = args[0]
        params = args[1:]
        target = (pred, *params)
        if target in self.prolog.facts:
            self.prolog.facts.remove(target)
            print(f"Fact kaldırıldı: {target}")
        else:
            print(f"Böyle bir fact yok: {target}")

    def cmd_pclear(self, args):
        """pCLEAR"""
        self.prolog.clear()
        print("Tüm facts ve rules temizlendi.")

    def cmd_pbacktrace(self, args):
        """pBACKTRACE"""
        self.prolog.backtrace()

    def cmd_pdump(self, args):
        """pDUMP"""
        dump_data = self.prolog.dump()
        print("Dump Bilgisi:")
        print(json.dumps(dump_data, indent=2))

    def cmd_pcount(self, args):
        """pCOUNT predicate"""
        if not args:
            print("Kullanım: pCOUNT predicate")
            return
        pred = args[0]
        cnt = self.prolog.count(pred)
        print(f"{pred} için {cnt} kayıt var.")

    def cmd_pexists(self, args):
        """pEXISTS predicate"""
        if not args:
            print("Kullanım: pEXISTS predicate")
            return
        pred = args[0]
        exists = self.prolog.exists(pred)
        print(f"Exists: {exists}")

    def cmd_pforall(self, args):
        """pFORALL predicate"""
        if not args:
            print("Kullanım: pFORALL predicate")
            return
        pred = args[0]
        result = self.prolog.forall(pred)
        print(f"ForAll sonucu: {result}")
# pdsXv13u Interpreter Ana Yapı
class pdsXv13u(pdsXv12Final, pdsXv13uPrologMixin):
    def __init__(self):
        super().__init__()
        self.prolog = PrologV3()
        self.event_manager = EventManager()
        self.libx = LibXCore(self)
        self.tree_nodes = {}
        self.graph_nodes = {}
        self.type_table.update({
            "INTEGER": int,
            "FLOAT": float,
            "STRING": str,
            "LIST": list,
            "DICT": dict,
            "ARRAY": np.ndarray,
            "STRUCT": StructInstance,
            "UNION": UnionInstance,
            "POINTER": Pointer,
            "CLASS": ClassInstance
        })

    def current_scope(self):
        return self.local_scopes[-1] if self.local_scopes else self.variables

    def execute_command(self, command, args=None, module_name="main"):
        if isinstance(command, tuple):
            command = " ".join(str(c) for c in command)
        command = command.strip()
        if not command:
            return
        parts = command.split()
        cmd = parts[0].upper()
        args = parts[1:] if len(parts) > 1 else []

        # Önce Prolog komutlarını kontrol et
        prolog_cmds = {
            "PFACT": self.cmd_pfact,
            "PRULE": self.cmd_prule,
            "PQUERY": self.cmd_pquery,
            "PASSERT": self.cmd_passert,
            "PRETRACT": self.cmd_pretract,
            "PCLEAR": self.cmd_pclear,
            "PBACKTRACE": self.cmd_pbacktrace,
            "PDUMP": self.cmd_pdump,
            "PCOUNT": self.cmd_pcount,
            "PEXISTS": self.cmd_pexists,
            "PFORALL": self.cmd_pforall
        }
        if cmd in prolog_cmds:
            prolog_cmds[cmd](args)
            return

        # INLINE ASM / C / REPLY
        if cmd == "INLINE":
            self.handle_inline(args)
            return

        # Normal komutlar
        if hasattr(self, f"cmd_{cmd.lower()}"):
            getattr(self, f"cmd_{cmd.lower()}")(args)
        else:
            raise Exception(f"Bilinmeyen komut: {cmd}")

    def handle_inline(self, args):
        if not args:
            print("INLINE kullanım hatası")
            return
        block_type = args[0].upper()
        if block_type == "ASM":
            self.inline_asm(args[1:])
        elif block_type == "C":
            self.inline_c(args[1:])
        elif block_type == "REPLY":
            self.inline_reply(args[1:])
        else:
            print(f"INLINE tipi tanınmadı: {block_type}")

    def inline_asm(self, code_lines):
        print("[INLINE ASM Başladı]")
        for line in code_lines:
            print(f"ASM: {line}")
        print("[INLINE ASM Bitti]")

    def inline_c(self, code_lines):
        print("[INLINE C Başladı]")
        for line in code_lines:
            print(f"C: {line}")
        print("[INLINE C Bitti]")

    def inline_reply(self, code_lines):
        print("[INLINE REPLY Başladı]")
        for line in code_lines:
            print(f"REPLY: {line}")
        print("[INLINE REPLY Bitti]")
    # --- Prolog V3 Komutları ---

    def cmd_pfact(self, args):
        """Gerçek ekler: PFACT parent(john, mary)"""
        if not args:
            print("PFACT kullanım hatası.")
            return
        fact_str = " ".join(args)
        parsed = self.parse_prolog_fact(fact_str)
        self.prolog.add_fact(parsed)

    def cmd_prule(self, args):
        """Kural ekler: PRULE grandparent(X, Y) :- parent(X, Z), parent(Z, Y)"""
        if not args:
            print("PRULE kullanım hatası.")
            return
        rule_str = " ".join(args)
        head, body = self.parse_prolog_rule(rule_str)
        self.prolog.add_rule(head, body)

    def cmd_pquery(self, args):
        """Sorgu yapar: PQUERY parent(john, mary)"""
        if not args:
            print("PQUERY kullanım hatası.")
            return
        query_str = " ".join(args)
        parsed = self.parse_prolog_fact(query_str)
        self.prolog.query(parsed)

    def cmd_passert(self, args):
        """Yeni gerçek ekler"""
        self.cmd_pfact(args)

    def cmd_pretract(self, args):
        """Gerçeği siler"""
        if not args:
            print("PRETRACT kullanım hatası.")
            return
        fact_str = " ".join(args)
        parsed = self.parse_prolog_fact(fact_str)
        if parsed in self.prolog.facts:
            self.prolog.facts.remove(parsed)
            print(f"FACT kaldırıldı: {parsed}")
        else:
            print(f"FACT bulunamadı: {parsed}")

    def cmd_pclear(self, args):
        """Tüm gerçekleri ve kuralları temizler"""
        self.prolog.clear()

    def cmd_pbacktrace(self, args):
        """Geri izleme başlatır"""
        self.prolog.backtrace_enabled = True
        print("Geri izleme açıldı.")

    def cmd_pdump(self, args):
        """Tüm gerçekleri ve kuralları döker"""
        print("--- Gerçekler ---")
        for fact in self.prolog.facts:
            print(f"  {fact}")
        print("--- Kurallar ---")
        for head, body in self.prolog.rules:
            print(f"  {head} :- {body}")

    def cmd_pcount(self, args):
        """Kaç gerçek ve kural olduğunu gösterir"""
        print(f"FACTS: {len(self.prolog.facts)}")
        print(f"RULES: {len(self.prolog.rules)}")

    def cmd_pexists(self, args):
        """Verilen bir gerçek var mı diye kontrol eder"""
        if not args:
            print("PEXISTS kullanım hatası.")
            return
        fact_str = " ".join(args)
        parsed = self.parse_prolog_fact(fact_str)
        exists = parsed in self.prolog.facts
        print("Evet" if exists else "Hayır")

    def cmd_pforall(self, args):
        """Tüm gerçekler bir şartı sağlıyor mu kontrol eder"""
        if not args:
            print("PFORALL kullanım hatası.")
            return
        fact_str = " ".join(args)
        parsed = self.parse_prolog_fact(fact_str)
        all_match = all(f == parsed for f in self.prolog.facts)
        print("Tüm kayıtlar uyuyor." if all_match else "Uymayan kayıtlar var.")

    # --- Yardımcı Fonksiyonlar ---

    def parse_prolog_fact(self, fact_str):
        """parent(john, mary) gibi string'i tuple yapar"""
        name, args = fact_str.split("(", 1)
        args = args.rstrip(")")
        return (name.strip(), *(arg.strip() for arg in args.split(",")))

    def parse_prolog_rule(self, rule_str):
        """grandparent(X, Y) :- parent(X, Z), parent(Z, Y) gibi stringi parçalara ayırır"""
        head, body = rule_str.split(":-")
        head = self.parse_prolog_fact(head.strip())
        body_parts = body.split(",")
        body_facts = [self.parse_prolog_fact(part.strip()) for part in body_parts]
        return head, body_facts
    # --- PROLOG V3 Motoru ---
class PrologEngine:
    def __init__(self):
        self.facts = []
        self.rules = []
        self.backtrace_enabled = False

    def add_fact(self, fact):
        self.facts.append(fact)

    def add_rule(self, head, body):
        self.rules.append((head, body))

    def query(self, goal):
        self.failed_paths = []
        result = self.match_goal(goal)
        if result:
            print(f"Evet: {goal}")
        else:
            print(f"Hayır: {goal}")
            if self.backtrace_enabled:
                self.print_backtrace()
        return result

    def match_goal(self, goal):
        if isinstance(goal, tuple) and goal[0].upper() in ("PAND", "AND"):
            return all(self.match_goal(subgoal) for subgoal in goal[1:])
        if isinstance(goal, tuple) and goal[0].upper() in ("POR", "OR"):
            return any(self.match_goal(subgoal) for subgoal in goal[1:])
        if isinstance(goal, tuple) and goal[0].upper() in ("PNOT", "NOT"):
            return not self.match_goal(goal[1])
        if isinstance(goal, tuple) and goal[0].upper() in ("PXOR", "XOR"):
            return sum(self.match_goal(subgoal) for subgoal in goal[1:]) == 1
        if isinstance(goal, tuple) and goal[0].upper() in ("PIMP", "IMP"):
            return not self.match_goal(goal[1]) or self.match_goal(goal[2])
        if isinstance(goal, tuple) and goal[0].upper() in ("PBICOND", "BI-COND"):
            return self.match_goal(("PIMP", goal[1], goal[2])) and self.match_goal(("PIMP", goal[2], goal[1]))
        else:
            return self.unify_goal(goal)

    def unify_goal(self, goal):
        for fact in self.facts:
            bindings = {}
            if self.unify(goal, fact, bindings):
                return True
        for head, body in self.rules:
            bindings = {}
            if self.unify(goal, head, bindings):
                if all(self.match_goal(self.apply_bindings(subgoal, bindings)) for subgoal in body):
                    return True
        self.failed_paths.append(goal)
        return False

    def unify(self, term1, term2, bindings):
        if isinstance(term1, str) and term1.startswith("#"):
            bindings[term1] = term2
            return True
        if isinstance(term2, str) and term2.startswith("#"):
            bindings[term2] = term1
            return True
        if isinstance(term1, str) and isinstance(term2, str):
            return term1 == term2
        if isinstance(term1, tuple) and isinstance(term2, tuple):
            if len(term1) != len(term2):
                return False
            return all(self.unify(t1, t2, bindings) for t1, t2 in zip(term1, term2))
        return False

    def apply_bindings(self, goal, bindings):
        if isinstance(goal, tuple):
            return tuple(self.apply_bindings(g, bindings) for g in goal)
        if goal in bindings:
            return bindings[goal]
        return goal

    def clear(self):
        self.facts.clear()
        self.rules.clear()

    def print_backtrace(self):
        print("Geri İzleme:")
        for step in self.failed_paths:
            print(f"  Başarısız: {step}")

# pdsXv13u Interpreter içine PrologEngine Entegrasyonu
class pdsXv13uInterpreter(pdsXv12Final):
    def __init__(self):
        super().__init__()
        self.prolog = PrologEngine()
    # --- Prolog Komutları ---
    def p_assert(self, fact):
        self.prolog.add_fact(fact)

    def p_rule(self, head, body):
        self.prolog.add_rule(head, body)

    def p_query(self, goal):
        return self.prolog.query(goal)

    def p_clear(self):
        self.prolog.clear()

    def p_backtrace(self, enabled=True):
        self.prolog.backtrace_enabled = enabled

    def p_dump(self):
        print("Gerçekler (Facts):")
        for fact in self.prolog.facts:
            print(f"  {fact}")
        print("Kurallar (Rules):")
        for head, body in self.prolog.rules:
            print(f"  {head} :- {body}")

    def p_count(self, goal):
        count = 0
        for fact in self.prolog.facts:
            bindings = {}
            if self.prolog.unify(goal, fact, bindings):
                count += 1
        print(f"Eşleşen sayısı: {count}")
        return count

    def p_exists(self, goal):
        return any(self.prolog.unify(goal, fact, {}) for fact in self.prolog.facts)

    def p_forall(self, goal):
        return all(self.prolog.unify(goal, fact, {}) for fact in self.prolog.facts)

    # Prolog'da yeni sözdizimi destekleri
    def normalize_prolog_variables(self, expr):
        """?degisken → #degisken çevir"""
        if isinstance(expr, str) and expr.startswith("?"):
            return "#" + expr[1:]
        if isinstance(expr, tuple):
            return tuple(self.normalize_prolog_variables(e) for e in expr)
        return expr

    def prolog_eval(self, command, *args):
        """Prolog komutlarını çalıştır"""
        cmd = command.lower()
        if cmd == "assert":
            fact = self.normalize_prolog_variables(args[0])
            self.p_assert(fact)
        elif cmd == "rule":
            head = self.normalize_prolog_variables(args[0])
            body = [self.normalize_prolog_variables(a) for a in args[1:]]
            self.p_rule(head, body)
        elif cmd == "query":
            goal = self.normalize_prolog_variables(args[0])
            return self.p_query(goal)
        elif cmd == "clear":
            self.p_clear()
        elif cmd == "backtrace":
            self.p_backtrace(args[0])
        elif cmd == "dump":
            self.p_dump()
        elif cmd == "count":
            goal = self.normalize_prolog_variables(args[0])
            return self.p_count(goal)
        elif cmd == "exists":
            goal = self.normalize_prolog_variables(args[0])
            return self.p_exists(goal)
        elif cmd == "forall":
            goal = self.normalize_prolog_variables(args[0])
            return self.p_forall(goal)
        else:
            raise Exception(f"Tanımsız Prolog komutu: {command}")
    # --- INLINE Kod Sistemleri ---
    def execute_inline(self, code_block, code_type="REPLY"):
        """INLINE kodları REPLY, ASM veya C olarak çalıştırır."""
        if code_type == "REPLY":
            self.execute_reply_block(code_block)
        elif code_type == "ASM":
            self.execute_asm_block(code_block)
        elif code_type == "C":
            self.execute_c_block(code_block)
        else:
            raise Exception(f"Bilinmeyen INLINE kod tipi: {code_type}")

    def execute_reply_block(self, code_block):
        """INLINE REPLY bloğunu çalıştırır."""
        print(f"[INLINE REPLY Başladı]")
        for line in code_block.splitlines():
            line = line.strip()
            if line:
                self.execute_command(line)
        print(f"[INLINE REPLY Bitti]")

    def execute_asm_block(self, code_block):
        """INLINE ASM bloğunu çalıştırır (taklit)."""
        print(f"[INLINE ASM Başladı]")
        for line in code_block.splitlines():
            line = line.strip()
            if line:
                print(f"ASM > {line}")
        print(f"[INLINE ASM Bitti]")

    def execute_c_block(self, code_block):
        """INLINE C bloğunu dosyaya yazıp gcc ile derleyip çalıştırır."""
        import subprocess
        c_filename = "inline_temp.c"
        exe_filename = "inline_temp.exe"
        with open(c_filename, "w", encoding="utf-8") as f:
            f.write(code_block)
        print(f"[INLINE C Derleniyor...]")
        try:
            subprocess.check_call(["gcc", c_filename, "-o", exe_filename])
            print(f"[INLINE C Çalıştırılıyor...]")
            subprocess.check_call([exe_filename])
        except subprocess.CalledProcessError as e:
            print(f"INLINE C Hatası: {e}")
        finally:
            if os.path.exists(c_filename):
                os.remove(c_filename)
            if os.path.exists(exe_filename):
                os.remove(exe_filename)

    # --- TREE Veri Yapısı ---
    class TreeNode:
        def __init__(self, value):
            self.value = value
            self.children = []

    def tree_add_child(self, parent_node, child_node):
        parent_node.children.append(child_node)

    def tree_traverse(self, node):
        if node is None:
            return
        print(node.value)
        for child in node.children:
            self.tree_traverse(child)
    # --- GRAPH Veri Yapısı ---
    class Graph:
        def __init__(self):
            self.nodes = {}
        
        def add_node(self, node):
            if node not in self.nodes:
                self.nodes[node] = []

        def add_edge(self, from_node, to_node):
            if from_node not in self.nodes:
                self.add_node(from_node)
            if to_node not in self.nodes:
                self.add_node(to_node)
            self.nodes[from_node].append(to_node)

        def traverse(self, start_node):
            visited = set()
            self._dfs(start_node, visited)

        def _dfs(self, node, visited):
            if node not in visited:
                print(node)
                visited.add(node)
                for neighbor in self.nodes.get(node, []):
                    self._dfs(neighbor, visited)

    # --- PROLOG V3 Başlangıcı ---
    class PrologV3:
        def __init__(self):
            self.facts = []
            self.rules = []
            self.variables = {}

        def add_fact(self, fact):
            self.facts.append(fact)

        def add_rule(self, head, body):
            self.rules.append((head, body))

        def clear(self):
            self.facts.clear()
            self.rules.clear()

        def query(self, goal):
            """Bir hedefi sorgular ve çözüm varsa değişkenleri gösterir."""
            self.variables = {}
            result = self._match(goal)
            if result:
                self._print_variables()
                print(f"Evet: {goal}")
            else:
                print(f"Hayır: {goal}")
            return result

        def _match(self, goal):
            if isinstance(goal, tuple) and goal[0] == "AND":
                return all(self._match(subgoal) for subgoal in goal[1:])
            elif isinstance(goal, tuple) and goal[0] == "OR":
                return any(self._match(subgoal) for subgoal in goal[1:])
            elif isinstance(goal, tuple) and goal[0] == "NOT":
                return not self._match(goal[1])
            elif isinstance(goal, tuple) and goal[0] == "XOR":
                return sum(self._match(subgoal) for subgoal in goal[1:]) == 1
            elif isinstance(goal, tuple) and goal[0] == "IMP":
                return not self._match(goal[1]) or self._match(goal[2])
            elif isinstance(goal, tuple) and goal[0] == "BI-COND":
                return self._match(("IMP", goal[1], goal[2])) and self._match(("IMP", goal[2], goal[1]))
            else:
                return self._unify(goal)

        def _unify(self, goal):
            for fact in self.facts:
                self.variables.clear()
                if self._unify_term(goal, fact):
                    return True
            for head, body in self.rules:
                self.variables.clear()
                if self._unify_term(goal, head):
                    if all(self._match(subgoal) for subgoal in body):
                        return True
            return False

        def _unify_term(self, term1, term2):
            if isinstance(term1, str) and term1.startswith("#"):
                self.variables[term1] = term2
                return True
            if isinstance(term2, str) and term2.startswith("#"):
                self.variables[term2] = term1
                return True
            if isinstance(term1, str) and isinstance(term2, str):
                return term1 == term2
            if isinstance(term1, tuple) and isinstance(term2, tuple):
                if len(term1) != len(term2):
                    return False
                return all(self._unify_term(t1, t2) for t1, t2 in zip(term1, term2))
            return False

        def _print_variables(self):
            for var, value in self.variables.items():
                print(f"{var} = {value}")
    # --- Prolog V3 Genişletilmiş Komutlar ---
    class PrologV3Extended(PrologV3):
        def __init__(self):
            super().__init__()

        def p_assert(self, fact):
            self.add_fact(fact)

        def p_retract(self, fact):
            if fact in self.facts:
                self.facts.remove(fact)

        def p_clear(self):
            self.clear()

        def p_count(self, predicate_name):
            return sum(1 for fact in self.facts if isinstance(fact, tuple) and fact[0] == predicate_name)

        def p_exists(self, predicate_name):
            return any(isinstance(fact, tuple) and fact[0] == predicate_name for fact in self.facts)

        def p_forall(self, predicate_name, condition_func):
            return all(condition_func(fact) for fact in self.facts if isinstance(fact, tuple) and fact[0] == predicate_name)

        def p_backtrace(self, goal):
            """Geri izleme mekanizması."""
            self.variables = {}
            result, path = self._match_backtrace(goal, [])
            if result:
                for step in path:
                    print(f"Adım: {step}")
                print(f"Evet: {goal}")
            else:
                print(f"Hayır: {goal}")
            return result

        def _match_backtrace(self, goal, path):
            if isinstance(goal, tuple) and goal[0] == "AND":
                for subgoal in goal[1:]:
                    success, new_path = self._match_backtrace(subgoal, path)
                    if not success:
                        return False, new_path
                    path = new_path
                return True, path
            elif isinstance(goal, tuple) and goal[0] == "OR":
                for subgoal in goal[1:]:
                    success, new_path = self._match_backtrace(subgoal, path)
                    if success:
                        return True, new_path
                return False, path
            elif isinstance(goal, tuple) and goal[0] == "NOT":
                success, _ = self._match_backtrace(goal[1], path)
                return not success, path
            elif isinstance(goal, tuple) and goal[0] == "XOR":
                successes = [self._match_backtrace(subgoal, path)[0] for subgoal in goal[1:]]
                return sum(successes) == 1, path
            elif isinstance(goal, tuple) and goal[0] == "IMP":
                success1, _ = self._match_backtrace(goal[1], path)
                success2, _ = self._match_backtrace(goal[2], path)
                return not success1 or success2, path
            elif isinstance(goal, tuple) and goal[0] == "BI-COND":
                success1, _ = self._match_backtrace(goal[1], path)
                success2, _ = self._match_backtrace(goal[2], path)
                return (success1 and success2) or (not success1 and not success2), path
            else:
                if self._unify(goal):
                    path.append(goal)
                    return True, path
                else:
                    return False, path

        def p_dump_facts_rules(self):
            print("=== Gerçekler (Facts) ===")
            for fact in self.facts:
                print(f"Fact: {fact}")
            print("=== Kurallar (Rules) ===")
            for head, body in self.rules:
                print(f"Rule: {head} :- {body}")
    # --- pdsXv13u Interpreter'e PrologV3Extended Entegrasyonu ---
    class pdsXv13uFinal(pdsXv13u):
        def __init__(self):
            super().__init__()
            self.prolog = PrologV3Extended()

        def execute_prolog_command(self, command, *args):
            cmd = command.upper()
            if cmd == "PFACT":
                self.prolog.add_fact(args[0])
            elif cmd == "PRULE":
                self.prolog.add_rule(args[0], args[1])
            elif cmd == "PQUERY":
                return self.prolog.query(args[0])
            elif cmd == "PASSERT":
                self.prolog.p_assert(args[0])
            elif cmd == "PRETRACT":
                self.prolog.p_retract(args[0])
            elif cmd == "PCLEAR":
                self.prolog.p_clear()
            elif cmd == "PBACKTRACE":
                return self.prolog.p_backtrace(args[0])
            elif cmd == "PDUMP":
                return self.prolog.p_dump_facts_rules()
            elif cmd == "PCOUNT":
                return self.prolog.p_count(args[0])
            elif cmd == "PEXISTS":
                return self.prolog.p_exists(args[0])
            elif cmd == "PFORALL":
                return self.prolog.p_forall(args[0], args[1])
            else:
                raise Exception(f"Bilinmeyen Prolog komutu: {command}")

        def repl(self):
            """Komut satırı etkileşimli çalışma modu."""
            print("pdsXv13u Ultimate Interpreter (REPL Modu)")
            print("Çıkmak için CTRL+C")
            try:
                while True:
                    line = input(">>> ").strip()
                    if not line:
                        continue
                    if line.upper().startswith("P"):
                        parts = line.split(maxsplit=1)
                        cmd = parts[0]
                        args = eval(parts[1]) if len(parts) > 1 else ()
                        if not isinstance(args, tuple):
                            args = (args,)
                        result = self.execute_prolog_command(cmd, *args)
                        if result is not None:
                            print(result)
                    else:
                        self.execute_command(line)
            except (EOFError, KeyboardInterrupt):
                print("\nÇıkılıyor...")

        def save_full_state(self, filename="pdsx_fullstate.json"):
            """Interpreterın tam durumunu kaydeder."""
            state = {
                "globals": self.global_vars,
                "pipes": self.pipe_storage,
                "databases": list(self.databases.keys()),
                "prolog_facts": self.prolog.facts,
                "prolog_rules": self.prolog.rules,
                "events": {eid: (e.trigger.__name__, e.action.__name__, e.priority, e.enabled) for eid, e in self.event_manager.events.items()},
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)

        def load_full_state(self, filename="pdsx_fullstate.json"):
            """Interpreterın tam durumunu yükler."""
            with open(filename, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.global_vars.update(state.get("globals", {}))
            self.pipe_storage.update(state.get("pipes", {}))
            for name in state.get("databases", []):
                self.open_database(name)
            self.prolog.facts = state.get("prolog_facts", [])
            self.prolog.rules = state.get("prolog_rules", [])
       # --- Yardımcı Fonksiyonlar (Ekstra) ---
    def parse_params(params_str):
        """Parametreleri ayrıştırır."""
        if not params_str:
            return []
        return [param.strip() for param in params_str.split(",") if param.strip()]

    def safe_eval(expr, interpreter):
        """Interpreter içinde güvenli ifade değerlendirme."""
        try:
            return interpreter.evaluate_expression(expr)
        except Exception as e:
            print(f"Değerlendirme hatası: {expr} -> {e}")
            return None

    # Ekstra Hızlı Fonksiyonlar
    def flatten(lst):
        """Listeyi düzleştirir."""
        for item in lst:
            if isinstance(item, list):
                yield from flatten(item)
            else:
                yield item

    def deep_copy(obj):
        """Nesnenin derin kopyasını oluşturur."""
        import copy
        return copy.deepcopy(obj)

    def is_iterable(obj):
        """Bir nesnenin iterable olup olmadığını kontrol eder."""
        try:
            iter(obj)
            return True
        except TypeError:
            return False

    # Event Helper Functions
    def event_trigger_true():
        return True

    def event_action_nop():
        pass
    # --- Zengin Matematik ve Mantık Fonksiyonları (LibXCore Extension) ---
    def sigmoid(x):
        """Sigmoid fonksiyonu."""
        return 1 / (1 + math.exp(-x))

    def relu(x):
        """ReLU fonksiyonu."""
        return max(0, x)

    def tanh(x):
        """Tanh fonksiyonu."""
        return math.tanh(x)

    def softmax(lst):
        """Softmax fonksiyonu."""
        exp_vals = [math.exp(x) for x in lst]
        total = sum(exp_vals)
        return [x / total for x in exp_vals]

    def logical_and(a, b):
        return a and b

    def logical_or(a, b):
        return a or b

    def logical_not(a):
        return not a

    def logical_xor(a, b):
        return bool(a) ^ bool(b)

    def logical_imp(a, b):
        return (not a) or b

    def logical_bicond(a, b):
        return a == b

    # Matematik Fonksiyonları libxcore ek
    def sigmoid(self, x):
    return 1 / (1 + math.exp(-x))

def logistic(self, x, L=1, k=1, x0=0):
    return L / (1 + math.exp(-k*(x - x0)))

def exp(self, x):
    return math.exp(x)

def pow(self, base, exponent):
    return math.pow(base, exponent)

def clamp(self, value, min_val, max_val):
    return max(min_val, min(value, max_val))

# Dosya Yönetimi ek
def copytree(self, src, dst):
    shutil.copytree(src, dst)

def remove_dir(self, path):
    shutil.rmtree(path, ignore_errors=True)

def touch(self, path):
    with open(path, 'a'):
        os.utime(path, None)

def exists_dir(self, path):
    return os.path.isdir(path)
# json araclari ek
 def merge_json(self, j1, j2):
    return {**j1, **j2}

def diff_json(self, j1, j2):
    return {k: j1[k] for k in j1 if k not in j2 or j1[k] != j2[k]}
# PDF ve Web araclari ek
def pdf_metadata(self, file_path):
    with pdfplumber.open(file_path) as pdf:
        return pdf.metadata

def pdf_image_extract(self, file_path):
    with pdfplumber.open(file_path) as pdf:
        return [page.images for page in pdf.pages]

def web_post(self, url, data):
    response = requests.post(url, json=data)
    return response.text

def web_headers(self, url):
    response = requests.get(url)
    return dict(response.headers)
# sistem bilgileri ek

def cpu_percent(self):
    return psutil.cpu_percent(interval=1)

def ram_usage(self):
    mem = psutil.virtual_memory()
    return {"used": mem.used, "available": mem.available, "total": mem.total}

def disk_info(self, path="/"):
    usage = shutil.disk_usage(path)
    return {"total": usage.total, "used": usage.used, "free": usage.free}
# Zamanlayıcı ve Async İşlemleri ek
def schedule(self, delay_sec, func):
    threading.Timer(delay_sec, func).start()

def delayed_exec(self, delay_sec, codeblock):
    def wrapper():
        exec(codeblock, {}, {})
    threading.Timer(delay_sec, wrapper).start()

def cron_expr_support(self, expr):
    return f"Simülasyon: '{expr}' ifadesi destekleniyor gibi işleniyor (gerçek cron yok)."

# Dil Algılama ve Çeviri ek
   def detect_language(self, text):
    if "und" in text:
        return "unknown"
    return "tr" if "bir" in text.lower() else "en"

def translate(self, text, to_lang="en"):
    translations = {"merhaba": "hello", "dünya": "world"}
    return " ".join([translations.get(word.lower(), word) for word in text.split()])

def lang_map(self):
    return {"en": "English", "tr": "Türkçe", "de": "Deutsch", "fr": "Français"}
# String & Metin İşlemleri ek

   def to_upper(self, s):
    return s.upper()

def to_lower(self, s):
    return s.lower()

def remove_punctuation(self, s):
    return re.sub(r'[^\w\s]', '', s)

def is_palindrome(self, s):
    s_clean = re.sub(r'[\W_]', '', s.lower())
    return s_clean == s_clean[::-1]

def count_words(self, s):
    return len(s.split())
#  Hata Kontrol ve Debug Yardımcıları

   def is_number(self, val):
    try:
        float(val)
        return True
    except:
        return False

def try_parse_int(self, val, default=0):
    try:
        return int(val)
    except:
        return default

def trace_last_exception(self):
    return traceback.format_exc()

def check_nulls(self, data):
    return [i for i, v in enumerate(data) if v is None]

# json ve xml islemleri ek

def json_pretty(self, obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)

def json_keys(self, obj):
    return list(obj.keys()) if isinstance(obj, dict) else []

def xml_escape(self, text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

# kolleksiyon islemleri ek
 def flatten(self, nested_list):
    return [item for sublist in nested_list for item in sublist]

def unique(self, items):
    return list(set(items))

def chunk(self, lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]

def group_by(self, iterable, key_func):
    grouped = defaultdict(list)
    for item in iterable:
        grouped[key_func(item)].append(item)
    return dict(grouped)
# gelismis zaman islemleri ek
def now_iso(self):
    return datetime.now().isoformat()

def timestamp(self):
    return int(time.time())

def time_diff_seconds(self, t1, t2):
    return abs((t2 - t1).total_seconds())

#rastgelelik ve simulasyon islemleri ek
def shuffle(self, items):
    items_copy = items[:]
    random.shuffle(items_copy)
    return items_copy

def roll_dice(self, sides=6):
    return random.randint(1, sides)

def simulate_coin_flip(self):
    return random.choice(["heads", "tails"])

# nlp islemleri ek
def tokenize_words(self, text):
    return re.findall(r'\b\w+\b', text.lower())

def word_freq(self, text):
    tokens = self.tokenize_words(text)
    freq = defaultdict(int)
    for word in tokens:
        freq[word] += 1
    return dict(freq)

def most_common_words(self, text, n=5):
    freq = self.word_freq(text)
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]

def remove_stopwords(self, tokens, stopwords):
    return [word for word in tokens if word not in stopwords]
# terminal yardimci fonksiyonler ek
def run_shell_command(self, cmd):
    return subprocess.getoutput(cmd)

def list_processes(self):
    return [p.info for p in psutil.process_iter(attrs=['pid', 'name', 'status'])]

def get_cpu_usage(self):
    return psutil.cpu_percent(interval=1)

def get_disk_usage(self, path="/"):
    usage = shutil.disk_usage(path)
    return {"total": usage.total, "used": usage.used, "free": usage.free}

#  Python İntrospection/Debug İşlemleri

def list_class_methods(self, cls):
    return [func for func in dir(cls) if callable(getattr(cls, func)) and not func.startswith("__")]

def list_variables(self):
    return list(self.interpreter.current_scope().keys())

def object_type(self, obj):
    return type(obj).__name__
#nlp profosyonel
    def nlp_lower(self, text):
    return text.lower()

def nlp_remove_punctuation(self, text):
    import string
    return text.translate(str.maketrans('', '', string.punctuation))

def nlp_tokenize(self, text):
    import re
    return re.findall(r'\b\w+\b', text)

def nlp_remove_stopwords(self, tokens, lang='english'):
    from nltk.corpus import stopwords
    return [t for t in tokens if t.lower() not in stopwords.words(lang)]

def nlp_stem(self, tokens, lang='english'):
    from nltk.stem import PorterStemmer, SnowballStemmer
    stemmer = PorterStemmer() if lang == 'english' else SnowballStemmer(lang)
    return [stemmer.stem(t) for t in tokens]

def nlp_lemmatize(self, tokens, lang='en'):
    import spacy
    nlp = spacy.load('en_core_web_sm' if lang == 'en' else 'xx_ent_wiki_sm')
    doc = nlp(" ".join(tokens))
    return [token.lemma_ for token in doc]

def nlp_sentiment(self, text):
    from textblob import TextBlob
    blob = TextBlob(text)
    return {"polarity": blob.sentiment.polarity, "subjectivity": blob.sentiment.subjectivity}

def nlp_language(self, text):
    from langdetect import detect
    return detect(text)
def nlp_sentence_split(self, text):
    import nltk
    nltk.download('punkt', quiet=True)
    return nltk.sent_tokenize(text)

def nlp_word_count(self, text):
    return len(self.nlp_tokenize(text))

def nlp_sentence_count(self, text):
    return len(self.nlp_sentence_split(text))

def nlp_avg_word_length(self, text):
    tokens = self.nlp_tokenize(text)
    return sum(len(w) for w in tokens) / len(tokens) if tokens else 0
def nlp_ngrams(self, tokens, n=2):
    return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def nlp_tfidf(self, corpus):
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    return X.toarray(), vectorizer.get_feature_names_out()
def nlp_ner(self, text, lang='en'):
    import spacy
    nlp = spacy.load('en_core_web_sm' if lang == 'en' else 'xx_ent_wiki_sm')
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def execute_line(self, line):
    line = line.strip()
    if not line or line.startswith("'") or line.startswith("#"):
        return  # Yorum satırı

    tokens = line.split()
    if not tokens:
        return

    cmd = tokens[0].upper()
    args = tokens[1:]

    # Yardımcılar
    def arg_str(idx): return " ".join(args[idx:]) if idx < len(args) else ""

    try:
        if cmd == "PRINT":
            print(self.evaluate_expression(arg_str(0)))

        elif cmd == "LET":
            var, expr = line[4:].split("=", 1)
            self.set_variable(var.strip(), self.evaluate_expression(expr.strip()))

        elif cmd == "GOTO":
            self.jump_to_label(args[0])

        elif cmd == "GOSUB":
            self.call_subroutine(args[0])

        elif cmd == "RETURN":
            self.return_from_subroutine()

        elif cmd == "SAVE":
            filename = args[0]
            compressed = ".zip" in filename or ".gz" in filename
            self.save_program(filename, compressed)

        elif cmd == "LOAD":
            filename = args[0]
            compressed = ".zip" in filename or ".gz" in filename
            self.load_program(filename, compressed)

        elif cmd == "PIPE":
            if args[0].upper() == "START":
                self.start_pipeline(args[1] if len(args) > 1 else None)
            elif args[0].upper() == "END":
                self.end_pipeline()
            elif args[0].upper() == "SAVE":
                self.save_pipeline(args[1], args[2], compressed=".zip" in args[2])
            elif args[0].upper() == "LOAD":
                varname = self.load_pipeline(args[1], compressed=".zip" in args[1])
                print(f"PIPE yüklenip {varname} olarak atandı")

        elif cmd == "SQL":
            if args[0].upper() == "OPEN":
                self.open_database(args[1], args[2] if len(args) > 2 else ":memory:")
            elif args[0].upper() == "CLOSE":
                self.close_database(args[1])
            elif args[0].upper() == "EXEC":
                self.exec_sql(" ".join(args[1:]))
            elif args[0].upper() == "QUERY":
                result = self.query_sql(" ".join(args[1:]))
                print(result)

        elif cmd == "ON":
            if args[0].upper() == "GOTO":
                self.on_error_goto(args[1])
            elif args[0].upper() == "GOSUB":
                self.on_error_gosub(args[1])
            elif args[0].upper() == "ERROR":
                if args[1].upper() == "RESUME" and args[2].upper() == "NEXT":
                    self.resume_on_error = True

        elif cmd == "TRY":
            self.try_stack.append(self.program_counter)

        elif cmd == "CATCH":
            self.handle_catch()

        elif cmd == "FINALLY":
            self.execute_finally()

        elif cmd == "INLINE":
            self.handle_inline_block(args)

        elif cmd == "ENUM" or cmd == "TUPLE" or cmd == "STACK" or cmd == "QUEUE":
            self.define_data_structure(cmd, args)

        elif cmd == "CLASS":
            self.define_class(args)

        elif cmd == "STRUCT" or cmd == "UNION":
            self.define_struct_union(cmd, args)

        elif cmd == "EVENT":
            self.define_event_from_line(args)

        elif cmd.startswith("P") and cmd[1:] in ("QUERY", "ASSERT", "RETRACT", "CLEAR", "FACT", "RULE",
                                                 "BACKTRACE", "DUMP", "COUNT", "EXISTS", "FORALL"):
            self.handle_prolog_command(cmd[1:], args)

        elif cmd.upper() == "HELP":
            self.show_help(args[0] if args else "")

        elif cmd.upper() == "EXIT":
            print("Programdan çıkılıyor...")
            sys.exit(0)

        else:
            # Fonksiyon veya modül çağrısı olabilir
            if hasattr(self.core, cmd.lower()):
                method = getattr(self.core, cmd.lower())
                result = method(*[self.evaluate_expression(a) for a in args])
                if result is not None:
                    print(result)
            elif cmd in self.user_functions:
                self.call_function(cmd, args)
            else:
                raise PdsXException(f"Bilinmeyen komut veya fonksiyon: {cmd}")

    except Exception as e:
        self.handle_execution_error(e, line)

   
   
   
   
   
   
   
   
   # --- Ana Başlatıcı (Yeni) ---
    def main():
        parser = argparse.ArgumentParser(description='pdsXv13u Ultimate Interpreter')
        parser.add_argument('file', nargs='?', help='Çalıştırılacak dosya')
        parser.add_argument('-i', '--interactive', action='store_true', help='Etkileşimli mod başlatır')
        parser.add_argument('--save-state', action='store_true', help='Çıkışta tam state kaydet')
        parser.add_argument('--load-state', action='store_true', help='Başlangıçta tam state yükle')
        parser.add_argument('--lang', type=str, default='en', help='Dil seçimi: en / tr')
        parser.add_argument('--pipe', type=str, help='Başlangıçta yüklemek için bir pipeline dosyası')
        parser.add_argument('--db', type=str, help='Başlangıçta yüklemek için bir veritabanı dosyası')
        parser.add_argument('--event', type=str, help='Başlangıç event dosyası')
        args = parser.parse_args()

        interpreter = pdsXv13uFinal()

        # Dil ayarı
        lang_path = f"lang_{args.lang.lower()}.json"
        if os.path.exists(lang_path):
            try:
                with open(lang_path, "r", encoding="utf-8") as f:
                    lang_data = json.load(f)
                    interpreter.lang_data = lang_data
            except:
                print("Dil dosyası okunamadı!")

        # State yüklemesi
        if args.load_state:
            try:
                interpreter.load_full_state()
                print("[OK] Önceki tam state yüklendi.")
            except Exception as e:
                print(f"State yükleme hatası: {e}")

        # Pipe ve database yüklemesi
        if args.pipe:
            try:
                interpreter.load_pipeline(args.pipe)
                print(f"[OK] Pipe yüklendi: {args.pipe}")
            except Exception as e:
                print(f"Pipe yüklenemedi: {e}")
        if args.db:
            try:
                interpreter.open_database("autodb", args.db)
                print(f"[OK] Veritabanı açıldı: {args.db}")
            except Exception as e:
                print(f"Veritabanı açılamadı: {e}")

        if args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    code = f.read()
                interpreter.run(code)
            except Exception as e:
                print(f"Dosya çalıştırma hatası: {e}")

        if args.interactive or not args.file:
            interpreter.repl()

        if args.save_state:
            try:
                interpreter.save_full_state()
                print("[OK] Tam state kaydedildi.")
            except Exception as e:
                print(f"State kaydetme hatası: {e}")

    if __name__ == "__main__":
        main()
        
# pdsXv13u Ultimate Interpreter
# Başlangıç ve Temel Yapılar

import os
import sys
import math
import time
import json
import glob
import re
import shutil
import random
import socket
import struct
import logging
import ctypes
import threading
import asyncio
import sqlite3
import requests
import pdfplumber
import numpy as np
import pandas as pd
import psutil
import traceback
from types import SimpleNamespace
from datetime import datetime
from collections import defaultdict, namedtuple
from packaging import version
import subprocess
import importlib.metadata
import argparse

# Eksik kütüphane kontrolü
def install_missing_libraries():
    required = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'scipy': 'scipy',
        'psutil': 'psutil',
        'pdfplumber': 'pdfplumber',
        'bs4': 'beautifulsoup4',
        'requests': 'requests',
        'packaging': 'packaging'
    }
    installed = {pkg.metadata['Name'].lower() for pkg in importlib.metadata.distributions()}
    missing = [lib for lib, pkg in required.items() if lib not in installed]
    if missing:
        print(f"Eksik kütüphaneler yükleniyor: {missing}")
        for lib in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", required[lib]])
                print(f"{lib} kuruldu.")
            except subprocess.CalledProcessError:
                print(f"Hata: {lib} yüklenemedi, elle kurun.")

install_missing_libraries()

# Loglama
logging.basicConfig(filename='pdsxv13u_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Memory Manager
class MemoryManager:
    def __init__(self):
        self.heap = {}
        self.ref_counts = {}

    def allocate(self, size):
        ptr = id(bytearray(size))
        self.heap[ptr] = bytearray(size)
        self.ref_counts[ptr] = 1
        return ptr

    def release(self, ptr):
        if ptr in self.ref_counts:
            self.ref_counts[ptr] -= 1
            if self.ref_counts[ptr] == 0:
                del self.heap[ptr]
                del self.ref_counts[ptr]

    def dereference(self, ptr):
        return self.heap.get(ptr, None)

    def set_value(self, ptr, value):
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

# Exception Sınıfı
class PdsXException(Exception):
    pass

# LibXCore Sınıfı
class LibXCore:
    def __init__(self, interpreter=None):
        self.interpreter = interpreter
        self.default_encoding = "utf-8"
        self.supported_encodings = [
            "utf-8", "cp1254", "iso-8859-9", "ascii", "utf-16", "utf-32",
            "cp1252", "iso-8859-1", "windows-1250", "latin-9",
            "cp932", "gb2312", "gbk", "euc-kr", "cp1251", "iso-8859-5",
            "cp1256", "iso-8859-6", "cp874", "iso-8859-7", "cp1257", "iso-8859-8"
        ]
        self.pipes = {}
        self.pipe_id_counter = 0
        self.databases = {}

    def sum(self, iterable):
        return sum(iterable)

    def mean(self, iterable):
        return sum(iterable) / len(iterable) if iterable else 0

    def min(self, iterable):
        return min(iterable) if iterable else None

    def max(self, iterable):
        return max(iterable) if iterable else None

    def floor(self, x):
        return math.floor(x)

    def ceil(self, x):
        return math.ceil(x)

    def round(self, x, digits=0):
        return round(x, digits)

    def exists(self, path):
        return os.path.exists(path)

    def mkdir(self, path):
        os.makedirs(path, exist_ok=True)

    def copy_file(self, src, dst):
        shutil.copy(src, dst)

    def move_file(self, src, dst):
        shutil.move(src, dst)

    def delete_file(self, path):
        os.remove(path)

    def list_dir(self, path):
        return os.listdir(path)

    def listfile(self, path, pattern="*"):
        files = glob.glob(os.path.join(path, pattern))
        return [{"name": f, "compressed": f.endswith(".hz")} for f in files]

    def read_lines(self, path):
        with open(path, "r", encoding=self.default_encoding) as f:
            return f.readlines()

    def write_json(self, obj, path):
        with open(path, "w", encoding=self.default_encoding) as f:
            json.dump(obj, f)

    def read_json(self, path):
        with open(path, "r", encoding=self.default_encoding) as f:
            return json.load(f)

    def sleep(self, seconds):
        time.sleep(seconds)

    def random_int(self, min_val, max_val):
        return random.randint(min_val, max_val)

    def ping(self, host):
        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False

    def getenv(self, name):
        return os.getenv(name)

    def join_path(self, *parts):
        return os.path.join(*parts)

    def timer(self):
        return time.time()

    def time_now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def date_now(self):
        return datetime.now().strftime("%Y-%m-%d")

    def memory_usage(self):
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def cpu_count(self):
        return multiprocessing.cpu_count()

    def str(self, value):
        return str(value)

    def val(self, s):
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                raise Exception(f"Geçersiz değer: {s}")

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
        else:
            return "UNKNOWN"
# Struct Yapısı
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

# Union Yapısı
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

# ArrayInstance Yapısı
class ArrayInstance:
    def __init__(self, dimensions, element_type, type_table, types):
        self.dimensions = dimensions
        self.element_type = element_type
        self.type_table = type_table
        self.types = types
        self.data = {}

    def set_element(self, indices, value):
        self.data[tuple(indices)] = value

    def get_element(self, indices):
        return self.data.get(tuple(indices))

# Pointer Yapısı
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

# ClassInstance
class ClassInstance(StructInstance):
    def __init__(self, info, type_table, types, interpreter):
        super().__init__(info["fields"], type_table)
        self.methods = info["methods"]
        self.access = info["access"]
        self.interpreter = interpreter

    def call_method(self, method_name, args):
        method = self.methods.get(method_name)
        if not method:
            raise Exception(f"Metot bulunamadı: {method_name}")
        params = [param for param, _ in method["params"]]
        scope = dict(zip(params, args))
        self.interpreter.local_scopes.append(scope)
        old_program = self.interpreter.program
        old_counter = self.interpreter.program_counter
        self.interpreter.program = [(line, None) for line in method["body"]]
        self.interpreter.program_counter = 0
        self.interpreter.running = True
        try:
            while self.interpreter.running and self.interpreter.program_counter < len(self.interpreter.program):
                line, _ = self.interpreter.program[self.interpreter.program_counter]
                result = self.interpreter.execute_command(line)
                if result is not None:
                    self.interpreter.program_counter = result
                else:
                    self.interpreter.program_counter += 1
        finally:
            self.interpreter.program = old_program
            self.interpreter.program_counter = old_counter
            self.interpreter.local_scopes.pop()
# pdsXv13u.py
# Ultimate Professional Development System Interpreter
# Author: Mete Dinler (Fikir) + ChatGPT (Kodlama Yardımcısı)

import os
import sys
import time
import math
import glob
import json
import ast
import re
import shutil
import random
import socket
import struct
import logging
import ctypes
import threading
import asyncio
import sqlite3
import requests
import pdfplumber
import numpy as np
import pandas as pd
import psutil
from types import SimpleNamespace
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict, namedtuple
from packaging import version
from threading import Thread
import multiprocessing
import subprocess
import importlib.metadata
import argparse
from abc import ABC, abstractmethod

# --- Bağımlılık Yönetimi ---
def install_missing_libraries():
    """Gerekli bağımlılıkları kontrol eder ve eksik olanları yükler."""
    required = {
        'numpy': 'numpy', 'pandas': 'pandas', 'scipy': 'scipy',
        'psutil': 'psutil', 'pdfplumber': 'pdfplumber', 'bs4': 'beautifulsoup4',
        'requests': 'requests', 'packaging': 'packaging', 'spacy': 'spacy',
        'transformers': 'transformers'
    }
    installed = {pkg.metadata['Name'].lower() for pkg in importlib.metadata.distributions()}
    missing = [lib for lib, pkg in required.items() if lib not in installed]
    if missing:
        print(f"Eksik kütüphaneler yükleniyor: {missing}")
        for lib in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", required[lib]])
                print(f"{lib} kuruldu.")
            except subprocess.CalledProcessError:
                print(f"Hata: {lib} yüklenemedi, elle kurun.")

install_missing_libraries()

# --- Loglama Ayarları ---
logging.basicConfig(filename='interpreter_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(message)s')

# --- Yardımcı Veri Yapıları ---
class ClassDef:
    def __init__(self, name, parent=None, abstract=False, interfaces=None):
        self.name = name
        self.parent = parent
        self.abstract = abstract
        self.interfaces = interfaces if interfaces else []
        self.constructor = None
        self.destructor = None
        self.methods = {}
        self.static_vars = {}
        self.is_mixin = False

class InterfaceDef:
    def __init__(self, name):
        self.name = name
        self.methods = []

class MethodDef:
    def __init__(self, name, body, params, private=False):
        self.name = name
        self.body = body
        self.params = params
        self.private = private

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
# --- Yapılar (Struct ve Union) ---

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

# --- Pointer Yapısı ---

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
# --- LibXCore Ana Yardımcı Fonksiyonlar ---

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
        self.pipes = {}
        self.databases = {}
        self.pipe_id_counter = 0

    def omega(self, *args):
        params = args[:-1]
        expr = args[-1]
        return lambda *values: eval(expr, {p: v for p, v in zip(params, values)})

    def list_lib(self, lib_name):
        module = self.interpreter.modules.get(lib_name, {})
        return {"functions": list(module.get("functions", {}).keys()),
                "classes": list(module.get("classes", {}).keys())}

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
        return process.memory_info().rss / 1024 / 1024  # MB cinsinden

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

    def database_open(self, name, path=":memory:"):
        conn = sqlite3.connect(path)
        self.databases[name] = conn

    def database_close(self, name):
        if name in self.databases:
            self.databases[name].close()
            del self.databases[name]

    def database_execute(self, name, sql, params=None):
        if name not in self.databases:
            raise Exception("Database açık değil")
        cur = self.databases[name].cursor()
        cur.execute(sql, params or [])
        self.databases[name].commit()

    def database_query(self, name, sql, params=None):
        if name not in self.databases:
            raise Exception("Database açık değil")
        cur = self.databases[name].cursor()
        cur.execute(sql, params or [])
        return cur.fetchall()

    def save_pipe(self, pipe_id, file_path, compressed=False):
        if pipe_id not in self.pipes:
            raise Exception("Boru hattı bulunamadı")
        data = self.pipes[pipe_id]
        if compressed:
            import gzip
            with gzip.open(file_path, "wt", encoding="utf-8") as f:
                json.dump(data, f)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

    def load_pipe(self, file_path, compressed=False):
        if compressed:
            import gzip
            with gzip.open(file_path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        pipe_id = self.pipe_id_counter
        self.pipes[pipe_id] = data
        self.pipe_id_counter += 1
        return pipe_id
    # --- NLP Fonksiyonları ---
    def nlp_detect_language(self, text):
        """Metnin dilini otomatik algılar."""
        try:
            from langdetect import detect
            return detect(text)
        except:
            return "unknown"

    def nlp_named_entities(self, text, lang='en'):
        """İsim Varlık Tanıma (NER) yapar."""
        import spacy
        nlp = spacy.load('en_core_web_sm' if lang == 'en' else 'xx_ent_wiki_sm')
        doc = nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def nlp_summarize(self, text, max_length=150):
        """Metni özetler."""
        import transformers
        model_name = "facebook/bart-large-cnn"
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
        model = transformers.AutoModelForSeq2SeqLM.from_pretrained(model_name)
        inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=max_length, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
        return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    def nlp_extract_keywords(self, text, num_keywords=5):
        """Anahtar kelimeleri çıkartır."""
        from sklearn.feature_extraction.text import CountVectorizer
        import numpy as np
        vectorizer = CountVectorizer(stop_words='english')
        X = vectorizer.fit_transform([text])
        keywords = vectorizer.get_feature_names_out()
        counts = X.toarray().sum(axis=0)
        sorted_indices = np.argsort(-counts)
        return [keywords[i] for i in sorted_indices[:num_keywords]]

    def nlp_sentiment(self, text):
        """Duygu analizi yapar."""
        from transformers import pipeline
        sentiment_pipeline = pipeline("sentiment-analysis")
        result = sentiment_pipeline(text)
        return result

    def nlp_tokenize(self, text):
        """Metni kelimelere böler."""
        import nltk
        nltk.download('punkt', quiet=True)
        from nltk.tokenize import word_tokenize
        return word_tokenize(text)

    def nlp_pos_tags(self, text):
        """Metindeki kelimelerin dil bilgisini tespit eder (POS tagging)."""
        import nltk
        nltk.download('averaged_perceptron_tagger', quiet=True)
        tokens = self.nlp_tokenize(text)
        return nltk.pos_tag(tokens)

    def nlp_translation(self, text, src_lang="auto", dest_lang="en"):
        """Metni başka bir dile çevirir."""
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src=src_lang, dest=dest_lang)
        return result.text

    def nlp_text_clean(self, text):
        """Metni temizler (noktalama ve boşlukları kaldırır)."""
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def nlp_summary_stats(self, text):
        """Metnin istatistiklerini çıkarır."""
        words = self.nlp_tokenize(text)
        num_words = len(words)
        num_chars = len(text)
        avg_word_length = num_chars / num_words if num_words else 0
        return {
            "kelime_sayısı": num_words,
            "karakter_sayısı": num_chars,
            "ortalama_kelime_uzunluğu": avg_word_length
        }
    # --- INLINE C, ASM, REPLY Desteği ---
    def inline_c_save(self, code_lines, filename=None):
        """INLINE C kodlarını dosyaya kaydeder."""
        if not filename:
            filename = f"inline_{int(time.time())}.c"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(code_lines))
        return filename

    def inline_c_compile(self, c_file, exe_file=None):
        """C kodunu derler."""
        if not exe_file:
            exe_file = os.path.splitext(c_file)[0] + ".exe"
        compiler = shutil.which("gcc") or shutil.which("clang")
        if not compiler:
            raise Exception("GCC veya CLANG bulunamadı!")
        cmd = [compiler, c_file, "-o", exe_file]
        subprocess.run(cmd, check=True)
        return exe_file

    def inline_c_run(self, exe_file):
        """Derlenmiş C uygulamasını çalıştırır."""
        subprocess.run([exe_file])

    def inline_c_save_and_run(self, code_lines):
        """INLINE C: Kaydet, Derle, Çalıştır zinciri."""
        c_file = self.inline_c_save(code_lines)
        exe_file = self.inline_c_compile(c_file)
        self.inline_c_run(exe_file)

    def inline_asm_save(self, asm_lines, filename=None):
        """INLINE ASM kodlarını dosyaya kaydeder."""
        if not filename:
            filename = f"inline_{int(time.time())}.asm"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(asm_lines))
        return filename

    def inline_reply_save(self, reply_lines, filename=None):
        """INLINE REPLY kodlarını dosyaya kaydeder."""
        if not filename:
            filename = f"inline_reply_{int(time.time())}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(reply_lines))
        return filename

    def inline_reply_execute(self, reply_lines):
        """INLINE REPLY: BASIC kodu içine hızlı satır içi komutlar işler."""
        for line in reply_lines:
            self.execute_line(line)
import subprocess
import tempfile
import os
import shutil

class InlineManager:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.inline_counter = 0
        self.temp_dir = tempfile.mkdtemp(prefix="pdsx_inline_")

    def cleanup(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def generate_filename(self, ext):
        filename = os.path.join(self.temp_dir, f"inline_{self.inline_counter}.{ext}")
        self.inline_counter += 1
        return filename

    def inline_c(self, code_block, compile=True, run=True, save_as=None):
        """INLINE C işlemi"""
        filename = self.generate_filename("c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_block)

        if save_as:
            shutil.copy(filename, save_as)

        if compile:
            exe_file = filename.replace(".c", ".exe")
            try:
                subprocess.check_call(["gcc", filename, "-o", exe_file])
                if run:
                    result = subprocess.check_output([exe_file], text=True)
                    return result.strip()
            except subprocess.CalledProcessError as e:
                raise Exception(f"INLINE C derleme/çalıştırma hatası: {e}")
        return None

    def inline_asm(self, code_block, assembler="nasm", compile=True, run=True, save_as=None):
        """INLINE ASM işlemi"""
        filename = self.generate_filename("asm")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_block)

        if save_as:
            shutil.copy(filename, save_as)

        if compile:
            obj_file = filename.replace(".asm", ".obj")
            exe_file = filename.replace(".asm", ".exe")
            try:
                # Örneğin: nasm ile .obj üret, sonra linkle
                subprocess.check_call([assembler, "-f", "win32", filename, "-o", obj_file])
                subprocess.check_call(["gcc", obj_file, "-o", exe_file])
                if run:
                    result = subprocess.check_output([exe_file], text=True)
                    return result.strip()
            except subprocess.CalledProcessError as e:
                raise Exception(f"INLINE ASM derleme/çalıştırma hatası: {e}")
        return None

    def inline_reply(self, commands, run=True, save_as=None):
        """INLINE REPLY işlemi"""
        filename = self.generate_filename("txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(commands))

        if save_as:
            shutil.copy(filename, save_as)

        if run:
            try:
                for line in commands:
                    self.interpreter.execute_line(line)
            except Exception as e:
                raise Exception(f"INLINE REPLY çalıştırma hatası: {e}")

    def inline_header(self, header_code, save_as=None):
        """INLINE C Header dosyası oluşturur"""
        filename = self.generate_filename("h")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(header_code)

        if save_as:
            shutil.copy(filename, save_as)

        return filename
class pdsXv13u:
    def __init__(self):
        self.interpreter = self
        self.inline_manager = InlineManager(self)  # INLINEManager ekleniyor
        # Diğer başlatmalar (değişkenler, fonksiyonlar, vs.) buraya eklenir

    def execute_line(self, line):
        # Komutları buradan işlemeye başlıyoruz
        if line.startswith("INLINE_C"):
            # INLINE C komutu işleniyor
            code = line[len("INLINE_C"):].strip()
            result = self.inline_manager.inline_c(code)
            print(result)
        elif line.startswith("INLINE_ASM"):
            # INLINE ASM komutu işleniyor
            code = line[len("INLINE_ASM"):].strip()
            result = self.inline_manager.inline_asm(code)
            print(result)
        elif line.startswith("INLINE_REPLY"):
            # INLINE REPLY komutu işleniyor
            code_lines = line[len("INLINE_REPLY"):].strip().split(",")  # kod satırlarını alıyoruz
            self.inline_manager.inline_reply(code_lines)
        else:
            # Diğer komutları işleme mantığı
            pass

    def run(self, code):
        # INLINE işlemleri dışındaki tüm kodların çalıştırıldığı yer
        lines = code.split("\n")
        for line in lines:
            self.execute_line(line)
class PrologV3:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.facts = []
        self.rules = []
        self.backtrace_enabled = True

    def add_fact(self, fact):
        self.facts.append(fact)

    def add_rule(self, head, body):
        self.rules.append((head, body))

    def query(self, goal):
        """Hedef sorgulama"""
        if self.match(goal):
            return True
        elif self.backtrace_enabled:
            return self.backtrace(goal)
        else:
            return False

    def match(self, goal):
        """Gerçek veya kural eşleşmesi"""
        for fact in self.facts:
            if self.unify(goal, fact):
                return True
        for head, body in self.rules:
            if self.unify(goal, head):
                return all(self.match(subgoal) for subgoal in body)
        return False

    def unify(self, term1, term2):
        """İki terimi karşılaştır"""
        if isinstance(term1, str) and term1.startswith("#"):
            return True
        if isinstance(term2, str) and term2.startswith("#"):
            return True
        return term1 == term2

    def backtrace(self, goal):
        """Backtrace mekanizması"""
        print(f"Backtrace: {goal} için alternatifler aranıyor...")
        for fact in self.facts:
            if self.unify(goal, fact):
                print(f"Bulundu: {fact}")
                return True
        return False

    def dump(self):
        """Veri tabanını göster"""
        print("Facts:")
        for fact in self.facts:
            print(f"  {fact}")
        print("Rules:")
        for rule in self.rules:
            print(f"  {rule}")

    def clear(self):
        """Tüm verileri temizle"""
        self.facts.clear()
        self.rules.clear()

    def count(self):
        """Veritabanındaki toplam eleman sayısı"""
        return len(self.facts) + len(self.rules)

    def exists(self, item):
        """Veritabanında var mı"""
        for fact in self.facts:
            if self.unify(item, fact):
                return True
        for head, _ in self.rules:
            if self.unify(item, head):
                return True
        return False

    def forall(self, condition_func):
        """Tüm faktlar için koşul sağlıyor mu"""
        return all(condition_func(fact) for fact in self.facts)
class pdsXv13u:
    def __init__(self):
        # ... diğer başlatmalar ...
        self.prolog = PrologV3(self)

    def execute_line(self, line):
        line_upper = line.strip().upper()

        if line_upper.startswith("PFACT "):
            args = self.parse_params(line[6:])
            self.prolog.add_fact(tuple(args))

        elif line_upper.startswith("PRULE "):
            head_body = self.parse_params(line[6:])
            head = tuple(head_body[0].split())
            body = [tuple(b.split()) for b in head_body[1:]]
            self.prolog.add_rule(head, body)

        elif line_upper.startswith("PQUERY "):
            goal = tuple(self.parse_params(line[7:]))
            result = self.prolog.query(goal)
            print(f"Sonuç: {result}")

        elif line_upper.startswith("PCLEAR"):
            self.prolog.clear()

        elif line_upper.startswith("PDUMP"):
            self.prolog.dump()

        elif line_upper.startswith("PBACKTRACE "):
            goal = tuple(self.parse_params(line[11:]))
            result = self.prolog.backtrace(goal)
            print(f"Backtrace Sonuç: {result}")

        elif line_upper.startswith("PEXISTS "):
            goal = tuple(self.parse_params(line[8:]))
            result = self.prolog.exists(goal)
            print(f"Exists: {result}")

        elif line_upper.startswith("PCOUNT"):
            count = self.prolog.count()
            print(f"Toplam veri: {count}")

        elif line_upper.startswith("PFORALL "):
            condition = lambda fact: eval(self.parse_params(line[8:])[0])
            result = self.prolog.forall(condition)
            print(f"Forall sonucu: {result}")

        else:
            # Diğer komutlara devam
            pass
class TreeNode:
    def __init__(self, value=None):
        self.value = value
        self.children = []

    def add_child(self, child_node):
        """Yeni bir alt düğüm (child) ekler."""
        self.children.append(child_node)

    def remove_child(self, child_node):
        """Belirtilen alt düğümü kaldırır."""
        self.children = [child for child in self.children if child != child_node]

    def traverse(self, level=0):
        """Ağacı ekrana yazdırır (önceden sırayla)."""
        print('  ' * level + str(self.value))
        for child in self.children:
            child.traverse(level + 1)

    def find(self, value):
        """Belirtilen değeri bulur."""
        if self.value == value:
            return self
        for child in self.children:
            found = child.find(value)
            if found:
                return found
        return None

    def to_dict(self):
        """Ağacı sözlük (dict) yapısına dönüştürür."""
        return {
            "value": self.value,
            "children": [child.to_dict() for child in self.children]
        }

    def count_nodes(self):
        """Ağacın toplam düğüm sayısını hesaplar."""
        count = 1
        for child in self.children:
            count += child.count_nodes()
        return count

    def depth(self):
        """Ağacın derinliğini hesaplar."""
        if not self.children:
            return 1
        return 1 + max(child.depth() for child in self.children)
class Graph:
    def __init__(self, directed=False):
        self.graph = {}
        self.directed = directed

    def add_node(self, node):
        """Yeni bir düğüm (node) ekler."""
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, node1, node2):
        """İki düğüm arasında bağlantı (edge) kurar."""
        if node1 not in self.graph:
            self.add_node(node1)
        if node2 not in self.graph:
            self.add_node(node2)
        self.graph[node1].append(node2)
        if not self.directed:
            self.graph[node2].append(node1)

    def remove_edge(self, node1, node2):
        """İki düğüm arasındaki bağlantıyı kaldırır."""
        if node1 in self.graph and node2 in self.graph[node1]:
            self.graph[node1].remove(node2)
        if not self.directed and node2 in self.graph and node1 in self.graph[node2]:
            self.graph[node2].remove(node1)

    def remove_node(self, node):
        """Bir düğümü ve ona bağlı tüm bağlantıları kaldırır."""
        if node in self.graph:
            del self.graph[node]
        for neighbors in self.graph.values():
            if node in neighbors:
                neighbors.remove(node)

    def find_path(self, start, end, path=[]):
        """İki düğüm arasında bir yol arar."""
        path = path + [start]
        if start == end:
            return path
        if start not in self.graph:
            return None
        for node in self.graph[start]:
            if node not in path:
                newpath = self.find_path(node, end, path)
                if newpath:
                    return newpath
        return None

    def has_cycle_util(self, v, visited, parent):
        visited[v] = True
        for neighbor in self.graph.get(v, []):
            if not visited.get(neighbor, False):
                if self.has_cycle_util(neighbor, visited, v):
                    return True
            elif parent != neighbor:
                return True
        return False

    def has_cycle(self):
        """Graf içinde döngü (cycle) olup olmadığını kontrol eder."""
        visited = {}
        for node in self.graph:
            if not visited.get(node, False):
                if self.has_cycle_util(node, visited, None):
                    return True
        return False

    def to_dict(self):
        """Grafı sözlük (dict) yapısına çevirir."""
        return self.graph

    def display(self):
        """Grafı ekrana yazdırır."""
        for node, neighbors in self.graph.items():
            print(f"{node} -> {neighbors}")

    def node_count(self):
        """Toplam düğüm sayısını döner."""
        return len(self.graph)

    def edge_count(self):
        """Toplam kenar (bağlantı) sayısını döner."""
        return sum(len(neighbors) for neighbors in self.graph.values()) // (1 if self.directed else 2)
class PrologEngine:
    def __init__(self):
        self.facts = []
        self.rules = []
        self.variables = {}

    def add_fact(self, fact):
        """Yeni bir gerçek (fact) ekler."""
        self.facts.append(fact)

    def add_rule(self, head, body):
        """Yeni bir kural (rule) ekler."""
        self.rules.append((head, body))

    def query(self, goal):
        """Sorgu yapar, True/False döner."""
        self.variables = {}
        result = self.match_goal(goal)
        return result

    def match_goal(self, goal):
        """Hedef (goal) için gerçekler ve kurallar arasında eşleşme arar."""
        if isinstance(goal, tuple) and goal[0] == "AND":
            return all(self.match_goal(subgoal) for subgoal in goal[1:])
        elif isinstance(goal, tuple) and goal[0] == "OR":
            return any(self.match_goal(subgoal) for subgoal in goal[1:])
        elif isinstance(goal, tuple) and goal[0] == "NOT":
            return not self.match_goal(goal[1])
        elif isinstance(goal, tuple) and goal[0] == "XOR":
            return sum(self.match_goal(subgoal) for subgoal in goal[1:]) == 1
        elif isinstance(goal, tuple) and goal[0] == "IMP":
            return not self.match_goal(goal[1]) or self.match_goal(goal[2])
        elif isinstance(goal, tuple) and goal[0] == "BI-COND":
            return self.match_goal(("IMP", goal[1], goal[2])) and self.match_goal(("IMP", goal[2], goal[1]))
        else:
            return self.unify_goal(goal)

    def unify_goal(self, goal):
        for fact in self.facts:
            self.variables = {}
            if self.unify(goal, fact, self.variables):
                return True
        for head, body in self.rules:
            self.variables = {}
            if self.unify(goal, head, self.variables):
                if all(self.match_goal(subgoal) for subgoal in body):
                    return True
        return False

    def unify(self, term1, term2, bindings):
        """İki terimi birleştirir (unify)."""
        if isinstance(term1, str) and term1.startswith("#"):
            bindings[term1] = term2
            return True
        if isinstance(term2, str) and term2.startswith("#"):
            bindings[term2] = term1
            return True
        if isinstance(term1, str) and isinstance(term2, str):
            return term1 == term2
        if isinstance(term1, tuple) and isinstance(term2, tuple):
            if len(term1) != len(term2):
                return False
            return all(self.unify(t1, t2, bindings) for t1, t2 in zip(term1, term2))
        return False

    def backtrace(self, goal):
        """Sorgu başarısız olduğunda alternatif yolları dener."""
        # Bu basitleştirilmiş versiyon, daha gelişmiş bir sistemde izleme detaylı olur.
        print(f"Backtracing for {goal}...")

    def clear_facts_rules(self):
        """Tüm gerçekleri ve kuralları temizler."""
        self.facts.clear()
        self.rules.clear()

    def dump_knowledge_base(self):
        """Bilgi tabanını yazdırır."""
        print("Facts:")
        for fact in self.facts:
            print(f"  {fact}")
        print("Rules:")
        for head, body in self.rules:
            print(f"  {head} :- {body}")

    def count_matches(self, goal):
        """Belirli bir koşula kaç eşleşme olduğunu döner."""
        count = 0
        for fact in self.facts:
            if self.unify(goal, fact, {}):
                count += 1
        return count

    def exists(self, goal):
        """Bir hedefin var olup olmadığını kontrol eder."""
        return self.query(goal)

    def forall(self, condition_func, iterable):
        """Tüm elemanların bir koşulu sağlamasını kontrol eder."""
        return all(condition_func(x) for x in iterable)
class PrologEngine:
    def __init__(self):
        self.facts = []
        self.rules = []
        self.debug = False

    def add_fact(self, fact):
        self.facts.append(fact)

    def add_rule(self, head, body):
        self.rules.append((head, body))

    def query(self, goal):
        print(f"Sorgu Başlatılıyor: {goal}")
        result = self.backtrack(goal, {})
        if result:
            print(f"Evet: {goal}")
            for var, val in result.items():
                print(f"{var} = {val}")
        else:
            print(f"Hayır: {goal}")
        return bool(result)

    def backtrack(self, goal, bindings):
        if self.debug:
            print(f"Backtrack: {goal}, Bindings: {bindings}")

        if isinstance(goal, tuple) and goal[0] == "AND":
            local_bindings = bindings.copy()
            for subgoal in goal[1:]:
                result = self.backtrack(subgoal, local_bindings)
                if not result:
                    if self.debug:
                        print(f"AND başarısız: {subgoal}")
                    return None
                local_bindings.update(result)
            return local_bindings

        elif isinstance(goal, tuple) and goal[0] == "OR":
            for subgoal in goal[1:]:
                result = self.backtrack(subgoal, bindings.copy())
                if result:
                    return result
            return None

        elif isinstance(goal, tuple) and goal[0] == "NOT":
            result = self.backtrack(goal[1], bindings.copy())
            return {} if not result else None

        elif isinstance(goal, tuple) and goal[0] == "XOR":
            successes = [self.backtrack(subgoal, bindings.copy()) for subgoal in goal[1:]]
            count = sum(1 for r in successes if r)
            return {} if count == 1 else None

        elif isinstance(goal, tuple) and goal[0] == "IMP":
            if not self.backtrack(goal[1], bindings.copy()) or self.backtrack(goal[2], bindings.copy()):
                return {}
            return None

        elif isinstance(goal, tuple) and goal[0] == "BI-COND":
            a = self.backtrack(goal[1], bindings.copy())
            b = self.backtrack(goal[2], bindings.copy())
            return {} if (bool(a) == bool(b)) else None

        else:
            for fact in self.facts:
                new_bindings = self.unify(goal, fact, bindings.copy())
                if new_bindings is not None:
                    return new_bindings

            for head, body in self.rules:
                head_bindings = self.unify(goal, head, bindings.copy())
                if head_bindings is not None:
                    for subgoal in body:
                        head_bindings = self.backtrack(subgoal, head_bindings)
                        if head_bindings is None:
                            break
                    else:
                        return head_bindings

        return None

    def unify(self, term1, term2, bindings):
        if self.debug:
            print(f"Unify: {term1} with {term2} -> {bindings}")

        if isinstance(term1, str) and term1.startswith("#"):
            if term1 in bindings:
                return self.unify(bindings[term1], term2, bindings)
            bindings[term1] = term2
            return bindings

        if isinstance(term2, str) and term2.startswith("#"):
            if term2 in bindings:
                return self.unify(term1, bindings[term2], bindings)
            bindings[term2] = term1
            return bindings

        if isinstance(term1, str) and isinstance(term2, str):
            return bindings if term1 == term2 else None

        if isinstance(term1, tuple) and isinstance(term2, tuple) and len(term1) == len(term2):
            for t1, t2 in zip(term1, term2):
                bindings = self.unify(t1, t2, bindings)
                if bindings is None:
                    return None
            return bindings

        return None

    def clear(self):
        self.facts.clear()
        self.rules.clear()

    def dump(self):
        print("Fakta ve Kurallar:")
        for fact in self.facts:
            print(f"  Fact: {fact}")
        for head, body in self.rules:
            print(f"  Rule: {head} :- {body}")

    def count(self, goal):
        count = 0
        for fact in self.facts:
            if self.unify(goal, fact, {}):
                count += 1
        return count

    def exists(self, goal):
        return bool(self.query(goal))

    def forall(self, condition, iterable):
        return all(self.query((condition, item)) for item in iterable)

    def enable_debug(self):
        self.debug = True

    def disable_debug(self):
        self.debug = False
if cmd_upper.startswith("PFACT"):
    args = command.split(maxsplit=1)[1]
    fact = eval(args)
    self.prolog_engine.add_fact(fact)
    return None

if cmd_upper.startswith("PRULE"):
    args = command.split(maxsplit=1)[1]
    head, *body = eval(args)
    self.prolog_engine.add_rule(head, body)
    return None

if cmd_upper.startswith("PQUERY"):
    args = command.split(maxsplit=1)[1]
    goal = eval(args)
    self.prolog_engine.query(goal)
    return None

if cmd_upper.startswith("PASSERT"):
    args = command.split(maxsplit=1)[1]
    fact = eval(args)
    self.prolog_engine.add_fact(fact)
    return None

if cmd_upper.startswith("PRETRACT"):
    args = command.split(maxsplit=1)[1]
    fact = eval(args)
    if fact in self.prolog_engine.facts:
        self.prolog_engine.facts.remove(fact)
    return None

if cmd_upper == "PCLEAR":
    self.prolog_engine.clear()
    return None

if cmd_upper == "PBACKTRACE ON":
    self.prolog_engine.enable_debug()
    return None

if cmd_upper == "PBACKTRACE OFF":
    self.prolog_engine.disable_debug()
    return None

if cmd_upper == "PDUMP":
    self.prolog_engine.dump()
    return None

if cmd_upper.startswith("PCOUNT"):
    args = command.split(maxsplit=1)[1]
    goal = eval(args)
    print(f"COUNT: {self.prolog_engine.count(goal)}")
    return None

if cmd_upper.startswith("PEXISTS"):
    args = command.split(maxsplit=1)[1]
    goal = eval(args)
    print(f"EXISTS: {self.prolog_engine.exists(goal)}")
    return None

if cmd_upper.startswith("PFORALL"):
    args = command.split(maxsplit=1)[1]
    condition, iterable = eval(args)
    print(f"FORALL: {self.prolog_engine.forall(condition, iterable)}")
    return None
class pdsXv13u(...):   # üst sınıfı burada temsil ediyoruz
    def __init__(self):
        super().__init__()
        self.help_data = {}
        self.help_language = 'en'
        self.load_help_file('lang.json')  # JSON'dan yükle

    def load_help_file(self, filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.help_data = json.load(f)
        else:
            self.help_data = {}

    def show_help(self, command=None):
        if command is None:
            print("Available commands:")
            for cmd in sorted(self.help_data.keys()):
                description = self.help_data[cmd].get(self.help_language, "No description.")
                print(f"{cmd}: {description}")
        elif command.upper() == "LANG":
            print(f"Current language: {self.help_language}")
        else:
            parts = command.split()
            if len(parts) == 2 and parts[0].upper() == "LANG":
                new_lang = parts[1].lower()
                if new_lang in ['en', 'tr']:
                    self.help_language = new_lang
                    print(f"Language changed to {new_lang}")
                else:
                    print(f"Unsupported language: {new_lang}")
            else:
                info = self.help_data.get(command.upper())
                if info:
                    print(info.get(self.help_language, "No description available."))
                else:
                    print(f"No help available for command: {command}")

    def execute_command(self, command, args=None, module_name="main"):
        ...
        if cmd_upper.startswith("HELP"):
            cmd_args = command[4:].strip()
            self.show_help(cmd_args if cmd_args else None)
            return None
        ...
class pdsXv13u(...):  # Ana yorumlayıcı sınıfı
    def __init__(self):
        super().__init__()
        self.help_data = {}
        self.help_language = 'en'
        self.load_help_file('lang.json')

    def load_help_file(self, filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.help_data = json.load(f)
        else:
            print(f"Warning: {filename} bulunamadı. Yardım sistemi boş başlatıldı.")
            self.help_data = {}

    def show_help(self, command=None):
        if command is None:
            print("\n[Available Commands]")
            for cmd in sorted(self.help_data.keys()):
                desc = self.help_data[cmd].get(self.help_language, "No description available.")
                print(f"  {cmd} : {desc}")
        elif command.upper().startswith("LANG"):
            parts = command.split()
            if len(parts) == 2:
                lang = parts[1].lower()
                if lang in ['en', 'tr']:
                    self.help_language = lang
                    print(f"Language switched to {lang.upper()}.")
                else:
                    print("Unsupported language.")
            else:
                print(f"Current help language: {self.help_language.upper()}")
        else:
            cmd_info = self.help_data.get(command.upper())
            if cmd_info:
                print(f"{command.upper()} : {cmd_info.get(self.help_language, 'No description available.')}")
            else:
                print(f"No help available for '{command.upper()}'.")
    def execute_command(self, command, args=None, module_name="main"):
        command = command.strip()
        cmd_upper = command.upper()

        try:
            if cmd_upper.startswith("HELP"):
                help_target = command[4:].strip()
                self.show_help(help_target if help_target else None)
                return None
            # Diğer komutlar burada...
        except Exception as e:
            if self.error_handler:
                self.jump_to_label(self.error_handler)
                return None
            raise
