"""
pdsX Linter - .basX dosyaları için sözdizimi ve tip kontrol aracı
"""

import re
from collections import defaultdict

class PdsxLinter:
    def __init__(self):
        self.defined_labels = set()
        self.defined_variables = {}
        self.used_variables = set()
        self.defined_functions = set()
        self.defined_subs = set()
        self.errors = []

    def lint(self, code):
        lines = code.splitlines()
        open_blocks = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            upper = stripped.upper()

            # --- A. Blok eşleştirme ---
            if upper.startswith("IF ") and "THEN" in upper:
                open_blocks.append(("IF", i))
            elif upper == "ELSE":
                if not any(b[0] == "IF" for b in open_blocks):
                    self.errors.append((i, "Blok Hatası", "ELSE için IF bulunamadı", "IF...THEN ile eşleştirin"))
            elif upper == "END IF":
                if not any(b[0] == "IF" for b in open_blocks):
                    self.errors.append((i, "Blok Hatası", "END IF için IF bulunamadı", "Blok yapısını kontrol edin"))
                else:
                    open_blocks = [b for b in open_blocks if b[0] != "IF"]

            # --- B. Etiket tanımı ve GOTO kontrolü ---
            if upper.startswith("LABEL"):
                match = re.match(r"LABEL\s+(\w+)", stripped, re.IGNORECASE)
                if match:
                    self.defined_labels.add(match.group(1))
            if upper.startswith("GOTO"):
                match = re.match(r"GOTO\s+(\w+)", stripped, re.IGNORECASE)
                if match and match.group(1) not in self.defined_labels:
                    self.errors.append((i, "Etiket Hatası", f"Tanımsız etiket: {match.group(1)}", "LABEL komutuyla tanımlayın"))

            # --- C. Değişken tanımı ve tip kontrolü ---
            if upper.startswith("DIM") or upper.startswith("GLOBAL"):
                match = re.match(r"(?:DIM|GLOBAL)\s+(\w+)\s+AS\s+(\w+)", stripped, re.IGNORECASE)
                if match:
                    var_name, var_type = match.groups()
                    self.defined_variables[var_name] = var_type.upper()

            if upper.startswith("LET"):
                match = re.match(r"LET\s+(\w+)\s*=\s*(.+)", stripped, re.IGNORECASE)
                if match:
                    var, expr = match.groups()
                    self.used_variables.add(var)
                    if var in self.defined_variables:
                        vtype = self.defined_variables[var]
                        if vtype == "INTEGER" and re.search(r'".+"', expr):
                            self.errors.append((i, "Tip Uyumsuzluğu", f'{var} INTEGER ama string atama yapılıyor', "STR$() ile dönüştürmeyi önerin"))
                        elif vtype == "STRING" and re.match(r"[\d\.]+", expr):
                            self.errors.append((i, "Tip Uyumsuzluğu", f'{var} STRING ama sayısal ifade atandı', "STR$() veya CAST kullanın"))

            # --- D. Fonksiyon çağrısı kontrolü ---
            match = re.match(r"(\w+)\s*\((.*?)\)", stripped)
            if match:
                fname = match.group(1)
                if fname not in self.defined_functions:
                    self.errors.append((i, "Fonksiyon Hatası", f"Tanımsız fonksiyon: {fname}", "Tanımını FUNCTION ile yapın"))

            if upper.startswith("FUNCTION"):
                match = re.match(r"FUNCTION\s+(\w+)", stripped, re.IGNORECASE)
                if match:
                    self.defined_functions.add(match.group(1))

            if upper.startswith("SUB"):
                match = re.match(r"SUB\s+(\w+)", stripped, re.IGNORECASE)
                if match:
                    self.defined_subs.add(match.group(1))

        return self.errors

    def print_report(self):
        print("| Satır | Hata Türü         | Açıklama                          | Öneri                  |")
        print("|-------|--------------------|-----------------------------------|------------------------|")
        for line, errtype, desc, sugg in self.errors:
            print(f"| {line:<5} | {errtype:<18} | {desc:<33} | {sugg:<22} |")

# Örnek kullanım:
if __name__ == "__main__":
    kod = """
    DIM x AS INTEGER
    LET x = "merhaba"
    GOTO SON
    PRINT "Deneme"
    FUNCTION Topla(a, b)
    LET y = Topla(1, 2)
    """
    linter = PdsxLinter()
    linter.lint(kod)
    linter.print_report()
