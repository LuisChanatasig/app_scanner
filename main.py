import cv2
import pytesseract
import json
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI()

# Coordenadas de los campos
zonas = {
    "placa_actual": (150, 60, 40, 110),
    "placa_anterior": (155, 320, 20, 50),
    "anio": (160, 530, 30, 100),
    "vin": (220, 60, 14, 125),
    "numero_motor": (220, 305, 20, 110),
    "ramv_cpn": (220, 520, 20, 110),
    "marca": (260, 90, 20, 120),
    "modelo": (260, 240, 20, 200),
    "cilindraje": (260, 500, 20, 50),
    "anio_modelo": (260, 610, 20, 50),
    "clase_vehiculo": (300, 90, 20, 120),
    "tipo_vehiculo": (300, 250, 30, 200),
    "pasajeros": (300, 510, 20, 10),
    "toneladas": (300, 615, 20, 20),
    "pais_origen": (350, 90, 20, 120),
    "combustible": (350, 250, 20, 200),
    "carroceria": (350, 470, 20, 90),
    "tipo_de_peso": (350, 570, 20, 110),
    "color_1": (390, 90, 20, 120),
    "color_2": (390, 320, 20, 120),
    "ortopedico": (390, 500, 20, 50),
    "remarcado": (390, 610, 20, 30),
    "observaciones": (425, 90, 30, 500)
}

# Función OCR por región
def ocr_region(img, coords):
    y, x, h, w = coords
    recorte = img[y:y+h, x:x+w]
    texto = pytesseract.image_to_string(recorte, lang='spa', config='--psm 7')
    return texto.strip()

@app.post("/scan/")
async def scan_matricula(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = np.array(pil_image)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        datos = {}
        for campo, coords in zonas.items():
            datos[campo] = ocr_region(gray, coords)

        return JSONResponse(content=datos)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
