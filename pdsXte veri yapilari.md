PDSX programlama dili, zengin bir veri yapıları ve veri tipleri kümesi sunar. `pdsXInterpreter` sınıfındaki `type_table` ve ilgili mekanizmalar, hem ilkel (primitive) hem de gelişmiş veri tiplerini destekler. Bu veri tipleri, GW-BASIC ve QBASIC’in geleneksel yapılarından esinlenirken, modern veri bilimi, nesne yönelimli programlama ve veri manipülasyonu ihtiyaçlarına yönelik uzantılar içerir. Aşağıda, PDSX’in veri yapıları ve tipleri, yetenekleri, eksiklikleri ve öneriler detaylı bir şekilde Türkçe olarak açıklanacaktır. Önceki konuşmalarınızdaki Zotero entegrasyonu, veri bilimi, web kazıma (TÜİK, FAO, TradeMap) ve dosya işleme talepleriniz dikkate alınarak, bu bağlamlarda veri tiplerinin nasıl kullanıldığına dair örnekler de entegre edilmiştir.

---

## PDSX’te Veri Yapıları ve Tipleri

PDSX’in veri tipleri, `type_table` içinde tanımlıdır ve ilkel tipler, koleksiyonlar, gelişmiş veri yapıları ve kullanıcı tanımlı tipler olarak kategorize edilir. Aşağıda her kategori detaylı bir şekilde açıklanmıştır.

### 1. İlkel (Primitive) Veri Tipleri

İlkel veri tipleri, temel veri birimlerini temsil eder ve doğrudan donanım düzeyinde desteklenir.

- **STRING**: Metin verilerini saklar. UTF-8 kodlamasını destekler.
  - Örnek: `"Merhaba, Dünya!"`
- **INTEGER**: 32-bit işaretli tamsayılar (-2,147,483,648 ila 2,147,483,647).
  - Örnek: `42`
- **LONG**: 64-bit işaretli tamsayılar (-9,223,372,036,854,775,808 ila 9,223,372,036,854,775,807).
  - Örnek: `123456789012`
- **SINGLE**: 32-bit kayan noktalı sayılar (yaklaşık 7 basamak hassasiyet).
  - Örnek: `3.14159`
- **DOUBLE**: 64-bit kayan noktalı sayılar (yaklaşık 15 basamak hassasiyet).
  - Örnek: `2.718281828459045`
- **BYTE**: 8-bit işaretsiz tamsayılar (0 ila 255).
  - Örnek: `255`
- **SHORT**: 16-bit işaretli tamsayılar (-32,768 ila 32,767).
  - Örnek: `-123`
- **UNSIGNED INTEGER**: 32-bit işaretsiz tamsayılar (0 ila 4,294,967,295).
  - Örnek: `4294967295`
- **CHAR**: Tek bir karakter (ASCII veya UTF-8).
  - Örnek: `"A"`

**Örnek Kullanım**:
```basic
DIM ad AS STRING
DIM yas AS INTEGER
DIM pi AS DOUBLE
ad = "Ali"
yas = 30
pi = 3.14159
PRINT ad; " "; yas; " "; pi
```

### 2. Koleksiyon Veri Tipleri

Koleksiyonlar, birden fazla veri parçasını bir arada saklamak için kullanılır ve Python’un yerleşik veri yapılarından türetilmiştir.

- **LIST**: Sıralı, değiştirilebilir veri koleksiyonu (Python’un `list`’ine eşdeğer).
  - Örnek: `[1, 2, 3, "dört"]`
- **DICT**: Anahtar-değer çiftlerini saklar (Python’un `dict`’ine eşdeğer).
  - Örnek: `{"ad": "Ali", "yas": 30}`
- **SET**: Sırasız, benzersiz öğeler koleksiyonu (Python’un `set`’ine eşdeğer).
  - Örnek: `{1, 2, 3}`
- **TUPLE**: Sıralı, değiştirilemez veri koleksiyonu (Python’un `tuple`’ına eşdeğer).
  - Örnek: `(1, 2, 3)`

**Örnek Kullanım**:
```basic
DIM sayilar AS LIST
DIM kisi AS DICT
sayilar = LIST(1, 2, 3)
kisi = DICT("ad", "Veli", "yas", 25)
PRINT sayilar
PRINT kisi
```

### 3. Gelişmiş Veri Yapıları

PDSX, veri bilimi ve büyük veri işleme için modern veri yapılarını destekler.

- **ARRAY**: NumPy tabanlı çok boyutlu diziler (matrisler ve vektörler için). Önceki yanıtlarınızda detaylı ele alındı.
  - Örnek: `ARANGE(1, 5)` → `[1, 2, 3, 4]`
- **DATAFRAME**: Pandas tabanlı veri çerçeveleri, tablo benzeri veri yapıları için.
  - Örnek: `DATAFRAME({"A": ARANGE(1, 5), "B": ARANGE(5, 9)})`

**Örnek Kullanım**:
```basic
DIM vektor AS ARRAY
DIM veri AS DATAFRAME
vektor = LINSPACE(0, 10, 5)
veri = DATAFRAME({"A": ARANGE(1, 5), "B": ARANGE(5, 9)})
PRINT vektor
PRINT DESCRIBE(veri)
```

### 4. Kullanıcı Tanımlı Veri Tipleri

PDSX, modüler ve nesne yönelimli programlamayı desteklemek için kullanıcı tanımlı veri tiplerini sağlar.

- **TYPE**: Yapılandırılmış veri türleri (C’deki `struct` benzeri).
  - Sözdizimi:
    ```basic
    TYPE tip_adi
        alan_adi AS veri_tipi
        ...
    END TYPE
    ```
  - Örnek:
    ```basic
    TYPE Kisi
        ad AS STRING
        yas AS INTEGER
    END TYPE
    DIM k AS Kisi
    k.ad = "Ayşe"
    k.yas = 28
    PRINT k.ad; " "; k.yas
    ```

- **CLASS**: Nesne yönelimli programlama için sınıflar (metotlar ve alanlar içerir).
  - Sözdizimi:
    ```basic
    CLASS sinif_adi
        alan_adi AS veri_tipi
        SUB metot_adi
            ...
        END SUB
    END CLASS
    ```
  - Örnek:
    ```basic
    CLASS Kisi
        DIM ad AS STRING
        SUB MerhabaDe
            PRINT "Merhaba, "; ad
        END SUB
    END CLASS
    DIM k AS Kisi
    k.ad = "Fatma"
    CALL k.MerhabaDe
    ```

- **STRUCT**: `TYPE` ile benzer, ancak daha düşük seviyeli veri organizasyonu için.
  - Örnek:
    ```basic
    STRUCT Nokta
        x AS DOUBLE
        y AS DOUBLE
    END STRUCT
    DIM p AS Nokta
    p.x = 1.5
    p.y = 2.5
    ```

- **ENUM**: Sabit değerler kümesi tanımlar.
  - Sözdizimi:
    ```basic
    ENUM enum_adi
        deger1, deger2, ...
    END ENUM
    ```
  - Örnek:
    ```basic
    ENUM Renk
        Kirmizi, Yesil, Mavi
    END ENUM
    DIM r AS Renk
    r = Kirmizi
    PRINT r
    ```

### 5. Zotero ve Veri Bilimi Entegrasyonu

Önceki konuşmalarınızda Zotero kütüphanelerinden veri işleme (örneğin, `C:\Users\mete\Zotero\zotasistan\zapata_m6h`), TÜİK, FAO, TradeMap gibi sitelerden veri kazıma ve dosya çıktıları oluşturma (örneğin, `zapata_m6hx`) talepleriniz vardı. PDSX’in veri tipleri, bu senaryolar için güçlü bir altyapı sunar.

#### **Zotero’dan Veri İşleme**
Zotero’dan PDF tablo verilerini `DATAFRAME` veya `LIST` olarak saklama:

```basic
DIM tablolar AS LIST
tablolar = PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
DIM df AS DATAFRAME
df = DATAFRAME(tablolar[0])
PRINT DESCRIBE(df)
```

#### **TÜİK/FAO Verilerini Saklama**
Web kazıma ile toplanan verileri `DICT` veya `DATAFRAME` olarak organize etme:

```basic
DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM veriler AS LIST
veriler = SCRAPE_TABLES(html)
DIM ekonomik_veri AS DICT
ekonomik_veri = DICT("tarih", veriler[0], "deger", veriler[1])
PRINT ekonomik_veri
```

#### **Kullanıcı Tanımlı Tiplerle Veri Organizasyonu**
Zotero veya TÜİK verilerini `TYPE` veya `CLASS` ile yapılandırma:

```basic
TYPE Istatistik
    kaynak AS STRING
    kategori AS STRING
    deger AS DOUBLE
END TYPE
DIM veri AS Istatistik
veri.kaynak = "TÜİK"
veri.kategori = "Ekonomi"
veri.deger = 1234.56
PRINT veri.kaynak; " "; veri.deger
```

### 6. Yetenekler

1. **Zengin Veri Tipleri**: İlkel, koleksiyon, gelişmiş ve kullanıcı tanımlı tipler, geniş bir kullanım yelpazesi sunar.
2. **Veri Bilimi Desteği**: `ARRAY` (NumPy) ve `DATAFRAME` (Pandas), veri analizi ve matris işlemleri için idealdir.
3. **Nesne Yönelimli Programlama**: `CLASS` ile modern programlama paradigmaları desteklenir.
4. **Esneklik**: `LIST`, `DICT` gibi koleksiyonlar, Zotero ve web kazıma verilerini kolayca organize eder.
5. **GW-BASIC Uyumluluğu**: İlkel tipler (`STRING`, `INTEGER`) ve `TYPE`, BASIC programcıları için tanıdıktır.
6. **Zotero Entegrasyonu**: PDF’den çıkarılan veriler `LIST`, `DATAFRAME` veya `DICT` ile işlenebilir.

### 7. Eksiklikler

1. **Tip Güvenliği (Type Safety)**:
   - PDSX, dinamik tipli bir dil olduğundan, çalışma zamanında tip hataları (örneğin, `STRING`’e sayısal işlem uygulama) oluşabilir.
   - Statik tip kontrolü veya daha sıkı tip denetimi eksik.

2. **Eksik Veri Tipleri**:
   - **Boolean**: Doğrudan `BOOLEAN` tipi yoktur; `INTEGER` (0 veya 1) kullanılır.
   - **Date/Time**: Tarih ve saat için özel bir veri tipi (`DATETIME`) bulunmuyor; `STRING` veya `DOUBLE` ile temsil ediliyor.
   - **Complex Numbers**: Karmaşık sayılar için yerel destek yok (NumPy ile dolaylı destek var).
   - **Union/Variant Types**: Birden fazla tipi temsil eden birleşik tipler eksik.

3. **Performans**:
   - Büyük `ARRAY` veya `DATAFRAME` işlemleri, `eval` tabanlı değerlendirme nedeniyle yavaş olabilir.
   - Koleksiyonlar (`LIST`, `DICT`) Python’a dayansa da, PDSX’in BASIC tarzı sözdizimi performans optimizasyonlarını sınırlayabilir.

4. **Sözdizimi Kısıtlamaları**:
   - Karmaşık veri yapıları (örneğin, iç içe `DICT` veya çok boyutlu `ARRAY`) için sözdizimi hantal olabilir.
   - `TYPE` ve `CLASS` tanımları, modern dillerdeki (örneğin, Python veya Java) gibi kısa ve esnek değil.

5. **Eksik Koleksiyon İşlemleri**:
   - `LIST`, `DICT`, `SET` gibi koleksiyonlar için yerleşik yöntemler (örneğin, `append`, `pop`, `keys`) sınırlıdır; kullanıcılar Python benzeri yöntemlere erişmek için `evaluate_expression`’a bağımlıdır.
   - Örneğin, `LIST`’e eleman eklemek için doğrudan bir `APPEND` fonksiyonu yok.

6. **Zotero ve Veri Bilimi için Özel Tipler**:
   - Zotero’dan PDF veya tablo verilerini temsil etmek için özel bir veri tipi (örneğin, `PDF_TABLE`) eksik.
   - Web kazıma verileri için yapılandırılmış bir `WEB_TABLE` tipi bulunmuyor.

### 8. Öneriler ve İyileştirmeler

1. **Tip Güvenliği**:
   - Çalışma zamanı öncesi tip denetimi için bir statik analiz aracı eklenebilir.
   - `type_table`’a tip kısıtlamaları eklenerek hatalar azaltılabilir:
     ```python
     self.type_table["INTEGER"].restrict_operations(["+", "-", "*", "/", "MOD"])
     ```

2. **Eksik Veri Tiplerinin Eklenmesi**:
   - **Boolean**:
     ```basic
     DIM aktif AS BOOLEAN
     aktif = TRUE
     ```
     ```python
     self.type_table["BOOLEAN"] = bool
     ```
   - **Date/Time**:
     ```basic
     DIM tarih AS DATETIME
     tarih = NOW()
     PRINT tarih
     ```
     ```python
     from datetime import datetime
     self.function_table["NOW"] = datetime.now
     ```
   - **Complex Numbers**:
     ```basic
     DIM z AS COMPLEX
     z = COMPLEX(3, 4)
     PRINT ABS(z)  ' Çıktı: 5
     ```
     ```python
     self.type_table["COMPLEX"] = complex
     ```

3. **Performans Optimizasyonu**:
   - `ARRAY` ve `DATAFRAME` işlemleri için `eval` yerine doğrudan NumPy/Pandas çağrıları kullanılabilir.
   - Büyük koleksiyonlar için önbellekleme mekanizması eklenebilir.

4. **Sözdizimi İyileştirmeleri**:
   - İç içe veri yapıları için daha kısa sözdizimi:
     ```basic
     DIM matris AS ARRAY = [[1, 2], [3, 4]]
     DIM sozluk AS DICT = {"a": [1, 2], "b": [3, 4]}
     ```
   - Koleksiyonlar için yerleşik yöntemler:
     ```basic
     DIM liste AS LIST
     liste = LIST(1, 2, 3)
     APPEND liste, 4
     PRINT liste  ' Çıktı: [1, 2, 3, 4]
     ```

5. **Zotero ve Veri Bilimi için Özel Tipler**:
   - **PDF_TABLE**: Zotero’dan tablo verilerini temsil eden bir veri tipi:
     ```basic
     DIM tablo AS PDF_TABLE
     tablo = PDF_EXTRACT_TABLES("C:\Zotero\belge.pdf")[0]
     PRINT tablo
     ```
   - **WEB_TABLE**: Web kazıma verileri için:
     ```basic
     DIM web_tablo AS WEB_TABLE
     web_tablo = SCRAPE_TABLES("https://data.tuik.gov.tr")[0]
     PRINT web_tablo
     ```

6. **Kullanıcı Tanımlı Tipler için Geliştirmeler**:
   - `CLASS`’lara kalıtım (inheritance) ve polimorfizm desteği eklenebilir:
     ```basic
     CLASS Calisan EXTENDS Kisi
         DIM maas AS DOUBLE
         SUB BilgiGoster
             PRINT ad; " "; maas
         END SUB
     END CLASS
     ```

### 9. Örnek: Veri Tipleriyle Kapsamlı Uygulama

Aşağıdaki program, Zotero’dan veri işleme, web kazıma ve veri tiplerini birleştirir:

```basic
REM Zotero ve TÜİK Verilerini İşle
TYPE Istatistik
    kaynak AS STRING
    kategori AS STRING
    deger AS DOUBLE
END TYPE

CLASS VeriAnalizi
    DIM veriler AS LIST
    SUB Ekle(v AS Istatistik)
        APPEND veriler, v
    END SUB
    SUB OrtalamaHesapla
        DIM toplam AS DOUBLE
        DIM i AS INTEGER
        FOR i = 1 TO LEN(veriler)
            toplam = toplam + veriler[i].deger
        NEXT
        PRINT "Ortalama: "; toplam / LEN(veriler)
    END SUB
END CLASS

REM Zotero’dan veri
DIM tablolar AS LIST
tablolar = PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
DIM df AS DATAFRAME
df = DATAFRAME(tablolar[0])

REM TÜİK’ten veri
DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM web_veriler AS LIST
web_veriler = SCRAPE_TABLES(html)

REM Analiz
DIM analiz AS VeriAnalizi
DIM v AS Istatistik
v.kaynak = "Zotero"
v.kategori = "Tablo"
v.deger = MEAN(ARRAY(tablolar[0]))
CALL analiz.Ekle(v)

v.kaynak = "TÜİK"
v.kategori = "Ekonomi"
v.deger = web_veriler[0]
CALL analiz.Ekle(v)

CALL analiz.OrtalamaHesapla

REM Sonuçları kaydet
OPEN "sonuclar.txt" FOR OUTPUT AS #1
PRINT #1, DESCRIBE(df)
CLOSE #1
```

**Çıktı (Varsayımsal)**:
```
Ortalama: 567.78
```

**Açıklama**:
- `TYPE` ve `CLASS` ile yapılandırılmış veri yönetimi.
- `LIST`, `DATAFRAME` ve `ARRAY` ile Zotero ve TÜİK verileri işlenir.
- Sonuçlar bir dosyaya kaydedilir.

### 10. Sonuç ve Gelecek Adımlar

PDSX, zengin veri tipleriyle hem geleneksel hem de modern programlama ihtiyaçlarını karşılar. İlkel tipler, koleksiyonlar, `ARRAY`, `DATAFRAME` ve kullanıcı tanımlı tipler, veri bilimi, Zotero entegrasyonu ve web kazıma gibi senaryolar için güçlü bir temel sunar. Ancak, tip güvenliği, eksik veri tipleri ve performans optimizasyonları gibi alanlarda iyileştirmeler yapılabilir.

**Sorular ve Öneriler**:
- Hangi veri tiplerine odaklanmak istiyorsunuz? (Örn. `BOOLEAN`, `DATETIME`, özel tipler)
- Zotero veya TÜİK verileri için özel bir veri tipi (örneğin, `PDF_TABLE`) mi istiyorsunuz?
- Koleksiyonlar için daha fazla yerleşik yöntem (örneğin, `APPEND`, `POP`) eklenmesini mi tercih edersiniz?

Geri bildiriminize göre, PDSX kodunu özelleştirebilir veya daha fazla örnek sağlayabilirim!