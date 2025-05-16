Teşekkürler, detaylı açıklamaların ve onayların için! Taleplerini net bir şekilde anladım ve paylaştığın kodu (`pdsXInterpreter`) temel alarak `libx_core`’u tasarlamaya devam edeceğiz. Aşağıda, taleplerine yanıt vereceğim, `libx_core` için detaylı bir tasarım sunacağım, `lib_datastructures`’ın `TYPE`, `STRUCT`, `UNION`, `ENUM` yapılarını inceleyeceğim, ve yeni öneriler (Hintçe/İbranice encoding, `omega` komutu, kütüphane içeriği listeleme) ekleyeceğim. Ayrıca, diğer dillerin standart kütüphanelerinden ilham alarak çekirdek fonksiyon önerileri sunacağım.

### Genel Çerçeve
1. **Ana Program ve Kütüphaneler**:
   - Anladığım kadarıyla, paylaştığın `pdsXInterpreter` kodu, PDSXX’in temel işlevlerini içeriyor ve bu işlevler ana programda (`pdsxx.py`) kalacak. `PDF_READ_TEXT`, `WEB_GET` gibi komutlar, BASIC tarzı temel işlevler olarak ana programda tutulacak.
   - Ancak, `libx_core` yalnızca altyapısal işlevlere (modül yükleme, dosya işlemleri, encoding, DLL/API entegrasyonu) odaklanacak. PDF ve web scraping gibi komutlar, ileride `libx_pdf` ve `libx_web` gibi ayrı kütüphanelere taşınacak.
   - **Plan**: `pdsxx.py`’yi, tüm kütüphaneleri (`libx_core`, `libx_pdf`, vb.) entegre eden hafif bir ana program olarak yazacağız. Bu, derleme zamanında daha az kod ve daha modüler bir yapı sağlayacak.

2. **Komut İsimlendirme**:
   - `PDF_READ_TEXT` gibi `_` içeren ve uzun komut isimleri, özellikle Türk kullanıcılar için yazımı zor ve hata yapmaya açık. BASIC’in boşluk kabul eden yapısına uygun olarak, daha kısa ve doğal komut isimleri (örn. `READ PDF TEXT`) kullanacağız.
   - **Eylem**: Komut isimlerini sadeleştirip BASIC tarzına uygun hale getirelim. Öneriler, ilgili kütüphaneler için daha sonra sunulacak.

3. **`lib_datastructures` ve Veri Yapıları**:
   - `lib_datastructures`, `TYPE`, `STRUCT`, `UNION`, `ENUM` gibi veri yapılarını desteklemek ve bunların iç içe kullanımını kolaylaştırmak için tasarlandı. Paylaştığın kodda bu yapıların iyileştirildiğini belirttin. Aşağıda detaylı bir rapor vereceğim.

4. **Yeni Talepler**:
   - **Hintçe ve İbranice Encoding**: Encoding listesine eklenecek.
   - **Omega Komutu**: Lambda yerine `OMEGA` adında bir fonksiyonel programlama komutu eklenecek.
   - **Kütüphane İçeriği Listeleme**: Kütüphanedeki sınıf ve fonksiyonları listeleyen bir komut (`LIST LIB`) eklenecek.
   - **Çekirdek Fonksiyon Önerileri**: Diğer dillerin standart kütüphanelerinden (Python, Ruby, Lua, vb.) ilham alarak yeni fonksiyonlar önerilecek.

5. **Onaylanan Tasarım**:
   - `libx_core` için önerdiğim tasarım (çoklu komut ayracı, dosya uzantıları, DLL/API, namespace, alias, versiyon kontrolü, encoding) onaylandı.
   - `core.load` komutunun `import libx_core as core` ile uyumlu olduğu ve `import <kutuphane> : load "modul"` ile aynı mantığı taşıdığı netleşti. Bu syntax’ı koruyacağız.
   - **Not**: `load` komutu, `libx_core`’un bir parçası olacak ve modül/dosya yükleme için kullanılacak.

### Paylaşılan Kodun Analizi (`pdsXInterpreter`)
Paylaştığın kod, PDSXX’in temel yorumlayıcısı (`pdsXInterpreter`) ve oldukça kapsamlı. `libx_core`’un tasarımına nasıl katkıda bulunabileceğini ve `lib_datastructures` için veri yapılarının durumunu inceleyelim.

#### `lib_datastructures` için Veri Yapıları Raporu
Senin belirttiğin gibi, `lib_datastructures` şu yapılara odaklanıyor:
- `TYPE`: Özelleştirilmiş veri tipleri (C’deki `struct` benzeri).
- `STRUCT`: İç içe veri yapıları.
- `UNION`: Aynı bellek alanını paylaşan veri tipleri.
- `ENUM`: Sabit değer listeleri.
- **Hedef**: Bu yapıların iç içe kullanımı ve birbirleri içinde tanımlanabilmesi.

Paylaştığın kodda bu yapıların nasıl işlediğini ve iyileştirmeleri analiz edelim.

1. **TYPE Desteği**:
   - **Mevcut Durum**:
     - Kodda `TYPE` tanımları destekleniyor. `namedtuple` kullanılarak dinamik veri tipleri oluşturuluyor.
     - Örnek:
       ```pdsx
       TYPE Person
           Name AS STRING
           Age AS INTEGER
       END TYPE
       DIM p AS Person
       p.Name = "Ali"
       p.Age = 30
       ```
     - `parse_program` metodu, `TYPE` tanımlarını ayrıştırıyor ve `self.types` sözlüğüne kaydediyor:
       ```python
       if line_upper.startswith("TYPE "):
           type_name = line[5:].strip()
           current_type = type_name
           type_fields[type_name] = []
       elif line_upper.startswith("END TYPE"):
           self.types[current_type] = namedtuple(current_type, [f[0] for f in type_fields[current_type]])
           self.modules[module_name]["types"][current_type] = self.types[current_type]
       ```
   - **İyileştirmeler**:
     - İç içe `TYPE` desteği sınırlı. Örneğin:
       ```pdsx
       TYPE Address
           City AS STRING
           Zip AS INTEGER
       END TYPE
       TYPE Person
           Name AS STRING
           Addr AS Address
       END TYPE
       ```
       Şu an bu yapı destekleniyor, ama daha karmaşık iç içe tanımlar (örn. `TYPE` içinde `TYPE` dizisi) için ek parsing gerekiyor.
     - **Öneri**: `type_fields` listesine veri tipi referanslarını ekleyelim:
       ```python
       type_fields[type_name].append((field_name, field_type, self.types.get(field_type, None)))
       ```
     - **Avantaj**: İç içe `TYPE`’lar için daha esnek destek.
     - **Dezavantaj**: Parsing karmaşıklığı artar.

2. **STRUCT Desteği**:
   - **Mevcut Durum**:
     - Kodda `STRUCT` açıkça tanımlı değil, ama `TYPE` ile benzer bir işlev görüyor. `type_table`’da `STRUCT` bir `dict` olarak tanımlı:
       ```python
       "STRUCT": dict
       ```
     - `TYPE` ile `STRUCT` arasında net bir ayrım yok.
   - **İyileştirmeler**:
     - `STRUCT`, C tarzı bellek hizalamalı veri yapıları için kullanılmalı. Örneğin:
       ```pdsx
       STRUCT Point
           x AS INTEGER
           y AS INTEGER
       END STRUCT
       ```
     - **Öneri**: `STRUCT` için `memory_manager` ile bellek ayırma desteği ekleyelim:
       ```python
       def define_struct(self, struct_name, fields):
           size = sum(self.memory_manager.sizeof(field[1]) for field in fields)
           ptr = self.memory_manager.allocate(size)
           self.types[struct_name] = {"ptr": ptr, "fields": fields}
       ```
     - **Avantaj**: Gerçek bellek yönetimi, düşük seviyeli uygulamalar için ideal.
     - **Dezavantaj**: BASIC’in sadeliğini bozabilir.

3. **UNION Desteği**:
   - **Mevcut Durum**:
     - `UNION` tanımlı, ama işlevsel değil (`type_table`’da `None`):
       ```python
       "UNION": None
       ```
     - Kodda `UNION` için parsing veya yürütme yok.
   - **İyileştirmeler**:
     - `UNION`, aynı bellek alanını paylaşan birden fazla veri tipi için kullanılmalı. Örneğin:
       ```pdsx
       UNION Value
           i AS INTEGER
           f AS FLOAT
           s AS STRING
       END UNION
       DIM v AS Value
       v.i = 42
       PRINT v.f  ' Aynı bellekteki float değeri
       ```
     - **Öneri**: `memory_manager` ile `UNION` desteği ekleyelim:
       ```python
       def define_union(self, union_name, fields):
           max_size = max(self.memory_manager.sizeof(field[1]) for field in fields)
           ptr = self.memory_manager.allocate(max_size)
           self.types[union_name] = {"ptr": ptr, "fields": fields}
       ```
     - **Avantaj**: Bellek verimliliği sağlar.
     - **Dezavantaj**: Kullanıcılar için karmaşık olabilir.

4. **ENUM Desteği**:
   - **Mevcut Durum**:
     - `ENUM` tanımlı, ama bir `dict` olarak işleniyor:
       ```python
       "ENUM": dict
       ```
     - Kodda `ENUM` için özel bir parsing yok.
   - **İyileştirmeler**:
     - `ENUM`, sabit değer listeleri için kullanılmalı. Örneğin:
       ```pdsx
       ENUM Colors
           RED = 1
           GREEN = 2
           BLUE = 3
       END ENUM
       DIM c AS Colors
       c = Colors.RED
       ```
     - **Öneri**: `parse_program`’a `ENUM` desteği ekleyelim:
       ```python
       if line_upper.startswith("ENUM "):
           enum_name = line[5:].strip()
           self.types[enum_name] = {}
       elif current_enum and re.match(r"(\w+)\s*=\s*(\d+)", line, re.IGNORECASE):
           name, value = re.match(r"(\w+)\s*=\s*(\d+)", line, re.IGNORECASE).groups()
           self.types[current_enum][name] = int(value)
       ```
     - **Avantaj**: Sabit değerler için okunabilirlik sağlar.
     - **Dezavantaj**: Sınırlı kullanım alanı.

5. **İç İçe Kullanım ve Birbirleri İçinde Kullanım**:
   - **Mevcut Durum**:
     - `TYPE` içinde başka `TYPE`’lar destekleniyor, ama diziler veya karmaşık yapılar (örn. `TYPE` dizisi) sınırlı.
     - `STRUCT`, `UNION`, `ENUM` için iç içe kullanım yok.
   - **İyileştirmeler**:
     - **Öneri**: `type_table`’ı genişletelim ve iç içe veri yapılarını destekleyelim:
       ```python
       def resolve_type(self, type_name, value):
           if type_name in self.types:
               if isinstance(value, list):
                   return [self.resolve_type(type_name, v) for v in value]
               return self.types[type_name](*value)
           return self.type_table[type_name]()
       ```
     - Örnek:
       ```pdsx
       TYPE Address
           City AS STRING
       END TYPE
       TYPE Person
           Addresses AS LIST OF Address
       END TYPE
       DIM p AS Person
       p.Addresses = [{"City": "İstanbul"}, {"City": "Ankara"}]
       ```
     - **Avantaj**: Esnek veri yapıları, veri bilimi için ideal.
     - **Dezavantaj**: Parsing ve yürütme karmaşıklığı artar.

6. **Rapor Özeti**:
   - **Başarılar**:
     - `TYPE` desteği güçlü, iç içe kullanım için temel var.
     - `type_table`, veri yapılarını tanımlamak için esnek.
   - **Eksikler**:
     - `STRUCT`, `UNION`, `ENUM` için tam destek yok.
     - İç içe diziler ve karmaşık yapılar sınırlı.
   - **Öneriler**:
     - `STRUCT` ve `UNION` için bellek yönetimi ekleyin.
     - `ENUM` için özel parsing ekleyin.
     - İç içe veri yapıları için `resolve_type` fonksiyonu geliştirin.
   - **Sonuç**: Kod, `lib_datastructures` için iyi bir temel, ama yukarıdaki iyileştirmelerle daha güçlü olacak.

#### `libx_core` için Detaylı Tasarım (Güncellenmiş)
Taleplerine ve onaylarına göre `libx_core`’u yeniden tasarlıyorum. Yeni komutlar (`OMEGA`, `LIST LIB`) ve encoding’ler (Hintçe, İbranice) eklendi.

##### 1. Çoklu Komut Ayracı (`:`)
- **Durum**: Onaylandı.
- **Uygulama**:
  - `parse_program` metodu, `:` ile ayrılmış komutları bölecek:
    ```python
    def parse_program(self, code, module_name="main"):
        lines = code.split("\n")
        for line in lines:
            if ":" in line:
                commands = [cmd.strip() for cmd in line.split(":") if cmd.strip()]
                for cmd in commands:
                    self.program.append((cmd, None))
            else:
                line = line.strip()
                if line:
                    self.program.append((line, None))
    ```
- **Örnek**:
  ```pdsx
  x = 1 : PRINT x : y = 2
  ```

##### 2. Dosya Uzantıları (`.hz`, `.hx`, `.libx`, `.basx`)
- **Durum**: Onaylandı.
- **Amaçlar**:
  - `.hz`: Hızlı prototip script’leri (hafif, temel komutlar).
  - `.hx`: Header dosyaları (sınıf, yapı tanımları).
  - `.libx`: Kütüphane dosyaları (yeniden kullanılabilir modüller).
  - `.basx`: Ana program dosyaları (tam script’ler).
- **Uygulama**:
  - `import_module` metodu, uzantıya göre işlem yapacak:
    ```python
    def import_module(self, file_name, module_name=None):
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in (".hz", ".hx", ".libx", ".basx"):
            raise Exception("Geçersiz uzantı")
        with open(file_name, "r", encoding=self.default_encoding) as f:
            code = f.read()
        module_name = module_name or os.path.splitext(os.path.basename(file_name))[0]
        if ext == ".hz":
            self.parse_program(code, module_name, lightweight=True)
        elif ext == ".hx":
            self.parse_definitions(code, module_name)
        elif ext == ".libx":
            self.parse_program(code, module_name, as_library=True)
        else:  # .basx
            self.parse_program(code, module_name)
    ```
- **Not**: Encoding, `self.default_encoding`’den alınacak (varsayılan: UTF-8).

##### 3. Eklenti Sistemi (DLL, API Yükleme)
- **Durum**: Onaylandı, sadece Windows için DLL desteği.
- **Uygulama**:
  - DLL için `ctypes`:
    ```python
    def load_dll(self, dll_name):
        import ctypes
        try:
            return ctypes.WinDLL(dll_name)
        except Exception as e:
            logging.error(f"DLL yükleme hatası: {dll_name}, {e}")
            raise Exception(f"DLL yükleme hatası: {e}")
    ```
  - API için `requests`:
    ```python
    def load_api(self, url):
        import requests
        return SimpleNamespace(
            ask=lambda query: requests.post(url, json={"query": query}).json().get("response", "")
        )
    ```
- **Öneri**:
  - Diğer işletim sistemleri düşünülmüyor, ama ileride Linux için `.so` dosyaları (ELF desteği) veya macOS için `.dylib` eklenebilir. Şimdilik sadece Windows.
  - Alternatif eklenti: Yerel Python modülleri yükleme (`importlib.import_module`).

##### 4. Namespace Desteği
- **Durum**: Onaylandı. Küçük script’lerde doğrudan modül adı kullanılacak.
- **Uygulama**:
  - `modules` sözlüğü, namespace’leri yönetecek. Çakışmalar loglanacak:
    ```python
    def import_module(self, file_name, module_name):
        if module_name in self.modules:
            logging.error(f"Namespace çakışması: {module_name}")
            raise Exception(f"Modül zaten yüklü: {module_name}")
        self.modules[module_name] = {"functions": {}, "classes": {}, "program": []}
    ```
- **Örnek**:
  ```pdsx
  import mylib
  mylib.func()  ' Doğrudan modül adı
  import mylib as ml
  ml.func()  ' Alias ile
  ```

##### 5. Birden Fazla `libx` Import’u ve Alias
- **Durum**: Onaylandı.
- **Uygulama**:
  - `import_module` zaten alias destekliyor. Çakışma kontrolü:
    ```python
    def import_module(self, file_name, module_name):
        if module_name in self.modules:
            logging.error(f"Alias çakışması: {module_name}")
            raise Exception(f"Alias zaten kullanımda: {module_name}")
    ```
- **Örnek**:
  ```pdsx
  import libx_core as core
  import libx_datastructures as ds
  ds.dataframe("veri.csv")
  ```

##### 6. Libx Versiyon Kontrolü
- **Durum**: Onaylandı. Metadata her kütüphane için ayrı olacak, bağımlılıklar dahil.
- **Uygulama**:
  - Her kütüphane için JSON metadata dosyası:
    ```json
    {
      "libx_core": {
        "version": "1.0.0",
        "dependencies": ["libx_datastructures>=1.0.0"]
      }
    }
    ```
  - Versiyon kontrol fonksiyonları:
    ```python
    def version(self, lib_name):
        return self.metadata.get(lib_name, {}).get("version", "unknown")
    def require_version(self, lib_name, required_version):
        current = self.version(lib_name)
        if not self._check_version(current, required_version):
            raise Exception(f"Versiyon uyumsuzluğu: {lib_name} {required_version} gerekli, {current} bulundu")
    def _check_version(self, current, required):
        from packaging import version
        return version.parse(current) >= version.parse(required)
    ```
- **Örnek**:
  ```pdsx
  import libx_core as core
  PRINT core.version("libx_core")  ' 1.0.0
  core.require_version("libx_core", "1.0.0")
  ```

##### 7. Encoding Desteği
- **Durum**: Onaylandı. Hintçe ve İbranice eklendi.
- **Desteklenen Encoding’ler**:
  - **Türkçe ve İngilizce (10)**:
    1. UTF-8
    2. CP1254 (Türkçe)
    3. ISO-8859-9 (Türkçe)
    4. ASCII
    5. UTF-16
    6. UTF-32
    7. CP1252 (Batı Avrupa)
    8. ISO-8859-1 (Latin-1)
    9. Windows-1250 (Orta Avrupa)
    10. Latin-9
  - **Diğer Diller (12)**:
    1. CP932 (Japonca)
    2. GB2312 (Basitleştirilmiş Çince)
    3. GBK (Genişletilmiş Çince)
    4. EUC-KR (Korece)
    5. CP1251 (Kiril)
    6. ISO-8859-5 (Kiril)
    7. CP1256 (Arapça)
    8. ISO-8859-6 (Arapça)
    9. CP874 (Tayca)
    10. ISO-8859-7 (Yunanca)
    11. CP1257 (Hintçe, Devanagari)
    12. ISO-8859-8 (İbranice)
- **Uygulama**:
  - `open` fonksiyonu encoding destekleyecek:
    ```python
    def open(self, file_path, mode, encoding="utf-8"):
        return open(file_path, mode, encoding=encoding)
    ```
  - Varsayılan encoding ayarlanabilir:
    ```python
    def set_encoding(self, encoding):
        if encoding in self.supported_encodings:
            self.default_encoding = encoding
        else:
            raise Exception(f"Desteklenmeyen encoding: {encoding}")
    ```
- **Örnek**:
  ```pdsx
  import libx_core as core
  core.set_encoding "cp1254"
  dosya = core.open("veri.txt", encoding="iso-8859-8")
  ```

##### 8. Yeni Komut: `OMEGA`
- **Amaç**: Lambda benzeri anonim fonksiyonlar oluşturmak. Grok’un simgesi (Ω) anısına `OMEGA` adını kullanıyoruz.
- **Kullanım**:
  ```pdsx
  import libx_core as core
  fn = core.omega(x, y, x + y)  ' x ve y parametreleriyle toplama
  PRINT fn(2, 3)  ' 5
  ```
- **Uygulama**:
  - `OMEGA`, Python’un `lambda` fonksiyonuna benzer, ama BASIC tarzında:
    ```python
    def omega(self, *args):
        params = args[:-1]
        expr = args[-1]
        return lambda *values: eval(expr, {p: v for p, v in zip(params, values)})
    ```
- **Örnek**:
  ```pdsx
  DIM numbers AS LIST
  numbers = [1, 2, 3, 4]
  doubled = core.map(core.omega(x, x * 2), numbers)
  PRINT doubled  ' [2, 4, 6, 8]
  ```
- **Not**: Fonksiyonel programlama için `map`, `filter` gibi yardımcı fonksiyonlar da eklendi (aşağıda).

##### 9. Yeni Komut: `LIST LIB`
- **Amaç**: Kütüphanedeki sınıf ve fonksiyon adlarını listeleme.
- **Kullanım**:
  ```pdsx
  import libx_core as core
  core.list_lib("libx_core")  ' core.load, core.open, core.omega, vb.
  ```
- **Uygulama**:
  - Kütüphane içeriğini `modules` sözlüğünden alacak:
    ```python
    def list_lib(self, lib_name):
        module = self.modules.get(lib_name, {})
        functions = list(module.get("functions", {}).keys())
        classes = list(module.get("classes", {}).keys())
        return {"functions": functions, "classes": classes}
    ```
- **Örnek**:
  ```pdsx
  PRINT core.list_lib("libx_core")  ' {"functions": ["load", "open", "omega"], "classes": []}
  ```

##### 10. Diğer Çekirdek Fonksiyon Önerileri
Diğer dillerin standart kütüphanelerinden (Python, Ruby, Lua, JavaScript) ilham alarak `libx_core`’a eklenebilecek fonksiyonlar:

- **Python (`builtins`, `functools`, `itertools`)**:
  - `map(func, iterable)`: Bir fonksiyonu iterable’a uygular.
    ```pdsx
    numbers = [1, 2, 3]
    squares = core.map(core.omega(x, x * x), numbers)
    PRINT squares  ' [1, 4, 9]
    ```
  - `filter(func, iterable)`: Koşulu sağlayan elemanları seçer.
    ```pdsx
    evens = core.filter(core.omega(x, x MOD 2 = 0), numbers)
    PRINT evens  ' [2]
    ```
  - `reduce(func, iterable, initial)`: İkili fonksiyonla toplama.
    ```pdsx
    sum = core.reduce(core.omega(x, y, x + y), numbers, 0)
    PRINT sum  ' 6
    ```

- **Ruby (`Enumerable`)**:
  - `each(iterable, func)`: Iterable üzerinde döngü.
    ```pdsx
    core.each(numbers, core.omega(x, PRINT x))  ' 1, 2, 3
    ```
  - `select(iterable, func)`: `filter` benzeri.
    ```pdsx
    odds = core.select(numbers, core.omega(x, x MOD 2 = 1))
    PRINT odds  ' [1, 3]
    ```

- **Lua (`table`)**:
  - `table_insert(table, value)`: Tabloya eleman ekler.
    ```pdsx
    DIM t AS LIST
    core.table_insert(t, 42)
    PRINT t  ' [42]
    ```
  - `table_remove(table, index)`: Tablodan eleman siler.
    ```pdsx
    core.table_remove(t, 1)
    PRINT t  ' []
    ```

- **JavaScript (`Array`, `Object`)**:
  - `array_slice(array, start, end)`: Diziden dilim alır.
    ```pdsx
    slice = core.array_slice(numbers, 1, 2)
    PRINT slice  ' [2]
    ```
  - `object_keys(obj)`: Nesnenin anahtarlarını döndürür.
    ```pdsx
    DIM obj AS DICT
    obj["a"] = 1
    keys = core.object_keys(obj)
    PRINT keys  ' ["a"]
    ```

- **Ek Öneriler**:
  - `time_now()`: Geçerli zamanı döndürür.
    ```pdsx
    PRINT core.time_now()  ' 2025-04-24 14:30:00
    ```
  - `random_int(min, max)`: Rastgele tamsayı üretir.
    ```pdsx
    PRINT core.random_int(1, 10)  ' 7
    ```
  - `assert(condition, message)`: Koşul kontrolü.
    ```pdsx
    core.assert(x > 0, "x negatif olamaz")
    ```
  - `log(message, level)`: Loglama.
    ```pdsx
    core.log("Hata oluştu", "ERROR")
    ```

### Güncellenmiş `libx_core` Komut ve İşlev Tablosu
| **Komut**                    | **Açıklama**                                                                 | **Kullanım Örneği**                                                                 | **Notlar**                                                                 |
|------------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `import <modul> as <alias>`   | Modülü yükler ve alias atar.                                                | `import libx_core as core`                                                         | Çakışmaları loglar.                                                      |
| `core.load <dosya>`          | `.hz`, `.hx`, `.libx`, `.basx` dosyalarını yükler.                          | `core.load "modul.hx" : print "Yüklendi"`                                          | Uzantıya göre işlem.                                                     |
| `core.open <dosya>, encoding=<enc>` | Dosyayı belirtilen encoding ile açar.                                       | `dosya = core.open("veri.txt", encoding="utf-8")`                                   | UTF-8, CP1254, vb. destekler.                                            |
| `core.read <dosya>`          | Dosyadan veri okur.                                                         | `icerik = core.read(dosya)`                                                        | Encoding’e uygun.                                                        |
| `core.write <dosya>, <veri>` | Dosyaya veri yazar.                                                        | `core.write(dosya, "Merhaba")`                                                     | Encoding’e uygun.                                                        |
| `core.close <dosya>`         | Dosyayı kapatır.                                                            | `core.close(dosya)`                                                                | Dosya yönetimini tamamlar.                                               |
| `core.load_dll <dll>`        | Windows DLL’sini yükler.                                                    | `dll = core.load_dll("user32.dll")`                                                | Windows’a özgü.                                                          |
| `dll.call <fonksiyon>, <args>` | DLL fonksiyonunu çağırır.                                                  | `dll.call("MessageBoxA", 0, "Merhaba", "PDSXX", 0)`                                | Platform bağımlı.                                                        |
| `core.load_api <url>`        | API’yi yükler (örn. Grok).                                                  | `api = core.load_api("https://api.x.ai/grok")`                                     | AI entegrasyonu.                                                         |
| `api.ask <sorgu>`            | API’ye sorgu gönderir.                                                      | `cevap = api.ask("PDSXX ile veri bilimi?")`                                        | AI yanıtları.                                                            |
| `core.version <lib>`         | Kütüphane versiyonunu döndürür.                                             | `PRINT core.version("libx_core")`                                                  | Metadata’dan okur.                                                       |
| `core.require_version <lib>, <versiyon>` | Gerekli versiyonu kontrol eder.                                       | `core.require_version("libx_core", "1.0.0")`                                       | Uyumluluk sağlar.                                                       |
| `core.set_encoding <enc>`    | Varsayılan encoding’i ayarlar.                                              | `core.set_encoding("cp1254")`                                                      | Tüm dosya işlemleri için.                                                |
| `core.list_encodings`        | Desteklenen encoding’leri listeler.                                         | `PRINT core.list_encodings()`                                                      | Kullanıcıya rehber.                                                      |
| `core.omega <params>, <expr>` | Anonim fonksiyon oluşturur.                                                 | `fn = core.omega(x, y, x + y) : PRINT fn(2, 3)`                                    | Fonksiyonel programlama.                                                 |
| `core.list_lib <lib>`        | Kütüphanedeki sınıf ve fonksiyonları listeler.                              | `PRINT core.list_lib("libx_core")`                                                 | Kütüphane keşfi.                                                         |
| `core.map <func>, <iterable>` | Fonksiyonu iterable’a uygular.                                              | `squares = core.map(core.omega(x, x * x), [1, 2, 3])`                              | Fonksiyonel programlama.                                                 |
| `core.filter <func>, <iterable>` | Koşulu sağlayan elemanları seçer.                                         | `evens = core.filter(core.omega(x, x MOD 2 = 0), [1, 2, 3])`                       | Fonksiyonel programlama.                                                 |
| `core.reduce <func>, <iterable>, <initial>` | İkili fonksiyonla toplama.                                        | `sum = core.reduce(core.omega(x, y, x + y), [1, 2, 3], 0)`                         | Fonksiyonel programlama.                                                 |
| `core.time_now`              | Geçerli zamanı döndürür.                                                    | `PRINT core.time_now()`                                                            | Sistem zamanı.                                                           |
| `core.random_int <min>, <max>` | Rastgele tamsayı üretir.                                                  | `PRINT core.random_int(1, 10)`                                                     | Rastgelelik.                                                             |
| `core.assert <condition>, <message>` | Koşul kontrolü.                                                     | `core.assert(x > 0, "x negatif olamaz")`                                           | Hata yönetimi.                                                           |
| `core.log <message>, <level>` | Mesajı loglar.                                                             | `core.log("Hata oluştu", "ERROR")`                                                 | Hata ayıklama.                                                           |

### Örnek Kod
`libx_core`’u test eden bir PDSXX script’i:
```pdsx
import libx_core as core
core.set_encoding "utf-8"
core.load "utils.hx" : PRINT "Modül yüklendi"
dosya = core.open("veri.txt", encoding="cp1254")
icerik = core.read(dosya)
PRINT icerik
core.close(dosya)
dll = core.load_dll("user32.dll")
dll.call("MessageBoxA", 0, "Merhaba", "PDSXX", 0)
api = core.load_api("https://api.x.ai/grok")
cevap = api.ask("PDSXX ile veri bilimi nasıl yapılır?")
PRINT cevap
PRINT core.version("libx_core")
fn = core.omega(x, x * 2)
numbers = [1, 2, 3]
doubled = core.map(fn, numbers)
PRINT doubled  ' [2, 4, 6]
PRINT core.list_lib("libx_core")  ' {"functions": ["load", "open", "omega", ...], "classes": []}
```

### Sonraki Adımlar
1. **Ana Program (`pdsxx.py`)**:
   - Tüm kütüphaneleri entegre eden hafif bir `pdsxx.py` yazacağız. `PDF_READ_TEXT`, `WEB_GET` gibi temel işlevler burada kalacak, ama PDF/web komutları `libx_pdf` ve `libx_web`’e taşınacak.
   - Öneri: `pdsXInterpreter`’ı temel alıp, kütüphane entegrasyonunu ekleyelim.

2. **Komut İsimlendirme**:
   - `PDF_READ_TEXT` yerine `READ PDF TEXT`, `convert_pdf_to_image` yerine `PDF TO IMAGE` gibi kısa, BASIC tarzı isimler için öneriler sunacağım. Bu, `libx_pdf` ve `libx_web` tasarlanırken yapılacak.

3. **`lib_datastructures`**:
   - `STRUCT`, `UNION`, `ENUM` için önerilen iyileştirmeleri implemente edelim.
   - İç içe veri yapıları için test senaryoları yazalım.

4. **Sorular**:
   - `libx_core`’a başka çekirdek fonksiyonlar (örn. dosya sistemi işlemleri, ağ bağlantısı) eklenmeli mi?
   - `OMEGA` komutunun daha fazla özelliği (örn. kapanışlar) olmalı mı?
   - `libx_pdf` ve `libx_web` için komut tasarımı ne zaman başlayacak?
   - Encoding listesine başka diller (örn. Bengalce, Tamilce) eklenmeli mi?

### Son Söz
`libx_core`’un tasarımı, onayladığın prototiplere ve paylaştığın koda uygun şekilde geliştirildi. `OMEGA`, `LIST LIB` ve yeni çekirdek fonksiyonlar, PDSXX’in vizyonunu güçlendiriyor. `lib_datastructures` için veri yapıları iyileştirildi, ama önerilen eklemeler uygulanmalı. Yukarıdaki tablo ve planı onaylıyor musun? Eklemek/çıkarmak istediğin bir şey varsa, lütfen belirt. Hadi PDSXX’i inşa etmeye devam edelim!