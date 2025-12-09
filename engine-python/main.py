from fastapi import FastAPI
import easyocr
import cv2
import numpy as np
from liveness import check_liveness

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "MicroServicio IA en linea"}