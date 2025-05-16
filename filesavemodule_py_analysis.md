# Modül Analizi: filesavemodule.py

## Genel Bakış
`filesavemodule.py` dosyası, Zapata M6H projesinde temiz metinler, tablolar, kaynakçalar ve embedding verilerini çeşitli formatlarda (.txt, .json, .csv, .ris, .bib) ve veritabanlarında (SQLite, ChromaDB) saklayan bir modüldür. Bu modül, veri saklama işlemlerini standartlaştırır ve hata yönetimi ile loglama mekanizmaları içerir.

## Sınıf: FileSaveModule

### Amaç
Çeşitli veri türlerini farklı formatlarda ve veritabanlarında saklayan, hata yönetimi ve loglama mekanizmaları içeren sınıf.

### Değişkenler
- `chroma_client`: ChromaDB bağlantısı
- `db_path`: SQLite veritabanı yolu
- `logger`: Loglama nesnesi

### Metodlar

#### `__init__(self)`
- **Amaç**: FileSaveModule sınıfını başlatır
- **Giriş Parametreleri**: Yok
- **Çıkış Değeri**: Yok
- **İşlem**: 
  - ChromaDB bağlantısını oluşturur
  - SQLite veritabanı yolunu yapılandırma dosyasından alır
  - Loglama sistemini kurar

#### `setup_logging(self)`
- **Amaç**: Loglama sistemini kurar
- **Giriş Parametreleri**: Yok
- **Çıkış Değeri**: 
  - `logger` (logging.Logger): Loglama nesnesi
- **İşlem**: 
  - Renkli loglama formatını ayarlar
  - Konsol ve dosya işleyicilerini yapılandırır
  - Loglama seviyesini DEBUG olarak ayarlar
  - Logger nesnesini döndürür

#### `save_text_to_file(self, text, file_path)`
- **Amaç**: Metni .txt dosyasına kaydeder
- **Giriş Parametreleri**: 
  - `text` (str): Kaydedilecek metin
  - `file_path` (str): Dosya yolu
- **Çıkış Değeri**: Yok
- **İşlem**: 
  - Metni belirtilen dosya yoluna UTF-8 kodlaması ile kaydeder
  - İşlemi loglar
  - Hata durumunda hatayı loglar

#### `save_json(self, data, file_path)`
- **Amaç**: Veriyi JSON dosyasına kaydeder
- **Giriş Parametreleri**: 
  - `data` (dict): Kaydedilecek veri
  - `file_path` (str): Dosya yolu
- **Çıkış Değeri**: Yok
- **İşlem**: 
  - Veriyi JSON formatında belirtilen dosya yoluna UTF-8 kodlaması ile kaydeder
  - İşlemi loglar
  - Hata durumunda hatayı loglar

#### `save_csv(self, data, file_path)`
- **Amaç**: Veriyi CSV dosyasına kaydeder
- **Giriş Parametreleri**: 
  - `data` (dict): Kaydedilecek veri
  - `file_path` (str): Dosya yolu
- **Çıkış Değeri**: Yok
- **İşlem**: 
  - Veriyi CSV formatında belirtilen dosya yoluna UTF-8 kodlaması ile kaydeder
  - İşlemi loglar
  - Hata durumunda hatayı loglar

#### `save_to_sqlite(self, table_name, data)`
- **Amaç**: Veriyi SQLite veritabanına kaydeder
- **Giriş Parametreleri**: 
  - `table_name` (str): Tablo adı
  - `data` (dict): Kaydedilecek veri
- **Çıkış Değeri**: Yok
- **İşlem**: 
  - SQLite veritabanına bağlanır
  - Veriyi belirtilen tabloya ekler
  - İşlemi loglar
  - Hata durumunda hatayı loglar

#### `save_to_chromadb(self, collection_name, doc_id, metadata)`
- **Amaç**: Veriyi ChromaDB'ye kaydeder
- **Giriş Parametreleri**: 
  - `collection_name` (str): Koleksiyon adı
  - `doc_id` (str): Belge kimliği
  - `metadata` (dict): Belge meta verileri
- **Çıkış Değeri**: Yok
- **İşlem**: 
  - Belirtilen adda bir koleksiyon oluşturur veya var olanı alır
  - Belge kimliği ve meta verileri ile koleksiyona ekler
  - İşlemi loglar
  - Hata durumunda hatayı loglar

## Test Komutları
- FileSaveModule sınıfını başlatır
- Örnek metin, JSON, CSV verilerini oluşturur
- Bu verileri dosyalara kaydeder
- Örnek verileri SQLite ve ChromaDB'ye kaydeder

## Bağımlılıklar
- `os`: Dosya sistemi işlemleri için
- `json`: JSON formatında veri işleme için
- `sqlite3`: SQLite veritabanı işlemleri için
- `csv`: CSV formatında veri işleme için
- `chromadb`: ChromaDB veritabanı işlemleri için
- `logging`: Loglama işlemleri için
- `colorlog`: Renkli loglama için
- `configmodule`: Proje yapılandırma ayarları için

## Veri Yapıları
- **sample_text**: Metin örneği
  ```python
  "Bu bir test metnidir."
  ```
- **sample_json**: JSON veri örneği
  ```python
  {"text": "Bu bir test metnidir.", "metadata": "Örnek veri"}
  ```
- **sample_csv**: CSV veri örneği
  ```python
  {"column1": "veri1", "column2": "veri2"}
  ```
- **sample_sql_data**: SQLite veri örneği
  ```python
  {"doc_id": "sample_001", "content": "Bu bir test metnidir."}
  ```
- **sample_chroma_data**: ChromaDB veri örneği
  ```python
  {"category": "test"}
  ```

## Sahte Kod (Pseudocode)
```
class FileSaveModule:
    function initialize():
        create ChromaDB client
        get SQLite database path from config
        setup logging system
    
    function setup_logging():
        configure colored log formatter
        create console handler
        create file handler
        set log level to DEBUG
        return logger
    
    function save_text_to_file(text, file_path):
        try:
            open file at file_path with UTF-8 encoding
            write text to file
            log success message
        catch Exception:
            log error message
    
    function save_json(data, file_path):
        try:
            open file at file_path with UTF-8 encoding
            dump data as JSON to file
            log success message
        catch Exception:
            log error message
    
    function save_csv(data, file_path):
        try:
            open file at file_path with UTF-8 encoding
            create CSV writer
            write header row with data keys
            write data row with data values
            log success message
        catch Exception:
            log error message
    
    function save_to_sqlite(table_name, data):
        try:
            connect to SQLite database
            create SQL insert statement with table_name and data keys
            execute SQL with data values
            commit changes
            log success message
        catch Exception:
            log error message
    
    function save_to_chromadb(collection_name, doc_id, metadata):
        try:
            get or create collection with collection_name
            add document with doc_id and metadata
            log success message
        catch Exception:
            log error message

main():
    create FileSaveModule instance
    define sample text
    save sample text to file
    define sample JSON data
    save sample JSON data to file
    define sample CSV data
    save sample CSV data to file
    define sample SQL data
    save sample SQL data to SQLite
    define sample ChromaDB data
    save sample ChromaDB data to ChromaDB
    print completion message
```

## Veri Akışı
1. FileSaveModule sınıfı başlatılır ve gerekli yapılandırmalar yapılır
2. Veri (metin, JSON, CSV, vb.) oluşturulur veya alınır
3. Veri, belirtilen formatta (TXT, JSON, CSV) dosyaya kaydedilir
4. Veri, SQLite veritabanına kaydedilir
5. Veri, ChromaDB'ye kaydedilir
6. Tüm işlemler loglanır

## Notlar ve İyileştirme Önerileri
- Daha fazla dosya formatı desteği eklenebilir (XML, YAML, vb.)
- Toplu veri kaydetme işlemleri için optimizasyonlar yapılabilir
- Veri doğrulama mekanizmaları eklenebilir
- Veri şifreleme seçenekleri eklenebilir
- Veri sıkıştırma seçenekleri eklenebilir
- Veri yedekleme mekanizmaları eklenebilir
- Veri güncelleme ve silme işlevleri eklenebilir
- Daha kapsamlı hata işleme mekanizmaları eklenebilir
- Birim testleri eklenebilir
- Dokümantasyon genişletilebilir
