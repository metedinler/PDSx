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
import tkinter as tk
import threading
import yaml
import xml.etree.ElementTree as ET
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from numba import jit
import pickle
from typing import Dict, List, Any, Optional, Callable
import signal
from copy import deepcopy

# Bağımlılık Yönetimi
def install_missing_libraries():
    required = {
        'numpy': 'numpy', 'pandas': 'pandas', 'scipy': 'scipy', 'psutil': 'psutil',
        'pdfplumber': 'pdfplumber', 'bs4': 'beautifulsoup4', 'requests': 'requests',
        'packaging': 'packaging', 'tkinter': 'tkinter', 'numba': 'numba',
        'pyyaml': 'pyyaml', 'watchdog': 'watchdog', 'sqlite3': 'sqlite3'
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

class PdsXException(Exception):
    pass

# Simüle Edilmiş Modüller
class LogicEngine:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

class GuiLibX:
    def __init__(self):
        self.root = None
        self.widgets = {}

    def create_window(self, title, width, height):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")

    def add_button(self, name, text, x, y):
        btn = tk.Button(self.root, text=text)
        btn.place(x=x, y=y)
        self.widgets[name] = btn

    def add_checkbox(self, name, text, x, y):
        chk = tk.Checkbutton(self.root, text=text)
        chk.place(x=x, y=y)
        self.widgets[name] = chk

    def add_label(self, name, text, x, y):
        lbl = tk.Label(self.root, text=text)
        lbl.place(x=x, y=y)
        self.widgets[name] = lbl

    def bind_event(self, widget_name, event, handler):
        if widget_name in self.widgets:
            self.widgets[widget_name].bind(event, handler)

    def bind_system_event(self, event_type, handler):
        if not self.root:
            return
        if event_type == "mouse_clicked":
            self.root.bind("<Button-1>", handler)
        elif event_type == "key_pressed":
            self.root.bind("<Key>", handler)

    def run(self):
        if self.root:
            self.root.mainloop()

class AsyncManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    async def run_tasks(self):
        await asyncio.gather(*self.tasks)

class InlineASM:
    def execute(self, code):
        pass  # Assembly simülasyonu

class InlineC:
    def execute(self, code):
        pass  # C kodu simülasyonu

class UnsafeMemoryManager:
    def poke(self, address, value):
        pass  # Bellek yazma simülasyonu

    def peek(self, address):
        return 0  # Bellek okuma simülasyonu

class SysCallWrapper:
    def call(self, syscall, args):
        pass  # Sistem çağrısı simülasyonu

class BytecodeCompiler:
    def compile(self, code):
        return []  # Bytecode simülasyonu

class DllManager:
    def load_dll(self, dll_name):
        return ctypes.WinDLL(dll_name)

class ApiManager:
    def load_api(self, url):
        return lambda query: requests.post(url, json={"query": query}).json().get("response", "")

class EventManager:
    def __init__(self):
        self.handlers = {}

    def register(self, event, handler):
        self.handlers[event] = handler

    def trigger(self, event):
        if event in self.handlers:
            self.handlers[event]()

class PrologEngine:
    def __init__(self):
        self.facts = []
        self.rules = []
        self.debug = False

    def add_fact(self, fact):
        self.facts.append(fact)
        if self.debug:
            print(f"Fact eklendi: {fact}")

    def add_rule(self, head, body, func=lambda x: x):
        self.rules.append((head, body, func))
        if self.debug:
            print(f"Rule eklendi: {head} :- {body}")

    def query(self, goal):
        if self.debug:
            print(f"Sorgu başlatılıyor: {goal}")
        bindings = self.backtrack(goal, {})
        if bindings:
            print(f"Evet: {goal}")
            if bindings:
                print("Sonuçlar:")
                for var, val in bindings.items():
                    print(f"  {var} = {val}")
            return True
        print(f"Hayır: {goal}")
        return False

    def backtrack(self, goal, bindings):
        if self.debug:
            print(f"Backtrack: Goal={goal}, Bindings={bindings}")

        if isinstance(goal, tuple) and goal[0] == "AND":
            local_bindings = bindings.copy()
            for subgoal in goal[1:]:
                result = self.backtrack(subgoal, local_bindings)
                if result is None:
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
            return {} if result is None else None

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

            for head, body, _ in self.rules:
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
            print(f"Unify: {term1} <=> {term2}, Bindings={bindings}")

        if term1 == term2:
            return bindings

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

        if isinstance(term1, tuple) and isinstance(term2, tuple) and len(term1) == len(term2):
            for t1, t2 in zip(term1, term2):
                bindings = self.unify(t1, t2, bindings)
                if bindings is None:
                    return None
            return bindings

        if term1 == term2:
            return bindings
        return None

    def clear(self):
        self.facts.clear()
        self.rules.clear()
        if self.debug:
            print("Bilgi tabanı temizlendi.")

    def dump(self):
        print("Bilgi Tabanı:")
        print("  Gerçekler:")
        for fact in self.facts:
            print(f"    {fact}")
        print("  Kurallar:")
        for head, body, _ in self.rules:
            print(f"    {head} :- {body}")

    def count(self, goal):
        count = 0
        for fact in self.facts:
            if self.unify(goal, fact, {}) is not None:
                count += 1
        return count

    def exists(self, goal):
        return self.query(goal)

    def forall(self, condition, items):
        return all(self.query((condition, item)) for item in items)

    def enable_debug(self):
        self.debug = True
        print("Debug modu aktif.")

    def disable_debug(self):
        self.debug = False
        print("Debug modu kapalı.")

class MemoryManager:
    def __init__(self):
        self.heap = {}
        self.ref_counts = {}

    def allocate(self, size: int) -> int:
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
    def __init__(self, fields, type_table, get_type_size):
        self.fields = {name: None for name, _, _ in fields}
        self.field_types = {name: type_name for name, type_name, _ in fields}
        self.init_values = {name: init_value for name, _, init_value in fields}
        self.type_table = type_table
        self.get_type_size = get_type_size
        self.sizes = {name: get_type_size(type_name) for name, type_name, _ in fields}
        self.offsets = {}
        offset = 0
        for name in self.fields:
            self.offsets[name] = offset
            offset += self.sizes[name]
        for name, init_value in self.init_values.items():
            if init_value.upper() == "NULL" and self.field_types[name].upper() != "VOID":
                self.fields[name] = None
            elif init_value.upper() == "NAN" and self.field_types[name].upper() in ("FLOAT", "DOUBLE", "SINGLE"):
                self.fields[name] = float('nan')
            elif init_value != "None":
                expected_type = self.type_table.get(self.field_types[name].upper(), object)
                try:
                    self.fields[name] = expected_type(init_value)
                except:
                    raise PdsXException(f"{name} için geçersiz başlangıç değeri: {init_value}")

    @jit(nopython=True)
    def set_field(self, field_name, value):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        expected_type = self.type_table.get(self.field_types[field_name].upper(), object)
        if value == "NULL" and self.field_types[field_name].upper() != "VOID":
            self.fields[field_name] = None
            return
        if value == "NAN" and self.field_types[field_name].upper() in ("FLOAT", "DOUBLE", "SINGLE"):
            self.fields[field_name] = float('nan')
            return
        if not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except:
                raise TypeError(f"{field_name} için beklenen tip {expected_type.__name__}, ancak {type(value).__name__} alındı")
        self.fields[field_name] = value

    @jit(nopython=True)
    def get_field(self, field_name):
        if field_name not in self.fields:
            raise ValueError(f"Geçersiz alan: {field_name}")
        return self.fields[field_name]

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
    def _get_size(self, type_name):
        size_map = {
            "INTEGER": 4, "DOUBLE": 8, "STRING": 8, "BYTE": 1,
            "SHORT": 2, "LONG": 8, "SINGLE": 4, "LIST": 8, "ARRAY": 8, "DICT": 8,
            "BITFIELD": 4, "ENUM": 4, "FLOAT128": 16, "FLOAT256": 32, "STRING8": 8, "STRING16": 16,
            "BOOLEAN": 1, "NULL": 8, "NAN": 8
        }
        return size_map.get(type_name.upper(), 8)

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
            "cp1256", "iso-8859-6", "cp874", "iso-8859-7", "cp1257", "iso-8859-8"
        ]
        self.type_table = {
            "STRING": str, "INTEGER": int, "LONG": int, "SINGLE": float, "DOUBLE": float,
            "BYTE": int, "SHORT": int, "UNSIGNED INTEGER": int, "CHAR": str,
            "LIST": list, "DICT": dict, "SET": set, "TUPLE": tuple,
            "ARRAY": np.array, "DATAFRAME": pd.DataFrame, "POINTER": None,
            "STRUCT": dict, "UNION": None, "ENUM": dict, "VOID": None, "BITFIELD": int,
            "FLOAT128": np.float128, "FLOAT256": np.float256, "STRING8": str, "STRING16": str,
            "BOOLEAN": bool, "NULL": type(None), "NAN": float
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

    # SQL Yardımcı Fonksiyonlar
    def open_database(self, db_name):
        if db_name not in self.db_connections:
            conn = sqlite3.connect(db_name)
            self.db_connections[db_name] = conn
            self.current_db = db_name

    def close_database(self):
        if hasattr(self, 'current_db') and self.current_db:
            conn = self.db_connections.get(self.current_db)
            if conn:
                conn.close()
                del self.db_connections[self.current_db]
                self.current_db = None

    def execute_sql(self, sql):
        if hasattr(self, 'current_db') and self.current_db:
            conn = self.db_connections[self.current_db]
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            result = cursor.fetchall()
            self.current_scope()['_LAST_SQL_RESULT'] = result
            return result
        else:
            if getattr(self, "auto_sql_mode", False):
                self.open_database("default.db")
                return self.execute_sql(sql)
            raise PdsXException("Veritabanı bağlı değil")

    # SQL Sonuç Dönüşümleri
    def sql_result_to_array(self):
        result = self.current_scope().get('_LAST_SQL_RESULT', [])
        return [list(row) for row in result]

    def sql_result_to_struct(self, struct_name=None):
        result = self.current_scope().get('_LAST_SQL_RESULT', [])
        if not result:
            return []
        if struct_name is None:
            struct_name = "AutoStruct"
        fields = [(f"Field{i+1}", "STRING") for i in range(len(result[0]))]
        instance_list = []
        for row in result:
            instance = StructInstance(fields, self.type_table, self._get_size)
            for idx, value in enumerate(row):
                instance.set_field(f"Field{idx+1}", value)
            instance_list.append(instance)
        return instance_list

    def sql_result_to_dataframe(self):
        result = self.current_scope().get('_LAST_SQL_RESULT', [])
        if not result:
            return pd.DataFrame()
        return pd.DataFrame(result)

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
            if command_upper.startswith("OPEN DATABASE"):
                match = re.match(r"OPEN DATABASE\s+(.+)", command, re.IGNORECASE)
                if match:
                    db_name = match.group(1).strip()
                    self.open_database(db_name)
                    return None

            if command_upper.startswith("CREATE TABLE"):
                sql = command.strip()
                self.execute_sql(sql)
                return None

            if any(command_upper.startswith(cmd) for cmd in ["INSERT INTO", "UPDATE", "DELETE FROM", "SELECT"]):
                result = self.execute_sql(command)
                return None

            if command_upper.startswith("CLOSE DATABASE"):
                self.close_database()
                return None

            if command_upper.startswith("ET SQL AUTO"):
                match = re.match(r"ET SQL AUTO\s+(ON|OFF)", command, re.IGNORECASE)
                if match:
                    mode = match.group(1).upper()
                    self.auto_sql_mode = (mode == "ON")
                    return None
                raise PdsXException("ET SQL AUTO komutunda geçersiz parametre")

            if command_upper.startswith("SQL RESULT TO ARRAY"):
                match = re.match(r"SQL RESULT TO ARRAY\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    self.current_scope()[var_name] = self.sql_result_to_array()
                    return None

            if command_upper.startswith("SQL RESULT TO STRUCT"):
                match = re.match(r"SQL RESULT TO STRUCT\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    self.current_scope()[var_name] = self.sql_result_to_struct()
                    return None

            if command_upper.startswith("SQL RESULT TO DATAFRAME"):
                match = re.match(r"SQL RESULT TO DATAFRAME\s+(\w+)", command, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    self.current_scope()[var_name] = self.sql_result_to_dataframe()
                    return None

            if command_upper.startswith("TRY"):
                match = re.match(r"TRY\s+(.+)\s+CATCH\s+(.+)(?:\s+FINALLY\s+(.+))?", command, re.IGNORECASE)
                if match:
                    try_block, catch_block, finally_block = match.groups()
                    try:
                        self.execute_command(try_block, scope_name)
                    except Exception as e:
                        self.current_scope()['_error'] = str(e)
                        self.execute_command(catch_block, scope_name)
                    finally:
                        if finally_block:
                            self.execute_command(finally_block, scope_name)
                    return None
                raise PdsXException("TRY CATCH FINALLY komutunda sözdizimi hatası")

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