import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# Güvenlik önlemi
pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0

mp_face_mesh = mp.solutions.face_mesh
SCREEN_W, SCREEN_H = pyautogui.size()

# Göz kırpma eşikleri (Hysteresis)
EAR_THRESH = 0.22      
EAR_OPEN_THRESH = 0.25 

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def get_ear(landmarks, eye_indices, cam_w, cam_h):
    pts = []
    for idx in eye_indices:
        x = int(landmarks.landmark[idx].x * cam_w)
        y = int(landmarks.landmark[idx].y * cam_h)
        pts.append(np.array([x, y]))
        
    dist_v1 = np.linalg.norm(pts[1] - pts[5])
    dist_v2 = np.linalg.norm(pts[2] - pts[4])
    dist_h = np.linalg.norm(pts[0] - pts[3])
    
    if dist_h == 0: return 0
    return (dist_v1 + dist_v2) / (2.0 * dist_h)

def draw_ui_panel(img, pt1, pt2, color, alpha=0.6):
    overlay = img.copy()
    cv2.rectangle(overlay, pt1, pt2, color, cv2.FILLED)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

def main():
    cap = cv2.VideoCapture(0)
    cam_w, cam_h = 640, 480
    cap.set(3, cam_w)
    cap.set(4, cam_h)
    
    BOX_X_MARGIN = 150
    BOX_Y_MARGIN = 100
    SMOOTHING = 5
    prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2
    
    click_mode_active = False
    
    both_is_closed = False
    left_is_closed = False
    right_is_closed = False
    
    # Uzun süre göz kapalı tutmayı ölçmek için zamanlayıcı
    both_closed_start_time = 0
    mode_toggled_this_closure = False
    
    pending_left_click = 0
    pending_right_click = 0
    
    last_action = "Sadece Takip Modu"
    action_color = (255, 255, 255)
    
    print("Argus Yüz Kontrol Sistemi Başlatılıyor...")
    
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as face_mesh:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success: break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            
            cv2.rectangle(frame, (BOX_X_MARGIN, BOX_Y_MARGIN), 
                          (cam_w - BOX_X_MARGIN, cam_h - BOX_Y_MARGIN), (255, 0, 255), 2)
                          
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                
                # --- FARE HAREKETİ ---
                nose_tip = landmarks.landmark[4]
                nose_x = int(nose_tip.x * cam_w)
                nose_y = int(nose_tip.y * cam_h)
                
                cv2.circle(frame, (nose_x, nose_y), 8, (0, 255, 255), cv2.FILLED)
                
                target_screen_x = np.interp(nose_x, (BOX_X_MARGIN, cam_w - BOX_X_MARGIN), (0, SCREEN_W))
                target_screen_y = np.interp(nose_y, (BOX_Y_MARGIN, cam_h - BOX_Y_MARGIN), (0, SCREEN_H))
                
                curr_x = prev_x + (target_screen_x - prev_x) / SMOOTHING
                curr_y = prev_y + (target_screen_y - prev_y) / SMOOTHING
                
                try:
                    pyautogui.moveTo(curr_x, curr_y)
                except pyautogui.FailSafeException:
                    pass
                
                prev_x, prev_y = curr_x, curr_y
                
                # --- GÖZ HESAPLAMALARI ---
                left_ear = get_ear(landmarks, LEFT_EYE, cam_w, cam_h)
                right_ear = get_ear(landmarks, RIGHT_EYE, cam_w, cam_h)
                
                current_time = time.time()
                is_both_closed_now = (left_ear < EAR_THRESH) and (right_ear < EAR_THRESH)
                
                # Çift Göz (MOD DEĞİŞTİRME) Kontrolü
                if is_both_closed_now:
                    if not both_is_closed:
                        both_is_closed = True
                        both_closed_start_time = current_time
                        mode_toggled_this_closure = False
                    else:
                        # İki göz de şu an kapalı. 1.2 saniyeden uzun süredir kapalıysa modu değiştir!
                        if not mode_toggled_this_closure and (current_time - both_closed_start_time > 1.2):
                            click_mode_active = not click_mode_active
                            mode_toggled_this_closure = True # Bu kapanışta modu sadece 1 kez değiştir
                            
                            if click_mode_active:
                                last_action = "TIKLAMA AKTIF!"
                                action_color = (0, 255, 255)
                            else:
                                last_action = "TIKLAMA KAPALI"
                                action_color = (100, 100, 100)
                                
                    # İki göz kapalıyken tekil tıklamaları durdur
                    pending_left_click = 0
                    pending_right_click = 0
                    left_is_closed = True
                    right_is_closed = True
                else:
                    if left_ear > EAR_OPEN_THRESH or right_ear > EAR_OPEN_THRESH:
                        both_is_closed = False
                        mode_toggled_this_closure = False

                    # Tekil Sol Göz
                    if left_ear < EAR_THRESH:
                        if not left_is_closed:
                            left_is_closed = True
                            if click_mode_active:
                                pending_left_click = current_time
                    elif left_ear > EAR_OPEN_THRESH:
                        left_is_closed = False

                    # Tekil Sağ Göz
                    if right_ear < EAR_THRESH:
                        if not right_is_closed:
                            right_is_closed = True
                            if click_mode_active:
                                pending_right_click = current_time
                    elif right_ear > EAR_OPEN_THRESH:
                        right_is_closed = False

                # --- TAMPONLANMIŞ TIKLAMALARI İŞLE ---
                if pending_left_click > 0 and (current_time - pending_left_click > 0.1):
                    pyautogui.click()
                    last_action = "SOL TIK"
                    action_color = (0, 255, 0)
                    pending_left_click = 0
                    
                if pending_right_click > 0 and (current_time - pending_right_click > 0.1):
                    pyautogui.rightClick()
                    last_action = "SAG TIK"
                    action_color = (0, 0, 255)
                    pending_right_click = 0

                # HUD EKRANI
                cv2.putText(frame, f"Sol EAR: {left_ear:.3f}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Sag EAR: {right_ear:.3f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                mod_text = "AKTIF" if click_mode_active else "PASIF"
                mod_color = (0, 255, 0) if click_mode_active else (0, 0, 255)
                cv2.putText(frame, f"TIK MODU: {mod_text}", (cam_w - 220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, mod_color, 2)
                
                # Ekrana basılı tutma süresini çiz
                if both_is_closed and not mode_toggled_this_closure:
                    hold_time = current_time - both_closed_start_time
                    cv2.putText(frame, f"Mod Degisiyor: {hold_time:.1f}s / 1.2s", (cam_w//2 - 150, cam_h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    
            draw_ui_panel(frame, (0, cam_h - 60), (cam_w, cam_h), (0, 0, 0), 0.7)
            cv2.putText(frame, "SON ISLEM:", (20, cam_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
            cv2.putText(frame, last_action, (180, cam_h - 20), cv2.FONT_HERSHEY_DUPLEX, 0.9, action_color, 2)
            
            cv2.imshow('Argus Yuz Kontrol', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
