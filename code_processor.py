import subprocess
import tempfile
import os
import re
from ctypes import CDLL
from pathlib import Path
import shutil

class PdsXException(Exception):
    pass

class CodeProcessor:
    def __init__(self, interpreter):
        """ Derleyici modülünü başlatır """
        self.interpreter = interpreter
        self.temp_dir = tempfile.mkdtemp()

    def process_lx(self, code, module_name):
        """ .lX dosyalarındaki C veya C++ kodlarını işler """
        if "CODE C" in code.upper() or "CODE C++" in code.upper():
            code_blocks = self._extract_code_blocks(code, ["CODE C", "CODE C++"], "END CODE")
            for lang, block in code_blocks:
                if lang == "CODE C":
                    self._compile_c(block, module_name)
                elif lang == "CODE C++":
                    self._compile_cpp(block, module_name)
        else:
            raise PdsXException("Geçersiz .lX dosyası: CODE C veya CODE C++ bloku bulunamadı")

    def process_mx(self, code, module_name):
        """ .mX dosyalarındaki Assembly kodlarını işler """
        if "CODE ASM" in code.upper():
            code_blocks = self._extract_code_blocks(code, ["CODE ASM"], "END CODE")
            for _, block in code_blocks:
                self._compile_asm(block, module_name)
        else:
            raise PdsXException("Geçersiz .mX dosyası: CODE ASM bloku bulunamadı")

    def _extract_code_blocks(self, code, start_markers, end_marker):
        """ Kod bloklarını ayıklar """
        blocks = []
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip().upper()
            for marker in start_markers:
                if line.startswith(marker):
                    block = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip().upper() != end_marker:
                        block.append(lines[j])
                        j += 1
                    blocks.append((marker, "\n".join(block)))
                    i = j
                    break
            i += 1
        return blocks

    def _compile_c(self, code, module_name):
        """ C kodunu derler ve yükler """
        with tempfile.NamedTemporaryFile(suffix=".c", delete=False, dir=self.temp_dir) as f:
            f.write(code.encode('utf-8'))
            c_file = f.name
        dll_file = os.path.join(self.temp_dir, f"{module_name}.so")
        try:
            subprocess.check_call(["gcc", "-shared", "-o", dll_file, c_file])
            self.interpreter.function_table[module_name] = CDLL(dll_file)
        except subprocess.CalledProcessError:
            raise PdsXException("C kodu derlenemedi")
        finally:
            os.remove(c_file)

    def _compile_cpp(self, code, module_name):
        """ C++ kodunu derler ve yükler """
        with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False, dir=self.temp_dir) as f:
            f.write(code.encode('utf-8'))
            cpp_file = f.name
        dll_file = os.path.join(self.temp_dir, f"{module_name}.so")
        try:
            subprocess.check_call(["g++", "-shared", "-o", dll_file, cpp_file])
            self.interpreter.function_table[module_name] = CDLL(dll_file)
        except subprocess.CalledProcessError:
            raise PdsXException("C++ kodu derlenemedi")
        finally:
            os.remove(cpp_file)

    def _compile_asm(self, code, module_name):
        """ Assembly kodunu derler ve yükler """
        with tempfile.NamedTemporaryFile(suffix=".asm", delete=False, dir=self.temp_dir) as f:
            f.write(code.encode('utf-8'))
            asm_file = f.name
        obj_file = os.path.join(self.temp_dir, f"{module_name}.o")
        dll_file = os.path.join(self.temp_dir, f"{module_name}.so")
        try:
            subprocess.check_call(["nasm", "-f", "elf64", asm_file, "-o", obj_file])
            subprocess.check_call(["ld", "-shared", "-o", dll_file, obj_file])
            self.interpreter.function_table[module_name] = CDLL(dll_file)
        except subprocess.CalledProcessError:
            raise PdsXException("Assembly kodu derlenemedi")
        finally:
            os.remove(asm_file)
            if os.path.exists(obj_file):
                os.remove(obj_file)

    def cleanup(self):
        """ Geçici dosyaları temizler """
        shutil.rmtree(self.temp_dir, ignore_errors=True)