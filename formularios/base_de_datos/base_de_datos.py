import os
import cv2
import imutils
import mediapipe as mp
from collections import deque

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

def ejecutar(nombre_carpeta):
    rutadata = "C:/Users/edwin/Documents/revisar/Interfaz-0.3/Interfaz_Eye_System/formularios/base_de_datos/Data"
    personadata = os.path.join(rutadata, nombre_carpeta)

    if not os.path.exists(personadata):
        print("Carpeta creada:", personadata)
        os.makedirs(personadata)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("Error al abrir la cámara")
        exit()

    faceclasif = cv2.CascadeClassifier(cv2.data.haarcascades + 'formularios/base_de_datos/haarcascade_frontalface_default.xml')
    count = 0
    
    # Buffer más simple usando deque
    last_detected = False
    fps_update_counter = 0
    current_fps = 0
    
    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        refine_landmarks=True) as face_mesh:
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error al leer frame")
                break

            frame = imutils.resize(frame, width=320)
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            auxframe = frame.copy()

            faces = faceclasif.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            # Actualizar FPS cada 30 frames
            fps_update_counter += 1
            if fps_update_counter >= 30:
                current_fps = int(cap.get(cv2.CAP_PROP_FPS))
                fps_update_counter = 0

            # Dibujar FPS en formato pequeño
            cv2.putText(frame, f"FPS:{current_fps}", (5, 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

            if len(faces) > 0:
                last_detected = True
                for (x, y, w, h) in faces:
                    padding = int(0.1 * w)
                    x1 = max(0, x - padding)
                    y1 = max(0, y - padding)
                    x2 = min(frame.shape[1], x + w + padding)
                    y2 = min(frame.shape[0], y + h + padding)
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    rostro = auxframe[y1:y2, x1:x2]
                    
                    if rostro.size > 0:
                        rostro = cv2.resize(rostro, (720, 720), interpolation=cv2.INTER_LANCZOS4)
                        
                        filename = f'rostro_{count}.jpg'
                        path = os.path.join(personadata, filename)
                        cv2.imwrite(path, rostro)
                        count += 1

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(frame_rgb)

                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            face_landmarks,
                            mp_face_mesh.FACEMESH_TESSELATION,
                            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=1),
                            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1))
            else:
                last_detected = False

            cv2.imshow("Captura de Rostros con Malla Facial", frame)
            k = cv2.waitKey(1) & 0xFF
            if k == 27 or count >= 200:
                break

    cap.release()
    cv2.destroyAllWindows()