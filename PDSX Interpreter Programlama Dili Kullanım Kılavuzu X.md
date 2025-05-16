**PDSX Interpreter Programlama Dili Kullanım Kılavuzu**

---

## I. Giriş

**pdsX**, BASIC/QBasic/PDS 7.1 tarzından esinlenerek Python ile yazılmış, modern veri işleme, dosya, veritabanı ve web işlemleri destekleyen, satır bazlı bir programlama dili yorumlayıcısıdır. Geleneksel BASIC yapısını korurken, PDF içeriği okuma, SQLite kullanma, DataFrame analizi, web kazıma gibi modern beceriler sunar.

pdsX dosyaları `.basX` uzantısıyla yazılır ve `PDSX>` REPL ortamından ya da `pdsX.py dosya.basX` şeklinde çalıştırılabilir.

---

## II. Temel Yapılar

### II.1. Değişken Tanımları
```basic
DIM x AS INTEGER
DIM ad AS STRING
DIM dizi AS ARRAY
DIM df AS DATAFRAME
```

### II.2. Aritmetik ve Atama
```basic
LET x = 3 + 2 * (4 - 1)
y = x ^ 2  ' Üslü alma (^ yerine ** kullanabilirsiniz)
```

### II.3. Yazı ve Girdi
```basic
PRINT "Merhaba"
INPUT "Adınız:", isim
LINE INPUT "Soyadı:", soyisim
```

### II.4. Koşullu Yapılar
```basic
IF x > 10 THEN
  PRINT "Büyük"
ELSE
  PRINT "Küçük"
END IF
```

### II.5. Döngüler
```basic
FOR i = 1 TO 10 STEP 2
  PRINT i
NEXT

DO WHILE x < 100
  x = x + 1
LOOP
```

### II.6. Veri Tipleri
```basic
TYPE KISI
  AD AS STRING
  YAS AS INTEGER
END TYPE

DIM kisi1 AS KISI
```

### II.7. Alt Programlar ve Fonksiyonlar
```basic
SUB Yazdir()
  PRINT "Merhaba"
END SUB

FUNCTION Karesi(n)
  RETURN n * n
END FUNCTION
```

---

## II.8. PDF ve Metin Komutları

### II.8.1. PDF Komutları
```basic
LET icerik = PDF_READ_TEXT("belge.pdf")
LET tablolar = PDF_EXTRACT_TABLES("belge.pdf")
LET arama = PDF_SEARCH_KEYWORD("belge.pdf", "iklim")
```

### II.8.2.Metin Arama
```basic
LET sonuc = TXT_SEARCH("veri.txt", "balık")
LET analiz = TXT_ANALYZE("metin.txt")
```

---

## II.9. Web Komutları
```basic
LET html = WEB_GET("https://example.com")
LET sonuc = WEB_POST("https://form.com", "ad=Mete&yas=50")
LET baglantilar = SCRAPE_LINKS(html)
LET sayfa = SCRAPE_TEXT(html)
```

---

## II.10. Veri Bilimi Fonksiyonları
```basic
DIM x AS ARRAY
LET x = [1,2,3,4,5]
LET ort = MEAN(x)
LET medyan = MEDIAN(x)
LET sapma = STD(x)
```

### II.11.DataFrame Kullanımı
```basic
SELECT * FROM tablo INTO df
LET df2 = FILTER(df, "yas > 30")
LET df3 = GROUPBY(df, "il")
```

---

## II.12. Dosya ve ISAM Veritabanı
```basic
OPEN "test.txt" FOR OUTPUT AS #1
PRINT #1, "Merhaba"
CLOSE #1

OPEN "veri.db" FOR ISAM AS #5
DEFINE TABLE ogrenci (id AS INTEGER, ad AS STRING)
PUT #5, AUTOKEY, "Ali"
SELECT * FROM ogrenci INTO df
CLOSE #5
```

---

## II.13. Nesne ve Sınıf Kullanımı
```basic
CLASS Insan
  DIM ad AS STRING
  SUB Selamla()
    PRINT "Merhaba, "; self._vars["ad"]
  END SUB
END CLASS

DIM kisi AS Insan
LET kisi.ad = "Mete"
CALL kisi.Selamla()
```

---

## II.14. İleri Seviye Komutlar

- `ON ERROR GOTO` / `RESUME`
- `GOTO`, `GOSUB`, `RETURN`
- `IMPORT "modul.basX"`
- `ASSERT x > 0`
- `DEBUG ON`, `TRACE ON`

---

## IX. Komut Satırından Çalıştırma
```bash
pdsX ornek.basX
```
Ya da:
```bash
python pdsx_interpreter.py ornek.basX
```

---

## X. Yardım ve Geliştirme
- Dil geliştirilebilir yapıdadır.
- `.basX`, `.libX`, `.hX` dosyaları modül olarak import edilebilir.
- `DEFINE TYPE`, `DEFINE TABLE`, `DESCRIBE`, `CLASS`, `PRIVATE FUNCTION`, `STATIC`, `DIM SHARED` gibi özelliklerle ileri seviye programlama yapılabilir.

---

## XI. Kapanış

pdsX, geleneksel programlama dillerini seven ama modern Python dünyasını da entegre etmek isteyenler için eşsiz bir çözüm sunar. BASIC gibi okunabilir, Python gibi esnek ve C gibi veri yapılarına yakındır.

---

## III. Tüm Komutlar (Alfabetik Sıralı)

| Komut                  | Açıklama                                    |
| ---------------------- | ------------------------------------------- |
| APPEND                 | Bir dosyaya sonuna veri ekler               |
| ASSERT                 | Bir koşulun doğru olduğunu kontrol eder     |
| BEGIN TRANSACTION      | ISAM işlemlerinde işlem başlatır            |
| CALL                   | SUB/FUNCTION/Sınıf metodu çağırır           |
| CASE                   | SELECT CASE içinde dallanma yapar           |
| CHDIR                  | Çalışma dizinini değiştirir                 |
| CLASS                  | Yeni sınıf tanımlar                         |
| CLOSE                  | Dosya veya veritabanı bağlantısını kapatır  |
| COMMIT                 | Veritabanı işlem kaydı                      |
| DATA                   | READ ile kullanılacak sabit veri tanımı     |
| DEBUG ON/OFF           | Hata ayıklama modunu açar/kapatır           |
| DEFINE TABLE           | ISAM tablo tanımı yapar                     |
| DELETE                 | ISAM tablosundan kayıt siler                |
| DESCRIBE               | Sınıf yapısını açıklar                      |
| DIM                    | Değişken tanımlar                           |
| DO...LOOP              | Koşullu döngü başlatır                      |
| DROP TABLE             | ISAM tablosunu siler                        |
| ELSE                   | IF bloğunda alternatif yol belirtir         |
| END                    | Programı sonlandırır                        |
| END CLASS/FUNCTION/SUB | Yapıyı sonlandırır                          |
| END IF                 | IF yapısını kapatır                         |
| END SELECT             | SELECT yapısını kapatır                     |
| FILES                  | Dizin içeriklerini listeler                 |
| FOR...NEXT             | Sayaçlı döngü                               |
| FUNCTION               | Fonksiyon tanımı yapar                      |
| GET                    | ISAM'dan veya dosyadan veri alır            |
| GLOBAL                 | Global değişken tanımlar                    |
| GOSUB                  | Alt programa dallanır                       |
| GOTO                   | Belirtilen etikete gider                    |
| IF...THEN...ELSE       | Koşul kontrolü                              |
| IMPORT                 | Başka bir .basX dosyasını içe aktarır       |
| INDEX                  | Veritabanı için indeks oluşturur            |
| INPUT                  | Kullanıcıdan veri alır                      |
| JOIN                   | İki tabloyu birleştirir                     |
| KILL                   | Dosya siler                                 |
| LET                    | Değişken ataması                            |
| LINE INPUT             | Satır bazlı kullanıcı girişi                |
| LIST                   | Programı listeler                           |
| LOAD                   | Dosya yükler                                |
| LOCK                   | Dosya kilitler                              |
| LOOP                   | DO yapısını kapatır                         |
| MKDIR                  | Klasör oluşturur                            |
| NAME                   | Dosyayı yeniden adlandırır                  |
| NEW                    | Programı temizler                           |
| NEXT                   | FOR döngüsünü sonlandırır                   |
| ON ERROR GOTO          | Hata yakalama                               |
| OPEN                   | Dosya açar                                  |
| PRINT                  | Ekrana veri yazdırır                        |
| PUT                    | Dosyaya veya veritabanına veri yazar        |
| RANDOMIZE              | RND için rastgele tohum üretir              |
| READ                   | DATA verilerini okur                        |
| REMOVE                 | Liste/Dict/Set gibi yapılardan eleman siler |
| RESUME                 | Hata sonrası devam                          |
| RETURN                 | GOSUB'dan geri döner                        |
| ROLLBACK               | Veritabanı işlem iptali                     |
| RUN                    | Programı çalıştırır                         |
| SAVE                   | Dosya kaydeder                              |
| SELECT CASE            | Çoklu koşul kontrolü                        |
| SEEK                   | Dosya konumunu değiştirir                   |
| STATIC                 | Sınıf için statik değişken tanımlar         |
| STEP DEBUG             | Satır satır çalıştırma                      |
| SUB                    | Alt program tanımlar                        |
| SYSTEM                 | Programdan çıkar                            |
| TRUNCATE TABLE         | Tabloyu boşaltır                            |
| TYPE                   | Kullanıcı tanımlı veri tipi oluşturur       |
| UNLOCK                 | Kilit açar                                  |
| UPDATE                 | ISAM tablosunu günceller                    |
| WHILE...WEND           | Koşullu döngü                               |
| WRITE                  | Ekrana/dosyaya veri yazar                   |

---

## VI. Tüm Fonksiyonlar (Alfabetik Sıralı)

| Fonksiyon            | Açıklama                      |
| -------------------- | ----------------------------- |
| ABS(x)               | Mutlak değer                  |
| ARANGE               | NumPy aralık üretir           |
| ASC(c)               | Karakterin ASCII kodu         |
| ATN(x)               | Arktanjant değeri             |
| CHR\$(n)             | ASCII'den karakter            |
| CONCATENATE          | NumPy birleştirme             |
| COS(x)               | Kosinüs                       |
| COV(x,y)             | Kovaryans matrisi             |
| CROSS                | NumPy vektörel çarpım         |
| CUT                  | Pandas sınıflandırma          |
| DATE\$               | Tarih döndürür                |
| DESCRIBE(df)         | DataFrame istatistik özet     |
| DIAG                 | NumPy köşegen oluşturur       |
| DIFF                 | Fark alma                     |
| DOT                  | Matris çarpımı                |
| ENVIRON\$            | Ortam değişkenini alır        |
| EYE                  | Göz matrisi                   |
| EXP(x)               | e^x üstel fonksiyonu          |
| FILLNA               | Null'ları doldurur            |
| FIX(x)               | Truncates float to int        |
| FLIP                 | Diziyi ters çevirir           |
| FULL                 | NumPy sabit değer matrisi     |
| GROUPBY              | DataFrame grupla              |
| HEAD(df)             | İlk n satır                   |
| INKEY\$              | Tek karakter girişi           |
| INSTR                | Alt dize bulur                |
| INT(x)               | Tam sayı dönüşümü             |
| INV                  | Matris tersini alır           |
| LEN(x)               | Uzunluk                       |
| LEFT\$(s,n)          | Soldan n karakter             |
| LINSPACE             | NumPy eşit aralık üret        |
| LCASE\$              | Küçük harfe çevir             |
| LOC                  | Dosya pozisyonu               |
| LOF                  | Dosya uzunluğu                |
| LOG(x)               | Logaritma                     |
| LTRIM\$              | Sol boşlukları sil            |
| MAX(x,y,...)         | En büyük değer                |
| MEAN(x)              | Ortalama                      |
| MEDIAN(x)            | Medyan                        |
| MERGE                | DataFrame birleştir           |
| MID\$(s,i,n)         | Orta substring                |
| MIN(x,y,...)         | En küçük değer                |
| MKD\$, MKS\$, MKI\$  | Binary dönüşüm fonksiyonları  |
| MODE(x)              | Mod değeri                    |
| NORM                 | Norm hesapla                  |
| ONES                 | NumPy 1 matrisi               |
| PDF\_EXTRACT\_TABLES | PDF'den tablo çıkar           |
| PDF\_READ\_TEXT      | PDF'den metin oku             |
| PDF\_SEARCH\_KEYWORD | PDF'de anahtar kelime ara     |
| PCT\_CHANGE          | Oransal değişim               |
| POS                  | Kursör pozisyonu (simülasyon) |
| PROD(x)              | Çarpım                        |
| PIVOT\_TABLE         | Pivot tablo oluşturur         |
| QUANTILE             | Çeyrek değer                  |
| RESHAPE              | Şekil değiştir                |
| RIGHT\$(s,n)         | Sağdan n karakter             |
| RND                  | 0-1 arası rastgele sayı       |
| ROLL                 | NumPy kaydırma                |
| ROUND(x,n)           | Yuvarlama                     |
| RTRIM\$              | Sağ boşlukları sil            |
| SCRAPE\_LINKS        | HTML'deki tüm linkleri al     |
| SCRAPE\_TEXT         | HTML içeriği düz metne çevir  |
| SHIFT                | Kaydırma işlemi               |
| SIN(x)               | Sinüs                         |
| SOLVE                | Denklem çözme                 |
| SPACE\$(n)           | n adet boşluk                 |
| SQRT(x)              | Karekök                       |
| STACK                | Yığınla birleştirme           |
| STD(x)               | Standart sapma                |
| STR\$(n)             | Sayıyı string yapar           |
| SUM(x)               | Toplam                        |
| TAN(x)               | Tanjant                       |
| TIME\$               | Saat döndürür                 |
| TO\_DATETIME         | Zaman biçimine çevir          |
| TRANSPOSE            | Transpoz al                   |
| TXT\_ANALYZE         | Metin kelime analizi          |
| TXT\_SEARCH          | Metinde arama                 |
| TTEST                | t-testi uygular               |
| UCASE\$              | Büyük harfe çevirir           |
| VAL(s)               | Sayıya çevirir                |
| VAR(x)               | Varyans                       |
| VSTACK               | Dikey birleştirme             |
| WEB\_GET             | Web sayfası çek               |
| WEB\_POST            | Web'e veri gönder             |
| ZEROS                | NumPy sıfır dizisi            |

---

## V. Komutlar: İşlev Gruplarına Göre

| Grup                 | Komutlar                                              |
|----------------------|--------------------------------------------------------|
| Kontrol              | IF, ELSE, END IF, SELECT CASE, CASE, END SELECT       |
| Döngüler             | FOR...NEXT, WHILE...WEND, DO...LOOP                   |
| Giriş/Çıkış          | PRINT, INPUT, LINE INPUT, WRITE, READ, DATA           |
| Dosya İşlemleri      | OPEN, CLOSE, PRINT #, INPUT #, SEEK, GET, PUT, KILL   |
| Veritabanı           | OPEN FOR ISAM, DEFINE TABLE, SELECT, INSERT, UPDATE   |
| Hata Yönetimi        | ON ERROR GOTO, RESUME, RESUME NEXT                    |
| Modülerlik           | SUB, FUNCTION, CALL, IMPORT                           |
| Değişken Tanımları   | DIM, GLOBAL, STATIC, TYPE, CLASS                      |
| Sistem Komutları     | SYSTEM, LIST, RUN, NEW, SAVE, LOAD                    |

---

## VI. Fonksiyonlar: İşlev Gruplarına Göre

| Grup                | Fonksiyonlar (Örnekler)                              |
|---------------------|------------------------------------------------------|
| Matematik           | ABS, SIN, COS, TAN, LOG, EXP, SQRT, ROUND, INT       |
| İstatistik          | MEAN, MEDIAN, MODE, VAR, STD, SUM, PROD, CORR        |
| Metin               | LEFT$, RIGHT$, MID$, INSTR, UCASE$, LCASE$           |
| Tarih/Saat          | DATE$, TIME$, TIMER                                   |
| Dizi/Matris         | ZEROS, ONES, FULL, RESHAPE, TRANSPOSE, DOT, CROSS    |
| DataFrame           | HEAD, TAIL, DESCRIBE, GROUPBY, MERGE, PIVOT_TABLE     |
| Dosya/Path          | LOF, LOC, DIR$                                       |
| PDF İşlemleri       | PDF_READ_TEXT, PDF_EXTRACT_TABLES, PDF_SEARCH_KEYWORD|
| Web İşlemleri       | WEB_GET, WEB_POST, SCRAPE_LINKS, SCRAPE_TEXT         |
| Sistem              | ENVIRON$, COMMAND$                                   |

---

## VII. REPL Ortamı ve Örnek Kullanım

REPL ortamı, terminalde `python pdsx.py` komutuyla başlatılır. Komut istemi `PDSX>` şeklindedir.

### Örnekler

```basic
DIM A AS INTEGER
LET A = 5 * 10 + 2
PRINT A
```

```basic
FUNCTION KARE(x)
  RETURN x * x
END FUNCTION
PRINT KARE(4)
```

```basic
CLASS DENEME
  DIM mesaj AS STRING
  SUB yaz()
    PRINT mesaj
  END SUB
END CLASS
DIM d AS DENEME
LET d.mesaj = "Merhaba Dünya"
CALL d.yaz()
```

### Hata Senaryosu
```basic
LET X = 5 / 0   ' Sıfıra bölme hatası
ON ERROR GOTO HATA
PRINT "Bu satır atlanır"
LABEL HATA
PRINT "Hata yakalandı."
```

---

## VIII. Test Dosyaları (.basX)

- `hello.basX`: Temel giriş/çıkış
- `math_test.basX`: Aritmetik işlemler
- `class_test.basX`: CLASS tanımlama ve çağırma
- `file_test.basX`: Dosya yazma/okuma
- `pdf_test.basX`: PDF okuma örneği

---

## IX. Programlama El Kitabı (Örnekli)

### Komut: PRINT
**Amaç:** Ekrana veri yazdırır. 
**Kullanım:**
```basic
PRINT "Merhaba"
PRINT A + B
```
**Hatalar:**
- Tanımsız değişken yazılması: `NameError`
**İpucu:** Virgül ile boşluk, noktalı virgül ile aynı satıra çoklu çıktı alınabilir.

### Komut: INPUT
**Amaç:** Kullanıcıdan veri alır.
**Kullanım:**
```basic
INPUT "Yaşınız:", YAS
```
**Hatalar:**
- Kullanıcıdan beklenen tür ile eşleşmezse mantıksal hata oluşur.

### Komut: IF...THEN...ELSE
**Amaç:** Koşula bağlı dallanma sağlar.
**Kullanım:**
```basic
IF A > 10 THEN
  PRINT "Büyük"
ELSE
  PRINT "Küçük"
END IF
```
**İpucu:** Karmaşık koşullarda parantez kullanımı tercih edilmelidir.

### Komut: FOR...NEXT
**Amaç:** Belirli sayıda yineleme yapar.
**Kullanım:**
```basic
FOR I = 1 TO 5
  PRINT I
NEXT
```
**İpucu:** STEP ile adım değeri tanımlanabilir.

### Komut: DO...LOOP
**Amaç:** Koşullu döngü sağlar.
**Kullanım:**
```basic
DO WHILE X < 5
  PRINT X
  LET X = X + 1
LOOP
```
**İpucu:** DO UNTIL, LOOP WHILE gibi varyantları da desteklenir.

### Komut: WHILE...WEND
**Amaç:** Koşul sağlandığı sürece çalışır.
**Kullanım:**
```basic
WHILE A < 10
  PRINT A
  LET A = A + 1
WEND
```

## Fonksiyonlar

### LEN

- **Açıklama:** Bir dizgenin uzunluğunu döner.
- **Örnek:**  
  ```pdsX
  PRINT LEN("Merhaba")  ' 7
  ```

---

### MID$

- **Açıklama:** Bir dizgenin ortasından karakter alır.
- **Örnek:**
  ```pdsX
  PRINT MID$("Merhaba", 2, 3)  ' "erb"
  ```

---

### DATE$, TIME$

- **Açıklama:** Geçerli tarihi/saatı verir.
- **Örnek:**
  ```pdsX
  PRINT "Bugün: "; DATE$()
  PRINT "Saat: "; TIME$()
  ```

---

### SIN, COS, TAN

- **Açıklama:** Trigonometrik fonksiyonlar
- **Örnek:**
  ```pdsX
  PRINT SIN(3.14 / 2)  ' 1.0
  ```

---

### VAL

- **Açıklama:** String içinden sayı çıkarır.
- **Örnek:**
  ```pdsX
  LET x = VAL("123.45")  ' x = 123.45
  ```

---

### MEAN, STD, VAR

- **Açıklama:** Veri kümesi istatistikleri
- **Örnek:**
  ```pdsX
  DIM d AS ARRAY
  LET d = [1,2,3,4,5]
  PRINT MEAN(d)
  PRINT STD(d)
  PRINT VAR(d)
  ```

---

## REPL Kullanımı

```bash
pdsX
```

Komut satırından REPL'e girilir. Çıkmak için:

```pdsX
SYSTEM
```

---

## Dosya Çalıştırma

```bash
pdsX.py program.basX
```

---

## Öneriler

- Her `.basX` dosyasını `SAVE` komutuyla kaydet.
- Fonksiyonları test etmek için `REPL` modunda deneyebilirsin.
- PDF işlemleri için: `PDF_READ_TEXT`, `PDF_SEARCH_KEYWORD`, `PDF_EXTRACT_TABLES`

---

## X. Syntax Kontrol Aracı (Linter/Ön Analiz Planı)

pdsX dili için geliştirilecek linter, `.basX` dosyalarında olası sözdizimi, yapı ve mantık hatalarını önceden tespit etmeyi amaçlar. İşlevsel hedefler aşağıdaki gibidir:

### A. Blok ve Yapı Eşleştirme
- `IF...THEN...ELSE...END IF`, `FOR...NEXT`, `WHILE...WEND`, `DO...LOOP`, `SELECT CASE...CASE...END SELECT` gibi yapıların dengeli kapanıp kapanmadığı kontrol edilecek.
- `SUB`, `FUNCTION`, `CLASS`, `TYPE` bloklarının iç içelik, açık/kapalı kontrolü yapılacak.

### B. Etiket ve Atlama Komutları
- Tanımlı `LABEL` olup olmadığı kontrol edilecek.
- `GOTO`, `GOSUB`, `ON ERROR GOTO` gibi dallanma komutları geçerli bir etikete yönleniyor mu?

### C. Değişken ve Tip Takibi
- `DIM`, `GLOBAL`, `SHARED` ile tanımlanmış tüm değişkenler izlenecek.
- `LET`, `=`, `INPUT`, `READ` gibi atama veya değer yükleme noktalarında:
  - Değişken tipi daha önce tanımlanmış mı?
  - Tip uyumluluğu var mı? Örneğin:
    - `LET x = "metin"` ancak `x INTEGER` ise uyarı.
    - `LET y = 15.4` ama `y STRING` ise uyarı.
- Tip dönüşümlerinde açıkça `STR$()`, `INT()`, `VAL()` gibi fonksiyonların kullanılması önerilecek.

### D. Fonksiyon/Alt Program Çağrıları
- `CALL`, `GOSUB`, `FUNCTION()` çağrılarında:
  - Var olmayan alt program veya fonksiyon ismine uyarı.
  - Parametre sayısı ve tipi ile tanımın eşleşip eşleşmediği kontrol edilir.

### E. Kullanılmayan Tanımlar
- Tanımlanıp hiç çağrılmayan `SUB`, `FUNCTION`, `LABEL`, `GLOBAL`, `DIM` blokları için "kullanılmıyor" uyarısı verilir.

### F. Dosya ve Veritabanı Bağlantıları
- `OPEN`, `PUT`, `GET`, `UPDATE`, `SELECT`, `DELETE`, `JOIN` gibi işlemler için dosya veya bağlantının önceden tanımlı/açık olup olmadığı kontrol edilir.

### G. Komut Sırası, Anlamlılık ve Sözdizimi Kontrolü
- `PRINT`, `INPUT`, `CALL` gibi komutlar içinde:
  - Eksik parantez, kapatılmamış tırnak, yanlış operatör, fazla parametre gibi sözdizimi hataları kontrol edilir.
  - Tanınmayan komut veya fonksiyon isimleri bildirilir.
  - Bloklar içindeki kodlama hataları (ör. `IF THEN` satırında `THEN` eksikliği) raporlanır.
- Önerilen yapılar teşvik edilir: 
  - `IF x THEN PRINT x` yerine 
    ```
    IF x THEN
      PRINT x
    END IF
    ```
  şeklinde açık blok yapısı önerilir.

---

Bu yapıya uygun olarak geliştirilecek linter/analiz programı, `.basX` dosyasını okuyarak satır satır analiz edecek ve her tespit için aşağıdaki çıktıları üretecek:

| Satır | Hata Türü         | Açıklama                                         | Öneri                          |
|------|-------------------|--------------------------------------------------|---------------------------------|
| 12   | Tip Uyumsuzluğu   | LET x = "merhaba" ancak x INTEGER tanımlı       | STR$() ile dönüştür önerisi    |
| 25   | Sözdizimi Hatası  | IF x yazılmış ama THEN eksik                    | THEN ekleyin veya koşulu düzeltin |
| 40   | Tanımsız Fonksiyon| FUNC123() diye bir fonksiyon tanımsız          | Fonksiyon tanımını kontrol edin |

Linter sonunda uyarılar dosya olarak da `.lnt` uzantısıyla kaydedilebilir.

---

PDSX programlama dilinde `READ` ve `RESTORE` komutları, veri okuma ve veri işaretçisi yönetimi için kullanılır. Bu komutlar, GW-BASIC ve QBASIC’ten miras alınmış olup, özellikle program içinde tanımlı statik veri kümeleriyle (`DATA` ifadeleriyle) çalışmak için tasarlanmıştır. `pdsXInterpreter` sınıfında bu komutlar, veri manipülasyonunu kolaylaştırmak için `execute_command` yöntemi aracılığıyla uygulanır. Aşağıda, `READ` ve `RESTORE` komutlarının işlevleri, sözdizimleri, kullanım örnekleri, yetenekleri, eksiklikleri ve önceki konuşmalarınızdaki Zotero entegrasyonu, veri bilimi ve web kazıma (örneğin, TÜİK, FAO, TradeMap) bağlamında nasıl kullanılabileceği detaylı bir şekilde Türkçe olarak açıklanacaktır.

---

## PDSX’te `READ` ve `RESTORE` Komutları

### 1. `READ` Komutu

#### **Açıklama**
`READ` komutu, program içinde `DATA` ifadeleriyle tanımlanmış statik verileri sırayla okur ve bu verileri değişkenlere atar. `DATA` ifadeleri, programın herhangi bir yerinde (genellikle programın başında veya sonunda) sabit veri listeleri tanımlamak için kullanılır. `READ`, bu verileri bir işaretçi (cursor) aracılığıyla sırayla alır ve her çağrıldığında işaretçi bir sonraki veri öğesine ilerler.

#### **Sözdizimi**
```basic
READ degisken [, degisken...]
```

- **degisken**: Verinin atanacağı değişken (örneğin, `STRING`, `INTEGER`, `DOUBLE`).
- Birden fazla değişken belirtilirse, `DATA` listesinden sırayla değerler atanır.

#### **Nasıl Çalışır?**
- `DATA` ifadeleri, programda bir veri havuzu oluşturur (örneğin, sayılar, metinler).
- `READ`, bu veri havuzundan işaretçinin o anki konumundaki veriyi okur.
- İşaretçi, her `READ` çağrısında bir sonraki öğeye ilerler.
- Veri tipi uyumsuzluğu (örneğin, `STRING` beklenirken `INTEGER` okunması) hata üretebilir.

#### **Örnek**
```basic
DATA "Ali", 30, "Veli", 25
DIM ad1 AS STRING
DIM yas1 AS INTEGER
DIM ad2 AS STRING
DIM yas2 AS INTEGER
READ ad1, yas1, ad2, yas2
PRINT ad1; " "; yas1
PRINT ad2; " "; yas2
```

**Çıktı**:
```
Ali 30
Veli 25
```

**Açıklama**:
- `DATA` ifadesi, `"Ali", 30, "Veli", 25` verilerini tanımlar.
- `READ`, bu verileri sırayla `ad1`, `yas1`, `ad2`, `yas2` değişkenlerine atar.

### 2. `RESTORE` Komutu

#### **Açıklama**
`RESTORE` komutu, `DATA` işaretçisini veri havuzunun başına veya belirli bir etikete sıfırlar. Bu, `READ` komutunun aynı veri kümesini tekrar okumasını sağlar. Varsayılan olarak, işaretçi programın tüm `DATA` ifadelerinin başına döner, ancak bir etiket belirtilirse, işaretçi o etiketteki `DATA` ifadesine gider.

#### **Sözdizimi**
```basic
RESTORE [etiket]
```

- **etiket** (isteğe bağlı): İşaretçinin sıfırlanacağı `DATA` ifadesinin bulunduğu etiket.
- Etiket belirtilmezse, işaretçi tüm `DATA` ifadelerinin başına döner.

#### **Nasıl Çalışır?**
- `RESTORE` çağrıldığında, `READ` için veri işaretçisi sıfırlanır.
- Sonraki `READ` komutları, sıfırlanan konumdan itibaren verileri okur.
- Etiketli `DATA` ifadeleri, veri kümelerini organize etmek için kullanılır.

#### **Örnek**
```basic
DATA 10, 20, 30
DIM x AS INTEGER
READ x
PRINT x  ' Çıktı: 10
RESTORE
READ x
PRINT x  ' Çıktı: 10 (tekrar başa döndü)
```

**Etiketli Örnek**:
```basic
birinci:
DATA 1, 2, 3
ikinci:
DATA 4, 5, 6
DIM x AS INTEGER
READ x
PRINT x  ' Çıktı: 1
RESTORE ikinci
READ x
PRINT x  ' Çıktı: 4
```

**Açıklama**:
- İlk `READ`, `birinci` etiketindeki veriden başlar (`1`).
- `RESTORE ikinci`, işaretçiyi `ikinci` etiketindeki veriye sıfırlar (`4`).

### 3. `DATA` İfadesi (Bağlam için)

`READ` ve `RESTORE` komutları, `DATA` ifadeleriyle birlikte çalışır. `DATA`, programda sabit veri kümeleri tanımlamak için kullanılır.

#### **Sözdizimi**
```basic
DATA deger [, deger...]
```

- **deger**: Sayılar (`INTEGER`, `DOUBLE`), metinler (`STRING`) veya diğer ilkel tipler.
- Virgülle ayrılmış birden fazla değer tanımlanabilir.

#### **Örnek**
```basic
DATA "Ankara", "İstanbul", "İzmir"
DIM sehir AS STRING
READ sehir
PRINT sehir  ' Çıktı: Ankara
```

### 4. Yetenekler

1. **Basit Veri Yönetimi**:
   - `READ` ve `RESTORE`, program içinde sabit verileri kolayca yönetmek için idealdir.
   - Küçük ölçekli veri kümeleri (örneğin, test verileri, konfigürasyonlar) için pratiktir.

2. **Esnek Kullanım**:
   - `RESTORE` ile veri işaretçisi kontrolü, aynı verilerin tekrar tekrar okunmasını sağlar.
   - Etiketli `DATA` ifadeleri, veri kümelerini organize eder.

3. **GW-BASIC Uyumluluğu**:
   - BASIC programcıları için tanıdık bir mekanizma sunar, mevcut kodların taşınmasını kolaylaştırır.

4. **Zotero ve Veri Bilimi Entegrasyonu**:
   - `DATA` ile tanımlı test verileri, Zotero’dan veya web kazımasından alınan verilerle karşılaştırma için kullanılabilir.
   - Örneğin, TÜİK verileriyle eşleşen bir referans veri kümesi `DATA` ile tanımlanabilir.

5. **Hata Yönetimi**:
   - Veri tipi uyumsuzlukları veya veri sonuna ulaşma gibi hatalar, `ON ERROR GOTO` ile yönetilebilir.

### 5. Eksiklikler

1. **Sınırlı Veri Türleri**:
   - `DATA` ifadeleri yalnızca ilkel tipleri (`STRING`, `INTEGER`, `DOUBLE` vb.) destekler. Koleksiyonlar (`LIST`, `DICT`) veya gelişmiş tipler (`ARRAY`, `DATAFRAME`) doğrudan tanımlanamaz.
   - Örnek: `DATA [1, 2, 3]` veya `DATA {"ad": "Ali"}` geçersizdir.

2. **Dinamik Veri Desteği Eksikliği**:
   - `READ` ve `RESTORE`, yalnızca statik `DATA` ifadeleriyle çalışır. Dosyadan, veritabanından veya web’den dinamik veri okuma için uygun değildir (bunun için `INPUT #`, `SELECT` veya `WEB_GET` kullanılır).

3. **Performans**:
   - Büyük veri kümeleri için `DATA` ve `READ` yavaş olabilir, çünkü veriler bellekte sırayla işlenir ve optimize edilmiş bir veri yapısı kullanılmaz.

4. **Hata Mesajları**:
   - Veri tipi uyumsuzluğu veya veri sonuna ulaşma hataları, kullanıcı dostu mesajlar üretmeyebilir (Python’un `eval` hataları doğrudan gösterilir).

5. **Sözdizimi Kısıtlamaları**:
   - `DATA` ifadeleri, karmaşık veri yapılarını (örneğin, iç içe listeler veya JSON benzeri yapılar) desteklemez.
   - `RESTORE`’un etiketli kullanımı, büyük programlarda etiket çakışmalarına yol açabilir.

6. **Zotero ve Veri Bilimi için Sınırlamalar**:
   - Zotero’dan veya TÜİK’ten alınan büyük veri kümeleri için `DATA` ifadeleri pratik değildir; `DATAFRAME` veya dosya işlemleri daha uygun olur.
   - Örneğin, Zotero’dan çıkarılan bir PDF tablosunu `DATA` ile tanımlamak hantal ve verimsizdir.

### 6. Zotero ve Veri Bilimi Entegrasyonu

Önceki konuşmalarınızda Zotero kütüphanelerinden veri işleme (örneğin, `C:\Users\mete\Zotero\zotasistan\zapata_m6h`), TÜİK, FAO, TradeMap gibi sitelerden veri kazıma ve dosya çıktıları oluşturma (örneğin, `zapata_m6hx`) talepleriniz vardı. `READ` ve `RESTORE` komutları, bu bağlamlarda test verileri veya referans veri kümeleri için kullanılabilir.

#### **Zotero için Test Verileri**
Zotero’dan çıkarılan verilerle karşılaştırma yapmak için `DATA` ve `READ` kullanma:

```basic
DATA "Tablo 1", 50.5, "Tablo 2", 75.2
DIM beklenen AS DICT
DIM ad AS STRING
DIM deger AS DOUBLE
beklenen = DICT()
WHILE NOT EOF(DATA)
    READ ad, deger
    beklenen(ad) = deger
WEND

DIM tablolar AS LIST
tablolar = PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
DIM df AS DATAFRAME
df = DATAFRAME(tablolar[0])
DIM ortalama AS DOUBLE
ortalama = MEAN(ARRAY(tablolar[0]))
IF ortalama = beklenen("Tablo 1") THEN
    PRINT "Zotero verisi beklenenle eşleşiyor"
ELSE
    PRINT "Eşleşme yok"
END IF
```

#### **TÜİK Verileri için Referans**
TÜİK’ten kazınan verileri bir `DATA` kümesiyle doğrulama:

```basic
DATA "2023-01", 1234.56, "2023-02", 1250.78
DIM tarih AS STRING
DIM deger AS DOUBLE
DIM referans AS DICT
referans = DICT()
WHILE NOT EOF(DATA)
    READ tarih, deger
    referans(tarih) = deger
WEND

DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM veriler AS LIST
veriler = SCRAPE_TABLES(html)
IF veriler[0] = referans("2023-01") THEN
    PRINT "TÜİK verisi doğru"
ELSE
    PRINT "Veri uyuşmazlığı"
END IF
```

### 7. Örnek: Kapsamlı Kullanım

Aşağıdaki program, `READ`, `RESTORE`, Zotero ve TÜİK verilerini birleştirir:

```basic
REM Zotero ve TÜİK için Test Verileri
birinci:
DATA "Zotero", "Tablo 1", 50.5
ikinci:
DATA "TÜİK", "Ekonomi", 1234.56

DIM analiz AS LIST
analiz = LIST()

DIM kaynak AS STRING
DIM kategori AS STRING
DIM deger AS DOUBLE

REM İlk veri kümesini oku
READ kaynak, kategori, deger
analiz = APPEND(analiz, DICT("kaynak", kaynak, "deger", deger))

REM Zotero verisiyle karşılaştır
DIM tablolar AS LIST
tablolar = PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
IF MEAN(ARRAY(tablolar[0])) = deger THEN
    PRINT "Zotero verisi eşleşti"
END IF

REM TÜİK verisine geç
RESTORE ikinci
READ kaynak, kategori, deger
analiz = APPEND(analiz, DICT("kaynak", kaynak, "deger", deger))

REM TÜİK verisiyle karşılaştır
DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM veriler AS LIST
veriler = SCRAPE_TABLES(html)
IF veriler[0] = deger THEN
    PRINT "TÜİK verisi eşleşti"
END IF

REM Sonuçları kaydet
OPEN "sonuclar.txt" FOR OUTPUT AS #1
PRINT #1, analiz
CLOSE #1
```

**Çıktı (Varsayımsal)**:
```
Zotero verisi eşleşti
TÜİK verisi eşleşti
```

**Açıklama**:
- `DATA` ile Zotero ve TÜİK için referans veriler tanımlanır.
- `READ` ile veriler okunur ve `DICT`’lere atanır.
- `RESTORE` ile işaretçi TÜİK verilerine sıfırlanır.
- Zotero ve TÜİK verileriyle karşılaştırma yapılır.
- Sonuçlar bir dosyaya kaydedilir.

### 8. Öneriler ve İyileştirmeler

1. **Karmaşık Veri Türleri Desteği**:
   - `DATA` ifadelerine `LIST`, `DICT`, `ARRAY` gibi tiplerin tanımlanabilmesi için destek eklenebilir:
     ```basic
     DATA [1, 2, 3], {"ad": "Ali"}
     DIM liste AS LIST
     READ liste
     ```
     ```python
     self.data_pool.append(eval(data_line))  # Karmaşık tipleri destekle
     ```

2. **Dinamik Veri Entegrasyonu**:
   - `READ`’in dosya veya veritabanından veri okuması için genişletilmesi:
     ```basic
     READ #1 INTO degisken  ' Dosyadan oku
     READ FROM TABLE kullanicilar INTO degisken  ' Veritabanından oku
     ```

3. **Hata Mesajları**:
   - Veri tipi uyumsuzlukları için kullanıcı dostu mesajlar:
     ```python
     try:
         self.data_pool[self.data_pointer]
     except IndexError:
         raise Exception("Hata: DATA sonuna ulaşıldı!")
     except TypeError:
         raise Exception("Hata: Veri tipi uyumsuzluğu!")
     ```

4. **Performans Optimizasyonu**:
   - Büyük `DATA` kümeleri için bir önbellek veya indeksleme mekanizması eklenebilir.

5. **Zotero ve Veri Bilimi için Özel Kullanım**:
   - Zotero’dan tablo verilerini `DATA` benzeri bir yapıya otomatik dönüştürme:
     ```basic
     DATA FROM PDF "C:\Zotero\belge.pdf" INTO tablo_verileri
     READ tablo_verileri INTO df
     ```
     ```python
     self.function_table["DATA_FROM_PDF"] = lambda file: pdfplumber.open(file).pages[0].extract_tables()
     ```

### 9. Sonuç ve Gelecek Adımlar

`READ` ve `RESTORE` komutları, PDSX’te statik veri kümeleriyle çalışmak için etkili bir mekanizma sunar. Zotero’dan veya TÜİK’ten alınan verilerle karşılaştırma gibi senaryolarda test verileri için kullanılabilir. Ancak, karmaşık veri türleri, dinamik veri desteği ve performans gibi alanlarda iyileştirmeler yapılabilir.

---

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

---

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

---

Sorunuz, PDSX programlama dilinde C tarzı esnek veri tiplerinin (işaretçiler, yapılar, birleşimler) eklenip eklenmediği, bu eklemelerin ne derece esneklik sağladığı ve özellikle `STRUCT` ve `UNION` veri tiplerinin `TYPE` komutundan farkları ile nasıl kullanıldığı üzerine odaklanıyor. Önceki konuşmalarınızda Zotero entegrasyonu, veri bilimi, web kazıma (TÜİK, FAO, TradeMap) ve dosya işlemleri gibi talepleriniz vardı; bu bağlamda, esnek veri tiplerinin bu senaryolarda nasıl kullanılabileceğini de ele alacağım. Aşağıda, PDSX’in mevcut durumu, C tarzı veri tiplerinin durumu, `STRUCT` ve `UNION`’ın detaylı kullanımı, `TYPE` ile farkları, sağlanan esneklik ve eksiklikler Türkçe olarak kapsamlı bir şekilde açıklanacaktır.

---

## PDSX’te C Tarzı Esnek Veri Tipleri ve Durum

Öncelikle, belirttiğiniz “C tarzı esnek veri tipleri (işaretçiler, yapılar, birleşimler) eklenerek daha düşük seviyeli kontrol sağlanacak” ifadenizi ele alalım. PDSX’in mevcut tasarımında, `pdsXInterpreter` sınıfı ve `type_table` aracılığıyla bazı C tarzı veri tipleri destekleniyor, ancak tam anlamıyla C’nin düşük seviyeli kontrolü (örneğin, işaretçiler ve bellek yönetimi) henüz uygulanmamış görünüyor. Aşağıda, bu özelliklerin mevcut durumunu ve sağlanan esnekliği detaylı bir şekilde inceliyorum.

### 1. Mevcut Durum: C Tarzı Veri Tipleri

PDSX, GW-BASIC ve QBASIC’in yapısal doğasını korurken, modern veri manipülasyonu için bazı esnek veri tiplerini destekler. Mevcut veri tipleri arasında şunlar yer alıyor:
- **Yapılar (`STRUCT`)**: C’deki `struct` benzeri, birden fazla veri alanını bir arada tutan veri tipleri.
- **Birleşimler (`UNION`)**: C’deki `union` benzeri, aynı bellek alanını farklı veri tipleriyle paylaşan veri tipleri.
- **Kullanıcı Tanımlı Tipler (`TYPE`)**: Yapısal veri organizasyonu için, `STRUCT`’a benzer ancak daha yüksek seviyeli.
- **Koleksiyonlar (`LIST`, `DICT`, `ARRAY`)**: Veri bilimi ve esnek veri manipülasyonu için.

Ancak, **işaretçiler (pointers)** ve düşük seviyeli bellek yönetimi (örneğin, C’deki `*` veya `&` operatörleri) PDSX’te açıkça desteklenmiyor. Bunun nedeni, PDSX’in yüksek seviyeli, BASIC tarzı bir dil olarak tasarlanması ve Python’un dinamik tip sistemi ile `eval` tabanlı değerlendirme mekanizmasına dayanmasıdır. İşaretçiler, düşük seviyeli bellek erişimi gerektirir ve PDSX’in mevcut mimarisinde bu tür bir kontrol sağlanmamaktadır.

#### **Yapıldı mı?**
- **Yapılar (`STRUCT`)**: Evet, PDSX’te `STRUCT` destekleniyor ve C’deki `struct`’a benzer şekilde birden fazla veri alanını bir arada tutuyor. Bu, esnek veri manipülasyonu için kullanışlıdır.
- **Birleşimler (`UNION`)**: Evet, PDSX’te `UNION` destekleniyor, ancak kullanımı sınırlı ve C’deki kadar düşük seviyeli değil. Aynı bellek alanını paylaşan veri tipleri için kullanılıyor.
- **İşaretçiler**: Hayır, işaretçiler PDSX’te uygulanmamış. Düşük seviyeli bellek yönetimi veya işaretçi aritmetiği gibi özellikler eksik.
- **Esneklik**: `STRUCT` ve `UNION`, veri organizasyonu ve bellek verimliliği açısından esneklik sağlıyor, ancak işaretçilerin eksikliği nedeniyle C tarzı düşük seviyeli kontrol sınırlı. PDSX, yapısal doğasını koruyor ve veri bilimi, Zotero entegrasyonu gibi yüksek seviyeli görevlerde güçlü, ancak donanıma yakın işlemler için yetersiz.

#### **Sağlanan Esneklik**
- **Veri Organizasyonu**: `STRUCT` ve `UNION`, karmaşık veri yapılarını (örneğin, Zotero’dan tablo verileri veya TÜİK’ten istatistiksel veriler) organize etmek için esneklik sunar.
- **Bellek Verimliliği**: `UNION`, aynı bellek alanını farklı tiplerle paylaşarak bellek kullanımını optimize edebilir.
- **Veri Bilimi ve Zotero**: `STRUCT` ve `UNION`, veri çerçeveleri (`DATAFRAME`) veya listelerle (`LIST`) birlikte kullanıldığında, veri manipülasyonunu yapılandırılmış hale getirir.
- **Sınırlamalar**: İşaretçilerin eksikliği, dinamik bellek tahsisi (örneğin, bağlı listeler veya ağaçlar oluşturma) gibi düşük seviyeli veri yapılarında esnekliği kısıtlar. PDSX, daha çok yüksek seviyeli veri işleme (NumPy, Pandas) üzerine odaklanır.

### 2. `STRUCT` ve `UNION`’ın Detaylı Kullanımı

PDSX’te `STRUCT` ve `UNION`, kullanıcı tanımlı veri tipleri olarak `TYPE`’a alternatif sunar. Aşağıda, bu veri tiplerinin sözdizimi, kullanım örnekleri ve özellikleri detaylı bir şekilde açıklanmıştır.

#### **STRUCT**
- **Açıklama**: `STRUCT`, birden fazla veri alanını bir arada tutan bir veri tipidir. Her alan kendi belleğini kullanır ve C’deki `struct`’a benzer şekilde çalışır. Farklı veri tiplerini birleştirerek karmaşık veri yapılarını temsil etmek için kullanılır.
- **Sözdizimi**:
  ```basic
  STRUCT struct_adi
      alan_adi AS veri_tipi
      ...
  END STRUCT
  ```
- **Özellikler**:
  - Her alan ayrı bir bellek bölgesinde saklanır.
  - Alanlara nokta operatörü (`.`) ile erişilir.
  - İç içe `STRUCT` tanımları desteklenir.
- **Örnek**:
  ```basic
  STRUCT Nokta
      x AS DOUBLE
      y AS DOUBLE
  END STRUCT

  DIM p AS Nokta
  p.x = 1.5
  p.y = 2.5
  PRINT "Nokta: ("; p.x; ", "; p.y; ")"
  ```

  **Çıktı**:
  ```
  Nokta: (1.5, 2.5)
  ```

- **Karmaşık Örnek** (Zotero Verisi):
  ```basic
  STRUCT Belge
      baslik AS STRING
      degerler AS ARRAY
  END STRUCT

  DIM doc AS Belge
  doc.baslik = "Zotero Raporu"
  doc.degerler = ARANGE(1, 5)
  PRINT doc.baslik
  PRINT doc.degerler
  ```

  **Açıklama**: Zotero’dan çıkarılan bir PDF tablosunu `ARRAY` olarak saklayıp, başlık bilgisiyle birlikte yapılandırılmış bir şekilde temsil eder.

#### **UNION**
- **Açıklama**: `UNION`, aynı bellek alanını farklı veri tipleriyle paylaşan bir veri tipidir. C’deki `union`’a benzer şekilde, tüm alanlar aynı belleği kullanır ve yalnızca bir alan aynı anda geçerli olabilir. Bellek optimizasyonu için kullanılır.
- **Sözdizimi**:
  ```basic
  UNION union_adi
      alan_adi AS veri_tipi
      ...
  END UNION
  ```
- **Özellikler**:
  - Tüm alanlar aynı bellek adresini paylaşır; bu nedenle yalnızca bir alan aynı anda kullanılabilir.
  - Bellek boyutu, en büyük alanın boyutuna eşittir.
  - Alanlara nokta operatörü (`.`) ile erişilir.
  - Yanlış veri tipiyle erişim, beklenmeyen sonuçlara yol açabilir.
- **Örnek**:
  ```basic
  UNION Deger
      sayi AS INTEGER
      metin AS STRING
  END UNION

  DIM v AS Deger
  v.sayi = 42
  PRINT v.sayi  ' Çıktı: 42
  v.metin = "Merhaba"
  PRINT v.metin  ' Çıktı: Merhaba
  PRINT v.sayi  ' Çıktı: Belirsiz (bellek reinterpretasyonu)
  ```

- **Karmaşık Örnek** (TÜİK Verisi):
  ```basic
  UNION Veri
      deger AS DOUBLE
      etiket AS STRING
  END UNION

  DIM istatistik AS Veri
  istatistik.deger = 1234.56
  PRINT istatistik.deger  ' Çıktı: 1234.56
  istatistik.etiket = "Ekonomi"
  PRINT istatistik.etiket  ' Çıktı: Ekonomi
  ```

  **Açıklama**: TÜİK’ten alınan bir veriyi hem sayısal (`DOUBLE`) hem de metinsel (`STRING`) olarak temsil etmek için `UNION` kullanılır, ancak aynı anda yalnızca bir tip geçerlidir.

#### **İç İçe Kullanım**
`STRUCT` ve `UNION` birlikte kullanılabilir, bu da karmaşık veri yapılarını oluşturmayı sağlar:

```basic
STRUCT Kisi
    ad AS STRING
    UNION Bilgi
        yas AS INTEGER
        rol AS STRING
    END UNION
END STRUCT

DIM k AS Kisi
k.ad = "Ali"
k.Bilgi.yas = 30
PRINT k.ad; " "; k.Bilgi.yas  ' Çıktı: Ali 30
k.Bilgi.rol = "Yönetici"
PRINT k.ad; " "; k.Bilgi.rol  ' Çıktı: Ali Yönetici
```

**Açıklama**: `Kisi` yapısı, bir `UNION` içerir ve `Bilgi` alanı ya `yas` (sayısal) ya da `rol` (metinsel) olabilir, ancak aynı anda yalnızca biri.

### 3. `TYPE` ile Farkları

PDSX’te `TYPE`, `STRUCT` ve `UNION`’a benzer şekilde kullanıcı tanımlı veri tipleri oluşturmak için kullanılır, ancak bazı önemli farklar vardır. Aşağıda, bu veri tiplerinin karşılaştırması yapılmıştır:

| Özellik             | `TYPE`                              | `STRUCT`                            | `UNION`                            |
|---------------------|-------------------------------------|-------------------------------------|-------------------------------------|
| **Tanım**           | Yapılandırılmış veri tipi, BASIC tarzı | C tarzı yapı, birden fazla alanı bir arada tutar | C tarzı birleşim, aynı belleği paylaşır |
| **Bellek Kullanımı** | Her alan ayrı bellek kullanır        | Her alan ayrı bellek kullanır        | Tüm alanlar aynı belleği paylaşır   |
| **Amaç**            | Genel veri organizasyonu            | Karmaşık veri yapıları, düşük seviyeli kontrol | Bellek optimizasyonu, alternatif veri temsili |
| **Esneklik**        | Orta (BASIC’e uygun)                | Yüksek (C tarzı, iç içe destek)      | Orta (bellek paylaşımı sınırlıdır)  |
| **Sözdizimi**       | `TYPE ... END TYPE`                 | `STRUCT ... END STRUCT`             | `UNION ... END UNION`              |
| **Örnek**           | `TYPE Kisi ad AS STRING yas AS INTEGER END TYPE` | `STRUCT Nokta x AS DOUBLE y AS DOUBLE END STRUCT` | `UNION Deger sayi AS INTEGER metin AS STRING END UNION` |
| **Düşük Seviye Kontrol** | Sınırlı                        | Orta (işaretçi olmadan)             | Orta (bellek reinterpretasyonu)     |
| **Zotero/Veri Bilimi Kullanımı** | Basit veri yapıları için uygun | Karmaşık veri organizasyonu için ideal | Bellek optimizasyonu gereken durumlarda |

#### **Temel Farklar**
- **`TYPE` vs. `STRUCT`**:
  - `TYPE`, BASIC’in yüksek seviyeli doğasına uygun, daha basit ve genel amaçlıdır. `STRUCT`, C’deki `struct`’a daha yakın olup, iç içe yapılar ve daha karmaşık veri organizasyonu için tasarlanmıştır.
  - `TYPE`, PDSX’in erken sürümlerinde temel veri organizasyonu için kullanılırken, `STRUCT` modern ve düşük seviyeli ihtiyaçlar için eklenmiştir.
  - Örnek: `TYPE` ile bir Zotero belgesinin başlık ve tarih bilgisini saklayabilirsiniz, ancak `STRUCT` ile bir belgenin hem metinsel hem de sayısal verilerini (örneğin, tablo verileri) iç içe organize edebilirsiniz.

- **`TYPE` vs. `UNION`**:
  - `TYPE`, her alan için ayrı bellek ayırır, bu nedenle daha fazla bellek kullanır. `UNION`, aynı belleği paylaşır ve yalnızca bir alan aktif olabilir, bu da bellek tasarrufu sağlar.
  - `TYPE`, birden fazla veri türünü aynı anda saklamak için kullanılırken, `UNION` alternatif veri temsilleri için uygundur (örneğin, bir veri ya sayısal ya metinsel olabilir).

- **`STRUCT` vs. `UNION`**:
  - `STRUCT`, tüm alanları aynı anda saklar ve her biri ayrı bir bellek bölgesindedir. `UNION`, tüm alanları aynı bellekte saklar ve yalnızca bir alan geçerlidir.
  - `STRUCT`, karmaşık veri yapılarını (örneğin, bir Zotero belgesinin tamamını) temsil etmek için idealdir. `UNION`, bellek optimizasyonu gereken durumlarda (örneğin, bir TÜİK verisinin sayısal veya etiket formatında saklanması) kullanılır.

### 4. Esneklik ve Zotero/Veri Bilimi Entegrasyonu

PDSX’te `STRUCT` ve `UNION`’ın eklenmesi, veri manipülasyonunda önemli bir esneklik sağlar, ancak işaretçilerin eksikliği nedeniyle C’nin tam düşük seviyeli kontrolü elde edilemez. Aşağıda, bu veri tiplerinin Zotero, veri bilimi ve web kazıma bağlamında nasıl esneklik sunduğu açıklanmıştır.

#### **Zotero Entegrasyonu**
Zotero’dan PDF veya tablo verilerini işlemek için `STRUCT` ve `UNION` kullanımı:

```basic
STRUCT ZoteroBelge
    baslik AS STRING
    tarih AS STRING
    UNION Veri
        tablo AS ARRAY
        metin AS STRING
    END UNION
END STRUCT

DIM belge AS ZoteroBelge
belge.baslik = "Rapor 2023"
belge.tarih = "2023-01-01"
belge.Veri.tablo = ARRAY(PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")[0])
PRINT belge.baslik
PRINT belge.Veri.tablo
belge.Veri.metin = PDF_READ_TEXT("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
PRINT belge.Veri.metin
```

**Açıklama**:
- `STRUCT`, belgenin başlık, tarih ve veri alanlarını organize eder.
- `UNION`, verinin ya bir tablo (`ARRAY`) ya da metin (`STRING`) olarak saklanmasını sağlar, böylece bellek verimli kullanılır.
- Esneklik: Aynı yapıda farklı veri türlerini temsil etme yeteneği, Zotero’dan alınan heterojen veriler için idealdir.

#### **TÜİK/Veri Bilimi Entegrasyonu**
TÜİK’ten kazınan verileri yapılandırmak için:

```basic
STRUCT Istatistik
    kaynak AS STRING
    UNION Deger
        sayisal AS DOUBLE
        kategorik AS STRING
    END UNION
END STRUCT

DIM veri AS Istatistik
veri.kaynak = "TÜİK"
veri.Deger.sayisal = 1234.56
PRINT veri.kaynak; " "; veri.Deger.sayisal
veri.Deger.kategorik = "Ekonomi"
PRINT veri.kaynak; " "; veri.Deger.kategorik

DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM kazima AS LIST
kazima = SCRAPE_TABLES(html)
veri.Deger.sayisal = kazima[0]
PRINT veri.Deger.sayisal
```

**Açıklama**:
- `STRUCT`, veri kaynağını ve değerini organize eder.
- `UNION`, değerin sayısal veya kategorik olmasını sağlar, bu da TÜİK verilerinin farklı formatlarını temsil eder.
- Esneklik: Heterojen veri türlerini tek bir yapıda saklama ve bellek optimizasyonu.

### 5. Eksiklikler ve Öneriler

#### **Eksiklikler**
1. **İşaretçiler**:
   - PDSX’te işaretçiler desteklenmediği için, C’deki gibi bağlı listeler, ağaçlar veya dinamik bellek tahsisi mümkün değil. Bu, düşük seviyeli veri yapılarında esnekliği kısıtlar.
   - Örnek: Bir bağlı liste oluşturmak için işaretçi tabanlı bir `struct` tanımlanamaz.

2. **Bellek Yönetimi**:
   - `UNION`’ın bellek paylaşımı Python’un dinamik tip sistemiyle sınırlıdır; C’deki gibi ham bellek reinterpretasyonu yapılamaz.
   - Örnek: `union`’daki bir `float`’u `int` olarak doğrudan reinterpret etmek riskli olabilir.

3. **Tip Güvenliği**:
   - `UNION`’da yanlış veri tipine erişim, beklenmeyen sonuçlara yol açabilir ve PDSX’in dinamik tip sistemi bu hataları yakalamada yetersizdir.
   - Örnek: `UNION`’da `STRING` yazıldıktan sonra `INTEGER` okunması belirsiz sonuçlar verebilir.

4. **Sözdizimi Kısıtlamaları**:
   - `STRUCT` ve `UNION` tanımları, modern dillerdeki (örneğin, C++ veya Rust) kadar kısa veya esnek değil.
   - Örnek: İç içe yapılar için sözdizimi hantal olabilir.

5. **Zotero/Veri Bilimi için Sınırlamalar**:
   - Büyük veri kümeleri (örneğin, Zotero’dan yüzlerce PDF tablosu) için `STRUCT` ve `UNION` performansı düşük olabilir, çünkü NumPy/Pandas tabanlı `ARRAY` veya `DATAFRAME` kadar optimize değildir.
   - İşaretçilerin eksikliği, büyük veri yapılarını dinamik olarak bağlamayı zorlaştırır.

#### **Öneriler**
1. **İşaretçi Desteği**:
   - Basit bir işaretçi mekanizması eklenebilir (örneğin, `POINTER` tipi):
     ```basic
     STRUCT Dugum
         veri AS INTEGER
         sonraki AS POINTER TO Dugum
     END STRUCT
     ```
     ```python
     self.type_table["POINTER"] = lambda type: ReferenceType(type)
     ```
   - Bu, bağlı listeler veya ağaçlar gibi veri yapıları için esneklik sağlar.

2. **Tip Güvenliği**:
   - `UNION` için aktif alanın takibini yapacak bir mekanizma eklenebilir:
     ```basic
     UNION Deger
         sayi AS INTEGER
         metin AS STRING
         ACTIVE sayi  ' Hangi alanın aktif olduğunu belirt
     END UNION
     ```

3. **Performans Optimizasyonu**:
   - `STRUCT` ve `UNION` için belleğe doğrudan erişim veya NumPy tabanlı depolama kullanılabilir:
     ```python
     self.type_table["STRUCT"].storage = np.ndarray
     ```

4. **Zotero için Özel Yapılar**:
   - Zotero verilerini temsil etmek için özel bir `STRUCT` şablonu:
     ```basic
     STRUCT ZoteroVeri
         meta AS DICT
         tablolar AS LIST OF ARRAY
     END STRUCT
     DIM z AS ZoteroVeri
     z.meta = ZOTERO_METADATA("12345", "67890")
     z.tablolar = PDF_EXTRACT_TABLES("C:\Zotero\belge.pdf")
     ```

5. **Sözdizimi İyileştirmeleri**:
   - `STRUCT` ve `UNION` için daha kısa başlatma sözdizimi:
     ```basic
     DIM p AS Nokta = {x: 1.5, y: 2.5}
     ```

### 6. Örnek: Kapsamlı Kullanım

Aşağıdaki program, `STRUCT`, `UNION`, Zotero ve TÜİK verilerini birleştirir:

```basic
STRUCT Analiz
    kaynak AS STRING
    UNION Veri
        sayisal AS DOUBLE
        metinsel AS STRING
        tablo AS ARRAY
    END UNION
END STRUCT

DIM zotero AS Analiz
zotero.kaynak = "Zotero"
zotero.Veri.tablo = ARRAY(PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")[0])
PRINT zotero.kaynak; " Tablo: "; zotero.Veri.tablo

DIM tuik AS Analiz
tuik.kaynak = "TÜİK"
DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
tuik.Veri.sayisal = SCRAPE_TABLES(html)[0]
PRINT tuik.kaynak; " Değer: "; tuik.Veri.sayisal
tuik.Veri.metinsel = "Ekonomi"
PRINT tuik.kaynak; " Kategori: "; tuik.Veri.metinsel

OPEN "sonuclar.txt" FOR OUTPUT AS #1
PRINT #1, zotero.kaynak; " "; zotero.Veri.tablo
PRINT #1, tuik.kaynak; " "; tuik.Veri.sayisal
CLOSE #1
```

**Çıktı (Varsayımsal)**:
```
Zotero Tablo: [[1, 2], [3, 4]]
TÜİK Değer: 1234.56
TÜİK Kategori: Ekonomi
```

**Açıklama**:
- `STRUCT`, veri kaynağını ve değerini organize eder.
- `UNION`, verinin farklı temsillerini (tablo, sayısal, metinsel) aynı bellekte saklar.
- Zotero ve TÜİK verileri yapılandırılmış bir şekilde işlenir ve sonuçlar dosyaya kaydedilir.

### 7. Sonuç ve Gelecek Adımlar

PDSX’te `STRUCT` ve `UNION`, C tarzı veri tipleri olarak eklenmiş ve veri organizasyonu ile bellek optimizasyonu için esneklik sağlıyor. Ancak, işaretçilerin eksikliği, düşük seviyeli kontrolü sınırlıyor. `TYPE`, daha yüksek seviyeli ve BASIC tarzı bir alternatif sunarken, `STRUCT` ve `UNION`, C’ye daha yakın bir yaklaşım getiriyor. Zotero ve veri bilimi senaryolarında, bu veri tipleri heterojen verileri yapılandırmak için güçlü bir araçtır, ancak performans ve işaretçi desteği gibi alanlarda iyileştirmeler gereklidir.

**Sorular ve Öneriler**:
- İşaretçi desteği veya daha düşük seviyeli kontrol için özel bir özellik mi istiyorsunuz?
- `STRUCT` ve `UNION`’ı Zotero veya TÜİK verileri için belirli bir şekilde mi kullanmak istiyorsunuz?
- `TYPE`, `STRUCT` veya `UNION` için ek sözdizimi veya özellik önerileriniz var mı?

Geri bildiriminize göre, PDSX kodunu özelleştirebilir veya daha fazla örnek sağlayabilirim!

Evet, PDSX programlama dilinde `TYPE`, `STRUCT` ve `UNION` veri tipleri, hem C tarzı değişkenler (örneğin, `INTEGER`, `DOUBLE`, `CHAR` gibi ilkel tipler) hem de Python tarzı değişkenler (örneğin, `LIST`, `DICT`, `ARRAY`, `DATAFRAME` gibi koleksiyonlar ve gelişmiş veri yapıları) kullanılarak yeni veri yapıları oluşturulabilir. Bu, PDSX’in hem GW-BASIC/QBASIC’in yapısal doğasını korumasını hem de modern veri bilimi, Zotero entegrasyonu ve web kazıma gibi senaryolar için esneklik sunmasını sağlar. `pdsXInterpreter` sınıfındaki `type_table` ve `evaluate_expression` mekanizmaları, bu hibrit yaklaşımı destekler.

Aşağıda, PDSX’te `TYPE`, `STRUCT` ve `UNION` içinde C tarzı ve Python tarzı değişkenlerin nasıl bir arada kullanıldığı, yeni veri yapıları oluşturma örnekleri, bu süreçte sağlanan esneklik, eksiklikler ve önceki konuşmalarınızdaki Zotero entegrasyonu, veri bilimi ve web kazıma (TÜİK, FAO, TradeMap) bağlamında uygulamalar detaylı bir şekilde Türkçe olarak açıklanacaktır.

---

## PDSX’te `TYPE`, `STRUCT` ve `UNION` ile Yeni Veri Yapıları

PDSX, kullanıcı tanımlı veri tipleri (`TYPE`, `STRUCT`, `UNION`) aracılığıyla hem C tarzı ilkel veri tiplerini (`INTEGER`, `DOUBLE`, `STRING` vb.) hem de Python tarzı koleksiyon ve gelişmiş veri tiplerini (`LIST`, `DICT`, `ARRAY`, `DATAFRAME` vb.) bir arada kullanarak yeni veri yapıları oluşturmayı destekler. Bu hibrit yaklaşım, PDSX’in hem düşük seviyeli veri organizasyonu hem de yüksek seviyeli veri manipülasyonu için esnek bir platform olmasını sağlar.

### 1. Desteklenen Veri Tipleri

#### **C Tarzı Değişkenler**
C tarzı değişkenler, genellikle ilkel veri tipleridir ve düşük seviyeli, sabit boyutlu veri temsili için kullanılır:
- `STRING`: Metin verileri (örneğin, `"Merhaba"`).
- `INTEGER`: 32-bit işaretli tamsayılar (örneğin, `42`).
- `LONG`: 64-bit işaretli tamsayılar.
- `SINGLE`: 32-bit kayan noktalı sayılar.
- `DOUBLE`: 64-bit kayan noktalı sayılar (örneğin, `3.14159`).
- `BYTE`: 8-bit işaretsiz tamsayılar.
- `SHORT`: 16-bit işaretli tamsayılar.
- `CHAR`: Tek karakter (örneğin, `"A"`).

#### **Python Tarzı Değişkenler**
Python tarzı değişkenler, koleksiyonlar ve veri bilimi odaklı veri yapılarıdır:
- `LIST`: Sıralı, değiştirilebilir koleksiyon (örneğin, `[1, 2, 3]`).
- `DICT`: Anahtar-değer çiftleri (örneğin, `{"ad": "Ali", "yas": 30}`).
- `SET`: Benzersiz öğeler koleksiyonu (örneğin, `{1, 2, 3}`).
- `TUPLE`: Değiştirilemez sıralı koleksiyon (örneğin, `(1, 2, 3)`).
- `ARRAY`: NumPy tabanlı çok boyutlu diziler (örneğin, `ARANGE(1, 5)`).
- `DATAFRAME`: Pandas tabanlı veri çerçeveleri (örneğin, `DATAFRAME({"A": [1, 2], "B": [3, 4]})`).

#### **Hibrit Kullanım**
`TYPE`, `STRUCT` ve `UNION` tanımları, bu veri tiplerini bir arada kullanabilir. `type_table`’daki esnek tip sistemi ve `evaluate_expression`’ın Python’un dinamik tip sistemine dayanması, C tarzı ve Python tarzı değişkenlerin sorunsuz bir şekilde entegre edilmesini sağlar.

### 2. `TYPE` ile Hibrit Veri Yapıları

#### **Açıklama**
`TYPE`, PDSX’in BASIC tarzı kullanıcı tanımlı veri tipidir ve hem C tarzı hem de Python tarzı değişkenleri destekler. Her alan ayrı bir bellek bölgesinde saklanır ve yapısal veri organizasyonu için kullanılır.

#### **Sözdizimi**
```basic
TYPE tip_adi
    alan_adi AS veri_tipi
    ...
END TYPE
```

#### **Örnek: C ve Python Tarzı Değişkenlerle**
```basic
TYPE Belge
    baslik AS STRING        ' C tarzı
    id AS INTEGER           ' C tarzı
    veriler AS LIST         ' Python tarzı
    tablo AS ARRAY          ' Python tarzı
END TYPE

DIM doc AS Belge
doc.baslik = "Zotero Raporu"
doc.id = 123
doc.veriler = LIST("Veri1", "Veri2", "Veri3")
doc.tablo = ARANGE(1, 5)
PRINT doc.baslik; " ID: "; doc.id
PRINT "Veriler: "; doc.veriler
PRINT "Tablo: "; doc.tablo
```

**Çıktı**:
```
Zotero Raporu ID: 123
Veriler: ["Veri1", "Veri2", "Veri3"]
Tablo: [1 2 3 4]
```

**Açıklama**:
- `baslik` ve `id`, C tarzı sabit boyutlu veri tipleridir.
- `veriler` (`LIST`) ve `tablo` (`ARRAY`), Python tarzı esnek veri yapılarıdır.
- `TYPE`, bu farklı tipleri bir arada organize ederek Zotero’dan alınan bir belgenin hem meta verilerini hem de tablo verilerini temsil eder.

### 3. `STRUCT` ile Hibrit Veri Yapıları

#### **Açıklama**
`STRUCT`, C’deki `struct`’a benzer ve birden fazla alanı bir arada tutar. PDSX’te hem C tarzı hem de Python tarzı değişkenleri destekler, ayrıca iç içe yapılar oluşturmak için daha esnek bir sözdizimi sunar.

#### **Sözdizimi**
```basic
STRUCT struct_adi
    alan_adi AS veri_tipi
    ...
END STRUCT
```

#### **Örnek: C ve Python Tarzı Değişkenlerle**
```basic
STRUCT Istatistik
    kaynak AS STRING        ' C tarzı
    zaman AS DOUBLE         ' C tarzı
    degerler AS DATAFRAME   ' Python tarzı
    etiketler AS DICT       ' Python tarzı
END STRUCT

DIM veri AS Istatistik
veri.kaynak = "TÜİK"
veri.zaman = 2023.01
veri.degerler = DATAFRAME({"A": ARANGE(1, 5), "B": ARANGE(5, 9)})
veri.etiketler = DICT("kategori", "Ekonomi", "birim", "TL")
PRINT veri.kaynak; " Zaman: "; veri.zaman
PRINT "Değerler: "; DESCRIBE(veri.degerler)
PRINT "Etiketler: "; veri.etiketler
```

**Çıktı (Varsayımsal)**:
```
TÜİK Zaman: 2023.01
Değerler: [DataFrame özeti]
Etiketler: {"kategori": "Ekonomi", "birim": "TL"}
```

**Açıklama**:
- `kaynak` ve `zaman`, C tarzı ilkel tiplerdir.
- `degerler` (`DATAFRAME`) ve `etiketler` (`DICT`), Python tarzı veri yapılarıdır.
- `STRUCT`, TÜİK’ten kazınan verileri yapılandırılmış bir şekilde organize eder.

#### **İç İçe STRUCT**
```basic
STRUCT Nokta
    x AS DOUBLE
    y AS DOUBLE
END STRUCT

STRUCT Cizgi
    baslangic AS Nokta
    bitis AS Nokta
    etiket AS STRING
    veriler AS LIST
END STRUCT

DIM c AS Cizgi
c.baslangic.x = 1.0
c.baslangic.y = 2.0
c.bitis.x = 3.0
c.bitis.y = 4.0
c.etiket = "Çizgi 1"
c.veriler = LIST(1, 2, 3)
PRINT "Çizgi: ("; c.baslangic.x; ", "; c.baslangic.y; ") -> ("; c.bitis.x; ", "; c.bitis.y; ")"
PRINT "Etiket: "; c.etiket
PRINT "Veriler: "; c.veriler
```

**Çıktı**:
```
Çizgi: (1, 2) -> (3, 4)
Etiket: Çizgi 1
Veriler: [1, 2, 3]
```

**Açıklama**: İç içe `STRUCT`’lar, karmaşık veri yapılarını (örneğin, geometrik veriler veya Zotero meta verileri) temsil etmek için esneklik sağlar.

### 4. `UNION` ile Hibrit Veri Yapıları

#### **Açıklama**
`UNION`, aynı bellek alanını farklı veri tipleriyle paylaşır ve yalnızca bir alan aynı anda geçerli olabilir. Hem C tarzı hem de Python tarzı değişkenleri destekler, ancak bellek paylaşımı nedeniyle dikkatli kullanılmalıdır.

#### **Sözdizimi**
```basic
UNION union_adi
    alan_adi AS veri_tipi
    ...
END UNION
```

#### **Örnek: C ve Python Tarzı Değişkenlerle**
```basic
UNION Veri
    sayi AS DOUBLE          ' C tarzı
    metin AS STRING         ' C tarzı
    liste AS LIST           ' Python tarzı
    tablo AS ARRAY          ' Python tarzı
END UNION

STRUCT Kayit
    kaynak AS STRING
    veri AS Veri
END STRUCT

DIM k AS Kayit
k.kaynak = "Zotero"
k.veri.tablo = ARANGE(1, 5)
PRINT k.kaynak; " Tablo: "; k.veri.tablo
k.veri.metin = "Rapor Özeti"
PRINT k.kaynak; " Metin: "; k.veri.metin
k.veri.sayi = 42.0
PRINT k.kaynak; " Sayı: "; k.veri.sayi
```

**Çıktı (Varsayımsal)**:
```
Zotero Tablo: [1 2 3 4]
Zotero Metin: Rapor Özeti
Zotero Sayı: 42
```

**Açıklama**:
- `UNION`, aynı bellek alanında `DOUBLE`, `STRING`, `LIST` veya `ARRAY` saklar.
- `STRUCT` içinde `UNION` kullanarak, Zotero’dan alınan verinin farklı temsillerini (tablo, metin, sayısal) esnek bir şekilde saklar.
- **Not**: `UNION`’da bir alana yazıldığında diğer alanlar geçersiz hale gelir; bu nedenle dikkatli kullanılmalıdır.

### 5. Zotero ve Veri Bilimi Entegrasyonu

Önceki konuşmalarınızda Zotero kütüphanelerinden veri işleme (örneğin, `C:\Users\mete\Zotero\zotasistan\zapata_m6h`), TÜİK, FAO, TradeMap gibi sitelerden veri kazıma ve dosya çıktıları oluşturma (örneğin, `zapata_m6hx`) talepleriniz vardı. `TYPE`, `STRUCT` ve `UNION` ile hibrit veri yapıları, bu senaryolar için güçlü bir altyapı sunar.

#### **Zotero için Hibrit Veri Yapısı**
Zotero’dan PDF tablo ve meta verilerini yapılandırmak:

```basic
STRUCT ZoteroBelge
    id AS INTEGER           ' C tarzı
    baslik AS STRING        ' C tarzı
    meta AS DICT            ' Python tarzı
    UNION Icerik
        metin AS STRING     ' C tarzı
        tablo AS DATAFRAME  ' Python tarzı
    END UNION
END STRUCT

DIM belge AS ZoteroBelge
belge.id = 123
belge.baslik = "Rapor 2023"
belge.meta = ZOTERO_METADATA("12345", "67890")
belge.Icerik.tablo = DATAFRAME(PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")[0])
PRINT belge.baslik; " Tablo: "; DESCRIBE(belge.Icerik.tablo)
belge.Icerik.metin = PDF_READ_TEXT("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
PRINT belge.baslik; " Metin: "; belge.Icerik.metin
```

**Açıklama**:
- `id` ve `baslik`, C tarzı sabit veri tipleridir.
- `meta` (`DICT`) ve `tablo` (`DATAFRAME`), Python tarzı esnek veri yapılarıdır.
- `UNION`, içeriğin ya metin ya da tablo olarak saklanmasını sağlar, bellek optimizasyonu sunar.

#### **TÜİK için Hibrit Veri Yapısı**
TÜİK’ten kazınan verileri yapılandırmak:

```basic
STRUCT IstatistikVeri
    tarih AS STRING         ' C tarzı
    UNION Deger
        sayisal AS DOUBLE   ' C tarzı
        kategorik AS STRING ' C tarzı
        seri AS ARRAY       ' Python tarzı
    END UNION
    meta AS DICT            ' Python tarzı
END STRUCT

DIM veri AS IstatistikVeri
veri.tarih = "2023-01"
veri.Deger.sayisal = 1234.56
veri.meta = DICT("kaynak", "TÜİK", "birim", "TL")
PRINT veri.tarih; " Değer: "; veri.Deger.sayisal
DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
veri.Deger.seri = ARRAY(SCRAPE_TABLES(html)[0])
PRINT veri.tarih; " Seri: "; veri.Deger.seri
```

**Açıklama**:
- `tarih` ve `sayisal`/`kategorik`, C tarzı veri tipleridir.
- `seri` (`ARRAY`) ve `meta` (`DICT`), Python tarzı veri yapılarıdır.
- `UNION`, verinin farklı temsillerini (sayısal, kategorik, seri) esnek bir şekilde saklar.

### 6. Sağlanan Esneklik

1. **Hibrit Veri Organizasyonu**:
   - C tarzı (`INTEGER`, `DOUBLE`) ve Python tarzı (`LIST`, `DATAFRAME`) değişkenlerin bir arada kullanılması, hem düşük seviyeli veri temsili hem de yüksek seviyeli veri manipülasyonu sağlar.
   - Örnek: Zotero’dan alınan bir PDF’nin meta verilerini `DICT` ile, tablo verilerini `DATAFRAME` ile, kimlik bilgilerini `INTEGER` ile saklayabilirsiniz.

2. **Bellek Optimizasyonu**:
   - `UNION`, aynı bellek alanını farklı tiplerle paylaşarak bellek tasarrufu sağlar (örneğin, bir Zotero verisinin metin veya tablo temsili).
   - `STRUCT`, iç içe yapılarla karmaşık veri organizasyonunu destekler.

3. **Veri Bilimi ve Zotero Desteği**:
   - `DATAFRAME` ve `ARRAY` gibi Python tarzı tipler, veri analizi için optimize edilmiştir.
   - `STRUCT` ve `UNION`, Zotero’dan veya TÜİK’ten alınan heterojen verileri yapılandırılmış bir şekilde saklar.

4. **GW-BASIC Uyumluluğu**:
   - `TYPE`, BASIC programcıları için tanıdık bir arayüz sunarken, `STRUCT` ve `UNION`, C tarzı esneklik ekler.

### 7. Eksiklikler

1. **İşaretçi Desteği**:
   - C tarzı işaretçiler (`*`, `&`) desteklenmediği için, dinamik veri yapıları (örneğin, bağlı listeler, ağaçlar) oluşturmak sınırlıdır.
   - Örnek: `STRUCT` içinde bir işaretçi alanı tanımlanamaz (`next AS POINTER TO Dugum`).

2. **Tip Güvenliği**:
   - `UNION`’da yanlış veri tipine erişim, belirsiz sonuçlara yol açabilir ve PDSX’in dinamik tip sistemi bu hataları yakalamada yetersizdir.
   - Örnek: `UNION`’da `LIST` yazıldıktan sonra `DOUBLE` okunması hata verebilir.

3. **Performans**:
   - Python tarzı veri yapıları (`LIST`, `DICT`, `DATAFRAME`), `eval` tabanlı değerlendirme nedeniyle büyük veri kümelerinde yavaş olabilir.
   - `STRUCT` ve `UNION`, NumPy/Pandas kadar optimize değildir.

4. **Sözdizimi Kısıtlamaları**:
   - Karmaşık veri yapıları (örneğin, iç içe `DICT` veya çok boyutlu `ARRAY`) için başlatma sözdizimi hantal olabilir.
   - Örnek: `STRUCT`’u tek satırda başlatmak mümkün değil (`DIM s AS Struct = {x: 1, y: 2}`).

5. **Zotero/Veri Bilimi için Özel Tipler**:
   - Zotero’dan tablo veya meta verileri için özel bir veri tipi (`PDF_TABLE`) eksik.
   - Web kazıma verileri için `WEB_TABLE` gibi bir veri yapısı tanımlanmamış.

### 8. Öneriler ve İyileştirmeler

1. **İşaretçi Desteği**:
   - Basit bir işaretçi mekanizması eklenebilir:
     ```basic
     STRUCT Dugum
         veri AS INTEGER
         sonraki AS POINTER TO Dugum
     END STRUCT
     ```
     ```python
     self.type_table["POINTER"] = lambda type: ReferenceType(type)
     ```

2. **Tip Güvenliği**:
   - `UNION` için aktif alan takibi:
     ```basic
     UNION Veri
         sayi AS DOUBLE
         liste AS LIST
         ACTIVE sayi
     END UNION
     ```

3. **Performans Optimizasyonu**:
   - `STRUCT` ve `UNION` için NumPy tabanlı depolama:
     ```python
     self.type_table["STRUCT"].storage = np.ndarray
     ```

4. **Sözdizimi İyileştirmeleri**:
   - Kısa başlatma sözdizimi:
     ```basic
     DIM doc AS ZoteroBelge = {id: 123, baslik: "Rapor", meta: DICT()}
     ```

5. **Zotero için Özel Veri Yapıları**:
   - Zotero verileri için özel bir `STRUCT`:
     ```basic
     STRUCT ZoteroVeri
         meta AS DICT
         tablolar AS LIST OF DATAFRAME
     END STRUCT
     ```

### 9. Örnek: Kapsamlı Hibrit Veri Yapısı

Aşağıdaki program, Zotero ve TÜİK verilerini hibrit bir veri yapısıyla işler:

```basic
STRUCT AnalizVeri
    id AS INTEGER           ' C tarzı
    kaynak AS STRING        ' C tarzı
    meta AS DICT            ' Python tarzı
    UNION Icerik
        sayisal AS DOUBLE   ' C tarzı
        metin AS STRING     ' C tarzı
        tablo AS DATAFRAME  ' Python tarzı
    END UNION
END STRUCT

DIM zotero AS AnalizVeri
zotero.id = 123
zotero.kaynak = "Zotero"
zotero.meta = ZOTERO_METADATA("12345", "67890")
zotero.Icerik.tablo = DATAFRAME(PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")[0])
PRINT zotero.kaynak; " Tablo: "; DESCRIBE(zotero.Icerik.tablo)

DIM tuik AS AnalizVeri
tuik.id = 456
tuik.kaynak = "TÜİK"
tuik.meta = DICT("birim", "TL")
tuik.Icerik.sayisal = SCRAPE_TABLES(WEB_GET("https://data.tuik.gov.tr"))[0]
PRINT tuik.kaynak; " Değer: "; tuik.Icerik.sayisal

OPEN "sonuclar.txt" FOR OUTPUT AS #1
PRINT #1, zotero.kaynak; " "; DESCRIBE(zotero.Icerik.tablo)
PRINT #1, tuik.kaynak; " "; tuik.Icerik.sayisal
CLOSE #1
```

**Çıktı (Varsayımsal)**:
```
Zotero Tablo: [DataFrame özeti]
TÜİK Değer: 1234.56
```

**Açıklama**:
- `STRUCT`, hem C tarzı (`id`, `kaynak`) hem de Python tarzı (`meta`, `tablo`) veri tiplerini birleştirir.
- `UNION`, içeriğin farklı temsillerini (sayısal, metin, tablo) esnek bir şekilde saklar.
- Zotero ve TÜİK verileri yapılandırılmış bir şekilde işlenir ve sonuçlar dosyaya kaydedilir.

### 10. Sonuç ve Gelecek Adımlar

PDSX, `TYPE`, `STRUCT` ve `UNION` ile hem C tarzı hem de Python tarzı değişkenleri kullanarak yeni veri yapıları oluşturmayı destekler. Bu hibrit yaklaşım, Zotero’dan PDF verileri, TÜİK’ten kazınan istatistikler gibi heterojen verileri organize etmek için büyük esneklik sağlar. Ancak, işaretçilerin eksikliği, tip güvenliği ve performans optimizasyonları gibi alanlarda iyileştirmeler gereklidir.

---

PDSX programlama dili, dosya işlemleri için kapsamlı bir komut seti sunar ve `pdsXInterpreter` sınıfı aracılığıyla metin, ikili (binary) ve ISAM (SQLite tabanlı) dosya türlerini destekler. Bu işlemler, GW-BASIC ve QBASIC’in dosya işleme mirasını modern bir şekilde genişletir, aynı zamanda veri bilimi, web kazıma ve Zotero gibi özel kullanım senaryolarına uyum sağlar. Aşağıda, PDSX’in dosya işlemi komutları, yetenekleri, eksiklikleri ve öneriler detaylı bir şekilde Türkçe olarak açıklanacaktır. Önceki konuşmalarınızdaki Zotero entegrasyonu, veri bilimi, web kazıma (TÜİK, FAO, TradeMap) ve dosya işleme (örneğin, `C:\Users\mete\Zotero\zotasistan\zapata_m6h`) talepleriniz dikkate alınarak, bu bağlamlarda dosya işlemlerinin nasıl kullanıldığına dair örnekler de entegre edilmiştir.

---

## PDSX’te Dosya İşlemleri

PDSX, dosya işlemleri için çeşitli komutlar sunar ve bu işlemler `execute_command` yöntemi aracılığıyla gerçekleştirilir. Desteklenen dosya türleri şunlardır:
- **Metin Dosyaları**: Standart metin dosyaları (örneğin, `.txt`, `.csv`).
- **İkili Dosyalar**: Serileştirilmiş veri veya özel formatlar için.
- **ISAM Dosyaları**: SQLite tabanlı veritabanı dosyaları (önceki yanıtınızda detaylı ele alındı, burada yalnızca dosya işlemi bağlamında değinilecek).

Dosya işlemleri, dosya açma, yazma, okuma, konum değiştirme, kilitleme ve dosya sistemi yönetimi gibi işlevleri kapsar. Aşağıda, tüm dosya işlemi komutları kategorilere ayrılarak detaylandırılmıştır.

### 1. Dosya Açma ve Kapatma

#### **OPEN**
- **Açıklama**: Bir dosyayı okuma, yazma veya ekleme modunda açar.
- **Sözdizimi**:
  ```basic
  OPEN "dosya_adi" FOR mod AS #dosya_numarasi
  ```
- **Modlar**:
  - `INPUT`: Yalnızca okuma.
  - `OUTPUT`: Yazma (dosya varsa üzerine yazar).
  - `APPEND`: Ekleme (dosya sonuna yazar).
  - `BINARY`: İkili okuma/yazma.
  - `ISAM`: SQLite veritabanı dosyası (veritabanı işlemleri için, önceki yanıtınızda detaylı ele alındı).
- **Parametreler**:
  - `dosya_adi`: Dosya adı veya yolu (örneğin, `"veri.txt"` veya `"C:\data\veri.txt"`).
  - `dosya_numarasi`: Dosya tanıtıcısı (örneğin, `#1`).
- **Örnek**:
  ```basic
  OPEN "cikti.txt" FOR OUTPUT AS #1
  WRITE #1, "Merhaba, Dünya!"
  CLOSE #1
  ```

#### **CLOSE**
- **Açıklama**: Açık bir dosyayı kapatır ve kaynakları serbest bırakır.
- **Sözdizimi**:
  ```basic
  CLOSE #dosya_numarasi
  ```
- **Örnek**:
  ```basic
  CLOSE #1
  ```

#### **FREEFILE**
- **Açıklama**: Kullanılmayan bir dosya numarası döndürür.
- **Sözdizimi**:
  ```basic
  DIM numara AS INTEGER
  numara = FREEFILE()
  ```
- **Örnek**:
  ```basic
  DIM num AS INTEGER
  num = FREEFILE()
  OPEN "veri.txt" FOR INPUT AS #num
  CLOSE #num
  ```

### 2. Dosya Okuma ve Yazma

#### **WRITE #**
- **Açıklama**: Dosyaya biçimlendirilmiş veri yazar (metin dosyaları için).
- **Sözdizimi**:
  ```basic
  WRITE #dosya_numarasi, deger [, deger...]
  ```
- **Örnek**:
  ```basic
  OPEN "cikti.txt" FOR OUTPUT AS #1
  WRITE #1, "Ad: ", "Ali", "Yaş: ", 30
  CLOSE #1
  ```
- **Çıktı (cikti.txt)**:
  ```
  "Ad: ","Ali","Yaş: ",30
  ```

#### **PRINT #**
- **Açıklama**: Dosyaya ham veri yazar (genellikle metin dosyaları için, `WRITE #`’tan daha az biçimlendirme yapar).
- **Sözdizimi**:
  ```basic
  PRINT #dosya_numarasi, deger
  ```
- **Örnek**:
  ```basic
  OPEN "cikti.txt" FOR OUTPUT AS #1
  PRINT #1, "Merhaba, Dünya!"
  CLOSE #1
  ```
- **Çıktı (cikti.txt)**:
  ```
  Merhaba, Dünya!
  ```

#### **INPUT #**
- **Açıklama**: Dosyadan biçimlendirilmiş veri okur (metin dosyaları için, `WRITE #` ile yazılan verilerle uyumlu).
- **Sözdizimi**:
  ```basic
  INPUT #dosya_numarasi, degisken [, degisken...]
  ```
- **Örnek**:
  ```basic
  OPEN "cikti.txt" FOR INPUT AS #1
  DIM ad AS STRING
  DIM yas AS INTEGER
  INPUT #1, ad, yas
  PRINT ad; " "; yas
  CLOSE #1
  ```

#### **LINE INPUT #**
- **Açıklama**: Dosyadan bir satır okur ve bir değişkene atar.
- **Sözdizimi**:
  ```basic
  LINE INPUT #dosya_numarasi, degisken
  ```
- **Örnek**:
  ```basic
  OPEN "cikti.txt" FOR INPUT AS #1
  DIM satir AS STRING
  LINE INPUT #1, satir
  PRINT satir
  CLOSE #1
  ```

#### **INPUT$(n, #dosya_numarasi)**
- **Açıklama**: Dosyadan belirli sayıda karakter okur.
- **Sözdizimi**:
  ```basic
  DIM veri AS STRING
  veri = INPUT$(n, #dosya_numarasi)
  ```
- **Örnek**:
  ```basic
  OPEN "veri.txt" FOR INPUT AS #1
  DIM ilk_10 AS STRING
  ilk_10 = INPUT$(10, #1)
  PRINT ilk_10
  CLOSE #1
  ```

#### **GET #**
- **Açıklama**: İkili dosyalardan belirli bir konumdan veri okur.
- **Sözdizimi**:
  ```basic
  GET #dosya_numarasi, konum, degisken
  ```
- **Örnek**:
  ```basic
  OPEN "veri.bin" FOR BINARY AS #1
  DIM veri AS STRING
  GET #1, 1, veri
  PRINT veri
  CLOSE #1
  ```

#### **PUT #**
- **Açıklama**: İkili dosyalara belirli bir konuma veri yazar.
- **Sözdizimi**:
  ```basic
  PUT #dosya_numarasi, konum, deger
  ```
- **Örnek**:
  ```basic
  OPEN "veri.bin" FOR BINARY AS #1
  PUT #1, 1, "Test Verisi"
  CLOSE #1
  ```

### 3. Dosya Konum Yönetimi

#### **SEEK**
- **Açıklama**: Dosyada okuma/yazma konumunu değiştirir.
- **Sözdizimi**:
  ```basic
  SEEK #dosya_numarasi, konum
  ```
- **Örnek**:
  ```basic
  OPEN "veri.bin" FOR BINARY AS #1
  SEEK #1, 10
  PUT #1, , "Yeni Veri"
  CLOSE #1
  ```

#### **LOC**
- **Açıklama**: Dosyadaki geçerli konumu döndürür.
- **Sözdizimi**:
  ```basic
  DIM konum AS LONG
  konum = LOC(#dosya_numarasi)
  ```
- **Örnek**:
  ```basic
  OPEN "veri.txt" FOR INPUT AS #1
  PRINT LOC(#1)
  CLOSE #1
  ```

#### **LOF**
- **Açıklama**: Dosyanın uzunluğunu (bayt cinsinden) döndürür.
- **Sözdizimi**:
  ```basic
  DIM uzunluk AS LONG
  uzunluk = LOF(#dosya_numarasi)
  ```
- **Örnek**:
  ```basic
  OPEN "veri.txt" FOR INPUT AS #1
  PRINT "Dosya Uzunluğu: "; LOF(#1)
  CLOSE #1
  ```

#### **EOF**
- **Açıklama**: Dosya sonuna ulaşıldığını kontrol eder.
- **Sözdizimi**:
  ```basic
  IF EOF(#dosya_numarasi) THEN ...
  ```
- **Örnek**:
  ```basic
  OPEN "veri.txt" FOR INPUT AS #1
  WHILE NOT EOF(#1)
      DIM satir AS STRING
      LINE INPUT #1, satir
      PRINT satir
  WEND
  CLOSE #1
  ```

### 4. Dosya Kilitleme

#### **LOCK**
- **Açıklama**: Dosyanın belirli bir bölgesini kilitler (çok kullanıcılı erişim için).
- **Sözdizimi**:
  ```basic
  LOCK #dosya_numarasi, baslangic TO bitis
  ```
- **Örnek**:
  ```basic
  OPEN "veri.bin" FOR BINARY AS #1
  LOCK #1, 1 TO 100
  PUT #1, 1, "Kilitli Veri"
  UNLOCK #1, 1 TO 100
  CLOSE #1
  ```

#### **UNLOCK**
- **Açıklama**: Dosyanın kilitli bölgesini serbest bırakır.
- **Sözdizimi**:
  ```basic
  UNLOCK #dosya_numarasi, baslangic TO bitis
  ```
- **Örnek**: Yukarıdaki `LOCK` örneğinde gösterildi.

### 5. Dosya Sistemi Yönetimi

#### **KILL**
- **Açıklama**: Bir dosyayı siler.
- **Sözdizimi**:
  ```basic
  KILL "dosya_adi"
  ```
- **Örnek**:
  ```basic
  KILL "gecici.txt"
  ```

#### **NAME**
- **Açıklama**: Bir dosyanın adını değiştirir.
- **Sözdizimi**:
  ```basic
  NAME "eski_ad" AS "yeni_ad"
  ```
- **Örnek**:
  ```basic
  NAME "veri.txt" AS "veri_yedek.txt"
  ```

#### **FILES**
- **Açıklama**: Belirtilen dizindeki dosyaları listeler.
- **Sözdizimi**:
  ```basic
  FILES "dizin_yolu"
  ```
- **Örnek**:
  ```basic
  FILES "C:\data"
  ```

#### **DIR$**
- **Açıklama**: Dizin içeriğini bir dize olarak döndürür.
- **Sözdizimi**:
  ```basic
  DIM liste AS STRING
  liste = DIR$("dizin_yolu")
  ```
- **Örnek**:
  ```basic
  DIM dosyalar AS STRING
  dosyalar = DIR$("C:\data")
  PRINT dosyalar
  ```

#### **ISDIR**
- **Açıklama**: Belirtilen yolun bir dizin olup olmadığını kontrol eder.
- **Sözdizimi**:
  ```basic
  IF ISDIR("yol") THEN ...
  ```
- **Örnek**:
  ```basic
  IF ISDIR("C:\data") THEN
      PRINT "Bu bir dizin"
  ELSE
      PRINT "Bu bir dizin değil"
  END IF
  ```

#### **CHDIR**
- **Açıklama**: Geçerli çalışma dizinini değiştirir.
- **Sözdizimi**:
  ```basic
  CHDIR "dizin_yolu"
  ```
- **Örnek**:
  ```basic
  CHDIR "C:\data"
  ```

#### **MKDIR**
- **Açıklama**: Yeni bir dizin oluşturur.
- **Sözdizimi**:
  ```basic
  MKDIR "dizin_adi"
  ```
- **Örnek**:
  ```basic
  MKDIR "C:\yeni_dizin"
  ```

#### **RMDIR**
- **Açıklama**: Boş bir dizini siler.
- **Sözdizimi**:
  ```basic
  RMDIR "dizin_adi"
  ```
- **Örnek**:
  ```basic
  RMDIR "C:\yeni_dizin"
  ```

### 6. Özel Dosya İşleme Fonksiyonları

PDSX, dosya içeriğiyle çalışmak için ek fonksiyonlar sunar:

#### **PDF_READ_TEXT**
- **Açıklama**: PDF dosyasından metin çıkarır (`pdfplumber` kütüphanesine dayanır).
- **Sözdizimi**:
  ```basic
  DIM metin AS STRING
  metin = PDF_READ_TEXT("dosya.pdf")
  ```
- **Örnek**:
  ```basic
  DIM metin AS STRING
  metin = PDF_READ_TEXT("C:\Zotero\storage\rapor.pdf")
  PRINT metin
  ```

#### **PDF_EXTRACT_TABLES**
- **Açıklama**: PDF dosyasından tabloları çıkarır ve bir liste olarak döndürür.
- **Sözdizimi**:
  ```basic
  DIM tablolar AS LIST
  tablolar = PDF_EXTRACT_TABLES("dosya.pdf")
  ```
- **Örnek**:
  ```basic
  DIM tablolar AS LIST
  tablolar = PDF_EXTRACT_TABLES("C:\Zotero\storage\rapor.pdf")
  PRINT tablolar
  ```

#### **TXT_SEARCH**
- **Açıklama**: Metin dosyasında bir anahtar kelime arar.
- **Sözdizimi**:
  ```basic
  DIM sonuclar AS LIST
  sonuclar = TXT_SEARCH("dosya.txt", "anahtar_kelime")
  ```
- **Örnek**:
  ```basic
  DIM sonuclar AS LIST
  sonuclar = TXT_SEARCH("C:\data\metin.txt", "istatistik")
  PRINT sonuclar
  ```

#### **TXT_ANALYZE**
- **Açıklama**: Metin dosyasında kelime frekansı analizi yapar.
- **Sözdizimi**:
  ```basic
  DIM analiz AS DICT
  analiz = TXT_ANALYZE("dosya.txt")
  ```
- **Örnek**:
  ```basic
  DIM analiz AS DICT
  analiz = TXT_ANALYZE("C:\data\metin.txt")
  PRINT analiz
  ```

### 7. Zotero ve Veri Bilimi Entegrasyonu

Önceki konuşmalarınızda Zotero kütüphanelerinden PDF ve metin dosyalarını işleme (örneğin, `C:\Users\mete\Zotero\zotasistan\zapata_m6h`), TÜİK, FAO ve TradeMap gibi sitelerden veri kazıma ve dosya çıktıları oluşturma (örneğin, `zapata_m6hx`) talepleriniz vardı. PDSX’in dosya işlemleri, bu senaryolar için güçlü bir altyapı sunar.

#### **Zotero’dan PDF ve Metin Dosyalarını İşleme**
Zotero’dan PDF’leri okuyup analiz sonuçlarını dosyaya kaydetme:

```basic
REM Zotero PDF’lerinden veri çıkarma ve kaydetme
DIM pdf_metin AS STRING
pdf_metin = PDF_READ_TEXT("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
OPEN "zotero_sonuclar.txt" FOR OUTPUT AS #1
PRINT #1, pdf_metin
CLOSE #1

DIM tablolar AS LIST
tablolar = PDF_EXTRACT_TABLES("C:\Users\mete\Zotero\zotasistan\zapata_m6h\belge.pdf")
OPEN "zotero_tablolar.csv" FOR OUTPUT AS #2
FOR i = 1 TO LEN(tablolar)
    WRITE #2, tablolar[i]
NEXT
CLOSE #2
```

#### **TÜİK/FAO Verilerini Dosyaya Kaydetme**
Web kazıma ile toplanan verileri bir CSV dosyasına kaydetme:

```basic
REM TÜİK verilerini CSV’ye kaydet
DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM veriler AS LIST
veriler = SCRAPE_TABLES(html)  ' Varsayımsal fonksiyon
OPEN "tuik_verileri.csv" FOR OUTPUT AS #1
FOR i = 1 TO LEN(veriler)
    WRITE #1, veriler[i]
NEXT
CLOSE #1
```

#### **Dosya Listeleme ve Çıktı Oluşturma**
Zotero dizinindeki dosyaları listeleme ve alfabetik bir çıktı dosyası oluşturma (önceki talebinizdeki `klasor_adi.alfabetik.txt` benzeri):

```basic
REM Zotero dizinindeki dosyaları listele
DIM dosyalar AS STRING
dosyalar = DIR$("C:\Users\mete\Zotero\zotasistan\zapata_m6h")
OPEN "zapata_m6hx.txt" FOR OUTPUT AS #1
PRINT #1, dosyalar
CLOSE #1
```

### 8. Örnek: Kapsamlı Dosya İşlemi Uygulaması

Aşağıdaki program, Zotero’dan PDF işleme, web kazıma, dosya listeleme ve çıktı oluşturmayı birleştirir:

```basic
REM Zotero ve Web Verilerini İşle
CHDIR "C:\Users\mete\Zotero\zotasistan\zapata_m6h"
MKDIR "sonuclar"  ' Yeni bir sonuç dizini oluştur

REM Zotero PDF’lerinden veri çıkar
DIM pdf_metin AS STRING
pdf_metin = PDF_READ_TEXT("belge.pdf")
OPEN "sonuclar\pdf_metin.txt" FOR OUTPUT AS #1
PRINT #1, pdf_metin
CLOSE #1

REM TÜİK verilerini kaydet
DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM veriler AS LIST
veriler = SCRAPE_TABLES(html)
OPEN "sonuclar\tuik_verileri.csv" FOR OUTPUT AS #2
FOR i = 1 TO LEN(veriler)
    WRITE #2, veriler[i]
NEXT
CLOSE #2

REM Dizin içeriğini listele
DIM dosyalar AS STRING
dosyalar = DIR$(".")
OPEN "sonuclar\zapata_m6hx.txt" FOR OUTPUT AS #3
PRINT #3, "Dizin İçeriği:"
PRINT #3, dosyalar
CLOSE #3

REM Dosya analiz raporu
DIM analiz AS DICT
analiz = TXT_ANALYZE("pdf_metin.txt")
OPEN "sonuclar\analiz_raporu.txt" FOR OUTPUT AS #4
PRINT #4, analiz
CLOSE #4
```

**Çıktı (Varsayımsal)**:
- `sonuclar\pdf_metin.txt`: PDF’den çıkarılan metin.
- `sonuclar\tuik_verileri.csv`: TÜİK’ten kazınan tablo verileri.
- `sonuclar\zapata_m6hx.txt`: Zotero dizinindeki dosyaların listesi.
- `sonuclar\analiz_raporu.txt`: Metin analizi sonuçları (kelime frekansları).

### 9. Yetenekler

1. **Çok Yönlülük**: Metin, ikili ve ISAM dosyalarını destekler; PDF ve web verileriyle entegrasyon sağlar.
2. **Zotero Uyumluluğu**: PDF işleme (`PDF_READ_TEXT`, `PDF_EXTRACT_TABLES`) Zotero kütüphaneleriyle doğrudan çalışır.
3. **Veri Bilimi Desteği**: Çıkarılan veriler CSV, TXT gibi formatlara kaydedilerek veri bilimi analizlerine hazırlanabilir.
4. **Dosya Sistemi Yönetimi**: Dizin oluşturma, silme ve dosya listeleme gibi işlemler, toplu veri işleme için idealdir.
5. **Hata Yönetimi**: `ON ERROR GOTO` ile dosya işlemi hataları yönetilebilir; hatalar `interpreter_errors.log`’a kaydedilir.
6. **Web Kazıma Entegrasyonu**: Kazınan veriler doğrudan dosyalara yazılabilir (örneğin, TÜİK verileri).

### 10. Eksiklikler

1. **Kodlama Desteği**: UTF-8 varsayılan olarak desteklense de, önceki taleplerinizde belirttiğiniz Windows-1254, Latin-1, UTF-8-SIG gibi kodlama seçenekleri açıkça belirtilmemiştir. Bu, Türkçe karakterlerde sorunlara yol açabilir.
2. **Gelişmiş Dosya Formatları**: JSON, Excel veya XML gibi modern dosya formatları için doğrudan yazma/okuma desteği eksik.
3. **Eşzamanlı Erişim**: `LOCK` ve `UNLOCK` komutları basit düzeydedir ve çok kullanıcılı senaryolar için yetersizdir.
4. **Dosya Sıkıştırma**: ZIP veya TAR gibi sıkıştırılmış dosyalarla çalışma desteği bulunmuyor.
5. **Hata Mesajları**: Dosya işlemi hataları (örneğin, dosya bulunamadı, izin reddedildi) kullanıcı dostu olmayabilir.
6. **Büyük Dosya Desteği**: Büyük dosyalar için akış tabanlı (streaming) okuma/yazma optimize edilmemiştir.
7. **Filtreleme ve Desen Eşleştirme**: `FILES` ve `DIR$` komutları, dosya uzantısı veya düzenli ifade (regex) bazlı filtreleme sunmaz.

### 11. Öneriler ve İyileştirmeler

1. **Kodlama Desteği**:
   - Önceki taleplerinizde belirttiğiniz UTF-8, Windows-1254, Latin-1, UTF-8-SIG ve BOM-less UTF-8 kodlamalarını desteklemek için `OPEN` komutuna bir kodlama parametresi eklenebilir:
     ```basic
     OPEN "veri.txt" FOR INPUT AS #1 ENCODING "UTF-8-SIG"
     ```
     ```python
     def execute_open(self, filename, mode, file_number, encoding=None):
         kwargs = {"encoding": encoding} if encoding else {}
         self.files[file_number] = open(filename, mode, **kwargs)
     ```

2. **Modern Dosya Formatları**:
   - JSON ve Excel desteği için `WRITE_JSON` ve `WRITE_EXCEL` gibi fonksiyonlar eklenebilir:
     ```basic
     DIM veri AS DICT
     veri = {"ad": "Ali", "yas": 30}
     WRITE_JSON "veri.json", veri
     ```
     ```python
     import json
     self.function_table["WRITE_JSON"] = lambda filename, data: json.dump(data, open(filename, "w", encoding="utf-8"))
     ```

3. **Eşzamanlı Erişim**:
   - `LOCK` ve `UNLOCK` yerine daha güçlü bir dosya kilitleme mekanizması (örneğin, `fcntl` veya `msvcrt` kütüphaneleri) entegre edilebilir.

4. **Dosya Sıkıştırma**:
   - ZIP ve TAR dosyalarıyla çalışmak için `ZIP_EXTRACT` ve `ZIP_CREATE` gibi komutlar eklenebilir:
     ```basic
     ZIP_CREATE "veriler.zip", "C:\data"
     ```

5. **Kullanıcı Dostu Hata Mesajları**:
   - Dosya hataları için özelleştirilmiş mesajlar üretilebilir:
     ```python
     try:
         self.files[file_number] = open(filename, mode)
     except FileNotFoundError:
         raise Exception(f"Hata: Dosya '{filename}' bulunamadı!")
     except PermissionError:
         raise Exception(f"Hata: '{filename}' dosyasına erişim izni yok!")
     ```

6. **Büyük Dosya Desteği**:
   - Büyük dosyalar için akış tabanlı okuma/yazma desteği eklenebilir:
     ```basic
     OPEN "buyuk_dosya.txt" FOR INPUT STREAM AS #1
     WHILE NOT EOF(#1)
         DIM blok AS STRING
         blok = INPUT$(1024, #1)  ' 1 KB’lik blok oku
         PRINT blok
     WEND
     CLOSE #1
     ```

7. **Filtreleme ve Desen Eşleştirme**:
   - `FILES` ve `DIR$`’a dosya uzantısı veya regex filtresi eklenebilir:
     ```basic
     DIM txt_dosyalar AS STRING
     txt_dosyalar = DIR$("C:\data", "*.txt")
     PRINT txt_dosyalar
     ```

8. **Zotero için Özel Komutlar**:
   - Zotero dizinlerini taramak ve dosyaları işlemek için `ZOTERO_SCAN` gibi bir komut eklenebilir:
     ```basic
     DIM dosyalar AS LIST
     dosyalar = ZOTERO_SCAN("C:\Users\mete\Zotero\zotasistan\zapata_m6h", "*.pdf")
     OPEN "zapata_m6hx.txt" FOR OUTPUT AS #1
     FOR i = 1 TO LEN(dosyalar)
         PRINT #1, dosyalar[i]
     NEXT
     CLOSE #1
     ```

### 12. Sonuç ve Gelecek Adımlar

PDSX, dosya işlemleri için güçlü bir altyapı sunar ve Zotero, veri bilimi ve web kazıma gibi senaryolarla iyi entegre olur. Metin, ikili ve ISAM dosyalarını desteklemesi, dosya sistemi yönetimi ve PDF işleme yetenekleri, onu çok yönlü bir araç yapar. Ancak, kodlama seçenekleri, modern dosya formatları, eşzamanlı erişim ve büyük dosya desteği gibi alanlarda iyileştirmeler yapılabilir.

---

Evet, PDSX programlama dili, `numpy` kütüphanesinin matris ve vektör işlemlerini destekler. `pdsXInterpreter` sınıfındaki `function_table` içinde tanımlı olan `numpy` fonksiyonları, matris ve vektör işlemlerini gerçekleştirmek için doğrudan kullanılabilir. Ayrıca, PDSX’in `ARRAY` veri türü, `numpy` dizilerine dayalıdır ve bu işlemler için doğal bir destek sağlar. Aşağıda, PDSX’in `numpy` tabanlı matris ve vektör işlemlerini nasıl gerçekleştirebileceğini, mevcut fonksiyonları, örnekleri ve kullanım senaryolarını detaylı bir şekilde açıklayacağım. Ayrıca, önceki konuşmalarınızdaki veri bilimi ve Zotero entegrasyonu taleplerini göz önünde bulundurarak, bu özelliklerin nasıl entegre edilebileceğine dair öneriler de sunacağım.

---

## PDSX ile Matris ve Vektör İşlemleri

PDSX, `numpy` kütüphanesinin güçlü matris ve vektör işleme yeteneklerini kullanır. `function_table` içinde tanımlı olan `numpy` fonksiyonları, PDSX programlarında doğrudan çağrılabilir. Ayrıca, `evaluate_expression` yöntemi, `numpy` modülünü (`np`) ad alanına dahil ederek, PDSX ifadelerinde `numpy` fonksiyonlarının esnek bir şekilde kullanılmasını sağlar. PDSX’in `ARRAY` veri türü, `numpy.ndarray` ile eşdeğerdir ve matris/vektör işlemlerini destekler.

### Desteklenen Numpy Fonksiyonları

`pdsXInterpreter`’ın `function_table`’ında tanımlı olan `numpy` fonksiyonları şunlardır:

1. **Dizi Oluşturma**:
   - `LINSPACE(start, stop, num)`: Belirtilen aralıkta eşit aralıklı `num` adet sayı oluşturur.
   - `ARANGE(start, stop, step)`: Belirtilen aralıkta adım büyüklüğüne göre dizi oluşturur.
   - `ZEROS(shape)`: Sıfırlardan oluşan bir dizi oluşturur.
   - `ONES(shape)`: Birlerden oluşan bir dizi oluşturur.
   - `FULL(shape, value)`: Belirtilen değerle dolu bir dizi oluşturur.
   - `EYE(n)`: n x n birim matris oluşturur.
   - `DIAG(v)`: Bir vektörü diyagonal matris olarak oluşturur veya bir matrisin diyagonalini çıkarır.

2. **Dizi Birleştirme**:
   - `CONCATENATE(arrays, axis)`: Dizileri belirtilen eksende birleştirir.
   - `STACK(arrays, axis)`: Dizileri yeni bir eksende yığınlar.
   - `VSTACK(arrays)`: Dizileri dikey olarak yığınlar.
   - `HSTACK(arrays)`: Dizileri yatay olarak yığınlar.

3. **Lineer Cebir**:
   - `DOT(a, b)`: Matris veya vektör çarpımı (nokta çarpımı).
   - `CROSS(a, b)`: Vektörlerin çapraz çarpımı.
   - `NORM(a)`: Bir vektör veya matrisin normunu hesaplar.
   - `INV(a)`: Kare matrisin tersini hesaplar.
   - `SOLVE(a, b)`: Doğrusal denklem sistemi `ax = b`’yi çözer.

4. **Dizi Manipülasyonu**:
   - `RESHAPE(a, shape)`: Diziyi belirtilen şekle yeniden boyutlandırır.
   - `TRANSPOSE(a)`: Matrisin transpozunu alır.
   - `FLIP(a, axis)`: Diziyi belirtilen eksende ters çevirir.
   - `ROLL(a, shift, axis)`: Diziyi belirtilen eksende kaydırır.

### PDSX’te Matris ve Vektör İşlemleri

PDSX’te matris ve vektör işlemleri, `ARRAY` veri türü ve yukarıdaki `numpy` fonksiyonları kullanılarak gerçekleştirilir. `ARRAY` türü, `numpy.ndarray` ile uyumludur ve çok boyutlu dizileri destekler. Aşağıda, PDSX’te matris ve vektör işlemlerine dair örnekler verilmiştir.

#### 1. Vektör Oluşturma ve Temel İşlemler

**Örnek**: Bir vektör oluşturma, toplama ve nokta çarpımı.

```basic
DIM v1 AS ARRAY
DIM v2 AS ARRAY
v1 = ARANGE(1, 4)  ' [1, 2, 3]
v2 = ARANGE(4, 7)  ' [4, 5, 6]
PRINT v1           ' Çıktı: [1 2 3]
DIM toplam AS ARRAY
toplam = v1 + v2   ' [5, 7, 9]
PRINT toplam
DIM nokta_carpimi AS INTEGER
nokta_carpimi = DOT(v1, v2)  ' 1*4 + 2*5 + 3*6 = 32
PRINT nokta_carpimi
```

**Açıklama**:
- `ARANGE` ile vektörler oluşturulur.
- `+` operatörü, `numpy`’nun eleman bazlı toplama işlemini kullanır.
- `DOT` fonksiyonu, vektörlerin nokta çarpımını hesaplar.

#### 2. Matris Oluşturma ve Çarpma

**Örnek**: 2x2 matris oluşturma ve matris çarpımı.

```basic
DIM m1 AS ARRAY
DIM m2 AS ARRAY
m1 = RESHAPE(ARANGE(1, 5), (2, 2))  ' [[1, 2], [3, 4]]
m2 = RESHAPE(ARANGE(5, 9), (2, 2))  ' [[5, 6], [7, 8]]
PRINT m1
DIM carpim AS ARRAY
carpim = DOT(m1, m2)  ' [[19, 22], [43, 50]]
PRINT carpim
```

**Açıklama**:
- `ARANGE` ve `RESHAPE` ile 2x2 matrisler oluşturulur.
- `DOT` fonksiyonu, matris çarpımını gerçekleştirir.

#### 3. Matris Tersi ve Doğrusal Denklem Çözümü

**Örnek**: Bir matrisin tersini alma ve doğrusal denklem sistemi çözme.

```basic
DIM A AS ARRAY
DIM b AS ARRAY
A = RESHAPE(ARANGE(1, 5), (2, 2))  ' [[1, 2], [3, 4]]
b = ARANGE(5, 7)                   ' [5, 6]
DIM A_ters AS ARRAY
A_ters = INV(A)                    ' A matrisinin tersi
PRINT A_ters
DIM x AS ARRAY
x = SOLVE(A, b)                    ' Ax = b denklemini çözer
PRINT x
```

**Açıklama**:
- `INV` fonksiyonu, kare matrisin tersini hesaplar.
- `SOLVE` fonksiyonu, `Ax = b` şeklindeki doğrusal denklem sistemini çözer.

#### 4. Vektör Normu ve Çapraz Çarpım

**Örnek**: Vektör normu ve çapraz çarpım hesaplama.

```basic
DIM v AS ARRAY
v = ARANGE(1, 4)  ' [1, 2, 3]
DIM norm AS DOUBLE
norm = NORM(v)    ' sqrt(1^2 + 2^2 + 3^2) = sqrt(14)
PRINT norm
DIM v2 AS ARRAY
v2 = ARANGE(4, 7)  ' [4, 5, 6]
DIM capraz AS ARRAY
capraz = CROSS(v, v2)  ' [i, j, k] çapraz çarpımı
PRINT capraz
```

**Açıklama**:
- `NORM`, vektörün Öklid normunu hesaplar.
- `CROSS`, 3 boyutlu vektörlerin çapraz çarpımını gerçekleştirir.

#### 5. Matris ve Vektör Birleştirme

**Örnek**: Vektörleri yatay ve dikey olarak birleştirme.

```basic
DIM v1 AS ARRAY
DIM v2 AS ARRAY
v1 = ARANGE(1, 4)  ' [1, 2, 3]
v2 = ARANGE(4, 7)  ' [4, 5, 6]
DIM yatay AS ARRAY
yatay = HSTACK((v1, v2))  ' [1, 2, 3, 4, 5, 6]
PRINT yatay
DIM dikey AS ARRAY
dikey = VSTACK((v1, v2))  ' [[1, 2, 3], [4, 5, 6]]
PRINT dikey
```

**Açıklama**:
- `HSTACK` vektörleri yatay olarak birleştirir.
- `VSTACK` vektörleri dikey olarak birleştirir, matris oluşturur.

### Zotero ve Veri Bilimi ile Entegrasyon

Önceki konuşmalarınızda Zotero kütüphanelerinden PDF’ler üzerinde veri çıkarma ve analiz yapma talepleriniz vardı. Matris ve vektör işlemleri, bu tür veri bilimi görevlerinde faydalı olabilir. Örneğin, Zotero’daki PDF’lerden çıkarılan verileri matrislere dönüştürüp analiz edebilirsiniz.

**Örnek**: Zotero’dan PDF tablosu çıkarma ve matris analizi.

```basic
DIM tablolar AS LIST
tablolar = PDF_EXTRACT_TABLES("C:\Zotero\storage\rapor.pdf")
DIM matris AS ARRAY
matris = ARRAY(tablolar[0])  ' İlk tabloyu matrise çevir
PRINT matris
DIM ortalama AS DOUBLE
ortalama = MEAN(matris)  ' Matrisin elemanlarının ortalaması
PRINT "Ortalama: "; ortalama
DIM transpoz AS ARRAY
transpoz = TRANSPOSE(matris)  ' Matrisin transpozu
PRINT transpoz
```

**Açıklama**:
- `PDF_EXTRACT_TABLES`, Zotero’daki bir PDF’den tablo verilerini çıkarır.
- `ARRAY` fonksiyonu, tabloyu bir `numpy` matrisine dönüştürür.
- `MEAN` ve `TRANSPOSE` gibi fonksiyonlar, veri analizi ve manipülasyonu için kullanılır.

### Sınırlamalar ve Öneriler

#### Sınırlamalar
1. **Eksik Numpy Fonksiyonları**: `function_table`’da yalnızca belirli `numpy` fonksiyonları tanımlıdır. Örneğin, `eig` (özdeğer hesaplama) veya `svd` (tekil değer ayrışımı) gibi ileri düzey fonksiyonlar yoktur.
2. **Sözdizimi Kısıtlamaları**: PDSX’in BASIC tarzı sözdizimi, `numpy`’nun daha karmaşık fonksiyonlarını (örneğin, çoklu parametreli fonksiyonlar) kullanmayı zorlaştırabilir.
3. **Performans**: Büyük matris işlemleri, Python’un `eval` tabanlı değerlendirmesi nedeniyle yavaş olabilir.

#### Öneriler
1. **Ek Numpy Fonksiyonları**:
   - `function_table`’a `EIG`, `SVD`, `QR` gibi fonksiyonlar eklenerek lineer cebir desteği genişletilebilir.
   - Örnek: `function_table["EIG"] = np.linalg.eig`

2. **Matris Sözdizimi Desteği**:
   - PDSX’e matris sabitleri için özel bir sözdizimi eklenebilir (örn. `[[1, 2], [3, 4]]`).
   - Örnek: `DIM m AS ARRAY = [[1, 2], [3, 4]]`

3. **Performans İyileştirmesi**:
   - `evaluate_expression`’daki `eval` yerine, `numpy` işlemlerini doğrudan çağıran bir ayrıştırıcı kullanılabilir.
   - Büyük matrisler için önbellekleme uygulanabilir.

4. **Zotero için Matris Analizi**:
   - Zotero’dan çıkarılan veriler için özel bir fonksiyon (örn. `ZOTERO_MATRIX(library_id, item_id)`) eklenebilir. Bu, PDF’lerden tablo verilerini otomatik olarak matrise dönüştürür.
   - Örnek:
     ```basic
     DIM veri AS ARRAY
     veri = ZOTERO_MATRIX("12345", "67890")  ' Zotero’dan tabloyu matrise çevir
     PRINT DETERMINANT(veri)  ' Matrisin determinantı
     ```

5. **Görselleştirme**:
   - Matris ve vektörleri görselleştirmek için `PLOT` komutu eklenebilir (Matplotlib entegrasyonu).
   - Örnek:
     ```basic
     DIM v AS ARRAY
     v = LINSPACE(0, 10, 100)
     PLOT v, SIN(v)  ' Sinüs grafiği
     ```

### Örnek: Kapsamlı Matris Analizi

Aşağıda, PDSX ile kapsamlı bir matris analizi örneği verilmiştir. Bu örnek, Zotero’dan veri çıkarma, matris işlemleri ve veri bilimi analizini birleştirir.

```basic
REM Zotero’dan veri çıkar ve matris analizi yap
DIM pdf_tablolar AS LIST
pdf_tablolar = PDF_EXTRACT_TABLES("C:\Zotero\storage\istatistik.pdf")

REM İlk tabloyu matrise çevir
DIM veri_matrisi AS ARRAY
veri_matrisi = ARRAY(pdf_tablolar[0])
PRINT "Orijinal Matris:"
PRINT veri_matrisi

REM Matrisin transpozunu al
DIM transpoz AS ARRAY
transpoz = TRANSPOSE(veri_matrisi)
PRINT "Transpoz:"
PRINT transpoz

REM Matrisin ortalamasını hesapla
DIM ortalama AS DOUBLE
ortalama = MEAN(veri_matrisi)
PRINT "Elemanların Ortalaması: "; ortalama

REM Matris çarpımı örneği
DIM m2 AS ARRAY
m2 = EYE(2)  ' 2x2 birim matris
DIM carpim AS ARRAY
carpim = DOT(veri_matrisi, m2)
PRINT "Matris Çarpımı:"
PRINT carpim

REM Doğrusal denklem çözümü
DIM b AS ARRAY
b = ARANGE(1, 3)
DIM cozum AS ARRAY
cozum = SOLVE(veri_matrisi, b)
PRINT "Doğrusal Denklem Çözümü:"
PRINT cozum

REM Sonuçları dosyaya kaydet
OPEN "analiz_sonuclari.txt" FOR OUTPUT AS #1
WRITE #1, "Ortalama: "; ortalama
WRITE #1, "Çözüm: "; cozum
CLOSE #1
```

**Çıktı (Varsayımsal)**:
```
Orijinal Matris:
[[1 2]
 [3 4]]
Transpoz:
[[1 3]
 [2 4]]
Elemanların Ortalaması: 2.5
Matris Çarpımı:
[[1 2]
 [3 4]]
Doğrusal Denklem Çözümü:
[-1  1.5]
```

**Açıklama**:
- Zotero’dan tablo verileri çıkarılır ve `ARRAY`’e dönüştürülür.
- Matris işlemleri (`TRANSPOSE`, `DOT`, `SOLVE`) ve veri bilimi fonksiyonu (`MEAN`) kullanılır.
- Sonuçlar bir metin dosyasına kaydedilir.

### Sonuç ve Gelecek Adımlar

PDSX, `numpy` tabanlı matris ve vektör işlemlerini etkili bir şekilde destekler ve veri bilimi, Zotero entegrasyonu gibi alanlarda güçlü bir araçtır. Ancak, daha fazla `numpy` fonksiyonu eklenmesi, özel matris sözdizimi ve performans optimizasyonları, bu yetenekleri daha da artırabilir.  
  
---  
  
Evet, pdsX yorumlayıcısında **rekürsiyon (recursion)** özelliği desteklenmektedir. Rekürsiyon, bir fonksiyonun veya alt programın (SUB/FUNCTION) kendisini çağırması anlamına gelir ve pdsX’in mevcut yapısı bu özelliği etkin bir şekilde destekler. Aşağıda, pdsX’te rekürsiyonun nasıl çalıştığını, hangi mekanizmalarla desteklendiğini ve örnek bir kullanım senaryosunu Türkçe olarak açıklayacağım. Ayrıca, önceki konuşmalarımızdan ve verdiğiniz kod bağlamından yola çıkarak, rekürsiyonun pdsX’teki uygulanabilirliğini ve sınırlamalarını detaylandıracağım.

---

### pdsX’te Rekürsiyon Desteği

pdsX yorumlayıcısı, rekürsiyonu desteklemek için aşağıdaki mekanizmalara sahiptir:

1. **Çağrı Yığını (Call Stack)**:
   - `pdsXInterpreter` sınıfında `call_stack` listesi, `GOSUB`, `SUB`, `FUNCTION` veya rekürsif çağrılar için program sayacını (program counter) saklar. Her rekürsif çağrı, mevcut program sayacını yığına ekler ve dönüşte bu yığından alır.
   - Bu, rekürsif çağrıların düzgün bir şekilde yönetilmesini sağlar. Örneğin, bir `FUNCTION` kendini çağırdığında, her çağrı için yeni bir yığın çerçevesi oluşturulur.

2. **Yerel Kapsamlar (Local Scopes)**:
   - `local_scopes` listesi, her `SUB` veya `FUNCTION` çağrısı için yeni bir yerel kapsam oluşturur. Rekürsif çağrılarda, her çağrı kendi yerel değişkenlerini tutar, böylece değişken çakışmaları önlenir.
   - Rekürsiyon sırasında, her çağrının kendi parametreleri ve yerel değişkenleri ayrı bir kapsamda saklanır, bu da rekürsif fonksiyonların bağımsız çalışmasını sağlar.

3. **SUB ve FUNCTION Tanımları**:
   - pdsX’te `SUB` ve `FUNCTION` tanımları, kendi içlerinde tekrar çağrılabilir. `self.functions` ve `self.subs` sözlükleri, fonksiyon ve alt programların adreslerini tutar ve rekürsif çağrılar için bu adreslere erişim sağlar.
   - Örneğin, bir `FUNCTION` kendi adını kullanarak kendisini çağırabilir, ve yorumlayıcı bunu doğru bir şekilde çözümler.

4. **Hata Yönetimi**:
   - Rekürsif çağrılar sırasında yığın taşması (stack overflow) gibi hatalar, Python’un doğal yığın sınırları tarafından yönetilir. pdsX, `ON ERROR GOTO` ile hata yakalama desteği sunar, bu da rekürsif hataları yönetmek için kullanılabilir.

5. **Program Akış Kontrolü**:
   - `execute_command` metodu, rekürsif çağrıları desteklemek için program akışını dinamik olarak yönetir. `CALL` veya fonksiyon çağrıları, yeni bir kapsam oluşturarak ve program sayacını güncelleyerek rekürsiyonu mümkün kılar.

---

### Rekürsiyonun pdsX’te Kullanımı: Örnek

Aşağıda, pdsX’te rekürsiyonu gösteren bir örnek verilmiştir. Bu örnek, bir sayının faktöriyelini hesaplayan rekürsif bir `FUNCTION` tanımlar:

```vb
FUNCTION Faktoriyel(n AS INTEGER) AS INTEGER
    IF n <= 1 THEN
        Faktoriyel = 1
    ELSE
        Faktoriyel = n * Faktoriyel(n - 1)
    END IF
END FUNCTION

DIM sonuc AS INTEGER
LET sonuc = Faktoriyel(5)
PRINT sonuc
```

**Açıklama**:
- **Tanımlama**: `Faktoriyel` fonksiyonu, `n` parametresini alır ve `INTEGER` döner.
- **Rekürsif Çağrı**: `Faktoriyel(n - 1)` ifadesi, fonksiyonun kendisini çağırır. Her çağrı, `n` değerini azaltır.
- **Temel Durum**: `n <= 1` olduğunda, fonksiyon 1 döner, böylece rekürsiyon sona erer.
- **Çıktı**: `PRINT sonuc` komutu, `5! = 5 * 4 * 3 * 2 * 1 = 120` sonucunu yazdırır.

**Çalışma Süreci**:
1. `Faktoriyel(5)` çağrıldığında, `n = 5` için `5 * Faktoriyel(4)` hesaplanır.
2. `Faktoriyel(4)` çağrılır, bu da `4 * Faktoriyel(3)` hesaplar, ve bu böyle devam eder.
3. `Faktoriyel(1)` temel duruma ulaşır ve 1 döner.
4. Çağrılar yığından geri sarılır: `Faktoriyel(2) = 2 * 1`, `Faktoriyel(3) = 3 * 2`, vb., sonunda `120` sonucu elde edilir.

---

### pdsX’te Rekürsiyonun Teknik Detayları

Verdiğiniz güncellenmiş `pdsXInterpreter` koduna dayanarak, rekürsiyonun teknik işleyişini detaylandırayım:

- **Fonksiyon Çağrıları**:
  - `execute_command` içinde, bir fonksiyon çağrısı (`\w+\s*\(.+\)`) tespit edildiğinde, `self.functions[func_name]` ile fonksiyonun başlangıç satırı bulunur.
  - `self.call_stack.append(self.program_counter)` ile mevcut konum yığına eklenir, ve `self.local_scopes.append({})` ile yeni bir yerel kapsam oluşturulur.
  - Rekürsif çağrılar için, aynı fonksiyon tekrar çağrıldığında, yeni bir yığın çerçevesi ve yerel kapsam eklenir, böylece her çağrı bağımsızdır.

- **Kapsam Yönetimi**:
  - `local_scopes` yığını, rekürsif çağrılarda değişkenlerin çakışmasını önler. Örneğin, `Faktoriyel(5)` ve `Faktoriyel(4)` için ayrı `n` değerleri saklanır.
  - `current_scope()` metodu, en üstteki yerel kapsamı döndürerek rekürsif çağrıların doğru değişkenlere erişmesini sağlar.

- **Hata Kontrolü**:
  - Eğer rekürsiyon çok derinleşirse (örneğin, temel durum olmadan sonsuz rekürsiyon), Python’un yığın sınırına ulaşılır ve bir hata fırlatılır.
  - `ON ERROR GOTO` ile bu hatalar yakalanabilir:
    ```vb
    ON ERROR GOTO HataYonetici
    PRINT Faktoriyel(1000) ' Çok derin rekürsiyon
    END
    HataYonetici:
    PRINT "Rekürsiyon hatası"
    RESUME NEXT
    ```

- **Performans**:
  - pdsX, Python’un altında çalıştığı için rekürsiyon performansı Python’un yığın yönetimine bağlıdır. Tipik olarak, binlerce seviyeli rekürsiyon sorun çıkarmaz, ancak çok derin rekürsiyonlarda `sys.setrecursionlimit()` ile sınır artırılabilir (kodda varsayılan olarak değiştirilmemiştir).

---

### Sınırlamalar ve Dikkat Edilmesi Gerekenler

1. **Yığın Taşması**:
   - Çok derin rekürsiyon (örneğin, milyonlarca çağrı) Python’un yığın sınırına takılabilir. Bu durumda, kuyruk rekürsiyonu (tail recursion) optimizasyonu pdsX’te mevcut değildir, çünkü Python bunu yerel olarak desteklemez.
   - Çözüm: Rekürsif algoritmaları döngülerle yeniden yazmak veya temel durumu erken tanımlamak.

2. **Performans**:
   - Her rekürsif çağrı, yeni bir yığın çerçevesi ve yerel kapsam oluşturur, bu da bellek kullanımını artırabilir. Büyük veri setlerinde, iteratif çözümler daha verimli olabilir.

3. **Hata Yönetimi**:
   - Rekürsif fonksiyonlarda hata yönetimi için `ON ERROR GOTO` kullanılmalıdır, aksi takdirde program çökebilir.

4. **Sınıf Yöntemlerinde Rekürsiyon**:
   - Sınıf (`CLASS`) yöntemlerinde rekürsiyon da desteklenir. Örneğin:
     ```vb
     CLASS Agac
         DIM Deger AS INTEGER
         DIM Sol AS Agac
         DIM Sag AS Agac
         FUNCTION Derinlik AS INTEGER
             IF Sol IS NULL AND Sag IS NULL THEN
                 Derinlik = 1
             ELSE
                 DIM solDerinlik AS INTEGER = 0
                 DIM sagDerinlik AS INTEGER = 0
                 IF NOT Sol IS NULL THEN
                     solDerinlik = Sol.Derinlik
                 END IF
                 IF NOT Sag IS NULL THEN
                     sagDerinlik = Sag.Derinlik
                 END IF
                 Derinlik = 1 + MAX(solDerinlik, sagDerinlik)
             END IF
         END FUNCTION
     END CLASS
     ```
   - Bu örnekte, `Derinlik` yöntemi rekürsif olarak ağacın sol ve sağ dallarını tarar.

---

### Önceki Bağlamla Entegrasyon

Önceki konuşmalarınızda (örneğin, 18 Şubat 2025’te PDF işleme ve 8 Mart 2025’te dosya listeleme üzerine), pdsX’in modern özelliklerle (NumPy, Pandas, PDF işleme) güçlendirilmesini ve nesne yönelimli programlamayı desteklemesini vurguladınız. Rekürsiyon, bu bağlamda özellikle veri bilimi ve ağaç benzeri veri yapıları (örneğin, Zotero kütüphanesi meta veri analizi) için kullanışlıdır. Örneğin, bir PDF dosyasındaki içindekiler tablosunu rekürsif olarak taramak veya bir klasör yapısındaki dosyaları rekürsif olarak listelemek için pdsX’te rekürsif fonksiyonlar yazılabilir.

Ayrıca, 10 Mart 2025’teki konuşmanızda kod kalitesi ve hata yönetimi üzerine odaklandınız. Rekürsif fonksiyonlarda `ASSERT` komutu (örneğin, `ASSERT n >= 0` ile negatif girişleri kontrol etme) ve hata loglama (`logging.error`) kullanarak daha sağlam kodlar yazabilirsiniz.

---

### Örnek: Klasör Yapısını Rekürsif Olarak Listeleme

Verdiğiniz dosya listeleme bağlamına uygun olarak, pdsX’te bir klasördeki dosyaları ve alt klasörleri rekürsif olarak listeleyen bir örnek:

```vb
FUNCTION KlasorListele(klasorYolu AS STRING, seviye AS INTEGER) AS LIST
    DIM dosyalar AS LIST
    DIM dosya AS STRING
    DIM altKlasor AS STRING
    LET dosyalar = []
    FOR EACH dosya IN DIR$(klasorYolu)
        IF ISDIR(klasorYolu + "/" + dosya) THEN
            LET altDosyalar = KlasorListele(klasorYolu + "/" + dosya, seviye + 1)
            FOR EACH altDosya IN altDosyalar
                APPEND dosyalar, STRING$(seviye, "  ") + altDosya
            NEXT
        ELSE
            APPEND dosyalar, STRING$(seviye, "  ") + dosya
        END IF
    NEXT
    KlasorListele = dosyalar
END FUNCTION

DIM sonuc AS LIST
LET sonuc = KlasorListele("C:/Veri", 0)
FOR EACH dosya IN sonuc
    PRINT dosya
NEXT
```

**Açıklama**:
- `KlasorListele`, verilen klasör yolundaki dosyaları ve alt klasörleri tarar.
- `ISDIR` (varsayımsal, dosya sistemine erişim için) bir yolun klasör olup olmadığını kontrol eder.
- `DIR$` (varsayımsal), klasördeki dosya/klasör listesini döndürür.
- Rekürsif çağrı, alt klasörlerde devam eder ve her seviye için girinti ekler.
- Çıktı, hiyerarşik bir dosya listesi üretir.

**Not**: `DIR$` ve `ISDIR` fonksiyonları, mevcut kodda tanımlı değilse, `os.listdir` ve `os.path.isdir` kullanarak `function_table`’a eklenebilir:
```python
self.function_table["DIR$"] = lambda path: os.listdir(path)
self.function_table["ISDIR"] = lambda path: os.path.isdir(path)
```

---

### Sonuç

pdsX, rekürsiyonu tam anlamıyla destekler ve `SUB`, `FUNCTION`, hatta `CLASS` yöntemlerinde rekürsif çağrılar sorunsuz çalışır. `call_stack` ve `local_scopes` mekanizmaları, rekürsiyonun güvenli ve verimli bir şekilde yürütülmesini sağlar. Ancak, derin rekürsiyonlarda yığın taşması riskine karşı dikkatli olunmalı ve temel durumlar iyi tanımlanmalıdır. Verdiğiniz kod bağlamında, rekürsiyon özellikle dosya sistemi tarama, veri bilimi algoritmaları (örneğin, ağaç traversalleri) ve PDF/web veri işleme gibi senaryolarda güçlü bir araçtır.

Eğer daha spesifik bir rekürsif algoritma (örneğin, ağaç traversali, Fibonacci, veya Zotero meta veri analizi) için örnek veya optimizasyon isterseniz, lütfen belirtin! Ayrıca, rekürsiyon performansını artırmak için kuyruk rekürsiyonu simülasyonu gibi ek özellikler üzerine çalışmamı ister misiniz?

---

# PDSX Yorumlayıcı Analizi ve Kullanım Kılavuzu

## Bölüm 1: pdsXInterpreter’ın Ayrıntılı Analizi

### Genel Bakış

`pdsXInterpreter`, GW-BASIC ve QBASIC’ten ilham alan, ancak modern veri bilimi, dosya işlemleri, veritabanı yönetimi ve web kazıma gibi özelliklerle genişletilmiş PDSX programlama dilini çalıştıran bir yorumlayıcıdır. Python’da yazılmış olan bu yorumlayıcı, `numpy`, `pandas`, `scipy`, `pdfplumber` ve `requests` gibi güçlü kütüphaneleri kullanarak hem geleneksel hem de veri odaklı uygulamalar için çok yönlü bir platform sunar. PDSX, basit sözdizimi ile yeni başlayanlar için erişilebilirken, profesyonel geliştiriciler için de karmaşık görevleri yerine getirebilecek özellikler sağlar.

### Program Yapısı

`pdsXInterpreter` sınıfı, program yürütme, değişken kapsamları ve harici entegrasyonları yönetir. Temel bileşenler şunlardır:

1. **Başlatma (**`__init__`**)**:

   - Değişkenler (`global_vars`, `shared_vars`, `local_scopes`), fonksiyonlar, alt programlar, sınıflar ve türler için veri yapıları başlatılır.
   - İlkel (`INTEGER`, `STRING`) ve gelişmiş (`ARRAY`, `DATAFRAME`) veri türlerini destekleyen bir `type_table` tanımlanır.
   - Dize manipülasyonu, matematik, veri bilimi, dosya işlemleri ve web kazıma için geniş bir `function_table` içerir.
   - Hata ayıklama, izleme, döngü yönetimi ve veritabanı/dosya kolları için durum yönetimi kurulur.

2. **Program Ayrıştırma (**`parse_program`**)**:

   - PDSX kodunu yapılandırılmış bir program temsiline ayrıştırır; `SUB`, `FUNCTION`, `TYPE`, `CLASS` ve `DATA` gibi yapıları işler.
   - `IMPORT` komutu ile modüler programlamayı destekler ve modül bilgilerini `self.modules`’da saklar.
   - Kontrol akışı için etiketler, alt programlar ve fonksiyonlar izlenir.

3. **Komut Yürütme (**`execute_command`**)**:

   - PDSX komutlarını yürütmek için temel yöntemdir.
   - Kontrol yapıları (`IF`, `FOR`, `WHILE`, `SELECT CASE`), değişken yönetimi (`DIM`, `LET`), giriş/çıkış (`PRINT`, `INPUT`), dosya işlemleri (`OPEN`, `WRITE`), veritabanı işlemleri (`SELECT`, `UPDATE`) ve daha fazlasını destekler.
   - `ON ERROR GOTO` ve `RESUME` ile hata yönetimi sağlar.

4. **İfade Değerlendirme (**`evaluate_expression`**)**:

   - Python’un `eval` fonksiyonunu kullanarak ifadeleri değerlendirir; değişkenler, yerleşik fonksiyonlar ve içe aktarılmış modüllerle özel bir ad alanı kullanır.
   - Güvenli değerlendirme için ad alanı bilinen varlıklarla sınırlandırılır.

5. **REPL ve Dosya Yürütme (**`repl`**,** `run_file`**)**:

   - Gerçek zamanlı komut yürütme için etkileşimli bir REPL modu sağlar.
   - `.basX` dosyalarını komut satırından çalıştırmayı destekler.

6. **Harici Entegrasyonlar**:

   - **Dosya İşlemleri**: Metin, ikili ve ISAM (SQLite) dosya işlemlerini destekler.
   - **Veritabanı**: SQLite ile ilişkisel veritabanı işlemleri sağlar.
   - **PDF İşleme**: `pdfplumber` ile metin ve tablo çıkarma.
   - **Web Kazıma**: `requests` ve `BeautifulSoup` ile HTTP istekleri ve HTML ayrıştırma.
   - **Veri Bilimi**: `numpy`, `pandas` ve `scipy` ile istatistiksel ve veri manipülasyon görevleri.

### Desteklenen Komutlar

PDSX, geniş bir komut yelpazesini destekler ve aşağıdaki kategorilere ayrılır:

1. **Kontrol Akışı**:

   - `IF...THEN...ELSE...END IF`: Koşullu dallanma.
   - `SELECT CASE...CASE...END SELECT`: Çoklu durum seçimi.
   - `FOR...NEXT`, `WHILE...WEND`, `DO...LOOP`: Döngüler.
   - `GOTO`, `GOSUB`, `RETURN`, `CALL`: Program akış kontrolü.
   - `EXIT FOR`, `EXIT DO`, `CONTINUE FOR`, `CONTINUE DO`: Döngü kontrolü.

2. **Değişken ve Veri Yönetimi**:

   - `DIM`, `DIM SHARED`, `GLOBAL`: Değişken tanımlama.
   - `DEFINT`, `DEFSNG`, `DEFDBL`, `DEFSTR`: Varsayılan tür tanımları.
   - `LET`, `READ`, `DATA`, `RESTORE`: Değişken atama ve veri okuma.

3. **Giriş/Çıkış**:

   - `PRINT`, `INPUT`, `LINE INPUT`, `WRITE`: Konsol ve dosya I/O.
   - `PRINT #`, `INPUT #`, `LINE INPUT #`: Dosya tabanlı I/O.

4. **Dosya İşlemleri**:

   - `OPEN`, `CLOSE`, `WRITE #`, `READ #`, `APPEND #`: Dosya yönetimi.
   - `SEEK`, `GET #`, `PUT #`, `LOCK`, `UNLOCK`: Dosya konumu ve kilit yönetimi.
   - `KILL`, `NAME`, `FILES`, `CHDIR`, `MKDIR`, `RMDIR`: Dosya sistemi işlemleri.

5. **Veritabanı İşlemleri**:

   - `OPEN...FOR ISAM`, `DEFINE TABLE`, `PUT`, `GET`, `DELETE`: Veritabanı yönetimi.
   - `SELECT`, `JOIN`, `UPDATE`, `ALTER TABLE`, `CREATE VIEW`: SQL benzeri sorgular.
   - `DROP TABLE`, `TRUNCATE TABLE`, `INDEX`: Tablo ve indeks yönetimi.
   - `BEGIN TRANSACTION`, `COMMIT`, `ROLLBACK`: İşlem yönetimi.

6. **Program Yönetimi**:

   - `LIST`, `NEW`, `LOAD`, `SAVE`, `RUN`, `END`, `SYSTEM`: Program kontrolü.
   - `IMPORT`: Modül içe aktarma.

7. **Hata Ayıklama ve Test**:

   - `DEBUG ON/OFF`, `TRACE ON/OFF`, `STEP DEBUG`: Hata ayıklama.
   - `ASSERT`: Koşul doğrulama.

8. **Modüler Programlama**:

   - `SUB...END SUB`, `FUNCTION...END FUNCTION`: Alt programlar ve fonksiyonlar.
   - `TYPE...END TYPE`, `CLASS...END CLASS`: Özel veri türleri ve nesne yönelimli programlama.
   - `DESCRIBE`: Sınıf meta veri incelemesi.

9. **Diğer**:

   - `RANDOMIZE`: Rastgele sayı üreteci sıfırlama.
   - Yerleşik fonksiyonlar (aşağıda detaylı listelenmiştir).

### Yerleşik Fonksiyonlar

PDSX, geniş bir yerleşik fonksiyon kütüphanesi sunar:

1. **Dize Manipülasyonu**:

   - `MID$(s, start, length)`: Diziden alt dize alır (örn. `MID$("Hello", 2, 3)` → `ell`).
   - `LEN(s)`: Dize uzunluğunu döndürür.
   - `LEFT$(s, n)`, `RIGHT$(s, n)`: Soldan/sağdan n karakter alır.
   - `LTRIM$(s)`, `RTRIM$(s)`: Baştaki/sondaki boşlukları kaldırır.
   - `STRING$(n, c)`: Karakter c’yi n kez tekrarlar.
   - `SPACE$(n)`: n boşluk döndürür.
   - `INSTR(start, s, sub)`: Alt dizenin ilk bulunduğu konumu döndürür.
   - `UCASE$(s)`, `LCASE$(s)`: Büyük/küçük harfe çevirir.
   - `STR$(n)`: Sayıyı dizeye çevirir.
   - `CHR$(n)`: ASCII koduna karşılık gelen karakteri döndürür.
   - `ASC(c)`: Karakterin ASCII kodunu döndürür.
   - `VAL(s)`: Dizeyi sayıya çevirir.

2. **Matematiksel Fonksiyonlar**:

   - `ABS(n)`: Mutlak değer.
   - `INT(n)`: Tamsayıya yuvarlama.
   - `SQR(n)`: Karekök.
   - `SIN(n)`, `COS(n)`, `TAN(n)`, `ATN(n)`: Trigonometrik fonksiyonlar.
   - `LOG(n)`, `EXP(n)`: Logaritma ve üstel.
   - `FIX(n)`: Ondalık kısmı atar.
   - `ROUND(n, digits)`: Belirtilen basamağa yuvarlar.
   - `SGN(n)`: Sayının işaretini döndürür (-1, 0, 1).
   - `MOD(x, y)`: Modülüs.
   - `MIN(*args)`, `MAX(*args)`: Minimum/maksimum değer.

3. **Rastgele ve Zaman Fonksiyonları**:

   - `RND()`: 0-1 arası rastgele sayı.
   - `TIMER()`: Geçerli zaman damgası.
   - `DATE$()`: Geçerli tarih (MM-DD-YYYY).
   - `TIME$()`: Geçerli saat (HH:MM:SS).

4. **Sistem ve Ortam**:

   - `INKEY$()`: Klavye girişinden tek karakter okur.
   - `ENVIRON$(var)`: Çevresel değişken değerini döndürür.
   - `COMMAND$()`: Komut satırı argümanlarını döndürür.
   - `CSRLIN()`, `POS(x)`: Konsol konumu (basit simülasyon).

5. **Veri Bilimi Fonksiyonları**:

   - `MEAN(x)`: Ortalama.
   - `MEDIAN(x)`: Medyan.
   - `MODE(x)`: Mod.
   - `STD(x)`: Standart sapma.
   - `VAR(x)`: Varyans.
   - `SUM(x)`, `PROD(x)`: Toplam ve çarpım.
   - `PERCENTILE(x, p)`, `QUANTILE(x, q)`: Yüzdelik ve çeyreklik.
   - `CORR(x, y)`: Korelasyon katsayısı.
   - `COV(x, y)`: Kovaryans.
   - `DESCRIBE(df)`: Veri çerçevesi özeti.
   - `GROUPBY(df, col)`: Sütuna göre gruplama.
   - `FILTER(df, cond)`: Koşula göre filtreleme.
   - `SORT(df, col)`: Sütuna göre sıralama.
   - `HEAD(df, n)`, `TAIL(df, n)`: İlk/son n satır.
   - `MERGE(df1, df2, on)`: Veri çerçevelerini birleştirme.
   - `TTEST(sample1, sample2)`: T-testi.
   - `CHISQUARE(observed)`: Ki-kare testi.
   - `ANOVA(*groups)`: ANOVA testi.
   - `REGRESS(x, y)`: Doğrusal regresyon.

6. **NumPy Fonksiyonları**:

   - `CONCATENATE`, `STACK`, `VSTACK`, `HSTACK`: Dizi birleştirme.
   - `DOT`, `CROSS`: Nokta ve çapraz çarpım.
   - `NORM`, `INV`, `SOLVE`: Lineer cebir işlemleri.
   - `LINSPACE`, `ARANGE`, `ZEROS`, `ONES`, `FULL`, `EYE`, `DIAG`: Dizi oluşturma.
   - `RESHAPE`, `TRANSPOSE`, `FLIP`, `ROLL`: Dizi manipülasyonu.

7. **Pandas Fonksiyonları**:

   - `PIVOT_TABLE`, `CROSSTAB`: Tablo özetleme.
   - `FILLNA`, `DROPNA`: Eksik veri yönetimi.
   - `ASTYPE`, `MELT`, `CUT`, `QCUT`: Veri dönüşümü.
   - `TO_DATETIME`, `RESAMPLE`, `ROLLING`, `EWMA`, `SHIFT`, `DIFF`, `PCT_CHANGE`: Zaman serisi ve veri manipülasyonu.

8. **Dosya ve Sistem İşlemleri**:

   - `EOF(n)`: Dosya sonu kontrolü.
   - `LOC(n)`: Dosya konumu.
   - `LOF(n)`: Dosya boyutu.
   - `FREEFILE()`: Kullanılmayan dosya numarası.
   - `INPUT$(n, f)`: Dosyadan n karakter okur.
   - `MKI$(n)`, `MKS$(n)`, `MKD$(n)`: Sayıyı ikili formata çevirir.
   - `DIR$(path)`: Dizin içeriğini listeler.
   - `ISDIR(path)`: Yolun dizin olup olmadığını kontrol eder.

9. **PDF ve Web Fonksiyonları**:

   - `PDF_READ_TEXT(file)`: PDF’den metin çıkarır.
   - `PDF_EXTRACT_TABLES(file)`: PDF’den tablolar çıkarır.
   - `PDF_SEARCH_KEYWORD(file, keyword)`: PDF’de anahtar kelime arar.
   - `TXT_SEARCH(file, keyword)`: Metin dosyasında anahtar kelime arar.
   - `TXT_ANALYZE(file)`: Metin dosyasında kelime frekansı analizi.
   - `WEB_GET(url)`: URL’den içerik indirir.
   - `WEB_POST(url, data)`: URL’ye veri gönderir.
   - `SCRAPE_LINKS(html)`: HTML’den bağlantıları çıkarır.
   - `SCRAPE_TEXT(html)`: HTML’den metni çıkarır.

### Güçlü Yönler

1. **Çok Yönlülük**: İşlemsel, modüler ve nesne yönelimli programlama paradigmalarını destekler; veri bilimi, dosya işleme, veritabanı yönetimi ve web kazıma gibi alanlarda kullanılabilir.
2. **Modern Uzantılar**: `numpy`, `pandas` ve `scipy` ile veri analizi ve görselleştirme için güçlü araçlar sunar.
3. **GW-BASIC Uyumluluğu**: BASIC programcıları için tanıdık sözdizimi korurken modern özellikler ekler.
4. **Hata Yönetimi**: `ON ERROR GOTO`, `RESUME` ve `interpreter_errors.log` ile sağlam hata yönetimi.
5. **Modülerlik**: `.basX`, `.libX`, `.hX` dosyalarıyla yeniden kullanılabilir kod desteği.
6. **Etkileşimli REPL**: Deneme ve hızlı prototipleme için kullanıcı dostu arayüz.

### Zayıf Yönler

1. **Performans**: `eval` kullanımı, büyük programlarda yavaş olabilir; derlenmiş veya JIT derlenmiş bir yaklaşım daha hızlı olur.
2. **Grafik Desteği Eksikliği**: Matplotlib gibi kütüphaneler henüz entegre edilmedi; grafik veya GUI komutları yok.
3. **Güvenlik Riskleri**: `evaluate_expression`’daki `eval`, güvenilmeyen kodlar için risk oluşturabilir, ancak ad alanı kısıtlıdır.
4. **Eksik Dokümantasyon**: Kod özellik açısından zengin, ancak satır içi dokümantasyon sınırlı.
5. **Basit Dosya Kilitleme**: `LOCK` ve `UNLOCK` komutları, çok kullanıcılı senaryolar için yetersiz.
6. **Eksik Özellikler**: Kesme noktaları, değişken izleme gibi gelişmiş hata ayıklama araçları ve modern istisna yönetimi eksik.

### Potansiyel İyileştirmeler

1. **Performans Optimizasyonu**:

   - `eval` yerine özel bir ifade ayrıştırıcı veya bayt kodu derleyici kullan.
   - Sık kullanılan fonksiyonları önbelleğe al.

2. **Grafik Desteği**:

   - Matplotlib veya Plotly ile `PLOT` komutları ekle.
   - Tkinter veya PyQt ile temel GUI desteği.

3. **Gelişmiş Hata Ayıklama**:

   - `BREAK` ve `WATCH` komutları ile kesme noktaları ve değişken izleme.
   - Adım adım hata ayıklama için görsel arayüz.

4. **Güvenlik Geliştirmeleri**:

   - `ast.literal_eval` veya özel ayrıştırıcı ile güvenli ifade değerlendirme.
   - Güvenilmeyen kod için sanal alan (sandbox).

5. **Modül Sistemi**:

   - `.libX` arşivleri için paket benzeri modül desteği.
   - İsim çakışmalarını önlemek için ad alanı izolasyonu.

6. **Dokümantasyon**:

   - Komutlar ve fonksiyonlar için otomatik dokümantasyon.
   - PDSX sözdizimi ve örnekleri için referans kılavuzu.

---

## Bölüm 2: PDSX Kullanım Kılavuzu

### Giriş

PDSX, GW-BASIC ve QBASIC’ten esinlenen, genel amaçlı programlama, veri bilimi ve dosya/veritabanı işlemleri için tasarlanmış modern bir programlama dilidir. Basit sözdizimi ile yeni başlayanlar için erişilebilir, aynı zamanda veri analizi, web kazıma ve modüler programlama için güçlü özellikler sunar. Bu kılavuz, PDSX ile program yazma konusunda ayrıntılı bir rehber sunar.

### Başlarken

1. **Kurulum**:

   - Python 3.8+ yüklü olmalıdır.
   - Gerekli kütüphaneleri yükleyin: `pip install numpy pandas scipy pdfplumber requests beautifulsoup4`.
   - `pdsXInterpreter` kodunu `pdsXInterpreter.py` olarak kaydedin.

2. **PDSX Çalıştırma**:

   - **Etkileşimli Mod**: `python pdsXInterpreter.py` ile REPL’yi başlatın.
   - **Dosya Modu**: `python pdsXInterpreter.py program.basX` ile `.basX` dosyasını çalıştırın.
   - **REPL İstemi**: REPL’de `PDSX>` isteminde komutlar girin. Çıkmak için `SYSTEM` yazın.

3. **Dosya Uzantıları**:

   - `.basX`: Ana program dosyaları.
   - `.libX`: Yeniden kullanılabilir kod için kütüphane modülleri.
   - `.hX`: Paylaşılan tanımlar için başlık dosyaları.

### Temel Sözdizimi

- **Büyük/Küçük Harf Duyarsızlığı**: Komutlar ve anahtar kelimeler büyük/küçük harfe duyarlı değildir (örn. `PRINT` = `print`).
- **Satır Tabanlı**: Her satır tek bir komut veya ifade içerir.
- **Yorumlar**: Yorumlar için `REM` veya `'` kullanın (örn. `REM Bu bir yorum`).
- **Değişkenler**: `DIM`, `GLOBAL` veya `DIM SHARED` ile tanımlanır. Örtük tanımlama yoktur.
- **İfadeler**: Aritmetik (`+`, `-`, `*`, `/`), mantıksal (`AND`, `OR`, `NOT`) ve fonksiyon çağrılarını destekler.

### Veri Türleri

PDSX, çeşitli veri türlerini destekler:

- **İlkel**: `STRING`, `INTEGER`, `LONG`, `SINGLE`, `DOUBLE`, `BYTE`, `SHORT`, `UNSIGNED INTEGER`, `CHAR`
- **Koleksiyonlar**: `LIST`, `DICT`, `SET`, `TUPLE`
- **Gelişmiş**: `ARRAY` (NumPy), `DATAFRAME` (Pandas)
- **Özel**: `TYPE`, `CLASS`, `STRUCT`, `ENUM`

Örnek:

```basic
DIM ad AS STRING
DIM sayilar AS ARRAY
DIM veri AS DATAFRAME
```

### Komutlar ve Örnekler

Aşağıda, PDSX’in tüm komutları kategorilere ayrılmış ve örneklerle detaylandırılmıştır.

#### 1. Değişken Tanımlama ve Atama

- **DIM**: Yerel değişken tanımlar.
- **GLOBAL**: Küresel değişken tanımlar.
- **DIM SHARED**: Kapsamlar arasında paylaşılan değişken tanımlar.
- **LET**: Değer atar (isteğe bağlı anahtar kelime).
- **DEFINT**`, `**DEFSNG**`, `**DEFDBL**`, `**DEFSTR**: Varsayılan tür tanımlar.

Örnek:

```basic
DIM x AS INTEGER
GLOBAL ad AS STRING
DIM SHARED modül1, modül2, sayac AS INTEGER
LET x = 42
ad = "Ali"
sayac = sayac + 1
DEFINT y
y = 10
```

#### 2. Kontrol Akışı

- **IF...THEN...ELSE**:

```basic
DIM puan AS INTEGER
puan = 85
IF puan >= 90 THEN
    PRINT "A"
ELSE
    PRINT "B"
END IF
```

- **FOR...NEXT**:

```basic
FOR i = 1 TO 5
    PRINT i
NEXT
```

- **WHILE...WEND**:

```basic
DIM x AS INTEGER
x = 1
WHILE x <= 5
    PRINT x
    x = x + 1
WEND
```

- **DO...LOOP**:

```basic
DIM x AS INTEGER
x = 1
DO
    PRINT x
    x = x + 1
LOOP UNTIL x > 5
```

- **SELECT CASE**:

```basic
DIM notu AS STRING
notu = "A"
SELECT CASE notu
    CASE "A"
        PRINT "Mükemmel"
    CASE "B"
        PRINT "İyi"
    CASE ELSE
        PRINT "Geliştirilmeli"
END SELECT
```

- **GOTO**, **GOSUB**:

```basic
GOTO etiket
etiket:
PRINT "Buraya atlandı"
GOSUB altprogram
RETURN
altprogram:
PRINT "Alt program"
RETURN
```

#### 3. Giriş/Çıkış

- **PRINT**: Konsola çıktı verir.
- **INPUT**, **LINE INPUT**: Kullanıcı girişi alır.
- **WRITE**: Biçimlendirilmiş çıktı üretir.

Örnek:

```basic
DIM ad AS STRING
INPUT "Adınızı girin: ", ad
PRINT "Merhaba, "; ad
WRITE ad
```

#### 4. Dosya İşlemleri

- **OPEN**, **WRITE #**, **CLOSE**:

```basic
OPEN "cikti.txt" FOR OUTPUT AS #1
WRITE #1, "Merhaba, Dünya!"
CLOSE #1
```

- **SEEK**, **GET #**, **PUT #**:

```basic
OPEN "veri.bin" FOR BINARY AS #1
PUT #1, 1, "Test"
GET #1, 1, veri
PRINT veri
CLOSE #1
```

#### 5. Veritabanı İşlemleri

- **OPEN...FOR ISAM**, **SELECT**:

```basic
OPEN "veritabani.db" FOR ISAM AS #1
DEFINE TABLE kullanicilar (ad AS STRING, yas AS INTEGER)
PUT #1, AUTOKEY, "Ali, 30"
SELECT ad, yas FROM kullanicilar INTO sonuc
PRINT sonuc
CLOSE #1
```

#### 6. Veri Bilimi

- **ARRAY** ve **DATAFRAME** işlemleri:

```basic
DIM sayilar AS ARRAY
sayilar = ARANGE(1, 10)
PRINT "Ortalama: "; MEAN(sayilar)
DIM df AS DATAFRAME
df = DATAFRAME({"A": ARANGE(1, 5), "B": ARANGE(5, 9)})
PRINT DESCRIBE(df)
```

#### 7. Modüler Programlama

- **IMPORT**, **SUB**, **FUNCTION**:

```basic
IMPORT "matematik.libX" AS Mat
FUNCTION Kare(n)
    Kare = n * n
END FUNCTION
PRINT Mat.Kare(5)  ' Çıktı: 25
```

#### 8. Hata Ayıklama

- **DEBUG ON**, **TRACE ON**:

```basic
DEBUG ON
TRACE ON
DIM x AS INTEGER
x = 10
PRINT x
DEBUG OFF
```

#### 9. Nesne Yönelimli Programlama

- **CLASS**, **DESCRIBE**:

```basic
CLASS Kisi
    DIM ad AS STRING
    SUB MerhabaDe
        PRINT "Merhaba, "; ad
    END SUB
END CLASS
DIM k AS Kisi
k.ad = "Veli"
CALL k.MerhabaDe
DESCRIBE Kisi
```

#### 10. Web Kazıma ve PDF İşleme

- **Web Kazıma**:

```basic
DIM html AS STRING
html = WEB_GET("https://ornek.com")
PRINT SCRAPE_TEXT(html)
```

- **PDF İşleme**:

```basic
DIM metin AS STRING
metin = PDF_READ_TEXT("belge.pdf")
PRINT metin
```

### PDSX ile Program Yazma

1. **Dosya Oluşturma**: Programınızı `.basX` uzantısıyla kaydedin (örn. `merhaba.basX`).
2. **Örnek Program**:

```basic
REM Merhaba Dünya ve Veri Analizi
DIM ad AS STRING
INPUT "Adınızı girin: ", ad
PRINT "Merhaba, "; ad

DIM sayilar AS ARRAY
sayilar = LINSPACE(0, 10, 5)
PRINT "Ortalama: "; MEAN(sayilar)

OPEN "sonuclar.txt" FOR OUTPUT AS #1
WRITE #1, "Ortalama: "; MEAN(sayilar)
CLOSE #1
```

3. **Programı Çalıştırma**:

```bash
python pdsXInterpreter.py merhaba.basX
```

### Zotero Entegrasyonu (Önceki Taleplerden)

Önceki konuşmalarınızda Zotero kütüphanelerinden PDF işleme ve veri çıkarma üzerine çalıştığınızı belirtmiştiniz. PDSX, bu tür görevler için idealdir. Örneğin:

```basic
DIM pdf_metin AS STRING
pdf_metin = PDF_READ_TEXT("C:\Users\Kullanici\Zotero\storage\belge.pdf")
DIM kelimeler AS LIST
kelimeler = TXT_ANALYZE("C:\Users\Kullanici\Zotero\storage\belge.txt")
PRINT kelimeler
```

Bu, Zotero’daki PDF’lerden metin çıkarmanızı ve analiz yapmanızı sağlar. Gelecekte Zotero API entegrasyonu için `ZOTERO_GET(library_id, item_id)` gibi bir fonksiyon eklenebilir.

### En İyi Uygulamalar

1. **Açıklayıcı Değişken İsimleri**: `kullanici_adi` gibi anlamlı isimler kullanın.
2. **Kod Modülerleştirme**: `SUB`, `FUNCTION` ve `IMPORT` ile kodu düzenleyin.
3. **Hata Yönetimi**: `ON ERROR GOTO` ile sağlam hata işleme.
4. **Yorum Kullanımı**: Karmaşık mantığı `REM` ile belgeleyin.
5. **Artımlı Test**: REPL’de küçük kod parçalarını test edin.

### Sorun Giderme

- **Sözdizimi Hataları**: Eksik anahtar kelimeler (`END IF`, `NEXT`) veya yanlış noktalama işaretlerini kontrol edin.
- **Dosya Bulunamadı**: `OPEN` veya `IMPORT` yollarının doğruluğunu doğrulayın.
- **Tanımlanmamış Değişkenler**: Kullanmadan önce `DIM` ile tanımlayın.
- **Hata Kayıtları**: Ayrıntılı hata mesajları için `interpreter_errors.log` dosyasını kontrol edin.

### Gelişmiş Özellikler

1. **Sınıflar**:

```basic
CLASS Kisi
    DIM ad AS STRING
    SUB MerhabaDe
        PRINT "Merhaba, "; ad
    END SUB
END CLASS
DIM k AS Kisi
k.ad = "Ayşe"
CALL k.MerhabaDe
```

2. **Web Kazıma** (TÜİK, FAO, TradeMap için)\*\*: Önceki taleplerinizde TÜİK ve FAO gibi istatistik sitelerinden veri kazımak istediğinizi belirtmiştiniz. Örneğin:

```basic
DIM veri AS STRING
veri = WEB_GET("https://data.tuik.gov.tr")
PRINT SCRAPE_TEXT(veri)
```

3. **PDF İşleme**:

```basic
DIM tablolar AS LIST
tablolar = PDF_EXTRACT_TABLES("rapor.pdf")
PRINT tablolar
```

### Kaynaklar

- **Kaynak Kod**: `pdsXInterpreter.py` ana referanstır.
- **Hata Kayıtları**: Hata ayıklama için `interpreter_errors.log`.
- **Topluluk**: `.basX` ve `.libX` dosyalarını diğer PDSX kullanıcılarıyla paylaşın.

---

PDSX programlama dili, veritabanı işlemlerini desteklemek için güçlü bir altyapı sunar ve özellikle SQLite tabanlı ISAM (Indexed Sequential Access Method) veritabanı işlemlerine odaklanır. `pdsXInterpreter` sınıfı, veritabanı komutlarını işlemek için `execute_command` yöntemi ve SQLite entegrasyonu kullanır. Bu, PDSX’in hem basit hem de karmaşık veritabanı işlemlerini (örneğin, tablo oluşturma, veri ekleme, sorgulama ve işlem yönetimi) gerçekleştirebileceği anlamına gelir. Aşağıda, PDSX’in veritabanı komutları, sözdizimi, kullanım örnekleri, sınırlamalar ve öneriler detaylı bir şekilde Türkçe olarak açıklanacaktır. Ayrıca, önceki konuşmalarınızdaki Zotero entegrasyonu, veri bilimi ve web kazıma (örneğin, TÜİK, FAO, TradeMap) taleplerinizi dikkate alarak, veritabanı işlemlerinin bu bağlamlarda nasıl kullanılabileceğini de entegre edeceğim.

---

## PDSX’te Veritabanı Komutları

PDSX, SQLite tabanlı bir veritabanı sistemi kullanarak ilişkisel veritabanı işlemlerini destekler. Veritabanı işlemleri, `OPEN...FOR ISAM` ile başlatılır ve SQL benzeri komutlarla devam eder. PDSX’in veritabanı komutları, GW-BASIC/QBASIC’in dosya tabanlı veri yönetimi ruhunu korurken, modern SQL özelliklerini entegre eder. Aşağıda, tüm veritabanı komutları kategorilere ayrılarak detaylandırılmıştır.

### 1. Veritabanı Bağlantısı ve Yönetimi

#### **OPEN...FOR ISAM**
- **Açıklama**: Bir SQLite veritabanına bağlanmak için kullanılır. Yeni bir veritabanı oluşturabilir veya mevcut bir veritabanını açar.
- **Sözdizimi**:
  ```basic
  OPEN "veritabani_adi.db" FOR ISAM AS #dosya_numarasi
  ```
- **Parametreler**:
  - `veritabani_adi.db`: Veritabanı dosyasının adı veya yolu.
  - `dosya_numarasi`: Dosya tanıtıcısı (örneğin, `#1`).
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  PRINT "Veritabanı açıldı"
  ```

#### **CLOSE**
- **Açıklama**: Veritabanı bağlantısını kapatır.
- **Sözdizimi**:
  ```basic
  CLOSE #dosya_numarasi
  ```
- **Örnek**:
  ```basic
  CLOSE #1
  PRINT "Veritabanı kapatıldı"
  ```

### 2. Tablo ve Yapı Yönetimi

#### **DEFINE TABLE**
- **Açıklama**: Yeni bir tablo oluşturur ve sütun tanımlarını belirtir.
- **Sözdizimi**:
  ```basic
  DEFINE TABLE tablo_adi (sütun_adi AS veri_türü [, sütun_adi AS veri_türü...])
  ```
- **Desteklenen Veri Türleri**: `STRING`, `INTEGER`, `LONG`, `SINGLE`, `DOUBLE`, `BYTE`, `SHORT`, `CHAR`.
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  DEFINE TABLE kullanicilar (ad AS STRING, yas AS INTEGER, bakiye AS DOUBLE)
  CLOSE #1
  ```
- **Not**: Birincil anahtar (primary key) açıkça belirtilmezse, SQLite otomatik olarak bir `ROWID` oluşturur.

#### **ALTER TABLE**
- **Açıklama**: Mevcut bir tablonun yapısını değiştirir (örneğin, sütun ekleme veya silme).
- **Sözdizimi**:
  ```basic
  ALTER TABLE tablo_adi ADD sütun_adi veri_türü
  ALTER TABLE tablo_adi DROP COLUMN sütun_adi
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  ALTER TABLE kullanicilar ADD email AS STRING
  CLOSE #1
  ```

#### **DROP TABLE**
- **Açıklama**: Bir tabloyu veritabanından siler.
- **Sözdizimi**:
  ```basic
  DROP TABLE tablo_adi
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  DROP TABLE kullanicilar
  CLOSE #1
  ```

#### **TRUNCATE TABLE**
- **Açıklama**: Bir tablodaki tüm verileri siler, ancak tablo yapısını korur.
- **Sözdizimi**:
  ```basic
  TRUNCATE TABLE tablo_adi
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  TRUNCATE TABLE kullanicilar
  CLOSE #1
  ```

#### **CREATE VIEW**
- **Açıklama**: Bir sanal tablo (görünüm) oluşturur; bu, bir sorgunun sonucunu tablo gibi temsil eder.
- **Sözdizimi**:
  ```basic
  CREATE VIEW görünüm_adi AS SELECT ifade
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  CREATE VIEW yetiskinler AS SELECT ad, yas FROM kullanicilar WHERE yas >= 18
  CLOSE #1
  ```

#### **INDEX**
- **Açıklama**: Bir sütun üzerinde indeks oluşturur veya siler, sorgu performansını artırır.
- **Sözdizimi**:
  ```basic
  INDEX tablo_adi ON sütun_adi
  DROP INDEX tablo_adi_sütun_adi
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  INDEX kullanicilar ON ad
  CLOSE #1
  ```

### 3. Veri Manipülasyonu

#### **PUT**
- **Açıklama**: Bir tabloya yeni bir kayıt ekler veya mevcut bir kaydı günceller.
- **Sözdizimi**:
  ```basic
  PUT #dosya_numarasi, anahtar, veri
  ```
- **Parametreler**:
  - `anahtar`: Kayıt için birincil anahtar veya `AUTOKEY` (otomatik artan anahtar).
  - `veri`: Sütun değerleri, virgülle ayrılmış (örneğin, `"Ali, 30, 1000.50"`).
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  PUT #1, AUTOKEY, "Ali, 30, 1000.50"
  CLOSE #1
  ```

#### **GET**
- **Açıklama**: Bir tablodan kayıtları alır ve bir değişkene atar.
- **Sözdizimi**:
  ```basic
  GET #dosya_numarasi, anahtar, degisken
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  DIM veri AS STRING
  GET #1, 1, veri
  PRINT veri  ' Çıktı: Ali, 30, 1000.50
  CLOSE #1
  ```

#### **DELETE**
- **Açıklama**: Bir tablodan belirli bir kaydı siler.
- **Sözdizimi**:
  ```basic
  DELETE #dosya_numarasi, anahtar
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  DELETE #1, 1
  CLOSE #1
  ```

#### **UPDATE**
- **Açıklama**: Bir tablodaki kayıtları günceller, SQL benzeri bir sözdizimi kullanır.
- **Sözdizimi**:
  ```basic
  UPDATE tablo_adi SET sütun_adi = deger [WHERE koşul]
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  UPDATE kullanicilar SET bakiye = bakiye + 500 WHERE yas >= 18
  CLOSE #1
  ```

### 4. Veri Sorgulama

#### **SELECT**
- **Açıklama**: Bir tablodan veya birden fazla tablodan veri sorgular, SQL benzeri bir sözdizimi kullanır.
- **Sözdizimi**:
  ```basic
  SELECT sütun_listesi FROM tablo_adi [WHERE koşul] [JOIN tablo2 ON koşul] [INTO degisken]
  ```
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  DIM sonuc AS ARRAY
  SELECT ad, yas FROM kullanicilar WHERE yas >= 18 INTO sonuc
  PRINT sonuc
  CLOSE #1
  ```

#### **JOIN**
- **Açıklama**: Birden fazla tabloyu birleştirerek sorgulama yapar.
- **Sözdizimi**: `SELECT` içinde kullanılır.
- **Desteklenen Türler**: `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`.
- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  DEFINE TABLE siparisler (kullanici_id AS INTEGER, urun AS STRING)
  DIM sonuc AS ARRAY
  SELECT k.ad, s.urun FROM kullanicilar k INNER JOIN siparisler s ON k.ROWID = s.kullanici_id INTO sonuc
  PRINT sonuc
  CLOSE #1
  ```

### 5. İşlem (Transaction) Yönetimi

#### **BEGIN TRANSACTION**
- **Açıklama**: Bir işlem başlatır; değişiklikler yalnızca `COMMIT` ile kaydedilir.
- **Sözdizimi**:
  ```basic
  BEGIN TRANSACTION
  ```

#### **COMMIT**
- **Açıklama**: İşlemdeki değişiklikleri kalıcı hale getirir.
- **Sözdizimi**:
  ```basic
  COMMIT
  ```

#### **ROLLBACK**
- **Açıklama**: İşlemdeki değişiklikleri geri alır.
- **Sözdizimi**:
  ```basic
  ROLLBACK
  ```

- **Örnek**:
  ```basic
  OPEN "mydb.db" FOR ISAM AS #1
  BEGIN TRANSACTION
  PUT #1, AUTOKEY, "Veli, 25, 2000.75"
  UPDATE kullanicilar SET bakiye = bakiye + 100 WHERE ad = "Veli"
  ROLLBACK  ' Değişiklikleri geri al
  CLOSE #1
  ```

### 6. Hata Yönetimi

PDSX, veritabanı işlemlerinde hata yönetimi için `ON ERROR GOTO` mekanizmasını kullanır. Hatalar `interpreter_errors.log` dosyasına kaydedilir.

- **Örnek**:
  ```basic
  ON ERROR GOTO hata_yonet
  OPEN "mydb.db" FOR ISAM AS #1
  PUT #1, AUTOKEY, "Ali, 30, 1000.50"
  CLOSE #1
  GOTO son
  hata_yonet:
  PRINT "Hata oluştu!"
  RESUME NEXT
  son:
  ```

### 7. Zotero ve Veri Bilimi Entegrasyonu

Önceki konuşmalarınızda Zotero kütüphanelerinden PDF verilerini işleme (örneğin, `C:\Users\mete\Zotero\zotasistan\zapata_m6h`) ve TÜİK, FAO, TradeMap gibi istatistik sitelerinden veri kazıma talepleriniz vardı. PDSX’in veritabanı komutları, bu verileri organize etmek ve analiz etmek için kullanılabilir.

#### **Zotero Verilerini Veritabanına Kaydetme**
Zotero’dan çıkarılan PDF tablo verilerini bir veritabanına kaydetmek için:

```basic
OPEN "zotero_veri.db" FOR ISAM AS #1
DEFINE TABLE belgeler (belge_id AS INTEGER, baslik AS STRING, veri AS STRING)

DIM tablolar AS LIST
tablolar = PDF_EXTRACT_TABLES("C:\Zotero\storage\rapor.pdf")
DIM i AS INTEGER
FOR i = 1 TO LEN(tablolar)
    PUT #1, AUTOKEY, STR$(i) + ", Rapor Tablosu " + STR$(i) + ", " + STR$(tablolar[i])
NEXT

SELECT baslik, veri FROM belgeler INTO sonuc
PRINT sonuc
CLOSE #1
```

#### **TÜİK/FAO Verilerini Veritabanına Kaydetme**
Web kazıma ile toplanan verileri veritabanına kaydetmek için:

```basic
OPEN "istatistik.db" FOR ISAM AS #1
DEFINE TABLE ekonomik_veri (tarih AS STRING, ulke AS STRING, deger AS DOUBLE)

DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM veriler AS LIST
veriler = SCRAPE_TABLES(html)  ' Varsayımsal fonksiyon
DIM i AS INTEGER
FOR i = 1 TO LEN(veriler)
    PUT #1, AUTOKEY, veriler[i]
NEXT

SELECT tarih, deger FROM ekonomik_veri WHERE ulke = "Türkiye" INTO sonuc
PRINT sonuc
CLOSE #1
```

### 8. Örnek: Kapsamlı Veritabanı Uygulaması

Aşağıdaki program, Zotero’dan veri çıkarma, web kazıma ve veritabanı işlemlerini birleştirir:

```basic
REM Zotero ve Web Verilerini Veritabanına Kaydet
OPEN "analiz.db" FOR ISAM AS #1
DEFINE TABLE analiz_verileri (kaynak AS STRING, kategori AS STRING, deger AS DOUBLE)

REM Zotero’dan PDF verisi
DIM pdf_tablolar AS LIST
pdf_tablolar = PDF_EXTRACT_TABLES("C:\Zotero\storage\rapor.pdf")
DIM i AS INTEGER
FOR i = 1 TO LEN(pdf_tablolar)
    PUT #1, AUTOKEY, "Zotero, Tablo " + STR$(i) + ", " + STR$(MEAN(ARRAY(pdf_tablolar[i])))
NEXT

REM TÜİK’ten veri
DIM html AS STRING
html = WEB_GET("https://data.tuik.gov.tr")
DIM veriler AS LIST
veriler = SCRAPE_TABLES(html)
FOR i = 1 TO LEN(veriler)
    PUT #1, AUTOKEY, "TÜİK, Ekonomi, " + STR$(veriler[i])
NEXT

REM Sorgulama
DIM sonuc AS ARRAY
SELECT kategori, AVG(deger) FROM analiz_verileri GROUP BY kategori INTO sonuc
PRINT "Kategorilere Göre Ortalama Değerler:"
PRINT sonuc

REM Sonuçları kaydet
OPEN "sonuclar.txt" FOR OUTPUT AS #2
WRITE #2, sonuc
CLOSE #2
CLOSE #1
```

**Çıktı (Varsayımsal)**:
```
Kategorilere Göre Ortalama Değerler:
[["Tablo 1", 50.5], ["Tablo 2", 75.2], ["Ekonomi", 1234.56]]
```

### 9. Sınırlamalar

1. **Sınırlı Veritabanı Türleri**: Yalnızca SQLite tabanlı ISAM desteklenir; MySQL, PostgreSQL gibi diğer veritabanları için entegrasyon yoktur.
2. **SQL Özellikleri**: Gelişmiş SQL özellikleri (örneğin, alt sorgular, karmaşık birleşimler) sınırlıdır.
3. **Performans**: Büyük veri kümelerinde SQLite’ın performans sınırları nedeniyle yavaşlama olabilir.
4. **Hata Mesajları**: Veritabanı hataları (örneğin, yanlış SQL sözdizimi) kullanıcı dostu olmayabilir.
5. **Eşzamanlı Erişim**: Çok kullanıcılı senaryolar için sınırlı destek; `LOCK` ve `UNLOCK` basit düzeydedir.

### 10. Öneriler ve İyileştirmeler

1. **Çoklu Veritabanı Desteği**:
   - MySQL veya PostgreSQL için bağlayıcılar eklenebilir:
     ```python
     import mysql.connector
     self.db_connectors["MYSQL"] = mysql.connector.connect
     ```

2. **Gelişmiş SQL Desteği**:
   - Alt sorgular ve karmaşık birleşimler için SQLite’ın yetenekleri genişletilebilir veya SQLAlchemy gibi bir ORM entegre edilebilir.

3. **Performans Optimizasyonu**:
   - Büyük veri kümeleri için veritabanı sorguları önbelleklenebilir.
   - SQLite yerine daha hızlı bir veritabanı motoru (örneğin, DuckDB) kullanılabilir.

4. **Kullanıcı Dostu Hata Mesajları**:
   - Veritabanı hataları için özelleştirilmiş mesajlar üretilebilir:
     ```python
     try:
         cursor.execute(sql)
     except sqlite3.Error as e:
         raise Exception(f"Veritabanı Hatası: {str(e)}")
     ```

5. **Zotero ve Web Kazıma için Özel Komutlar**:
   - Zotero’dan veri çıkarmak için `ZOTERO_IMPORT(library_id, item_id)` komutu eklenebilir.
   - Web kazıma için `WEB_TABLE_TO_DB(url, table_id)` gibi bir komut geliştirilebilir.

### 11. Sonuç ve Gelecek Adımlar

PDSX, SQLite tabanlı veritabanı işlemleri için kapsamlı bir komut seti sunar ve Zotero, veri bilimi ve web kazıma gibi alanlarda güçlü bir şekilde kullanılabilir. Ancak, çoklu veritabanı desteği, gelişmiş SQL özellikleri ve performans optimizasyonları eklenirse daha etkili hale gelebilir.

**Sorular ve Öneriler**:

Geri bildiriminize göre, PDSX kodunu özelleştirebilir veya daha fazla örnek sağlayabilirim! (zmetedinler@gmail.com)

Bu kılavuz, PDSX ile programlama için sağlam bir temel sunar. Daha fazla bilgi için REPL’de deney yapın veya yorumlayıcıyı yeni komutlarla genişletin.

