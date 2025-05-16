Teşekkürler, geri bildirimin için! `libx_core`’un mevcut tasarımının sağlam bir temel oluşturduğunu görüyorum, ancak daha fazla özellik ve işlevsellik ekleyerek PDSXX’in çekirdek kütüphanesini daha kapsamlı ve güçlü hale getirebiliriz. Aşağıda, önceki onayladığın tasarıma (çoklu komut ayracı, dosya uzantıları, DLL/API, namespace, encoding, `omega`, `ifthen`, vb.) ek olarak, diğer dillerin standart kütüphanelerinden ve PDSXX’in veri bilimi odaklı vizyonundan ilham alarak yeni öneriler sunacağım. Ayrıca, PDSXX’in `pdsXInterpreter` kodundaki mevcut komutları dikkate alarak `libx_core`’u nasıl genişletebileceğimizi değerlendireceğim. Öneriler, BASIC’in sadeliğini korurken modern programlama ihtiyaçlarını karşılamaya odaklanacak.

### Mevcut Durumun Özeti
- **Onaylanan Özellikler**:
  - Çoklu komut ayracı (`:`), dosya uzantıları (`.hz`, `.hx`, `.libx`, `.basx`), DLL/API yükleme, namespace, alias, versiyon kontrolü, encoding (Hintçe ve İbranice dahil).
  - Yeni komutlar: `omega` (global ve `core.omega`), `list_lib`, `each`, `select`, `insert`, `remove`, `pop`, `clear`, `slice`, `keys`, `ifthen`, `time_now`, `date_now`, `timer`, `random_int`, `assert`, `log`, `exists`, `mkdir`, `getenv`, `exit`, `join_path`, `copy_file`, `move_file`, `delete_file`, `floor`, `ceil`, `split`, `join`.
  - `PDF_READ_TEXT`, `WEB_GET` gibi komutlar ana programda (`pdsxx.py`) kalacak, ancak ileride `libx_pdf` ve `libx_web`’e taşınacak.
  - `lib_datastructures` için `TYPE`, `STRUCT`, `UNION`, `ENUM` iyileştirmeleri önerildi.

- **Eksik veya Genişletilebilir Alanlar**:
  - Daha fazla dosya sistemi ve ağ işlevleri.
  - Matematiksel ve istatistiksel fonksiyonlar (veri bilimi için).
  - String ve veri yapısı manipülasyonu.
  - Hata yönetimi ve debugging araçları.
  - Zaman ve tarih işlemleri için ek fonksiyonlar.
  - Paralel programlama veya asenkron işlemler için temel destek.
  - Diğer dillerden ilham alan pratik araçlar.

### Yeni Öneri Kategorileri ve Detaylar
Aşağıda, `libx_core`’a eklenebilecek yeni fonksiyonları kategorilere ayırarak sunuyorum. Her öneri, PDSXX’in BASIC tarzı sadeliğine uygun olacak ve veri bilimi, prototipleme veya genel programlama ihtiyaçlarını destekleyecek. Öneriler, Python, Ruby, Lua, Go, JavaScript, C++, Rust gibi dillerin standart kütüphanelerinden ve modern programlama trendlerinden ilham alıyor.

#### 1. Dosya Sistemi ve I/O İşlevleri
PDSXX’in veri bilimi odaklı yapısı, dosya işlemlerini sık kullanır (örn. CSV, PDF, JSON). Mevcut `open`, `read`, `write`, `close`’a ek olarak:
- `core.read_lines(path)`: Dosyayı satır satır okur.
  - **Amaç**: Büyük dosyaları bellek dostu şekilde işlemek.
  - **Örnek**:
    ```pdsx
    import libx_core as core
    lines = core.read_lines("veri.txt")
    FOR line IN lines
        PRINT line
    NEXT
    ```
  - **Uygulama**:
    ```python
    def read_lines(self, path):
        with open(path, "r", encoding=self.default_encoding) as f:
            return f.readlines()
    ```
- `core.write_json(obj, path)`: Nesneyi JSON olarak dosyaya yazar.
  - **Amaç**: Veri bilimi projelerinde JSON verilerini kaydetmek.
  - **Örnek**:
    ```pdsx
    DIM data AS DICT
    data["name"] = "Ali"
    core.write_json(data, "veri.json")
    ```
  - **Uygulama**:
    ```python
    def write_json(self, obj, path):
        import json
        with open(path, "w", encoding=self.default_encoding) as f:
            json.dump(obj, f)
    ```
- `core.read_json(path)`: JSON dosyasını okur.
  - **Örnek**:
    ```pdsx
    data = core.read_json("veri.json")
    PRINT data["name"]  ' Ali
    ```
  - **Uygulama**:
    ```python
    def read_json(self, path):
        import json
        with open(path, "r", encoding=self.default_encoding) as f:
            return json.load(f)
    ```
- `core.list_dir(path)`: Dizindeki dosyaları listeler.
  - **Amaç**: Veri dosyalarını taramak.
  - **Örnek**:
    ```pdsx
    files = core.list_dir("data")
    FOR file IN files
        PRINT file
    NEXT
    ```
  - **Uygulama**:
    ```python
    def list_dir(self, path):
        import os
        return os.listdir(path)
    ```

#### 2. Ağ ve HTTP İşlevleri
`WEB_GET` ana programda kalacak, ama `libx_core`’a temel ağ işlevleri ekleyebiliriz (ileride `libx_web`’e taşınabilir).
- `core.download(url, path)`: URL’den dosya indirir.
  - **Amaç**: Veri bilimi için veri setlerini çekmek.
  - **Örnek**:
    ```pdsx
    core.download("https://ornek.com/veri.csv", "veri.csv")
    ```
  - **Uygulama**:
    ```python
    def download(self, url, path):
        import requests
        response = requests.get(url)
        with open(path, "wb") as f:
            f.write(response.content)
    ```
- `core.ping(host)`: Host’un erişilebilirliğini kontrol eder.
  - **Amaç**: Ağ bağlantısını test etmek.
  - **Örnek**:
    ```pdsx
    IF core.ping("google.com") THEN PRINT "Bağlantı var"
    ```
  - **Uygulama**:
    ```python
    def ping(self, host):
        import socket
        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False
    ```

#### 3. Matematiksel ve İstatistiksel Fonksiyonlar
PDSXX, veri bilimi için tasarlandı (Zotaix, Örümcek). Mevcut `floor`, `ceil`’e ek olarak:
- `core.sum(iterable)`: Iterable’ın toplamını hesaplar.
  - **Örnek**:
    ```pdsx
    numbers = [1, 2, 3]
    total = core.sum(numbers)
    PRINT total  ' 6
    ```
  - **Uygulama**:
    ```python
    def sum(self, iterable):
        return sum(iterable)
    ```
- `core.mean(iterable)`: Ortalamayı hesaplar.
  - **Örnek**:
    ```pdsx
    avg = core.mean(numbers)
    PRINT avg  ' 2
    ```
  - **Uygulama**:
    ```python
    def mean(self, iterable):
        return sum(iterable) / len(iterable) if iterable else 0
    ```
- `core.min(iterable)` ve `core.max(iterable)`: Minimum ve maksimum değerleri bulur.
  - **Örnek**:
    ```pdsx
    PRINT core.min(numbers)  ' 1
    PRINT core.max(numbers)  ' 3
    ```
  - **Uygulama**:
    ```python
    def min(self, iterable):
        return min(iterable) if iterable else None
    def max(self, iterable):
        return max(iterable) if iterable else None
    ```
- `core.round(x, digits)`: Sayıyı yuvarlar.
  - **Örnek**:
    ```pdsx
    PRINT core.round(3.14159, 2)  ' 3.14
    ```
  - **Uygulama**:
    ```python
    def round(self, x, digits=0):
        return round(x, digits)
    ```

#### 4. String Manipülasyonu
PDSXX’in mevcut `LEFT`, `RIGHT`, `MID` gibi string fonksiyonlarına ek olarak:
- `core.trim(str)`: Baştaki ve sondaki boşlukları kaldırır.
  - **Örnek**:
    ```pdsx
    text = "  Merhaba  "
    PRINT core.trim(text)  ' Merhaba
    ```
  - **Uygulama**:
    ```python
    def trim(self, s):
        return s.strip()
    ```
- `core.replace(str, old, new)`: String’de değiştirme yapar.
  - **Örnek**:
    ```pdsx
    text = "Merhaba Dünya"
    new_text = core.replace(text, "Dünya", "PDSXX")
    PRINT new_text  ' Merhaba PDSXX
    ```
  - **Uygulama**:
    ```python
    def replace(self, s, old, new):
        return s.replace(old, new)
    ```
- `core.format(str, *args)`: String formatlama (Python’un `str.format`’u gibi).
  - **Örnek**:
    ```pdsx
    text = core.format("Merhaba {0}, yaş: {1}", "Ali", 30)
    PRINT text  ' Merhaba Ali, yaş: 30
    ```
  - **Uygulama**:
    ```python
    def format(self, s, *args):
        return s.format(*args)
    ```

#### 5. Hata Yönetimi ve Debugging
Mevcut `assert` ve `log`’a ek olarak:
- `core.trace()`: Çalışma zamanı yığın izini döndürür.
  - **Amaç**: Hata ayıklamada kullanılır.
  - **Örnek**:
    ```pdsx
    PRINT core.trace()  ' Mevcut çağrı yığını
    ```
  - **Uygulama**:
    ```python
    def trace(self):
        import traceback
        return traceback.format_stack()
    ```
- `core.try_catch(block, handler)`: Hata yakalama mekanizması.
  - **Amaç**: BASIC’in `ON ERROR GOTO`’suna alternatif, modern hata yönetimi.
  - **Örnek**:
    ```pdsx
    core.try_catch(
        omega(), 10 / 0,  ' Hatalı işlem
        omega(e), PRINT "Hata: " + e  ' Hata işleyici
    )
    ```
  - **Uygulama**:
    ```python
    def try_catch(self, block, handler):
        try:
            return block()
        except Exception as e:
            return handler(str(e))
    ```

#### 6. Zaman ve Tarih İşlevleri
Mevcut `time_now`, `date_now`, `timer`’a ek olarak:
- `core.sleep(seconds)`: Programı belirtilen süre duraklatır.
  - **Örnek**:
    ```pdsx
    PRINT "Başla"
    core.sleep(2)
    PRINT "2 saniye sonra"
    ```
  - **Uygulama**:
    ```python
    def sleep(self, seconds):
        import time
        time.sleep(seconds)
    ```
- `core.date_diff(date1, date2, unit)`: İki tarih arasındaki farkı hesaplar.
  - **Örnek**:
    ```pdsx
    diff = core.date_diff("2025-04-24", "2025-04-26", "days")
    PRINT diff  ' 2
    ```
  - **Uygulama**:
    ```python
    def date_diff(self, date1, date2, unit="days"):
        from datetime import datetime
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        delta = d2 - d1
        if unit == "days":
            return delta.days
        elif unit == "seconds":
            return delta.total_seconds()
        raise Exception("Geçersiz birim")
    ```

#### 7. Paralel ve Asenkron İşlemler
PDSXX’in hızlı prototipleme için hafif bir paralel işlem desteği olabilir.
- `core.run_async(func)`: Fonksiyonu asenkron çalıştırır.
  - **Amaç**: Ağ çağrıları veya uzun işlemler için.
  - **Örnek**:
    ```pdsx
    result = core.run_async(omega(), core.download("https://ornek.com/veri.csv", "veri.csv"))
    PRINT "İndirme başladı"
    ```
  - **Uygulama**:
    ```python
    def run_async(self, func):
        from threading import Thread
        t = Thread(target=func)
        t.start()
        return t
    ```
- `core.wait(tasks)`: Asenkron görevlerin tamamlanmasını bekler.
  - **Örnek**:
    ```pdsx
    tasks = [core.run_async(omega(), PRINT "Görev 1"), core.run_async(omega(), PRINT "Görev 2")]
    core.wait(tasks)
    PRINT "Tüm görevler bitti"
    ```
  - **Uygulama**:
    ```python
    def wait(self, tasks):
        for t in tasks:
            t.join()
    ```

#### 8. Veri Yapısı Manipülasyonu
`insert`, `remove`, `slice`, `keys`’e ek olarak:
- `core.merge(col1, col2)`: İki koleksiyonu birleştirir (`LIST` veya `DICT`).
  - **Örnek**:
    ```pdsx
    lst1 = [1, 2]
    lst2 = [3, 4]
    merged = core.merge(lst1, lst2)
    PRINT merged  ' [1, 2, 3, 4]
    d1 = {"x": 1}
    d2 = {"y": 2}
    merged_dict = core.merge(d1, d2)
    PRINT merged_dict  ' {"x": 1, "y": 2}
    ```
  - **Uygulama**:
    ```python
    def merge(self, col1, col2):
        if isinstance(col1, list) and isinstance(col2, list):
            return col1 + col2
        elif isinstance(col1, dict) and isinstance(col2, dict):
            return {**col1, **col2}
        raise Exception("Geçersiz veri tipi")
    ```
- `core.sort(iterable, key=None)`: Iterable’ı sıralar.
  - **Örnek**:
    ```pdsx
    numbers = [3, 1, 2]
    sorted_nums = core.sort(numbers)
    PRINT sorted_nums  ' [1, 2, 3]
    ```
  - **Uygulama**:
    ```python
    def sort(self, iterable, key=None):
        return sorted(iterable, key=key)
    ```

#### 9. Sistem ve Performans İzleme
- `core.memory_usage()`: Programın bellek kullanımını döndürür.
  - **Amaç**: Veri bilimi projelerinde performans izleme.
  - **Örnek**:
    ```pdsx
    PRINT core.memory_usage()  ' 50.2 MB
    ```
  - **Uygulama**:
    ```python
    def memory_usage(self):
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB cinsinden
    ```
- `core.cpu_count()`: CPU çekirdek sayısını döndürür.
  - **Örnek**:
    ```pdsx
    PRINT core.cpu_count()  ' 8
    ```
  - **Uygulama**:
    ```python
    def cpu_count(self):
        import multiprocessing
        return multiprocessing.cpu_count()
    ```

#### 10. Çeşitli Yardımcı Fonksiyonlar
- `core.type_of(value)`: Değişkenin tipini döndürür.
  - **Örnek**:
    ```pdsx
    PRINT core.type_of(42)  ' INTEGER
    PRINT core.type_of("Merhaba")  ' STRING
    ```
  - **Uygulama**:
    ```python
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
    ```
- `core.is_empty(collection)`: Koleksiyonun boş olup olmadığını kontrol eder.
  - **Örnek**:
    ```pdsx
    DIM lst AS LIST
    IF core.is_empty(lst) THEN PRINT "Boş"
    ```
  - **Uygulama**:
    ```python
    def is_empty(self, collection):
        return len(collection) == 0
    ```

### PDSXX Komutlarıyla Entegrasyon
Paylaştığın `pdsXInterpreter` kodundaki komutlar, `libx_core`’a şu şekilde entegre edilebilir:
- **Mevcut Komutlar**:
  - `PRINT`, `INPUT`, `IF`, `FOR`, `GOTO`, `GOSUB`, `DIM`, `LET` gibi BASIC komutları ana programda (`pdsxx.py`) kalacak.
  - `OPEN`, `READ`, `WRITE`, `CLOSE` zaten `libx_core`’da (`core.open`, `core.read`, vb.).
  - `RND` ile `core.random_int` uyumlu, ikisi de kalabilir.
- **Eksik Komutlar**:
  - `LEN`, `LEFT`, `RIGHT`, `MID` gibi string fonksiyonları `libx_core`’a taşınabilir:
    ```pdsx
    PRINT core.len("Merhaba")  ' 7
    PRINT core.left("Merhaba", 3)  ' Mer
    ```
  - `VAL`, `STR` gibi tip dönüştürme fonksiyonları:
    ```pdsx
    PRINT core.val("42")  ' 42
    PRINT core.str(42)  ' "42"
    ```
- **Öneri**: `libx_core`, PDSXX’in temel komutlarını (`LEN`, `VAL`, vb.) desteklemeli, ama veri bilimi komutları (`PDF_READ_TEXT`) `libx_pdf`’e taşınmalı.

### Güncellenmiş `libx_core` Komut ve İşlev Tablosu
Mevcut tabloya yeni öneriler eklendi. Sadece yeni ve değiştirilen komutları listeliyorum (tam tablo için önceki mesajlara bakılabilir):
| **Komut**                           | **Açıklama**                                                                 | **Kullanım Örneği**                                                                 | **Notlar**                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `core.read_lines <path>`            | Dosyayı satır satır okur.                                                   | `lines = core.read_lines("veri.txt")`                                              | Büyük dosyalar için.                                                     |
| `core.write_json <obj>, <path>`     | Nesneyi JSON olarak dosyaya yazar.                                          | `core.write_json({"x": 1}, "veri.json")`                                           | Veri bilimi için.                                                        |
| `core.read_json <path>`             | JSON dosyasını okur.                                                        | `data = core.read_json("veri.json")`                                               | Veri bilimi için.                                                        |
| `core.list_dir <path>`              | Dizindeki dosyaları listeler.                                               | `files = core.list_dir("data")`                                                    | Dosya tarama.                                                            |
| `core.download <url>, <path>`       | URL’den dosya indirir.                                                      | `core.download("https://ornek.com/veri.csv", "veri.csv")`                          | Ağ işlemleri.                                                            |
| `core.ping <host>`                  | Host’un erişilebilirliğini kontrol eder.                                    | `IF core.ping("google.com") THEN PRINT "Bağlantı var"`                             | Ağ testi.                                                                |
| `core.sum <iterable>`               | Iterable’ın toplamını hesaplar.                                             | `total = core.sum([1, 2, 3])`                                                     | Matematik.                                                               |
| `core.mean <iterable>`              | Ortalamayı hesaplar.                                                        | `avg = core.mean([1, 2, 3])`                                                      | İstatistik.                                                              |
| `core.min <iterable>`               | Minimum değeri bulur.                                                       | `PRINT core.min([1, 2, 3])`                                                       | İstatistik.                                                              |
| `core.max <iterable>`               | Maksimum değeri bulur.                                                      | `PRINT core.max([1, 2, 3])`                                                       | İstatistik.                                                              |
| `core.round <x>, <digits>`          | Sayıyı yuvarlar.                                                            | `PRINT core.round(3.14159, 2)`                                                    | Matematik.                                                               |
| `core.trim <str>`                   | Baştaki ve sondaki boşlukları kaldırır.                                     | `PRINT core.trim("  Merhaba  ")`                                                  | String işleme.                                                           |
| `core.replace <str>, <old>, <new>`  | String’de değiştirme yapar.                                                 | `PRINT core.replace("Merhaba Dünya", "Dünya", "PDSXX")`                            | String işleme.                                                           |
| `core.format <str>, <*args>`        | String formatlama.                                                          | `PRINT core.format("Merhaba {0}", "Ali")`                                          | String işleme.                                                           |
| `core.trace`                        | Çalışma zamanı yığın izini döndürür.                                        | `PRINT core.trace()`                                                              | Hata ayıklama.                                                           |
| `core.try_catch <block>, <handler>` | Hata yakalama mekanizması.                                                 | `core.try_catch(omega(), 10/0, omega(e), PRINT e)`                                 | Hata yönetimi.                                                           |
| `core.sleep <seconds>`              | Programı duraklatır.                                                        | `core.sleep(2)`                                                                   | Zaman kontrolü.                                                          |
| `core.date_diff <date1>, <date2>, <unit>` | Tarihler arasındaki farkı hesaplar.                                   | `diff = core.date_diff("2025-04-24", "2025-04-26", "days")`                        | Zaman işleme.                                                            |
| `core.run_async <func>`             | Fonksiyonu asenkron çalıştırır.                                             | `task = core.run_async(omega(), PRINT "Görev")`                                    | Paralel işlem.                                                           |
| `core.wait <tasks>`                 | Asenkron görevleri bekler.                                                  | `core.wait([task1, task2])`                                                       | Paralel işlem.                                                           |
| `core.merge <col1>, <col2>`         | Koleksiyonları birleştirir.                                                 | `merged = core.merge([1, 2], [3, 4])`                                             | Veri yapısı.                                                             |
| `core.sort <iterable>, key=<func>`  | Iterable’ı sıralar.                                                         | `sorted = core.sort([3, 1, 2])`                                                   | Veri yapısı.                                                             |
| `core.memory_usage`                 | Bellek kullanımını döndürür.                                                | `PRINT core.memory_usage()`                                                       | Performans izleme.                                                       |
| `core.cpu_count`                    | CPU çekirdek sayısını döndürür.                                             | `PRINT core.cpu_count()`                                                          | Performans izleme.                                                       |
| `core.type_of <value>`              | Değişkenin tipini döndürür.                                                 | `PRINT core.type_of(42)`                                                          | Tip kontrolü.                                                            |
| `core.is_empty <collection>`        | Koleksiyonun boş olup olmadığını kontrol eder.                              | `IF core.is_empty(lst) THEN PRINT "Boş"`                                          | Veri yapısı.                                                             |
| `core.len <str>`                    | String veya koleksiyon uzunluğunu döndürür.                                 | `PRINT core.len("Merhaba")`                                                       | PDSXX entegrasyonu.                                                      |
| `core.val <str>`                    | String’i sayıya çevirir.                                                    | `PRINT core.val("42")`                                                            | PDSXX entegrasyonu.                                                      |
| `core.str <value>`                  | Değeri string’e çevirir.                                                    | `PRINT core.str(42)`                                                              | PDSXX entegrasyonu.                                                      |

### Örnek Kod
`libx_core`’u test eden bir PDSXX script’i:
```pdsx
import libx_core as core
core.set_encoding "utf-8"
core.load "utils.hx" : PRINT "Modül yüklendi"
DIM data AS DICT
data["name"] = "Ali"
core.write_json(data, "veri.json")
loaded = core.read_json("veri.json")
PRINT loaded["name"]  ' Ali
files = core.list_dir("data")
FOR file IN files
    PRINT file
NEXT
core.download("https://ornek.com/veri.csv", "veri.csv")
numbers = [1, 2, 3]
PRINT core.mean(numbers)  ' 2
text = "  Merhaba PDSXX  "
PRINT core.trim(text)  ' Merhaba PDSXX
core.try_catch(
    omega(), 10 / 0,
    omega(e), PRINT "Hata: " + e
)
core.sleep(1)
PRINT "1 saniye bekledi"
task = core.run_async(omega(), PRINT "Asenkron görev")
core.wait([task])
merged = core.merge([1, 2], [3, 4])
PRINT merged  ' [1, 2, 3, 4]
PRINT core.memory_usage()  ' Bellek kullanımı
```

### Sonraki Adımlar
1. **Ana Program (`pdsxx.py`)**:
   - `pdsxx.py`’yi, `libx_core` ve diğer kütüphaneleri entegre eden hafif bir yorumlayıcı olarak geliştirelim.
   - `PDF_READ_TEXT`, `WEB_GET`’i geçici olarak ana programda tutalım.

2. **Komut İsimlendirme**:
   - `libx_pdf` ve `libx_web` için kısa, BASIC tarzı komut isimleri tasarlayalım (örn. `READ PDF`, `GET WEB`).

3. **`lib_datastructures`**:
   - `STRUCT`, `UNION`, `ENUM` için önerilen iyileştirmeleri implemente edelim.
   - İç içe veri yapıları için test senaryoları yazalım.

4. **Sorular**:
   - Yukarıdaki yeni fonksiyonlardan hangilerini önceliklendirelim?
   - Daha fazla ağ (örn. WebSocket, FTP) veya veritabanı (örn. SQLite bağlantısı) işlevi eklenmeli mi?
   - `libx_core`’a başka hangi dillerden (örn. Rust, Julia) ilham alınabilir?
   - `libx_pdf` ve `libx_web` tasarımına ne zaman başlayalım?

### Son Söz
`libx_core`, yeni önerilerle daha kapsamlı ve güçlü bir çekirdek haline geldi. Dosya işlemleri, ağ, matematik, string manipülasyonu, hata yönetimi ve asenkron destek gibi özellikler, PDSXX’in veri bilimi ve prototipleme vizyonunu destekliyor. Yukarıdaki tablo ve planı onaylıyor musun? Eklemek/çıkarmak istediğin bir şey varsa, lütfen belirt. PDSXX’i inşa etmeye devam edelim!