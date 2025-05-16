**PDSX Interpreter Programlama Dili Kullanım Kılavuzu**

---

## I. Giriş

**pdsX**, BASIC/QBasic/PDS 7.1 tarzından esinlenerek Python ile yazılmış, modern veri işleme, dosya, veritabanı ve web işlemleri destekleyen, satır bazlı bir programlama dili yorumlayıcısıdır. Geleneksel BASIC yapısını korurken, PDF içeriği okuma, SQLite kullanma, DataFrame analizi, web kazıma gibi modern beceriler sunar.

pdsX dosyaları `.basX` uzantısıyla yazılır ve `PDSX>` REPL ortamından ya da `pdsX dosya.basX` şeklinde çalıştırılabilir.

---

## II. Tüm Komutlar (Alfabetik Sıralı)

(Tablo korunmuştur.)

---

## VIII. Programlama El Kitabı (Örnekli)

(**İPTAL EDİLDİ**) – Bu bölüm kaldırıldı. Geliştirilmeyecek.

---

## IX. Syntax Kontrol Aracı (Linter/Ön Analiz Planı)

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
  - Ayrıca **aşağıdaki durumlar için de uyarı verilmelidir:**
    - Matematiksel işlemlerde `STRING` tipinin kullanımı.
    - `INPUT` ile girilen değerin tipi beklenenle uyumsuzsa uyarı.
    - `LET x = FUNC1()` çağrısında `FUNC1` fonksiyonunun döndürdüğü tip ile `x` tipi eşleşiyor mu?

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
  - Aritmetik işlemlerde uygun olmayan tür kullanımı tespit edilir (örn. `LET toplam = "abc" + 5`).
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
| 30   | Tip Uyumsuzluğu   | LET toplam = "abc" + 5 — string ile sayı toplama | Değişken tipini kontrol edin   |
| 40   | Tanımsız Fonksiyon| FUNC123() diye bir fonksiyon tanımsız          | Fonksiyon tanımını kontrol edin |

Linter sonunda uyarılar dosya olarak da `.lnt` uzantısıyla kaydedilebilir.

Kodlamaya geçmemi istersen hemen yazabilirim abi.
