import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

pyautogui.PAUSE = 0 
pyautogui.FAILSAFE = False

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

SCREEN_W, SCREEN_H = pyautogui.size()

curr_x, curr_y = SCREEN_W // 2, SCREEN_H // 2
prev_x, prev_y = 0, 0
SENSITIVITY = 2.5 # Serbest takip hassasiyeti

clicking = False
right_clicking = False
holding = False
last_click_time = 0

def draw_ui_panel(img, pt1, pt2, color, alpha=0.6):
    overlay = img.copy()
    cv2.rectangle(overlay, pt1, pt2, color, cv2.FILLED)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

def main():
    global curr_x, curr_y, prev_x, prev_y
    global clicking, right_clicking, holding, last_click_time
    
    cap = cv2.VideoCapture(0)
    cam_w, cam_h = 1280, 720
    cap.set(3, cam_w)
    cap.set(4, cam_h)
    
    p_time = 0
    
    print("Argus: Efsanevi Final Surumu Aktif!")
    
    with mp_hands.Hands(
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5 
    ) as hands:
        
        while True:
            success, frame = cap.read()
            if not success:
                break
                
            frame = cv2.flip(frame, 1)
            frame = cv2.GaussianBlur(frame, (3, 3), 0)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            action_text = "Bekleniyor..."
            action_color = (255, 255, 255)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=2)
                    )
                    
                    # TAKİP NOKTASI: İşaret Parmağı Ucu
                    target_node = hand_landmarks.landmark[8]
                    x_target, y_target = int(target_node.x * cam_w), int(target_node.y * cam_h)
                    
                    # PARMAK UÇLARI VE MESAFELER
                    index_tip = hand_landmarks.landmark[8]
                    middle_tip = hand_landmarks.landmark[12]
                    ring_tip = hand_landmarks.landmark[16]
                    thumb_tip = hand_landmarks.landmark[4]
                    
                    x1, y1 = int(index_tip.x * cam_w), int(index_tip.y * cam_h)
                    x2, y2 = int(thumb_tip.x * cam_w), int(thumb_tip.y * cam_h)
                    x_mid, y_mid = int(middle_tip.x * cam_w), int(middle_tip.y * cam_h)
                    x_ring, y_ring = int(ring_tip.x * cam_w), int(ring_tip.y * cam_h)
                    
                    length_index = np.hypot(x2 - x1, y2 - y1)
                    length_middle = np.hypot(x2 - x_mid, y2 - y_mid)
                    length_ring = np.hypot(x2 - x_ring, y2 - y_ring)
                    
                    # HANGİ PARMAKLAR HAVADA?
                    tips = [8, 12, 16, 20]
                    pips = [6, 10, 14, 18]
                    fingers_up = []
                    for t, p in zip(tips, pips):
                        fingers_up.append(1 if hand_landmarks.landmark[t].y < hand_landmarks.landmark[p].y else 0)
                        
                    is_fully_open = (fingers_up == [1, 1, 1, 1])
                    
                    # --- HAREKET KONTROLÜ (GÖRELİ / SERBEST MANTIK) ---
                    # İmleç SADECE ve SADECE tüm parmaklar açıkken (5 yaparken) hareket eder!
                    # Kameranın merkezi değil, elin o anki konumu merkez kabul edilir.
                    if is_fully_open and not holding:
                        action_text = "TAKIP AKTIF (SERBEST)"
                        action_color = (0, 255, 255)
                        cv2.circle(frame, (x_target, y_target), 15, (255, 255, 255), cv2.FILLED)
                        
                        if prev_x != 0 and prev_y != 0:
                            dx = (x_target - prev_x) * SENSITIVITY
                            dy = (y_target - prev_y) * SENSITIVITY
                            
                            curr_x += dx
                            curr_y += dy
                            
                            curr_x = max(0, min(SCREEN_W - 1, curr_x))
                            curr_y = max(0, min(SCREEN_H - 1, curr_y))
                            
                            try:
                                pyautogui.moveTo(curr_x, curr_y)
                            except:
                                pass
                                
                        prev_x, prev_y = x_target, y_target
                    else:
                        # Parmaklardan biri bile kıvrılırsa imleç olduğu yere çakılır. (Clutch mekanizması)
                        # Bu sayede elinizi geri merkeze çekip harekete devam edebilirsiniz!
                        prev_x, prev_y = x_target, y_target 
                        action_text = "DURAKLATILDI / TIKLANIYOR"
                        action_color = (100, 100, 100)
                        
                    # --- TIKLAMALAR ---
                    # Sol Tık (İşaret parmağı kıvrık ve baş parmağa yakın)
                    if length_index < 40 and fingers_up[0] == 0 and not holding:
                        action_text = "SOL TIK"
                        action_color = (0, 255, 0)
                        cv2.circle(frame, (x1, y1), 20, (0, 255, 0), cv2.FILLED)
                        if not clicking:
                            clicking = True
                            current_time = time.time()
                            if current_time - last_click_time < 0.4:
                                pyautogui.doubleClick()
                                action_text = "CIFT TIK!"
                                last_click_time = 0
                            else:
                                pyautogui.click()
                                last_click_time = current_time
                    else:
                        clicking = False
                        
                    # Sağ Tık (Orta parmak kıvrık)
                    if length_middle < 40 and fingers_up[1] == 0 and not holding:
                        action_text = "SAG TIK"
                        action_color = (0, 0, 255)
                        cv2.circle(frame, (x_mid, y_mid), 20, (0, 0, 255), cv2.FILLED)
                        if not right_clicking:
                            pyautogui.rightClick()
                            right_clicking = True
                    else:
                        right_clicking = False
                        
                    # Sürükle Bırak (Yüzük parmağı kıvrık)
                    if length_ring < 40 and fingers_up[2] == 0:
                        action_text = "SURUKLENIYOR..."
                        action_color = (255, 0, 0)
                        cv2.circle(frame, (x_ring, y_ring), 20, (255, 0, 0), cv2.FILLED)
                        if not holding:
                            pyautogui.mouseDown()
                            holding = True
                        
                        # Sürüklerken imleç hareket edebilmeli (İşaret parmağı açıksa)
                        if holding and fingers_up[0] == 1:
                            if prev_x != 0 and prev_y != 0:
                                dx = (x_target - prev_x) * SENSITIVITY
                                dy = (y_target - prev_y) * SENSITIVITY
                                curr_x += dx
                                curr_y += dy
                                curr_x = max(0, min(SCREEN_W - 1, curr_x))
                                curr_y = max(0, min(SCREEN_H - 1, curr_y))
                                try:
                                    pyautogui.moveTo(curr_x, curr_y)
                                except:
                                    pass
                            prev_x, prev_y = x_target, y_target
                    else:
                        if holding:
                            pyautogui.mouseUp()
                            holding = False
                            
                    # --- SCROLL & VOLUME EKLENTİSİ ---
                    if fingers_up == [1, 1, 0, 0] and not holding:
                        action_text = "SCROLL MODU"
                        action_color = (255, 200, 0)
                        cv2.circle(frame, (x1, y1), 20, (255, 200, 0), 2)
                        scroll_dy = y_target - prev_y
                        if abs(scroll_dy) > 2:
                            pyautogui.scroll(int(-scroll_dy * 2.0))
                            
                    if fingers_up == [0, 0, 0, 1] and not holding:
                        action_text = "DJ MODU (SES)"
                        action_color = (0, 150, 255)
                        vol_dy = y_target - prev_y
                        if vol_dy > 10:
                            pyautogui.press('volumedown')
                        elif vol_dy < -10:
                            pyautogui.press('volumeup')

            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time

            draw_ui_panel(frame, (0, 0), (cam_w, 80), (0, 0, 0), 0.7)
            cv2.putText(frame, "ARGUS V6: MASTERPIECE (Acik El)", (30, 50), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 255), 2)
            cv2.putText(frame, f"FPS: {int(fps)}", (cam_w - 180, 50), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 2)
            
            draw_ui_panel(frame, (0, cam_h - 100), (cam_w, cam_h), (0, 0, 0), 0.7)
            cv2.putText(frame, "AKSIYON:", (30, cam_h - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
            cv2.putText(frame, action_text, (200, cam_h - 40), cv2.FONT_HERSHEY_DUPLEX, 1.2, action_color, 2)
            
            cv2.imshow('Argus HUD', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
