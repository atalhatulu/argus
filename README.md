# 👁️ Argus: Temassız Arayüz Algılama Sistemi

Argus, bilgisayar görüsü tabanlı gelişmiş bir temassız arayüz sistemidir. Projenin ilk fazında planlanan göz takibi (eye-tracking), performans ve kullanım kolaylığı (UX) açısından değerlendirilerek yerini çok daha stabil, yorulmayı önleyen ve akıcı olan **Sihirli El Kontrolüne (Hand Tracking)** bırakmıştır.

Akıllı asistanımız **Dorina** ile birlikte geliştirilen bu sistem, standart bir web kamerasını fütüristik bir masaüstü kontrol merkezine dönüştürerek geleneksel donanımları (fare) devre dışı bırakır.

---

## ✨ Öne Çıkan Özellikler (Sihirli Güncelleme)

*   **İşaret Parmağı ile Navigasyon:** Sadece işaret parmağınızı ekrana doğru tutarak imleci doğal ve pürüzsüz bir şekilde yönlendirin. Gelişmiş Anti-Jitter filtresi ile titremeler engellenmiştir.
*   **İmleç Dondurma Teknolojisi:** Tıklama hareketi yaparken imleç otomatik olarak donar. Böylece eliniz hareket etse bile hedefinizden sapmazsınız.
*   **Keskin Tıklama Hareketleri (Tek El Kontrolü):**
    *   **Sol Tık / Çift Tık:** Baş parmak ve İşaret parmağını birleştir (Çimdik).
    *   **Sağ Tık:** Baş parmak ve Orta parmağı birleştir.
    *   **Basılı Tut (Sürükle-Bırak):** Baş parmak ve Yüzük parmağını birleştir.
*   **Mousepad Modu (Avuç Kapatma):** Elinizi yumruk yaptığınızda sistem "Relative" (Göreli) moda geçer. Eliniz ekranın neresinde olursa olsun bir laptop touchpad'i gibi çalışır. Tekrar yumruk yaparak tam ekran kontrolüne dönebilirsiniz.
*   **Sihirli Jestler:**
    *   **Sayfa Kaydırma (Scroll):** Elinizle 'V' işareti yapın (işaret ve orta parmak açık) ve elinizi aşağı yukarı hareket ettirin.
    *   **Ses Kontrolü:** Sadece serçe parmağınızı havaya kaldırıp asansör gibi yukarı/aşağı indirin.
    *   **Hızlı Geçiş (Swipe):** 5 parmağınız açıkken bileğinizi hızlıca sağa (Alt+Tab) veya sola (Masaüstü) savurun.

## 🛠️ Teknik Altyapı

*   **Yapay Zeka Asistanı:** Dorina Agent
*   **Dil ve Kütüphaneler:** Python, OpenCV, Google MediaPipe (Hands), PyAutoGUI, Numpy

---

## 🚀 Başlangıç ve Kurulum

1. Depoyu bilgisayarınıza klonlayın:
   ```bash
   git clone https://github.com/KULLANICI_ADINIZ/argus.git
   cd argus
   ```
2. Python sanal ortamını oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   # Windows için:
   .\venv\Scripts\activate
   ```
3. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install opencv-python mediapipe pyautogui numpy
   ```
4. Argus'u çalıştırın:
   ```bash
   python main.py
   ```

*(Not: `venv` klasörü `.gitignore` dosyası ile Git takibinden izole edilmiştir, GitHub deponuzda yer kaplamaz.)*
