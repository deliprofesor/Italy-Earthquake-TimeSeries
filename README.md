# Italy Earthquake Time Series Analysis

<img width="976" height="487" alt="image" src="https://github.com/user-attachments/assets/cd074c6e-af7a-40fb-a777-3d7e6ad51c1c" />


## Proje Tanımı

Bu proje, 2016 Orta İtalya deprem serisinin ana şokunu takip eden artçı sarsıntı aktivitesinin yoğunluğunu ve zamanla azalma eğilimini modellemek için sismolojide temel bir yasa olan **Omori Yasası**'nı kullanır.

### Problem
Ana deprem sonrası artçı sarsıntıların yoğunluğunun zamanla azalması farklı bölgelerde farklı hızlarda gözlemlenebilir. Hangi modelin bu azalmayı en iyi tahmin ettiği ve bölgenin sismik karakteristiği model parametreleri aracılığıyla nasıl yorumlanabilir sorularına yanıt aranmıştır.

### Amaç
Artçı sarsıntıların yoğunluğunu ve zamanla azalma şeklini modelleyerek elde edilen $p$ (azalma hızı) ve $c$ (zaman kayması) parametrelerini hesaplamak ve bu parametrelerle deprem sonrası **risk yönetimi** ve **sismolojik tahminleri** desteklemek.

---

##  Veri Seti
- **Kaynak:** Kaggle / İtalya Deprem Verisi 2016  
- **İçerik:** Her satır bir deprem olayı, sütunlar:  
  - `Time`: Depremin zamanı (UTC)  
  - `Latitude`: Enlem  
  - `Longitude`: Boylam  
  - `Depth/Km`: Depremin derinliği  
  - `Magnitude`: Depremin büyüklüğü  
- **Boyut:** 2016-08-24 – 2016-11-30 arası toplam deprem sayısı ~ 100.  


## Metodoloji ve Analiz Özeti

### Veri Seti
* **Kaynak:** Kaggle / İtalya Deprem Verisi 2016
* **Kapsam:** 2016-08-24 – 2016-11-30 arası deprem olayları.
* **Ana Şok:** Veri setindeki en büyük deprem **M6.5 (2016-10-30)** olarak belirlenmiştir.
* **Filtreleme:** Analiz, artçı sarsıntı gürültüsünü azaltmak için sadece **M $\ge 2.0$** büyüklüğündeki olaylar üzerinde gerçekleştirilmiştir.

### Modelleme Yöntemi
1.  **Hassas Zaman Serisi Gruplaması:** Depremler, ana şokun yaşandığı andan itibaren başlayan eşit 24 saatlik periyotlara (günlük) gruplandırılmıştır (Pandas `resample` metodu ve `offset` ile).
2.  **Omori Yasası Fonksiyonu:** Modifiye Edilmiş Omori Yasası kullanılmıştır: $$\lambda(t) = \frac{K}{(t+c)^p}$$
3.  **Model Uydurma:** `scipy.optimize.curve_fit` (Doğrusal Olmayan En Küçük Kareler) kullanılarak $K$, $c$ ve $p$ parametreleri tahmin edilmiştir. Uyumun fiziksel olarak anlamlı olması için parametrelere sınırlar (`bounds`) tanımlanmıştır.
4.  **Uyum Değerlendirmesi:** Modelin başarısı $R^2$ (Belirlilik Katsayısı) metriği ile ölçülmüştür.

---

## Analiz Sonuçları ve Yorumlama

### Tahmin Edilen Omori Parametreleri

| Parametre | Değer | Birim | Yorum |
| :--- | :--- | :--- | :--- |
| **$R^2$ Skoru** | **0.9531** | Boyutsuz | Model, verideki varyansın %95'inden fazlasını açıklar. **Mükemmel Uyum.** |
| **$p$ (Azalma Hızı)** | **1.772** | Boyutsuz | **Çok Hızlı Azalma.** $p$ değerinin 1.0'dan anlamlı derecede büyük olması, artçı sarsıntı yoğunluğunun hızla düştüğünü gösterir. |
| **$c$ (Zaman Kayması)** | **8.75** | Gün | Teorik modelin başlangıcını kaydıran faktör. İlk günlerdeki karmaşık veya eksik veriyi telafi eder. |
| **$K$ (Aktivite Ölçeği)** | *Yüksek* | Sayı/Gün | Artçı sarsıntı aktivitesinin genel ölçeği. |

### Risk Yönetimi Çıkarımları

1.  **Hızlı Risk Düşüşü:** $p = 1.772$ değeri, Orta İtalya bölgesinin, ana şokun ardından gerilimi ve dolayısıyla artçı sarsıntı riskini hızla azalttığını göstermektedir. Bu, deprem sonrası risk değerlendirmelerinde kritik bir bilgidir.
2.  **Güvenilirlik:** Modelin yüksek $R^2$ başarısı, elde edilen Omori eğrisinin (grafikteki kırmızı çizgi) bölgenin davranışını güvenilir bir şekilde temsil ettiğini ve kısa vadeli risk tahminleri için kullanılabileceğini kanıtlar.

---

## Kullanım

Analizi yeniden çalıştırmak için:
1.  Gerekli kütüphaneleri yükleyin (`pandas`, `numpy`, `matplotlib`, `scipy`).
2.  `italy_omori_analysis.py` dosyasını çalıştırın.
3.  `italy_earthquakes_from_2016-08-24_to_2016-11-30.csv` dosyasının kodla aynı dizinde olduğundan emin olun.
