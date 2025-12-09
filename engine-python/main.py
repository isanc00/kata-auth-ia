from fastapi import FastAPI, UploadFile, File
import easyocr
import numpy as np
import cv2
from liveness import check_liveness # Importamos nuestra lógica

app = FastAPI()

# Cargamos el modelo OCR una sola vez al iniciar (puede tardar un poco)
print("Cargando modelo OCR... espere...")
reader = easyocr.Reader(['es'], gpu=False) 
print("Modelo OCR cargado.")

@app.get("/")
def health_check():
    return {"status": "IA Engine Ready", "model": "Python 3.9 + MediaPipe + EasyOCR"}

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...), type: str = "document"):
    """
    Endpoint único: Recibe imagen y tipo ('document' o 'face')
    """
    # 1. Leer la imagen recibida
    contents = await file.read()
    nparr = np.fromstring(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    response = {}

    # 2. Decidir qué hacer según el tipo
    if type == "face":
        # Análisis de Liveness (Parpadeo)
        liveness_result = check_liveness(img)
        response["liveness"] = liveness_result
        
    elif type == "document":
        # Análisis de OCR (Lectura de cédula)
        # detail=0 devuelve solo el texto, sin coordenadas
        text_result = reader.readtext(img, detail=0)
        response["ocr_text"] = text_result
        response["raw_text"] = " ".join(text_result) # Texto plano unido
        
    else:
        return {"error": "Tipo de análisis no válido. Use 'face' o 'document'"}

    return response