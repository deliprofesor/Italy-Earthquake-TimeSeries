import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ----------------------------------------------------------------------
# 1. Veri Yükleme ve İlk İnceleme
# ----------------------------------------------------------------------

file_path = 'data/italy_earthquakes_from_2016-08-24_to_2016-11-30.csv'

try:
    # 'Time' sütununu yüklerken doğrudan datetime olarak okuma
    df = pd.read_csv(file_path, parse_dates=['Time'])
except FileNotFoundError:
    print(f"HATA: Dosya bulunamadı. Lütfen '{file_path}' dosyasının doğru yerde olduğundan emin olun.")
    exit()

# Sütun adlarını temizleme
df.columns = ['Time', 'Latitude', 'Longitude', 'Depth_Km', 'Magnitude']

print("--- 1. Veri Seti Bilgisi ---")
print(df.info())

# ----------------------------------------------------------------------
# 2. Veri Ön İşleme ve Ana Şok Belirleme
# ----------------------------------------------------------------------

# Ana Depremi (Main Shock) Belirleme: En yüksek büyüklüğe sahip deprem (M6.5)
main_shock_index = df['Magnitude'].idxmax()
main_shock = df.loc[main_shock_index]
main_shock_time = main_shock['Time']
main_shock_mag = main_shock['Magnitude']

print(f"\n--- 2. Ana Şok Bilgisi ---")
print(f"Ana Şok Zamanı: {main_shock_time} (UTC)")
print(f"Ana Şok Büyüklüğü: M{main_shock_mag}")

# Artçı Sarsıntıları Filtreleme ve Hazırlama (M >= 2.0 ve Ana Şoktan Sonra)
aftershocks_df = df[df.index != main_shock_index].copy()
aftershocks_df = aftershocks_df[aftershocks_df['Magnitude'] >= 2.0]
aftershocks_df = aftershocks_df[aftershocks_df['Time'] >= main_shock_time].copy()

# ----------------------------------------------------------------------
# 3. Hassas Zaman Serisi Gruplaması (Resampling) - Hata Düzeltildi
# ----------------------------------------------------------------------

aftershocks_df_indexed = aftershocks_df.set_index('Time')

# Gece yarısı (00:00:00) ve ana şok zamanı arasındaki farkı (timedelta) hesapla.
# Bu, resample için gerekli olan başlangıç kaymasıdır.
midnight = main_shock_time.normalize()
offset_timedelta = main_shock_time - midnight

# 'D' (Günlük) gruplamayı Timedelta offset ile ana şok anından başlat
daily_counts_resampled = aftershocks_df_indexed.resample('D', offset=offset_timedelta).size()

# Sayım verisini DataFrame'e dönüştür
daily_counts = daily_counts_resampled.reset_index(name='Count')
daily_counts.columns = ['Time', 'Count']

# Göreceli Zaman Hesaplama (Gün cinsinden)
daily_counts['Day'] = (daily_counts['Time'] - main_shock_time).dt.total_seconds() / (24 * 3600)

# t_obs değerleri [0, 1, 2, 3, ...] şeklindedir (Gün endeksi).
# Omori Yasası için t > 0 olmalıdır. En basit çözüm, gün sayısını 1'den başlatmaktır.
t_obs = daily_counts['Day'].values
t_obs = t_obs + 1.0 # t = [1.0, 2.0, 3.0, ...]
N_obs = daily_counts['Count'].values

# Sayım değeri sıfır olan günleri dışlama (Opsiyonel ama Omori için yaygın pratik)
valid_indices = N_obs > 0
t_obs = t_obs[valid_indices]
N_obs = N_obs[valid_indices]

print(f"\nGünlük Sayım Verisi Başlangıcı (t={t_obs[0]:.1f} gün): {N_obs[0]} artçı")

# ----------------------------------------------------------------------
# 4. Omori Yasası Modellemesi (İyileştirilmiş)
# ----------------------------------------------------------------------

# Modifiye Edilmiş Omori Yasası Fonksiyonu
def omori_law(t, K, c, p):
    """ Lambda(t) = K / (t + c)^p """
    return K / (t + c) ** p

# Başlangıç Değerleri (Initial Guess) ve Sınırlar (Bounds)
p0 = [1000.0, 1.0, 1.0] 
lower_bounds = [0.1, 0.0, 0.5]  
upper_bounds = [50000.0, 15.0, 3.0] 

# Model Uydurma
try:
    params, covariance = curve_fit(omori_law, t_obs, N_obs, p0=p0, 
                                   bounds=(lower_bounds, upper_bounds), 
                                   maxfev=10000) # Max iterasyon artırıldı
    K_fit, c_fit, p_fit = params
    
    # Model Uyum Metriği (R-kare) Hesaplama
    N_pred = omori_law(t_obs, K_fit, c_fit, p_fit)
    ss_total = np.sum((N_obs - np.mean(N_obs)) ** 2)
    ss_residual = np.sum((N_obs - N_pred) ** 2)
    R_squared = 1 - (ss_residual / ss_total)
    
    print("\n--- 4. Omori Yasası Parametre Tahminleri ---")
    print(f"Model Uyum (R^2 Skoru): {R_squared:.4f}")
    print(f"K (Aktivite Ölçeği): {K_fit:.2f}")
    print(f"c (Zaman Kayması): {c_fit:.2f} gün")
    print(f"p (Azalma Hızı): {p_fit:.3f}")
    
except Exception as e:
    print(f"\nUYARI: Omori Yasası model uyumu başarısız oldu: {e}")
    # Başarısızlık durumunda varsayılan değerleri kullan
    K_fit, c_fit, p_fit = p0
    R_squared = 0.0

# Tahmin edilen model eğrisini oluşturma
t_fit = np.linspace(min(t_obs), max(t_obs), 500)
N_fit = omori_law(t_fit, K_fit, c_fit, p_fit)

# ----------------------------------------------------------------------
# 5. Görselleştirme
# ----------------------------------------------------------------------

plt.figure(figsize=(12, 7))

# Gerçek Veriyi Çizme
plt.scatter(t_obs, N_obs, color='darkgray', marker='o', s=30, label='Gözlemlenen Günlük Artçı Sarsıntı Sayısı (M ≥ 2.0)')

# Omori Yasası Modelini Çizme
model_label = f'Uydurulan Omori Yasası\n' \
              r'$N(t) = \frac{%.0f}{(t + %.2f)^{%.3f}}$' % (K_fit, c_fit, p_fit) + \
              f'\n$R^2$: {R_squared:.4f}'
              
plt.plot(t_fit, N_fit, color='red', linestyle='-', linewidth=2, label=model_label)

# Grafik Başlık ve Etiketleri
plt.title(f'İtalya Depremleri (M{main_shock_mag}) Sonrası Artçı Sarsıntı Azalması (2016)', fontsize=14)
plt.xlabel('Ana Şoktan Sonra Geçen Süre (Gün)', fontsize=12)
plt.ylabel('Günlük Artçı Sarsıntı Sayısı (N)', fontsize=12)
plt.yscale('log') # Logaritmik y-ekseni
plt.grid(True, which="both", ls="--", linewidth=0.5)
plt.legend(loc='upper right', fontsize=10)
plt.show()

# ----------------------------------------------------------------------
# 6. Yorumlama (Console Output)
# ----------------------------------------------------------------------

print("\n--- 6. Model Yorumu ve Çıkarımlar ---")
print(f"Omori Yasası'nın Azalma Hızı (p) değeri: {p_fit:.3f}")
if p_fit > 1.0:
    print(f"p > 1.0 olduğu için, artçı sarsıntı aktivitesi zamanla beklenenden daha hızlı bir şekilde azalmıştır. Bu, bölgenin enerjiyi çabuk boşalttığını gösterir. 📉")
elif p_fit < 1.0:
    print(f"p < 1.0 olduğu için, artçı sarsıntı aktivitesi zamanla beklenenden daha yavaş bir şekilde azalmıştır. Bu, riskin uzun süre devam ettiğini gösterir.")
else:
    print(f"p ≈ 1.0. Azalma hızı klasik Omori beklentileriyle tutarlıdır.")
print(f"c parametresi (Zaman Kayması): {c_fit:.2f} gün.")
print(f"Modelin uydurma başarısı R-kare: {R_squared:.4f}")