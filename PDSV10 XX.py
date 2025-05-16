import sys
import subprocess
import importlib.metadata
import platform
import json
import asyncio
import ast
import math
import re
import logging
import struct as py_struct
from collections import defaultdict
import random
import sqlite3
import numpy as np
import pandas as pd
import scipy.stats as stats
import os
import time
import argparse
import psutil
from abc import ABC, abstractmethod

# Bağımlılık Yönetimi
def install_missing_libraries():
    required = {'numpy': 'numpy', 'pandas': 'pandas', 'scipy': 'scipy', 'psutil': 'psutil'}
    installed = {pkg.metadata['Name'].lower() for pkg in importlib.metadata.distributions()}
    missing = [lib for lib, pkg in required.items() if lib not in installed]
    if missing:
        print(f"Eksik kütüphaneler: {missing}")
        for lib in missing:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', required[lib]])

install_missing_libraries()

# Yardımcı Sınıflar
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
        if ptr in self.ref_counts and self.ref_counts[ptr] > 0:
            self.ref_counts[ptr] -= 1
            if self.ref_counts[ptr] == 0:
                del self.heap[ptr]
                del self.ref_counts[ptr]

    def dereference(self, ptr):
        return self.heap.get(ptr)

    def set_value(self, ptr, value):
        if ptr in self.heap:
            if isinstance(value, (int, float)):
                self.heap[ptr][:] = py_struct.pack('d', float(value))
            elif isinstance(value, str):
                self.heap[ptr][:] = value.encode()

class StructInstance:
    def __init__(self, fields, type_table):
        self.fields = {name: None for name, _ in fields}
        self.field_types = {name: type_name for name, type_name in fields}
        self.type_table = type_table

    def set_field(self, field_name, value):
        if field_name in self.fields:
            expected_type = self.type_table.get(self.field_types[field_name].upper(), object)
            self.fields[field_name] = expected_type(value) if not isinstance(value, expected_type) else value

    def get_field(self, field_name):
        return self.fields.get(field_name)

class Pointer:
    def __init__(self, address, target_type, interpreter):
        self.address = address
        self.target_type = target_type
        self.interpreter = interpreter

    def dereference(self):
        return self.interpreter.memory_pool.get(self.address, {}).get("value")

    def set(self, value):
        if self.address in self.interpreter.memory_pool:
            self.interpreter.memory_pool[self.address]["value"] = value

# Interpreter Çekirdeği
class pdsXv11(ABC):
    def __init__(self):
        self.global_vars = {}
        self.local_scopes = [{}]
        self.functions = {}
        self.subs = {}
        self.labels = {}
        self.program = []
        self.program_counter = 0
        self.call_stack = []
        self.running = False
        self.error_handler = None
        self.debug_mode = False
        self.loop_stack = []
        self.memory_manager = MemoryManager()
        self.memory_pool = {}
        self.modules = {"main": {"program": [], "functions": {}, "subs": {}, "labels": {}}}
        self.current_module = "main"
        self.repl_mode = False
        self.bytecode = []
        self.type_table = {
            "INTEGER": int, "DOUBLE": float, "STRING": str, "LIST": list, "ARRAY": np.ndarray
        }
        self.function_table = {
            "LEN": len, "ABS": abs, "INT": int, "RND": random.random,
            "SQR": math.sqrt, "SIN": math.sin, "COS": math.cos, "TAN": math.tan
        }

    def current_scope(self):
        return self.local_scopes[-1]

    def parse_program(self, code, module_name="main"):
        self.current_module = module_name
        self.modules[module_name] = {"program": [], "functions": {}, "subs": {}, "labels": {}}
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
                i += 1
            elif line_upper.startswith("FUNCTION "):
                func_name = line[8:].split("(")[0].strip()
                self.functions[func_name] = i + 1
                self.modules[module_name]["functions"][func_name] = i + 1
                i += 1
            elif line_upper.startswith("LABEL "):
                label_name = line[6:].strip()
                self.labels[label_name] = i
                self.modules[module_name]["labels"][label_name] = i
                i += 1
            else:
                self.program.append((line, module_name))
                self.modules[module_name]["program"].append((line, None))
                i += 1

    def evaluate_expression(self, expr, scope_name=None):
        tree = ast.parse(expr, mode='eval')
        namespace = {**self.global_vars, **self.current_scope(), **self.function_table}
        return eval(compile(tree, '<string>', 'eval'), namespace)

    def execute_command(self, command, scope_name=None):
        command = command.strip()
        if not command:
            return
        cmd_upper = command.upper()

        if cmd_upper.startswith("PRINT"):
            value = self.evaluate_expression(command[5:].strip(), scope_name)
            print(value)
        elif cmd_upper.startswith("LET"):
            var_name, expr = re.match(r"LET\s+(\w+)\s*=\s*(.+)", command, re.I).groups()
            value = self.evaluate_expression(expr, scope_name)
            self.current_scope()[var_name] = value
        elif cmd_upper.startswith("DIM"):
            var_name, var_type = re.match(r"DIM\s+(\w+)\s+AS\s+(\w+)", command, re.I).groups()
            if var_type == "STRUCT":
                self.current_scope()[var_name] = StructInstance([], self.type_table)
            else:
                self.current_scope()[var_name] = self.type_table.get(var_type, object)()
        elif cmd_upper.startswith("IF"):
            condition = re.match(r"IF\s+(.+)\s+THEN", command, re.I).group(1)
            if self.evaluate_expression(condition, scope_name):
                return
            else:
                while self.program_counter < len(self.program) and \
                      self.program[self.program_counter][0].upper() != "END IF":
                    self.program_counter += 1
        elif cmd_upper == "END IF":
            return
        elif cmd_upper.startswith("FOR"):
            var_name, start, end = re.match(r"FOR\s+(\w+)\s*=\s*(.+)\s+TO\s+(.+)", command, re.I).groups()
            self.current_scope()[var_name] = self.evaluate_expression(start, scope_name)
            self.loop_stack.append({
                "start": self.program_counter,
                "var": var_name,
                "end": self.evaluate_expression(end, scope_name),
                "step": 1
            })
        elif cmd_upper.startswith("NEXT"):
            loop = self.loop_stack[-1]
            var_name = loop["var"]
            current = self.current_scope()[var_name] + loop["step"]
            self.current_scope()[var_name] = current
            if current <= loop["end"]:
                self.program_counter = loop["start"]
            else:
                self.loop_stack.pop()
        elif cmd_upper.startswith("GOTO"):
            label = re.match(r"GOTO\s+(\w+)", command, re.I).group(1)
            return self.labels.get(label, self.program_counter + 1)
        elif cmd_upper.startswith("ON ERROR GOTO"):
            label = re.match(r"ON ERROR GOTO\s+(\w+)", command, re.I).group(1)
            self.error_handler = self.labels.get(label)
        else:
            raise Exception(f"Bilinmeyen komut: {command}")

    def run(self, code=None):
        if code:
            self.parse_program(code)
        self.running = True
        while self.running and self.program_counter < len(self.program):
            cmd, scope = self.program[self.program_counter]
            try:
                next_pc = self.execute_command(cmd, scope)
                self.program_counter = next_pc if next_pc is not None else self.program_counter + 1
            except Exception as e:
                if self.error_handler:
                    self.program_counter = self.error_handler
                else:
                    raise e
        self.running = False

    def repl(self):
        self.repl_mode = True
        print("pdsXv11 REPL - Çıkış için 'EXIT'")
        while True:
            cmd = input("> ")
            if cmd.upper() == "EXIT":
                break
            try:
                self.execute_command(cmd)
            except Exception as e:
                print(f"Hata: {e}")
        self.repl_mode = False

    def compile_to_bytecode(self, code):
        self.bytecode = []
        for line in code.split("\n"):
            line = line.strip()
            if line:
                tokens = line.split(maxsplit=1)
                opcode = tokens[0].upper()
                operands = tokens[1] if len(tokens) > 1 else ""
                self.bytecode.append((opcode, operands))
        return self.bytecode

    def execute_bytecode(self):
        self.running = True
        pc = 0
        while self.running and pc < len(self.bytecode):
            opcode, operands = self.bytecode[pc]
            if opcode == "PRINT":
                print(self.evaluate_expression(operands))
            elif opcode == "LET":
                var, val = operands.split("=", 1)
                self.current_scope()[var.strip()] = self.evaluate_expression(val.strip())
            pc += 1
        self.running = False

    @abstractmethod
    def abstract_method(self):
        pass

class ConcreteInterpreter(pdsXv11):
    def abstract_method(self):
        print("Soyut metod implementasyonu")

def main():
    parser = argparse.ArgumentParser(description='pdsXv11 Interpreter')
    parser.add_argument('file', nargs='?', help='Çalıştırılacak dosya')
    parser.add_argument('-i', '--interactive', action='store_true', help='Etkileşimli mod')
    args = parser.parse_args()

    interpreter = ConcreteInterpreter()
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
        interpreter.run(code)
    if args.interactive or not args.file:
        interpreter.repl()

if __name__ == "__main__":
    main()