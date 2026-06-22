# 👁️ Argus: Temassız Yüz ve Göz İzleme Sistemi

Argus, bilgisayar görüsü tabanlı gelişmiş bir temassız arayüz sistemidir. Kontrol tamamen **yüzünüz ve gözlerinize** bırakılmıştır.

Akıllı asistanınız **Dorina** ile birlikte geliştirilen bu sistem, baş hareketlerinizle farenizi yönlendirmenizi, göz kırpmalarınızla tıklama yapmanızı sağlar. Yeni "Tıklama Modu" sayesinde istenmeyen tıklamaların önüne geçilmiştir.

---

## ✨ Öne Çıkan Özellikler

*   **Burun ile Hassas Navigasyon:** Farenizin imlecini kafanızı hareket ettirerek yönlendirin. Ekranda gördüğünüz pembe çerçeve içinde burnunuzu hareket ettirdiğinizde imleç tüm ekranı kapsayacak şekilde pürüzsüzce hareket eder.
*   **Akıllı Tıklama Modu (Çift Göz Kırpma):** 
    *   Fare sürekli rastgele yerlere tıklamasın diye sistem başlangıçta "Sadece İzleme" modunda açılır.
    *   Tıklama modunu **AÇMAK veya KAPATMAK** için iki gözünüzü aynı anda hızlıca iki kez (1 saniye içinde) açıp kapatın.
*   **Göz Kırparak Tıklama (Tıklama Modu Açıkken):**
    *   **Sol Tık:** Sol gözünüzü kırpın.
    *   **Çift Tık:** Sol gözünüzü arka arkaya hızlıca iki kez kırpın (Aynı farenizdeki gibi tık-tık yapın).
    *   **Sağ Tık:** Sağ gözünüzü kırpın.
*   **Gerçek Zamanlı Göz Kapalılık (EAR) Oranları:** Ekranda (HUD) gözlerinizin açıklık/kapalılık durumu anlık float değeri olarak gösterilir.
*   **Anti-Jitter ve Güvenlik:** Fare imlecinin titremesini önleyen EMA filtresi ve işler ters giderse fareyi ekranın köşesine çekerek sistemi anında kilitleyebileceğiniz FailSafe modu aktiftir.

## 🛠️ Teknik Altyapı

*   **Yapay Zeka Asistanı:** Dorina
*   **Dil ve Kütüphaneler:** Python, OpenCV, Google MediaPipe (Face Mesh), PyAutoGUI, Numpy

---

## 🚀 Başlangıç ve Kurulum

1. Python sanal ortamını oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install opencv-python mediapipe pyautogui numpy
   ```
3. Argus'u çalıştırın:
   ```bash
   python main.py
   ```
