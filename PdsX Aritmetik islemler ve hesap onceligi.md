PDSX programlama dili, aritmetik hesaplamaları destekler ve bu hesaplamalar `pdsXInterpreter` sınıfındaki `evaluate_expression` yöntemi aracılığıyla Python’un `eval` fonksiyonu kullanılarak gerçekleştirilir. Bu, PDSX’in Python’un aritmetik operatörlerini ve işlem önceliğini miras aldığı anlamına gelir. Ayrıca, PDSX’in `function_table`’ında tanımlı matematiksel fonksiyonlar (örneğin, `ABS`, `SQR`, `SIN`) aritmetik hesaplamaları genişletir. Aşağıda, PDSX’in aritmetik hesaplamaları, işlem önceliği, desteklenen operatörler, eksik yönler ve öneriler detaylı bir şekilde ele alınacaktır. Önceki konuşmalarınızdaki veri bilimi ve matris işlemleriyle ilgili talepler de göz önünde bulundurulmuştur.

---

## PDSX’te Aritmetik Hesaplamalar ve İşlem Önceliği

### 1. Aritmetik Hesaplamalar

PDSX, aritmetik ifadeleri değerlendirmek için Python’un `eval` fonksiyonunu kullanır ve aşağıdaki temel aritmetik operatörleri destekler:

- **Toplama**: `+` (örneğin, `5 + 3` → `8`)
- **Çıkarma**: `-` (örneğin, `5 - 3` → `2`)
- **Çarpma**: `*` (örneğin, `5 * 3` → `15`)
- **Bölme**: `/` (örneğin, `6 / 2` → `3.0`, her zaman ondalık sonuç)
- **Tamsayı Bölmesi**: `\` (örneğin, `7 \ 2` → `3`, PDSX’te Python’un `//` operatörüne eşdeğer)
- **Modülüs**: `MOD` veya `%` (örneğin, `7 MOD 2` → `1`)
- **Üs Alma**: `^` veya `**` (örneğin, `2 ^ 3` → `8`)

Ayrıca, PDSX’in `function_table`’ında tanımlı matematiksel fonksiyonlar aritmetik hesaplamaları zenginleştirir:

- `ABS(n)`: Mutlak değer (örneğin, `ABS(-5)` → `5`)
- `INT(n)`: Tamsayıya yuvarlama (örneğin, `INT(3.7)` → `3`)
- `SQR(n)`: Karekök (örneğin, `SQR(16)` → `4`)
- `SIN(n)`, `COS(n)`, `TAN(n)`, `ATN(n)`: Trigonometrik fonksiyonlar (radyan cinsinden)
- `LOG(n)`: Doğal logaritma
- `EXP(n)`: Üstel fonksiyon (e^n)
- `FIX(n)`: Ondalık kısmı atar (örneğin, `FIX(3.7)` → `3`)
- `ROUND(n, digits)`: Belirtilen basamağa yuvarlama (örneğin, `ROUND(3.14159, 2)` → `3.14`)
- `SGN(n)`: Sayının işaretini döndürür (-1, 0, 1)
- `MIN(*args)`, `MAX(*args)`: Minimum veya maksimum değer

**Örnek Aritmetik İfade**:
```basic
DIM sonuc AS DOUBLE
sonuc = 5 + 3 * 2 ^ 2 - 4 / 2
PRINT sonuc  ' Çıktı: 15.0
```
**Açıklama**: Yukarıdaki ifade, işlem önceliğine göre değerlendirilir (detaylar aşağıda).

### 2. İşlem Önceliği

PDSX, Python’un işlem önceliği kurallarını kullanır ve bu kurallar GW-BASIC/QBASIC’in geleneksel öncelik kurallarıyla uyumludur. İşlem önceliği, ifadelerin hangi sırayla değerlendirileceğini belirler ve aşağıdaki hiyerarşiye sahiptir (en yüksek öncelik üstte):

1. **Parantezler**: `( )` – Parantez içindeki ifadeler her zaman önce değerlendirilir.
2. **Üs Alma**: `^` veya `**` – Sağdan sola değerlendirilir (örneğin, `2 ^ 3 ^ 2` → `2 ^ (3 ^ 2)` = `2 ^ 9` = `512`).
3. **Tekli Operatörler**: `+` (pozitif), `-` (negatif) – Örneğin, `-5 * 2` → `-10`.
4. **Çarpma ve Bölme**: `*`, `/`, `\`, `MOD` – Soldan sağa değerlendirilir.
5. **Toplama ve Çıkarma**: `+`, `-` – Soldan sağa değerlendirilir.
6. **Karşılaştırma Operatörleri**: `<`, `>`, `<=`, `>=`, `=`, `<>` – Soldan sağa (aritmetik ifadelerde nadiren kullanılır).
7. **Mantıksal Operatörler**: `NOT`, `AND`, `OR` – Mantıksal ifadelerde kullanılır, ancak aritmetik bağlamda düşük önceliklidir.

**Örnek**:
```basic
DIM x AS DOUBLE
x = 2 + 3 * 4  ' 3 * 4 = 12, sonra 2 + 12 = 14
PRINT x         ' Çıktı: 14
x = (2 + 3) * 4  ' Parantez önce: 2 + 3 = 5, sonra 5 * 4 = 20
PRINT x          ' Çıktı: 20
x = 2 ^ 3 * 4    ' 2 ^ 3 = 8, sonra 8 * 4 = 32
PRINT x          ' Çıktı: 32
```

**Parantez Kullanımı**: Karmaşık ifadelerde işlem sırasını netleştirmek için parantez kullanılması önerilir. Örneğin:
```basic
DIM sonuc AS DOUBLE
sonuc = (5 + 3) * (2 ^ 2 - 4 / 2)  ' (5 + 3) * (4 - 2) = 8 * 2 = 16
PRINT sonuc                         ' Çıktı: 16
```

### 3. Desteklenen Matematiksel Fonksiyonlar

PDSX’in `function_table`’ındaki matematiksel fonksiyonlar, aritmetik hesaplamaları güçlendirir. Aşağıda tüm ilgili fonksiyonlar detaylandırılmıştır:

- **ABS(n)**: Mutlak değer. Örnek: `ABS(-10)` → `10`.
- **INT(n)**: En yakın küçük tamsayıya yuvarlar. Örnek: `INT(3.9)` → `3`.
- **SQR(n)**: Karekök. Örnek: `SQR(25)` → `5`.
- **SIN(n)**, **COS(n)**, **TAN(n)**, **ATN(n)**: Trigonometrik fonksiyonlar (n radyan cinsindedir). Örnek: `SIN(3.14159 / 2)` → `1`.
- **LOG(n)**: Doğal logaritma. Örnek: `LOG(2.71828)` → `1`.
- **EXP(n)**: Üstel fonksiyon. Örnek: `EXP(1)` → `2.71828`.
- **FIX(n)**: Ondalık kısmı atar. Örnek: `FIX(-3.7)` → `-3`.
- **ROUND(n, digits)**: Belirtilen basamağa yuvarlar. Örnek: `ROUND(3.14159, 3)` → `3.142`.
- **SGN(n)**: Sayının işaretini döndürür. Örnek: `SGN(-5)` → `-1`, `SGN(0)` → `0`.
- **MOD(x, y)**: Modülüs. Örnek: `MOD(10, 3)` → `1`.
- **MIN(*args)**, **MAX(*args)**: Birden fazla argümanın minimum/maksimum değerini döndürür. Örnek: `MIN(1, 2, 3)` → `1`.

**Örnek Kullanım**:
```basic
DIM pi AS DOUBLE
pi = 3.14159
PRINT SIN(pi / 2)      ' Çıktı: 1
PRINT ROUND(pi, 2)     ' Çıktı: 3.14
PRINT MOD(17, 5)       ' Çıktı: 2
PRINT MIN(10, 5, 8)    ' Çıktı: 5
```

### 4. Eksik Yönler

PDSX’in aritmetik hesaplamaları ve işlem önceliği genel olarak sağlam olsa da, bazı eksiklikler ve sınırlamalar vardır:

1. **Eksik Matematiksel Fonksiyonlar**:
   - **Hiperbolik Fonksiyonlar**: `sinh`, `cosh`, `tanh` gibi hiperbolik trigonometrik fonksiyonlar `function_table`’da tanımlı değil.
   - **Logaritma Çeşitleri**: Sadece doğal logaritma (`LOG`) destekleniyor; `log10` veya `log2` gibi diğer tabanlar eksik.
   - **Özel Fonksiyonlar**: Gamma, beta, erf gibi özel matematiksel fonksiyonlar bulunmuyor.
   - **Kombinasyonel Fonksiyonlar**: Faktöriyel, permütasyon, kombinasyon gibi fonksiyonlar eksik.

2. **Operatör Eksiklikleri**:
   - **Bit Operatörleri**: `AND`, `OR`, `XOR` gibi bit düzeyinde operatörler aritmetik bağlamda desteklenmiyor (sadece mantıksal operatörler olarak mevcut).
   - **Artırma/Azaltma Operatörleri**: `++`, `--` gibi operatörler PDSX’te bulunmuyor; bunun yerine `x = x + 1` kullanılmalı.
   - **Matris Operatörleri**: Matris ve vektör işlemleri için özel operatörler (örneğin, `@` Python’un matris çarpımı için) doğrudan desteklenmiyor, ancak `DOT` fonksiyonu bunu telafi ediyor.

3. **Hassasiyet ve Sayısal Kararlılık**:
   - PDSX, Python’un `float` türünü kullanır, bu nedenle çok büyük veya çok küçük sayılarla çalışırken sayısal hassasiyet sorunları yaşanabilir.
   - Büyük sayılar için `decimal` veya `mpmath` gibi yüksek hassasiyetli kütüphaneler entegre edilmemiştir.

4. **Sözdizimi Kısıtlamaları**:
   - Karmaşık ifadelerde, BASIC tarzı sözdizimi (örneğin, `LET` veya operatörlerin açık yazımı) modern dillerdeki kısa yazımlara kıyasla hantal olabilir.
   - Fonksiyon çağrıları için parantez zorunluluğu, bazı durumlarda (örneğin, `SIN 3.14` yerine `SIN(3.14)`) fazladan yazım gerektirir.

5. **Hata Mesajları**:
   - Aritmetik hatalar (örneğin, sıfıra bölme) `eval` tarafından yakalanır, ancak hata mesajları PDSX kullanıcıları için yeterince kullanıcı dostu olmayabilir (Python hata mesajları doğrudan gösterilir).

### 5. Öneriler ve İyileştirmeler

PDSX’in aritmetik hesaplamalarını güçlendirmek için aşağıdaki öneriler uygulanabilir:

1. **Eksik Fonksiyonların Eklenmesi**:
   - **Hiperbolik Fonksiyonlar**: `function_table`’a `SINH`, `COSH`, `TANH` eklenabilir.
     ```python
     self.function_table["SINH"] = np.sinh
     self.function_table["COSH"] = np.cosh
     self.function_table["TANH"] = np.tanh
     ```
   - **Logaritma Çeşitleri**: `LOG10`, `LOG2` eklenerek farklı tabanlar desteklenebilir.
     ```python
     self.function_table["LOG10"] = np.log10
     self.function_table["LOG2"] = np.log2
     ```
   - **Kombinasyonel Fonksiyonlar**: Faktöriyel ve kombinasyon için `FACT`, `COMB`, `PERM` eklenebilir.
     ```python
     from math import factorial, comb, perm
     self.function_table["FACT"] = factorial
     self.function_table["COMB"] = comb
     self.function_table["PERM"] = perm
     ```

2. **Bit Operatörleri Desteği**:
   - Bit düzeyinde operatörler (`&`, `|`, `^`, `~`) için destek eklenebilir.
     ```basic
     DIM a AS INTEGER
     DIM b AS INTEGER
     a = 5  ' Binary: 0101
     b = 3  ' Binary: 0011
     PRINT a & b  ' Çıktı: 1 (Binary: 0001)
     ```

3. **Yüksek Hassasiyetli Aritmetik**:
   - Büyük sayılar veya hassas hesaplamalar için `decimal` veya `mpmath` kütüphaneleri entegre edilebilir.
     ```python
     from decimal import Decimal
     self.function_table["DECIMAL"] = Decimal
     ```
     ```basic
     DIM x AS DOUBLE
     x = DECIMAL("0.1") + DECIMAL("0.2")  ' Hassas toplama
     PRINT x                              ' Çıktı: 0.3
     ```

4. **Kullanıcı Dostu Hata Mesajları**:
   - Aritmetik hatalar için özel hata mesajları üretilebilir.
     ```python
     def evaluate_expression(self, expr, scope_name=None):
         try:
             return eval(expr, namespace)
         except ZeroDivisionError:
             raise Exception("Hata: Sıfıra bölme!")
         except OverflowError:
             raise Exception("Hata: Sayı çok büyük!")
     ```

5. **Sözdizimi İyileştirmeleri**:
   - Parantezsiz fonksiyon çağrılarını desteklemek için `parse_program` yöntemi güncellenebilir (örneğin, `SIN 3.14` → `SIN(3.14)`).
   - Artırma/azaltma operatörleri (`++`, `--`) için destek eklenebilir.
     ```basic
     DIM x AS INTEGER
     x = 5
     x++  ' x = x + 1
     PRINT x  ' Çıktı: 6
     ```

6. **Zotero ve Veri Bilimi Entegrasyonu**:
   - Önceki taleplerinizde Zotero’dan veri çıkarma ve analiz yapma üzerine çalıştığınızı belirtmiştiniz. Aritmetik hesaplamalar, bu verilerle çalışırken faydalı olabilir. Örneğin, Zotero’dan çıkarılan sayısal verilerle aritmetik analiz:
     ```basic
     DIM veri AS ARRAY
     veri = ARRAY(PDF_EXTRACT_TABLES("C:\Zotero\storage\rapor.pdf")[0])
     DIM toplam AS DOUBLE
     toplam = SUM(veri)  ' Verilerin toplamı
     PRINT "Toplam: "; toplam
     DIM ortalama AS DOUBLE
     ortalama = toplam / LEN(veri)  ' Ortalama hesaplama
     PRINT "Ortalama: "; ortalama
     ```

### 6. Örnek: Aritmetik Hesaplamalar ve İşlem Önceliği

Aşağıdaki PDSX programı, aritmetik hesaplamaları ve işlem önceliğini gösterir, aynı zamanda veri bilimi bağlamında Zotero’dan veri işleme içerir:

```basic
REM Aritmetik Hesaplamalar ve Zotero Verisi
DIM x AS DOUBLE
DIM y AS DOUBLE
x = 10
y = 3

REM Temel aritmetik ve işlem önceliği
DIM sonuc1 AS DOUBLE
sonuc1 = x + y * 2 ^ 2  ' y * 2^2 = 12, x + 12 = 22
PRINT "Sonuç 1: "; sonuc1

DIM sonuc2 AS DOUBLE
sonuc2 = (x + y) * (2 ^ 2)  ' (10 + 3) * 4 = 52
PRINT "Sonuç 2: "; sonuc2

REM Matematiksel fonksiyonlar
DIM karekok AS DOUBLE
karekok = SQR(x)
PRINT "Karekök(x): "; karekok

DIM yuvarlama AS DOUBLE
yuvarlama = ROUND(3.14159, 2)
PRINT "Yuvarlanmış Pi: "; yuvarlama

REM Zotero’dan veri ile aritmetik
DIM tablo AS ARRAY
tablo = ARRAY(PDF_EXTRACT_TABLES("C:\Zotero\storage\veriler.pdf")[0])
DIM toplam AS DOUBLE
toplam = SUM(tablo)
DIM eleman_sayisi AS INTEGER
eleman_sayisi = LEN(tablo)
DIM ortalama AS DOUBLE
ortalama = toplam / eleman_sayisi
PRINT "Zotero Verisi Ortalaması: "; ortalama

REM Sonuçları kaydet
OPEN "aritmetik_sonuclar.txt" FOR OUTPUT AS #1
WRITE #1, "Sonuç 1: "; sonuc1
WRITE #1, "Sonuç 2: "; sonuc2
WRITE #1, "Zotero Ortalaması: "; ortalama
CLOSE #1
```

**Çıktı (Varsayımsal)**:
```
Sonuç 1: 22
Sonuç 2: 52
Karekök(x): 3.1622776601683795
Yuvarlanmış Pi: 3.14
Zotero Verisi Ortalaması: 5.5
```

**Açıklama**:
- Program, işlem önceliğini (`y * 2^2` önce değerlendirilir) ve parantez kullanımını gösterir.
- Matematiksel fonksiyonlar (`SQR`, `ROUND`) kullanılır.
- Zotero’dan tablo verisi çıkarılır ve aritmetik ortalama hesaplanır.
- Sonuçlar bir dosyaya kaydedilir.

### 7. Sonuç ve Gelecek Adımlar

PDSX, aritmetik hesaplamalar için sağlam bir temel sunar ve Python’un işlem önceliği kurallarını tamamen destekler. Ancak, eksik matematiksel fonksiyonlar, bit operatörleri ve hassasiyetle ilgili sınırlamalar giderilirse daha güçlü hale gelebilir. Zotero entegrasyonu ve veri bilimi odaklı talepleriniz için, aritmetik hesaplamalar veri analizi süreçlerini destekleyebilir.

**Sorular ve Öneriler**:
- Hangi spesifik aritmetik fonksiyonlara ihtiyaç duyuyorsunuz? (Örn. hiperbolik fonksiyonlar, faktöriyel)
- Bit düzeyinde işlemler veya yüksek hassasiyetli aritmetik öncelikli mi?
- Zotero verileriyle daha karmaşık aritmetik analizler (örneğin, istatistiksel hesaplamalar) için örnekler mi istiyorsunuz?

Geri bildiriminize göre, PDSX kodunu özelleştirebilir veya daha fazla örnek sağlayabilirim!