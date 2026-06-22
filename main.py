import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import winsound

pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0

mp_face_mesh = mp.solutions.face_mesh
SCREEN_W, SCREEN_H = pyautogui.size()

# --- MODLAR ---
tracking_mode = "GAZE" # "GAZE" veya "NOSE"

def get_gaze_ratio(landmarks, iris_center_idx, p_left_idx, p_right_idx, p_up_idx, p_down_idx, cam_w, cam_h):
    iris_p = np.array([landmarks.landmark[iris_center_idx].x * cam_w, landmarks.landmark[iris_center_idx].y * cam_h])
    left_p = np.array([landmarks.landmark[p_left_idx].x * cam_w, landmarks.landmark[p_left_idx].y * cam_h])
    right_p = np.array([landmarks.landmark[p_right_idx].x * cam_w, landmarks.landmark[p_right_idx].y * cam_h])
    up_p = np.array([landmarks.landmark[p_up_idx].x * cam_w, landmarks.landmark[p_up_idx].y * cam_h])
    down_p = np.array([landmarks.landmark[p_down_idx].x * cam_w, landmarks.landmark[p_down_idx].y * cam_h])
    
    h_vec = right_p - left_p
    h_len = np.linalg.norm(h_vec)
    h_ratio = np.dot(iris_p - left_p, h_vec / h_len) / h_len if h_len > 0 else 0.5
    
    v_vec = down_p - up_p
    v_len = np.linalg.norm(v_vec)
    v_ratio = np.dot(iris_p - up_p, v_vec / v_len) / v_len if v_len > 0 else 0.5
    
    return h_ratio, v_ratio

def draw_ui_panel(img, pt1, pt2, color, alpha=0.6):
    overlay = img.copy()
    cv2.rectangle(overlay, pt1, pt2, color, cv2.FILLED)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

def main():
    global tracking_mode
    
    cap = cv2.VideoCapture(0)
    cam_w, cam_h = 640, 480
    cap.set(3, cam_w)
    cap.set(4, cam_h)
    
    # Pencereyi oluştur ve tam ekranın ortasına yerleştir
    display_w, display_h = 800, 300
    cv2.namedWindow('Argus Goz Kamerasi', cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow('Argus Goz Kamerasi', (SCREEN_W - display_w) // 2, (SCREEN_H - display_h) // 2)
    
    curr_x, curr_y = SCREEN_W // 2, SCREEN_H // 2
    
    last_action = "Senkronizasyon Bekleniyor..."
    action_color = (255, 255, 255)
    
    # --- 4 KÖŞE KALİBRASYON DEĞİŞKENLERİ ---
    sync_active = True
    sync_start_time = time.time() + 2.0 
    SYNC_DURATION = 8.0 # Toplam 8 saniye (her köşe için 2 sn)
    
    calib_h_min, calib_h_max = 1.0, 0.0
    calib_v_min, calib_v_max = 1.0, 0.0
    calib_face_widths = []
    
    H_MIN, H_MAX = 0.42, 0.58
    V_MIN, V_MAX = 0.40, 0.60
    CENTER_H, CENTER_V = 0.5, 0.5
    REF_FACE_W = 200.0
    
    last_corner_idx = -1
    flash_frames = 0
    
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
            current_time = time.time()
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                target_screen_x, target_screen_y = curr_x, curr_y
                
                left_face = np.array([landmarks.landmark[234].x * cam_w, landmarks.landmark[234].y * cam_h])
                right_face = np.array([landmarks.landmark[454].x * cam_w, landmarks.landmark[454].y * cam_h])
                face_width = np.linalg.norm(right_face - left_face)
                
                distance_ratio = REF_FACE_W / face_width if face_width > 0 else 1.0
                
                h_l, v_l = get_gaze_ratio(landmarks, 473, 33, 133, 159, 145, cam_w, cam_h)
                h_r, v_r = get_gaze_ratio(landmarks, 468, 362, 263, 386, 374, cam_w, cam_h)
                
                raw_h_ratio = (h_l + h_r) / 2.0
                raw_v_ratio = (v_l + v_r) / 2.0
                
                # --- ÇİZİMLER (Göz akı ve İris) ---
                l_out = (int(landmarks.landmark[33].x * cam_w), int(landmarks.landmark[33].y * cam_h))
                l_in = (int(landmarks.landmark[133].x * cam_w), int(landmarks.landmark[133].y * cam_h))
                cv2.circle(frame, l_out, 3, (255, 0, 0), -1)
                cv2.circle(frame, l_in, 3, (255, 0, 0), -1)
                cv2.line(frame, l_out, l_in, (255, 0, 0), 2)
                
                r_in = (int(landmarks.landmark[362].x * cam_w), int(landmarks.landmark[362].y * cam_h))
                r_out = (int(landmarks.landmark[263].x * cam_w), int(landmarks.landmark[263].y * cam_h))
                cv2.circle(frame, r_in, 3, (255, 0, 0), -1)
                cv2.circle(frame, r_out, 3, (255, 0, 0), -1)
                cv2.line(frame, r_in, r_out, (255, 0, 0), 2)
                
                l_iris = (int(landmarks.landmark[473].x * cam_w), int(landmarks.landmark[473].y * cam_h))
                r_iris = (int(landmarks.landmark[468].x * cam_w), int(landmarks.landmark[468].y * cam_h))
                cv2.circle(frame, l_iris, 4, (0, 255, 0), -1)
                cv2.circle(frame, r_iris, 4, (0, 255, 0), -1)
                
                # --- 4 KÖŞE SENKRONİZASYONU (Sessiz ve Parlayan Yönlendirme) ---
                sync_msg = ""
                if sync_active:
                    elapsed = current_time - sync_start_time
                    if elapsed < 0:
                        sync_msg = f"Hazirlaniliyor: {-elapsed:.1f}s"
                        last_corner_idx = -1
                    elif elapsed < SYNC_DURATION:
                        calib_h_min = min(calib_h_min, raw_h_ratio)
                        calib_h_max = max(calib_h_max, raw_h_ratio)
                        calib_v_min = min(calib_v_min, raw_v_ratio)
                        calib_v_max = max(calib_v_max, raw_v_ratio)
                        calib_face_widths.append(face_width)
                        
                        rem = SYNC_DURATION - elapsed
                        corner_idx = int(elapsed // 2.0)
                        
                        # Köşe değiştiğinde Ses çıkar ve Ekranı parlat!
                        if corner_idx != last_corner_idx:
                            winsound.MessageBeep(0) # Kısa ping sesi (Asenkron)
                            last_corner_idx = corner_idx
                            flash_frames = 5 # 5 kare boyunca ekran beyaz olacak
                            
                        if corner_idx == 0:
                            sync_msg = f"1. SOL UST Koseye Bakin! ({rem:.1f}s)"
                        elif corner_idx == 1:
                            sync_msg = f"2. SAG UST Koseye Bakin! ({rem:.1f}s)"
                        elif corner_idx == 2:
                            sync_msg = f"3. SAG ALT Koseye Bakin! ({rem:.1f}s)"
                        else:
                            sync_msg = f"4. SOL ALT Koseye Bakin! ({rem:.1f}s)"
                    else:
                        if last_corner_idx != 4:
                            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION) # Bitiş sesi
                            last_corner_idx = 4
                            
                        sync_active = False
                        pad_h = (calib_h_max - calib_h_min) * 0.1
                        pad_v = (calib_v_max - calib_v_min) * 0.1
                        
                        H_MIN = calib_h_min + pad_h
                        H_MAX = calib_h_max - pad_h
                        V_MIN = calib_v_min + pad_v
                        V_MAX = calib_v_max - pad_v
                        
                        CENTER_H = (H_MIN + H_MAX) / 2.0
                        CENTER_V = (V_MIN + V_MAX) / 2.0
                        
                        if len(calib_face_widths) > 0:
                            REF_FACE_W = sum(calib_face_widths) / len(calib_face_widths)
                        
                    target_screen_x, target_screen_y = SCREEN_W // 2, SCREEN_H // 2
                else:
                    h_dev = raw_h_ratio - CENTER_H
                    v_dev = raw_v_ratio - CENTER_V
                    
                    scaled_h_ratio = CENTER_H + (h_dev * distance_ratio)
                    scaled_v_ratio = CENTER_V + (v_dev * distance_ratio)
                    
                    target_screen_x = np.interp(scaled_h_ratio, (H_MIN, H_MAX), (0, SCREEN_W))
                    target_screen_y = np.interp(scaled_v_ratio, (V_MIN, V_MAX), (0, SCREEN_H))
                
                # --- DİNAMİK YUMUŞATMA FİLTRESİ ---
                dx = target_screen_x - curr_x
                dy = target_screen_y - curr_y
                dist = np.hypot(dx, dy)
                
                alpha = np.interp(dist, [0, 100], [0.03, 0.25])
                curr_x += dx * alpha
                curr_y += dy * alpha
                
                try:
                    pyautogui.moveTo(curr_x, curr_y)
                except pyautogui.FailSafeException:
                    pass
                
                # --- GÖZ KESİTİNİ AL (CROP) ---
                all_eye_landmarks = [33, 133, 159, 145, 362, 263, 386, 374]
                min_x = int(min([landmarks.landmark[idx].x for idx in all_eye_landmarks]) * cam_w)
                max_x = int(max([landmarks.landmark[idx].x for idx in all_eye_landmarks]) * cam_w)
                min_y = int(min([landmarks.landmark[idx].y for idx in all_eye_landmarks]) * cam_h)
                max_y = int(max([landmarks.landmark[idx].y for idx in all_eye_landmarks]) * cam_h)
                
                padding_x = 60
                padding_y = 50
                c_min_x = max(0, min_x - padding_x)
                c_max_x = min(cam_w, max_x + padding_x)
                c_min_y = max(0, min_y - padding_y)
                c_max_y = min(cam_h, max_y + padding_y)
                
                eye_crop = frame[c_min_y:c_max_y, c_min_x:c_max_x]
                
                if eye_crop.shape[0] > 0 and eye_crop.shape[1] > 0:
                    eye_crop_resized = cv2.resize(eye_crop, (display_w, display_h))
                    
                    if flash_frames > 0:
                        # Ekranı beyaz ile parlat (Köşe değiştiğini belli et)
                        eye_crop_resized[:] = (255, 255, 255)
                        flash_frames -= 1
                    else:
                        draw_ui_panel(eye_crop_resized, (0, 0), (display_w, 80), (0,0,0), 0.7)
                        cv2.putText(eye_crop_resized, f"Yatay Oran: {raw_h_ratio:.3f}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        cv2.putText(eye_crop_resized, f"Dikey Oran: {raw_v_ratio:.3f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        cv2.putText(eye_crop_resized, "TIKLAMA GECICI OLARAK DEVRE DISI", (display_w - 400, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
                        
                        if sync_msg != "":
                            cv2.putText(eye_crop_resized, sync_msg, (display_w//2 - 250, display_h - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
                    
                    cv2.imshow('Argus Goz Kamerasi', eye_crop_resized)
            else:
                blank_image = np.zeros((300, 800, 3), np.uint8)
                cv2.putText(blank_image, "Yuz Bulunamadi...", (300, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.imshow('Argus Goz Kamerasi', blank_image)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                sync_active = True
                sync_start_time = time.time()
                calib_h_min, calib_h_max = 1.0, 0.0
                calib_v_min, calib_v_max = 1.0, 0.0
                calib_face_widths = []

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
