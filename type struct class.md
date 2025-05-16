### pdsX’te Kayıt‑ve‑Nesne Yapıları  
*(TYPE / STRUCT / UNION / ENUM / CLASS)*  

Aşağıdaki notlar, gönderdiğiniz **pdsXInterpreter** kaynağını satır satır inceleyerek çıkarılmıştır; gerçekten çalışan kısımlar, henüz tasarlanıp ama kodlanmamış yerler ve olası genişletme noktaları ayrı ayrı belirtilmiştir.

| Yapı | Dile giren anahtar sözcük(ler) | Yorumlayıcının yaptığı | Dilde nasıl kullanılır? | Olası kısıt / eksik |
|------|--------------------------------|------------------------|-------------------------|----------------------|
| **TYPE** | `TYPE … END TYPE` | 1. `parse_program` fonksiyonu satır okurken **`current_type`** moduna girer.<br>2. Her alan satırını `(?P<name>\w+)\s+AS\s+(?P<tip>\w+)` ile parse eder.<br>3. Bittiğinde **`collections.namedtuple`** ile Python tarafında tek seferlik bir kayıt sınıfı üretir ve `self.types` & `modules[…]` içine kaydeder. | ```basX<br>TYPE Person<br>  Name AS STRING<br>  Age  AS INTEGER<br>END TYPE<br><br>DIM p AS Person<br>p.Name = "Ada"<br>p.Age  = 32<br>PRINT p.Name, p.Age``` | - Alanlara nokta `.` erişimi **şimdilik yok** (namedtuple olduğu için `p.Name` değil `p[0]` döner).<br>- Atama kolaylığı için `DIM x AS Person` sonrası bir “wrapper” katmanı eklemek gerek. |
| **CLASS** | `CLASS … [EXTENDS Base] … END CLASS`<br>`SUB/FUNCTION`, `PRIVATE …`, `STATIC`, `DIM` | 1. Yorumlayıcı sınıf tanımını satır satır *toplar*.<br>2. Kapanışta **dinamik `type()`** ile gerçek Python sınıfı üretir.<br>   • Miras desteklenir (`EXTENDS`).<br>   • Özel (private) metodlar ayrı sözlükte tutulur.<br>   • Sınıf‐genel değişkenler `_static_vars`.<br>   • Örnek değişkenler `_vars`.<br>3. Nesne oluşturmak için **`DIM var AS ClassName`** kullanılır.<br>4. Metot çağrısı **`CALL var.Method(…)`** sentaksı ile yapılır (veya `PRIVATE` ise `var` içinden dolaylı). | ```basX<br>CLASS Counter<br>  DIM value AS INTEGER<br><br>  SUB Inc()<br>    LET value = value + 1<br>  END SUB<br><br>  FUNCTION Get()<br>    RETURN value<br>  END FUNCTION<br>END CLASS<br><br>DIM c AS Counter<br>CALL c.Inc()<br>PRINT CALL c.Get()``` | - `value` alanına doğrudan `c.value` diyerek erişim **desteklenmiyor**; yalnızca metot içinden `_vars` dolaylı kullanımı var.<br>- `STATIC` alanlar tanımlanabilir ama başlangıç değeri *tip tablosundan* gelen “boş” değer (0, "" …).<br>- Metot içinde `RETURN x` atamak yerine `LET RETURN = x` yazmanız gerekiyor. |
| **STRUCT / UNION / ENUM** | Anahtar kelimeler `STRUCT`, `UNION`, `ENUM` **yalnız type_table’de yer alıyor** ancak parser’da karşılığı yok. | - Yorumlayıcı bu blokları **tanımaz**; yazarsanız “Bilinmeyen komut” hatası verir.<br>- `type_table` girişleri, gelecekte Python tarafında `dict` / `typing.NamedTuple` / `enum.Enum` ile map’lenmek üzere placeholder olarak eklenmiş. | — (şimdilik kullanılamaz) | Eklenecekse:<br>• `STRUCT` → TYPE’a benzer fakat mutasyona izin veren `SimpleNamespace` ya da `dataclass`.<br>• `UNION` → aynı hafızayı paylaşma gerektirmediği için, Python’da `typing.Union` + `__annotations__` ile semantik kontrol.<br>• `ENUM` → `enum.Enum` alt sınıfı üretmek. |

---

#### Tip Sistemi ile Etkileşim  
`self.type_table` sözlüğü, **string → Python tip/başlatıcı** haritasıdır. Bu yüzden:

* `DIM x AS INTEGER` → `0`  
* `DIM y AS LIST`    → `[]`  
* Özel bir `CLASS` veya `TYPE` adı verilirse, önceden derlenmiş nesnelerden örnek üretilir.

Atama anında (`LET`, doğrudan `=` veya `INPUT`’tan gelen), yorumlayıcı **hiçbir statik tip denetimi yapmaz**. Soru‑cevaplarınızda dile getirdiğiniz “linter” bu boşluğu kapatmak üzere tasarlanmıştı.

---

### Hızlı Örnek – `TYPE` ve `CLASS` Birlikte

```basX
'--- kayıt tipi
TYPE Vec2
  X AS SINGLE
  Y AS SINGLE
END TYPE

'--- sınıf
CLASS Player
  DIM Pos AS Vec2          'örnek değişken
  STATIC Count AS INTEGER  'sınıf değişkeni

  SUB __init__()
    LET Pos = TYPE(Vec2, 0, 0)  'manuel kurulum gerekir
    LET Count = Count + 1
  END SUB

  SUB Move(dx, dy)
    LET Pos.X = Pos.X + dx
    LET Pos.Y = Pos.Y + dy
  END SUB
END CLASS

DIM p AS Player
CALL p.Move(3, 4)
```

> ⚠️ `TYPE(Vec2, …)` gibi bir yapıcı henüz yok; üstteki satır Python tarafındaki namedtuple’ı doğrudan çağırıyor (hata almamak için böyle “hack” gerekir).

---

## Eksik veya İyileştirilebilecek Noktalar

1. **Alan Erişimi**  
   `p.Name` veya `p.Pos.X` gibi noktalı sentaks yorumlayıcıda çözümlenmiyor.  
   *Çözüm:* `evaluate_expression` içinde `.` operatörü için özel regex bölmek ya da `__getattr__` proxy’si.

2. **ENUM/UNION/STRUCT**  
   Sadece anahtar kelime eklemek değil, parser akışında `current_struct`, `current_union`, `current_enum` benzeri durum makineleri gerekecek.

3. **Tip Güvenliği**  
   Çalışma anında “yanlış tipe atama” hatası yok; yalnızca çalışırken Python `TypeError` fırlarsa hata mesajına yansıyor.  
   *Çözüm:* linter adımında değişken tablosu tutup `LET`/`INPUT`/fonksiyon dönüş tiplerini kesiştirmek.

4. **Metot Söz Dizimi**  
   BASIC’e yakın “`p.Move 3,4`” veya “`CALL Move(p,3,4)`” türü çağrılar da desteklenebilir.

---

### Kısaca

* **TYPE**: Şu anda çalışan tek kayıt yapısı; namedtuple olarak derleniyor.  
* **CLASS**: Miras, statik/özel/örnek metod‑değişken ayrımı var; fakat alan erişimi sınırlı.  
* **STRUCT / UNION / ENUM**: Sadece planlandı. Yazarsanız yorumlayıcı hata verir.  

Bu temelin üzerine eklenmesi gerekenler net: alan erişim sentaksı, tip güvenliği, eksik veri yapılarının parse‑zinciri. İleride bu konularda kod örnekleriyle derinleştirebiliriz.