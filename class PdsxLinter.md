import re

class PdsxLinter:
    def __init__(self, code):
        self.code = code.splitlines()
        self.variables = {}
        self.labels = set()
        self.errors = []

    def lint(self):
        for lineno, line in enumerate(self.code, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("'"):  # Boş veya yorum satırı
                continue

            self.check_label(stripped, lineno)
            self.check_dim(stripped, lineno)
            self.check_let(stripped, lineno)
            self.check_if(stripped, lineno)
            self.check_func_call(stripped, lineno)

        return self.errors

    def check_label(self, line, lineno):
        if line.upper().startswith("LABEL "):
            label = line[6:].strip()
            self.labels.add(label)

    def check_dim(self, line, lineno):
        match = re.match(r"DIM\s+(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
        if match:
            var, var_type = match.groups()
            self.variables[var] = var_type.upper()

    def check_let(self, line, lineno):
        match = re.match(r"LET\s+(\w+)\s*=\s*(.+)", line, re.IGNORECASE)
        if match:
            var, expr = match.groups()
            expected_type = self.variables.get(var)
            if expected_type:
                if expected_type == "INTEGER" and re.match(r'".*"', expr.strip()):
                    self.errors.append((lineno, "Tip Uyumsuzluğu", f"{var} INTEGER ancak metin atanmış.", "STR$() ile dönüştürün veya türü değiştirin"))
                elif expected_type == "STRING" and re.match(r'^[\d\.]+$', expr.strip()):
                    self.errors.append((lineno, "Tip Uyumsuzluğu", f"{var} STRING ancak sayı atanmış.", "STR$() veya tip kontrolü önerilir"))

    def check_if(self, line, lineno):
        if line.upper().startswith("IF") and "THEN" not in line.upper():
            self.errors.append((lineno, "Sözdizimi Hatası", "IF komutunda THEN eksik.", "THEN ifadesini ekleyin"))

    def check_func_call(self, line, lineno):
        match = re.match(r"(\w+)\s*\((.*)\)", line)
        if match:
            func_name = match.group(1)
            if func_name.upper() not in ("LEN", "MID$", "LEFT$", "RIGHT$", "STR$", "INT", "SIN", "COS", "TAN", "LOG", "EXP"):  # Örnek sabit liste
                self.errors.append((lineno, "Tanımsız Fonksiyon", f"{func_name} fonksiyonu tanımsız.", "Fonksiyon adını kontrol edin"))


# Örnek kullanım
if __name__ == "__main__":
    with open("example.basX", "r", encoding="utf-8") as f:
        code = f.read()

    linter = PdsxLinter(code)
    results = linter.lint()

    for lineno, err_type, msg, suggestion in results:
        print(f"Satır {lineno} | {err_type}: {msg} => {suggestion}")
