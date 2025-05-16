pdsX yorumlayıcısında `CLASS` yapısı, QuickBASIC PDS'nin yeteneklerini genişleterek nesne yönelimli programlama (OOP) kavramlarını sunar. QuickBASIC PDS'de sınıflar için yerel destek bulunmazken, pdsX, modern dillerden (örneğin Python) ilham alarak `CLASS` yapısını ekler. Bu, kullanıcıların veri (nitelikler) ve davranışları (yöntemler) birleştiren yeniden kullanılabilir veri yapıları tanımlamasına olanak tanır. Bu özellik, BASIC'in yordamsal doğasıyla modern programlama paradigmaları arasında köprü kurarak modüler ve bakımı kolay kod yazımını mümkün kılar. Aşağıda, pdsX'te sınıfların nasıl oluşturulacağını ve kullanılacağını, özelliklerini detaylı bir şekilde açıklayacağım ve Türkçe örnekler vereceğim. Açıklamalar, pdsX yorumlayıcısının mevcut koduna ve daha önce belirttiğiniz geliştirme planına dayanmaktadır.

---

### `CLASS` Yapısına Genel Bakış
- **Amaç**: `CLASS`, veri (nitelikler) ve davranışları (yöntemler) birleştiren nesneler için bir şablon tanımlar. Kapsülleme, temel yöntem tanımları ve sınırlı kalıtım ile çok biçimlilik destekler.
- **Sözdizimi**: Sınıf, `CLASS ... END CLASS` yapısıyla tanımlanır. Nitelikler, değişken tanımlarıyla (örneğin `DIM`) ve yöntemler, `SUB` veya `FUNCTION` ile belirtilir.
- **Kapsam**: Sınıf nitelik ve yöntemleri sınıf içinde erişilebilirdir. Yöntemler, sınıfın iç durumunu (nitelikleri) değiştirebilir. Dış kod, sınıf örnekleriyle nesne referansları aracılığıyla etkileşime girer.
- **Mevcut Sınırlamalar**: Daha önce tartıştığımız üzere, pdsX şu anda temel sınıf işlevselliğini (nitelik ve yöntem tanımları) destekler. Gelişmiş özellikler (örneğin tam kalıtım, özel yöntemler, yöntem aşırı yükleme) planlanmış ancak henüz tam uygulanmamıştır.

---

### Sınıf Tanımlama
Bir sınıf, aşağıdaki yapıyla tanımlanır:

```vb
CLASS SınıfAdı
    [Nitelik Tanımlamaları]
    [Yöntem Tanımlamaları]
END CLASS
```

- **Nitelik Tanımlamaları**: Sınıf içinde örnek değişkenleri (nitelikler) tanımlamak için `DIM` kullanılır. Bunlar genellikle bir veri türüyle (örneğin `INTEGER`, `STRING`, `LIST`) tanımlanır.
- **Yöntem Tanımlamaları**: Değer döndürmeyen yordamlar için `SUB`, değer döndüren yöntemler için `FUNCTION` kullanılır. Yöntemler, sınıfın niteliklerine erişebilir ve bunları değiştirebilir.
- **Örnek Oluşturma**: Sınıfın bir örneği, `DIM değişken AS SınıfAdı` ile oluşturulur.

---

### Desteklenen Özellikler
pdsX yorumlayıcı koduna ve geliştirme planınıza göre desteklenen veya kısmen uygulanan özellikler şunlardır:

1. **Nitelikler**:
   - Sınıf içinde `DIM` ile tanımlanır.
   - Herhangi bir pdsX veri türünü kullanabilir (örneğin `INTEGER`, `STRING`, `LIST`, `DATAFRAME`, `TYPE`).
   - Her örnek için `_vars` adlı içsel bir sözlükte saklanır.

2. **Yöntemler**:
   - `SUB` veya `FUNCTION` ile tanımlanır.
   - Yöntemler, örtülü bir `self` referansı (yorumlayıcıda simüle edilir) aracılığıyla örnek niteliklerine erişir.
   - Şu anda yöntemler temel düzeydedir ve aşırı yükleme gibi gelişmiş özellikleri desteklemez.

3. **Örnek Oluşturma**:
   - Örnekler, `DIM değişken AS SınıfAdı` ile oluşturulur.
   - Her örnek, kendi nitelik kopyasını tutar.

4. **Temel Yöntem Çağrıları**:
   - Yöntemler, `CALL` ile veya doğrudan örnek üzerinden (örneğin `nesne.YöntemAdı`) çağrılır.
   - Yöntemler, örnek niteliklerini değiştirebilir veya hesaplama yapabilir.

5. **Planlanan Özellikler (Kısmi veya Gelecek)**:
   - **Kalıtım**: `CLASS Çocuk EXTENDS Ebeveyn` desteği planlanmış ancak tam uygulanmamış.
   - **Özel Yöntemler**: Yalnızca sınıf içinde erişilebilir `PRIVATE SUB` planlanmış.
   - **Statik Değişkenler**: Sınıf düzeyinde veri için `STATIC değişken AS tür` planlanmış.
   - **Yapıcı Yöntem**: Örnek başlatma için `SUB New` kısmen destekleniyor ancak tam sağlam değil.
   - **Yöntem Yeniden Tanımlama**: Alt sınıfların ebeveyn yöntemlerini yeniden tanımlaması planlanmış.

---

### Sınıf Oluşturma ve Kullanma Adımları
pdsX’te bir sınıfı tanımlamak ve kullanmak için şu adımları izleyin:

#### 1. Sınıfı Tanımla
Nitelikler ve yöntemler içeren bir sınıf tanımlamak için `CLASS` kullanın.

```vb
CLASS Sayac
    DIM Deger AS INTEGER
    SUB Artir
        Deger = Deger + 1
    END SUB
    FUNCTION DegerAl AS INTEGER
        DegerAl = Deger
    END FUNCTION
END CLASS
```

- **Nitelikler**: `Deger`, varsayılan olarak 0’a başlatılan bir tamsayı niteliğidir (`INTEGER` için varsayılan).
- **Yöntemler**:
  - `Artir`: `Deger`’i 1 artıran bir `SUB`.
  - `DegerAl`: Mevcut `Deger`’i döndüren bir `FUNCTION`.

#### 2. Sınıf Örneği Oluştur
Sınıfın bir örneğini `DIM` ile oluşturun.

```vb
DIM s AS Sayac
```

Bu, `Sayac` sınıfının `s` adında bir örneğini oluşturur ve kendi `Deger` niteliğine sahip olur.

#### 3. Niteliklere Eriş ve Yöntemleri Çağır
Örneğin niteliklerini değiştirin ve yöntemlerini çağırın.

```vb
s.Deger = 5        ' Deger'i 5 yap
CALL s.Artir       ' Deger'i 6'ya çıkar
PRINT s.DegerAl    ' Çıktı: 6
```

- **Nitelik Erişimi**: `nesne.Nitelik` sözdizimi kullanılır (örneğin `s.Deger`).
- **Yöntem Çağrıları**: `CALL nesne.Yöntem` veya `nesne.Yöntem` ile yöntemler çağrılır.

#### 4. Çoklu Örneklerle Örnek
Sınıflar, her biri bağımsız duruma sahip birden çok örneği destekler.

```vb
CLASS Kisi
    DIM Ad AS STRING
    DIM Yas AS INTEGER
    SUB BilgiAta(n AS STRING, a AS INTEGER)
        Ad = n
        Yas = a
    END SUB
    FUNCTION BilgiAl AS STRING
        BilgiAl = Ad + ", Yas: " + STR$(Yas)
    END FUNCTION
END CLASS

DIM k1 AS Kisi
DIM k2 AS Kisi

CALL k1.BilgiAta("Ali", 30)
CALL k2.BilgiAta("Ayşe", 25)

PRINT k1.BilgiAl   ' Çıktı: Ali, Yas: 30
PRINT k2.BilgiAl   ' Çıktı: Ayşe, Yas: 25
```

---

### Özellikler ve Karakteristikler
pdsX yorumlayıcı implementasyonuna ve belirttiğiniz özelliklere göre, sınıfların temel özellikleri şunlardır:

1. **Kapsülleme**:
   - Nitelikler ve yöntemler sınıf içinde birleştirilir.
   - Nitelikler, her örnek için `_vars` sözlüğünde saklanır ve örneğe özeldir.
   - Örnek: `Sayac` sınıfında `Deger`, her örneğe özgüdür.

2. **Örnek Yöntemleri**:
   - Yöntemler (`SUB` veya `FUNCTION`), örnek verileri üzerinde çalışır.
   - Yorumlayıcı, yöntemlerin örnek niteliklerine erişmesi için örtülü bir `self` referansı simüle eder.
   - Örnek: `Artir`, örneğin `Deger` niteliğini değiştirir.

3. **Veri Türü Desteği**:
   - Nitelikler, tüm pdsX veri türlerini kullanabilir:
     - Temel türler: `INTEGER`, `STRING`, `DOUBLE`, `BYTE`, `SHORT`, `CHAR`, vb.
     - Python türleri: `LIST`, `DICT`, `SET`, `TUPLE`.
     - Gelişmiş türler: `ARRAY` (NumPy), `DATAFRAME` (Pandas), `TYPE`, `STRUCT`, vb.
   - Örnek: Bir sınıf, dinamik veri depolamak için `LIST` niteliği kullanabilir.

4. **Örnek Oluşturma ve Bellek**:
   - Her örnek, `DIM ... AS SınıfAdı` ile oluşturulan benzersiz bir nesnedir.
   - Yorumlayıcı, nitelikler için `_vars` sözlüğünde bellek ayırır.
   - Örnek: `Kisi` örneğinde `k1` ve `k2`, ayrı `Ad` ve `Yas` niteliklerine sahiptir.

5. **Yöntem Yürütmesi**:
   - Yöntemler, sınıf tanımında saklanır ve çağrıldığında yürütülür.
   - Yorumlayıcı, yöntem çağrılarını `class_methods` sözlüğündeki Python lambda fonksiyonlarına eşler.
   - Örnek: `CALL s.Artir`, `Artir` lambdasını çalıştırır ve `Deger`’i günceller.

6. **Hata İşleme**:
   - Geçersiz yöntem çağrıları veya tanımlanmamış nitelikler, PDSX hataları üretir (örneğin `Tanımlanmamış değişken: değişken`).
   - `ON ERROR GOTO` mekanizması, sınıf ilgili hataları yönetebilir.
   - Örnek: `s.Bilinmeyen` erişimi hata tetikler.

7. **Genişletilebilirlik**:
   - Sınıflar, modern veri bilimi özellikleriyle entegre olabilir (örneğin Pandas işlemleri için `DATAFRAME` nitelikleri).
   - Kalıtım ve statik değişkenler gibi planlanan özellikler modülerliği artıracak.
   - Örnek: Bir sınıf, bir `DATAFRAME` saklayabilir ve onu filtrelemek veya sıralamak için yöntemler içerebilir.

---

### Gelişmiş Örnek
pdsX’in modern özelliklerini entegre eden daha karmaşık bir örnek, örneğin `DATAFRAME` niteliği ve veritabanı etkileşimi:

```vb
CLASS VeriAnalizci
    DIM Veri AS DATAFRAME
    DIM Ad AS STRING
    SUB VeritabanindanYukle(dbNum AS INTEGER, tablo AS STRING)
        SELECT * FROM tablo INTO Veri
    END SUB
    SUB VeriFiltrele(kosul AS STRING)
        Veri = FILTER(Veri, kosul)
    END SUB
    FUNCTION OzetAl AS STRING
        OzetAl = Ad + ": " + STR$(DESCRIBE(Veri))
    END FUNCTION
END CLASS

DIM analizci AS VeriAnalizci
analizci.Ad = "SatisAnalizi"
OPEN "veri.db" FOR ISAM AS #1
CALL analizci.VeritabanindanYukle(1, "Satis")
CALL analizci.VeriFiltrele("Gelir > 1000")
PRINT analizci.OzetAl
CLOSE #1
```

- **Açıklama**:
  - `VeriAnalizci` sınıfı, bir `DATAFRAME` niteliği (`Veri`) ve bir `STRING` niteliği (`Ad`) içerir.
  - `VeritabanindanYukle`, bir veritabanından `SELECT` komutuyla `Veri`’yi doldurur.
  - `VeriFiltrele`, `Veri`’ye Pandas filtresi uygular.
  - `OzetAl`, `DESCRIBE` fonksiyonunu kullanarak bir özet döndürür.
  - Program, bir örnek oluşturur, veriyi yükler, filtreler ve bir özet yazdırır.

---

### Sınırlamalar ve Gelecekteki İyileştirmeler
Önceki konuşmalarınıza ve yorumlayıcının mevcut durumuna dayanarak:
- **Mevcut Sınırlamalar**:
  - Kalıtım (`EXTENDS`) tam uygulanmadı, bu da sınıf hiyerarşilerini sınırlandırıyor.
  - Özel yöntemler ve statik değişkenler planlandı ancak henüz mevcut değil.
  - Yöntem aşırı yükleme (aynı isimle farklı parametrelerle yöntemler) desteklenmiyor.
  - Yapıcı yöntemler (`SUB New`) temel düzeyde ve sağlam başlatma mantığı eksik.
- **Planlanan İyileştirmeler** (geliştirme planınızdan):
  - **Kalıtım**: `CLASS Çocuk EXTENDS Ebeveyn` ile alt sınıfların nitelik ve yöntemleri miras alması.
  - **Özel Yöntemler**: Yalnızca sınıf içinde erişilebilir `PRIVATE SUB`.
  - **Statik Değişkenler**: Sınıf düzeyinde veri için `STATIC değişken AS tür`.
  - **Yöntem Yeniden Tanımlama**: Alt sınıfların ebeveyn yöntemlerini yeniden tanımlaması.
  - **Yapıcı/Yıkıcı**: Başlatma ve temizleme için `SUB New` ve `SUB Destroy`.
  - **Meta Veri İnceleme**: Nitelik ve yöntemleri listelemek için `DESCRIBE SınıfAdı`.

---

### Sınıflarda Hata İşleme
Sınıflar, yorumlayıcının hata işleme sistemi tarafından yönetilen PDSX hatalarını tetikleyebilir. Yaygın hatalar şunlardır:

| **Hata** | **Neden** | **Çözüm** |
|-----------|-----------|--------------|
| `Tanımlanmamış değişken` | Tanımlanmamış bir niteliğe erişim (örneğin `s.Bilinmeyen`). | Niteliğin sınıf tanımında olduğundan emin olun. |
| `Bilinmeyen komut` | Var olmayan bir yöntemin çağrılması (örneğin `CALL s.BilinmeyenYontem`). | Yöntemin sınıf tanımında olduğunu doğrulayın. |
| `Sözdizimi hatası` | Yanlış sınıf tanımı sözdizimi (örneğin `END CLASS` eksik). | Sınıf sözdizimini belgelenmiş formata göre kontrol edin. |

Bu hataları zarifçe yönetmek için `ON ERROR GOTO` kullanın:

```vb
ON ERROR GOTO HataYonetici
DIM s AS Sayac
s.Bilinmeyen = 5  ' Hata tetikler
END

HataYonetici:
PRINT "Hata: Tanımlanmamış değişken"
RESUME
```

---

### Önceki Bağlamla Entegrasyon
Önceki konuşmalarınızda, pdsX yorumlayıcısını modern özelliklerle güçlendirirken PDS uyumluluğunu koruma vurguladınız. `CLASS` implementasyonu bu hedefle uyumludur:
- Python’dan ilham alan nesne yönelimli programlamayı destekler (örneğin `LIST`, `DICT` gibi veri türleri için isteğiniz).
- Veri bilimi araçlarıyla entegredir (örneğin Pandas işlemleri için `DATAFRAME` nitelikleri).
- Geliştirme planınızda belirtilen kalıtım ve özel yöntemler gibi gelişmiş nesne yönelimli özelliklere yönelik planlama yapar.

Ayrıca, sağlam hata işleme ve dokümantasyon talebinizi de dikkate alarak, detaylı örnekler ve hata tabloları ekledim. Web kazıma talebinizden (15 Nisan 2025) farklı olarak, bu yanıt yalnızca pdsX yorumlayıcısına odaklanır ve grafik ile ses komutları açıkça hariç tutulmuştur.

---

### Sonuç
pdsX’teki `CLASS` yapısı, nesne yönelimli programlama ilkelerini kullanarak kodu düzenlemenin güçlü bir yolunu sunar ve BASIC’in sadeliğini modern programlama paradigmalarıyla birleştirir. Nitelik ve yöntemler tanımlayarak, kullanıcılar basit sayaçlardan karmaşık veri analizine kadar çeşitli görevler için modüler, yeniden kullanılabilir nesneler oluşturabilir. Bazı gelişmiş özellikler hala geliştirme aşamasında olsa da, mevcut implementasyon temel nesne yönelimli görevler için sağlamdır ve pdsX’in veri türleri, veritabanı işlemleri ve veri bilimi yetenekleriyle sorunsuz bir şekilde entegre olur. Daha fazla örnek veya belirli planlanmış özelliklere (örneğin kalıtım) öncelik vermek isterseniz, lütfen belirtin!