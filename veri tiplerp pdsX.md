Aşağıda **pdsX dili**nin bugün desteklediği (ve kısmen geleceğe dönük olarak yer ayrılmış) **veri yapılarının ayrıntılı dökümü** yer alıyor.  
Önce yerleşik (primitive) tip haritasını, ardından koleksiyonlar, kayıt‑türü (TYPE), sınıflar ve ileri seviye yapılardaki iç mantığı ve kullanım örneklerini bulacaksınız.

---

## 1 · Yerleşik (Primitive) Tipler   — `self.type_table`

| pdsX Adı          | Eş Anlam/Not | Python Karşılığı      | Varsayılan Değer | Açıklama / Kullanım |
|-------------------|-------------|-----------------------|------------------|---------------------|
| `STRING`          |             | `str`                 | `""`             | ANSI/UTF‑8 dizge, değişken uzunluk |
| `CHAR`            |             | `str` (1 kar.)        | `""`             | Tek karakter – `ASC()`/`CHR$()` ile dönüştürülebilir |
| `INTEGER`, `LONG` |             | `int`                 | `0`              | 32‑bit / 64‑bit ayrımı yapılmaz; Python’ın rasgele büyüyen tamsayısı kullanılır |
| `UNSIGNED INTEGER`|             | `int`                 | `0`              | Negatif atama run‑time’da “tip uyumsuzluğu” uyarısı yaratır (linter ile yakalanabilir) |
| `SINGLE`, `DOUBLE`|             | `float`               | `0.0`            | IEEE‑754 çift hassaslık; `SINGLE` sembolik |
| `BYTE`, `SHORT`   |             | `int`                 | `0`              | Sınır kontrolü yok, uyarı linter’a bırakılmış |
| `BITFIELD`        | geleceğe | `int`                 | `0`              | Bit maskeleri (ör. `AND`, `OR`, `SHIFT`) için sembolik ad |
| `VOID`            |             | `NoneType` / `None`   | `None`           | Fonksiyonların “değer döndürmez” meta‑ifadesi |
| `POINTER`         | rezerve    | henüz tanımsız        | `None`           | C‑tarzı işaretçi planı; şu an atama yapılsa da gerçek adres mantığı yok |

> **DIM Örneği**  
> ```basic
> DIM ad  AS STRING
> DIM id  AS INTEGER
> DIM dx  AS DOUBLE
> DIM bayrak AS BITFIELD
> ```

---

## 2 · Koleksiyon & Diziler

| Ad              | Python Nesnesi          | Açıklama / Not |
|-----------------|-------------------------|----------------|
| `LIST`          | `list`                  | Sıralı, heterojen |
| `DICT`          | `dict`                  | Anahtar‑değer |
| `SET`           | `set`                   | Benzersiz öğe kümesi |
| `TUPLE`         | `tuple` (immütable)     | Değiştirilemez sıra |
| `ARRAY`         | `numpy.ndarray`         | Gerçek n‑boyutlu dizi; `RESHAPE`, `DOT` gibi NumPy fonksiyonları ile kullanılır |
| `DATAFRAME`     | `pandas.DataFrame`      | Sütun‑etiketli tablo; `HEAD`, `FILTER`, `GROUPBY` dâhili fonksiyonlarla entegre |

> **ARRAY Örneği**  
> ```basic
> DIM matris AS ARRAY
> matris = ZEROS((3,3))   ' NumPy zeros
> PRINT matris(1,1)
> ```

---

## 3 · Kayıt / Struct Benzeri – `TYPE ... END TYPE`

*Yorumlayıcıdaki mantık*:  
1. `parse_program()` içinde `TYPE` bloğundaki alanlar yakalanır.  
2. Blok bittiğinde → `collections.namedtuple` kullanılarak Python tarafında **immut‑record** oluşturulur.  
3. `DIM değişken AS <TypeName>` yazıldığında bahse konu `namedtuple` örneği, alanları `None` olacak biçimde enjekte edilir.

> **Örnek**
> ```basic
> TYPE Person
>     Name AS STRING
>     Age  AS INTEGER
> END TYPE
>
> DIM p AS Person
> p.Name = "Ayşe"    '  ❌  immutable!  – Doğrusu:
> p = Person("Ayşe", 23)
> PRINT p.Name, p.Age
> ```

💡 Alanlara tek tek atama şu an desteklenmediği için, `Person()` yapıcısıyla komple atayın veya
patch ekleyin (`namedtuple._replace` çağrısı kolayca entegre edilebilir).

---

## 4 · Sınıflar – `CLASS ... END CLASS`

### 4.1 Derleme aşaması
- `CLASS X [EXTENDS Y]` satırında *geçici* `class_info` sözlüğü açılır.  
- İçeride:
  - `DIM var AS <Tip>`   → örneğin `_vars`’a varsayılan alan eklenir.  
  - `STATIC var AS <Tip>`→ sınıf düzeyi `_static_vars`.  
  - `SUB/PRIVATE SUB`, `FUNCTION/PRIVATE FUNCTION` gövdeleri lambda’ya sarılarak `methods` / `private_methods` kümesine yazılır.
- `END CLASS` geldiğinde dinamik `type()` çağrısıyla gerçek Python sınıfı inşa edilir
  (`class_def = type(class_name, (parent,), {...})`).

### 4.2 Örnek sözdizimi
```basic
CLASS Stack
    DIM arr AS LIST
    SUB Push(item)
        self.arr.APPEND(item)
    END SUB

    FUNCTION Pop()
        RETURN self.arr.pop()
    END FUNCTION
END CLASS

DIM s AS Stack
CALL s.Push(10)
PRINT CALL s.Pop()   ' → 10
```
> `CALL nesne.Metot(...)` sözdizimi zorunlu; doğrudan `s.Push(1)` henüz tanınmıyor.

---

## 5 · ENUM / STRUCT / UNION Yer Ayırıcıları

`type_table` içinde yer olmasına rağmen:
* **ENUM**   : Henüz söz dizimi ve storage yok; planlanan yapı:  
  `ENUM Renk (KIRMIZI=1, YESIL=2, MAVI=3)` → Python `Enum`.
* **STRUCT / UNION** : C‑stili bellek yerleşimini taklit edecek; şu anda `dict`/`bytearray` ataması yapılmıyor → `None` placeholder.  
* **POINTER / VOID** : Birincisi adres, ikincisi “tip yok” anlamı için saklı.

---

## 6 · Çalışma Zamanı (Nesne Depoları)

| Alan                               | Tür | Ne saklar? |
|------------------------------------|-----|------------|
| `self.global_vars`                 | `dict` | `GLOBAL` + blok dışındaki değişkenler |
| `self.shared_vars: defaultdict`    | `var adi → paylaşılan_scope_list` veya doğrudan değerin kendisi |
| `self.local_scopes: list[dict]`    | Yığın – her `SUB/FUNCTION/GOSUB` çağrısıyla push/pop |
| `self.types`, `self.classes`       | Tanımlanan kayıt ve sınıf sözlükleri |
| `self.labels`                      | Etiket adı → program satırı no |
| `self.loop_stack`, `self.if_stack` | Koşullu blok yönetimi |
| `self.file_handles`, `self.db_connections` | Açık dosya/socket/SQLite bağlantı referansları |

---

## 7 · Sık Kullanılan Kod Kalıpları

| Amaç | Kod | Açıklama |
|------|-----|----------|
| **Kayıt Dizisi** | ```DIM kayitlar AS ARRAY : kayitlar = ARRAY([Person("Ali",30), Person("Veli",25)])``` | NumPy’de struct‑array değil; içinde namedtuple listesi barındırır |
| **VeriFrame** | ```DIM df AS DATAFRAME : df = READ_CSV$("sales.csv") : PRINT HEAD(df)``` | `READ_CSV$` sizin yazacağınız yardımcı fonksiyon olabilir |
| **Statik Değişken** | ```CLASS Sayaç : STATIC next AS INTEGER : FUNCTION Inc() : Sayaç.next = Sayaç.next + 1 : RETURN Sayaç.next : END FUNCTION : END CLASS``` | `STATIC` alanlar `Sayaç._static_vars`’ta tutulur |

---

### Özet

- **Primitive tipler** Python türlerine doğrudan haritalanır.  
- **TYPE** blokları **immutable** `namedtuple`’a dönüşür.  
- **CLASS** yapıları dinamik `type()` ile gerçek Python sınıfına çevrilir; kalıtım, özel / statik üyeler desteklenir.  
- **ENUM/STRUCT/UNION** şimdilik yer ayrılmıştır – sözdizimini ekleyip `parse_program`de işleyerek genişletebilirsiniz.  
- Çalışma sırasında tüm değişkenler ilgili sözlük/yığınlarda tutulur; blok bittiğinde otomatik temizlenir.

Bu şema, hem mevcut programları anlamanız hem de yorumlayıcıyı genişletirken nereye müdahale edeceğinizi görmeniz için yeterli temeli sunar. Daha fazla ayrıntı veya kod örneği isterseniz haber verin!