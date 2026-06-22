import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

SCREEN_W, SCREEN_H = pyautogui.size()
pyautogui.FAILSAFE = False

# Fare konumları
curr_x, curr_y = SCREEN_W // 2, SCREEN_H // 2
prev_mapped_x, prev_mapped_y = 0, 0
SMOOTHING = 5
SENSITIVITY = 1.5 

# Mod state
mode = 'ABSOLUTE' 
fist_pressed = False

# Swipe state
prev_wrist_x = 0
swiped = False

# Tıklama state'leri
clicking = False
right_clicking = False
holding = False
last_click_time = 0

def main():
    global curr_x, curr_y, prev_mapped_x, prev_mapped_y, mode, fist_pressed
    global clicking, right_clicking, holding, last_click_time, prev_wrist_x, swiped
    
    cap = cv2.VideoCapture(0)
    cam_w, cam_h = 640, 480
    cap.set(3, cam_w)
    cap.set(4, cam_h)
    
    frame_r = 100 
    
    print("Argus (Sihirli Guncelleme) basladi! 'q' ile cikabilirsiniz.")
    
    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:
        
        while True:
            success, frame = cap.read()
            if not success:
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            cv2.putText(frame, f"MOD: {mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            if mode == 'ABSOLUTE':
                cv2.rectangle(frame, (frame_r, frame_r), (cam_w - frame_r, cam_h - frame_r), (255, 0, 255), 2)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    index_tip = hand_landmarks.landmark[8]
                    middle_tip = hand_landmarks.landmark[12]
                    ring_tip = hand_landmarks.landmark[16]
                    pinky_tip = hand_landmarks.landmark[20]
                    thumb_tip = hand_landmarks.landmark[4]
                    wrist = hand_landmarks.landmark[0]
                    
                    x1, y1 = int(index_tip.x * cam_w), int(index_tip.y * cam_h)
                    x2, y2 = int(thumb_tip.x * cam_w), int(thumb_tip.y * cam_h)
                    x_mid, y_mid = int(middle_tip.x * cam_w), int(middle_tip.y * cam_h)
                    x_ring, y_ring = int(ring_tip.x * cam_w), int(ring_tip.y * cam_h)
                    
                    mapped_x = np.interp(x1, (frame_r, cam_w - frame_r), (0, SCREEN_W))
                    mapped_y = np.interp(y1, (frame_r, cam_h - frame_r), (0, SCREEN_H))
                    
                    # Hangi parmaklar havada? (Parmak ucu, kök boğumundan daha yukarıdaysa havadadır)
                    tips = [8, 12, 16, 20]
                    pips = [6, 10, 14, 18]
                    fingers_up = []
                    for t, p in zip(tips, pips):
                        fingers_up.append(1 if hand_landmarks.landmark[t].y < hand_landmarks.landmark[p].y else 0)
                    # fingers_up: [İşaret, Orta, Yüzük, Serçe]
                    
                    # 1. SWIPE MODU (Tüm 4 parmak açık ve bilek sağa/sola hızlı hareket ediyorsa)
                    if sum(fingers_up) == 4:
                        if prev_wrist_x != 0:
                            swipe_dx = wrist.x - prev_wrist_x
                            if swipe_dx > 0.08 and not swiped: # Sağa sert kaydırma
                                pyautogui.hotkey('alt', 'tab')
                                swiped = True
                                cv2.putText(frame, "ALT+TAB", (cam_w//2-50, cam_h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                            elif swipe_dx < -0.08 and not swiped: # Sola sert kaydırma
                                pyautogui.hotkey('win', 'd') # Masaüstünü göster
                                swiped = True
                                cv2.putText(frame, "MASAUSTU", (cam_w//2-80, cam_h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                            elif abs(swipe_dx) < 0.02:
                                swiped = False
                        prev_wrist_x = wrist.x
                        
                    # 2. SCROLL (SAYFA KAYDIRMA) MODU (Sadece İşaret ve Orta parmak havada - 'V' işareti)
                    elif fingers_up == [1, 1, 0, 0]:
                        cv2.putText(frame, "SCROLL MODU (Yukari/Asagi kaydir)", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)
                        cv2.circle(frame, (x1, y1), 15, (255, 100, 100), cv2.FILLED)
                        if prev_mapped_y != 0:
                            scroll_dy = mapped_y - prev_mapped_y
                            if abs(scroll_dy) > 2:
                                pyautogui.scroll(int(-scroll_dy * 2)) # Elini yukarı çıkarırsan sayfa yukarı kayar
                                
                    # 3. SES KONTROL MODU (Sadece Serçe parmak havada)
                    elif fingers_up == [0, 0, 0, 1]:
                        cv2.putText(frame, "SES KONTROLU (Yukari Ac / Asagi Kis)", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 255), 2)
                        cv2.circle(frame, (int(pinky_tip.x * cam_w), int(pinky_tip.y * cam_h)), 15, (100, 100, 255), cv2.FILLED)
                        if prev_mapped_y != 0:
                            vol_dy = mapped_y - prev_mapped_y
                            if vol_dy > 15: # Eli aşağı indirme (Ses Kıs)
                                pyautogui.press('volumedown')
                                time.sleep(0.05)
                            elif vol_dy < -15: # Eli yukarı kaldırma (Ses Aç)
                                pyautogui.press('volumeup')
                                time.sleep(0.05)
                                
                    # 4. AVUÇ KAPATMA (Mod Değişimi: Absolute <-> Relative)
                    elif fingers_up == [0, 0, 0, 0]:
                        if not fist_pressed:
                            mode = 'RELATIVE' if mode == 'ABSOLUTE' else 'ABSOLUTE'
                            fist_pressed = True
                            cv2.putText(frame, "MOD DEGISTI!", (cam_w//2-100, cam_h//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    else:
                        fist_pressed = False
                        prev_wrist_x = wrist.x
                        
                        # --- NORMAL FARE HAREKETİ VE TIKLAMALAR ---
                        cv2.circle(frame, (x1, y1), 10, (255, 255, 0), cv2.FILLED)
                        
                        length_index = np.hypot(x2 - x1, y2 - y1)
                        length_middle = np.hypot(x2 - x_mid, y2 - y_mid)
                        length_ring = np.hypot(x2 - x_ring, y2 - y_ring)
                        
                        # Hareket ettirme (İmleç Dondurma aktif)
                        if not ((length_index < 40 or length_middle < 40) and not holding): 
                            if mode == 'ABSOLUTE':
                                curr_x += (mapped_x - curr_x) / SMOOTHING
                                curr_y += (mapped_y - curr_y) / SMOOTHING
                            elif mode == 'RELATIVE':
                                if prev_mapped_x != 0 and prev_mapped_y != 0:
                                    curr_x += (mapped_x - prev_mapped_x) * SENSITIVITY
                                    curr_y += (mapped_y - prev_mapped_y) * SENSITIVITY
                                
                            curr_x = max(0, min(SCREEN_W - 1, curr_x))
                            curr_y = max(0, min(SCREEN_H - 1, curr_y))
                            
                            try:
                                pyautogui.moveTo(curr_x, curr_y)
                            except:
                                pass
                        
                        # Sol Tık / Çift Tık (Baş + İşaret)
                        if length_index < 40 and not holding:
                            cv2.circle(frame, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                            if not clicking:
                                clicking = True
                                current_time = time.time()
                                if current_time - last_click_time < 0.4:
                                    pyautogui.doubleClick()
                                    last_click_time = 0
                                else:
                                    pyautogui.click()
                                    last_click_time = current_time
                        else:
                            clicking = False
                            
                        # Sağ Tık (Baş + Orta)
                        if length_middle < 40 and not holding:
                            cv2.circle(frame, (x_mid, y_mid), 15, (0, 0, 255), cv2.FILLED)
                            if not right_clicking:
                                pyautogui.rightClick()
                                right_clicking = True
                        else:
                            right_clicking = False
                            
                        # Sürükle Bırak (Baş + Yüzük)
                        if length_ring < 40:
                            cv2.circle(frame, (x_ring, y_ring), 15, (255, 0, 0), cv2.FILLED)
                            cv2.putText(frame, "SURUKLENIYOR...", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                            if not holding:
                                pyautogui.mouseDown()
                                holding = True
                        else:
                            if holding:
                                pyautogui.mouseUp()
                                holding = False
                                
                    prev_mapped_x, mapped_x
                    prev_mapped_y = mapped_y

            cv2.imshow('Argus - Sihirli El Kontrolu', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
