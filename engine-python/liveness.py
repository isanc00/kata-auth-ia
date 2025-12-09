import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

def euclidean_distance(point1, point2):
    x1, y1 = point1.ravel()
    x2, y2 = point2.ravel()
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def get_blink_ratio(img, landmarks, right_indices, left_indices):

    rh_right = landmarks[right_indices[0]]
    rh_left = landmarks[right_indices[3]]

    rv_top = landmarks[right_indices[1]]
    rv_bottom = landmarks[right_indices[5]]

    lh_right = landmarks[left_indices[0]]
    lh_left = landmarks[left_indices[3]]

    lv_top = landmarks[left_indices[1]]
    lv_bottom = landmarks[left_indices[5]]

    rh_dist = euclidean_distance(rh_right, rh_left)
    rv_dist = euclidean_distance(rv_top, rv_bottom)

    lh_dist = euclidean_distance(lh_right, lh_left)
    lv_dist = euclidean_distance(lv_top, lv_bottom)


    re_ratio = rh_dist / rv_dist
    le_ratio = lh_dist / lv_dist
    
    ratio = (re_ratio + le_ratio) / 2
    return ratio

def check_liveness(image_np):
    """
    Recibe una imagen en numpy array.
    Retorna un diccionario con el resultado del análisis.
    """
    results = face_mesh.process(image_np)
    
    if not results.multi_face_landmarks:
        return {"detected": False, "message": "No se detectó rostro"}

    mesh_coords = []
    h, w = image_np.shape[:2]
    

    for face_landmarks in results.multi_face_landmarks:
        for lm in face_landmarks.landmark:
            x, y = int(lm.x * w), int(lm.y * h)
            mesh_coords.append([x, y])
            
    mesh_coords = np.array(mesh_coords)
    
    ratio = get_blink_ratio(image_np, mesh_coords, RIGHT_EYE, LEFT_EYE)
    
    is_blinking = ratio > 4.5 
    
    return {
        "detected": True, 
        "blink_ratio": round(ratio, 2), 
        "is_blinking": bool(is_blinking),
        "message": "Ojos cerrados/parpadeo detectado" if is_blinking else "Ojos abiertos"
    }