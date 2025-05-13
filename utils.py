import pytesseract
from PIL import Image
import cv2
import numpy as np
import re

# Descomenta esta línea solo si estás en Windows y Tesseract no está en el PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(pil_image: Image.Image) -> Image.Image:
    image = np.array(pil_image.convert('RGB'))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=15,
        C=8
    )
    return Image.fromarray(thresh)

def extract_plate_data(original_image: Image.Image) -> dict:
    image = preprocess_image(original_image)
    custom_config = r'--oem 3 --psm 6 -l spa'
    text = pytesseract.image_to_string(image, config=custom_config)

    print("\n=== TEXTO DETECTADO POR OCR ===\n", text, "\n==============================")

    lines = [line.strip().upper() for line in text.split('\n') if line.strip()]

    data = {
        "placa_actual": "",
        "placa_anterior": "",
        "año": "",
        "vin": "",
        "motor": "",
        "marca": "",
        "modelo": "",
        "clase": "",
        "tipo_vehiculo": "",
        "pais_origen": "",
        "combustible": "",
        "color_1": "",
        "color_2": "",
        "cilindraje": "",
        "pasajeros": "",
        "carroceria": "",
        "tipo_peso": "",
    }

    for line in lines:
        if "PLACA ACTUAL" in line:
            match = re.search(r'[A-Z]{3}[0-9]{3}[A-Z]?', line)
            if match:
                data["placa_actual"] = match.group()
        elif "PLACA ANTERIOR" in line:
            match = re.search(r'[A-Z]{3}[0-9]{3}[A-Z]?', line)
            if match:
                data["placa_anterior"] = match.group()
        elif "AÑO" in line:
            match = re.search(r'\b(19|20)\d{2}\b', line)
            if match:
                data["año"] = match.group()
        elif "CHASIS" in line or "VIN" in line:
            match = re.search(r'\b[A-Z0-9]{10,}\b', line)
            if match:
                data["vin"] = match.group()
        elif "MOTOR" in line:
            match = re.search(r'\b[A-Z0-9]{6,}\b', line)
            if match:
                data["motor"] = match.group()
        elif "MARCA" in line:
            data["marca"] = line.replace("MARCA", "").strip()
        elif "MODELO" in line:
            data["modelo"] = line.replace("MODELO", "").strip()
        elif "CLASE" in line:
            data["clase"] = line.replace("CLASE DE VEHÍCULO", "").replace("CLASE", "").strip()
        elif "TIPO DE VEHÍCULO" in line:
            data["tipo_vehiculo"] = line.replace("TIPO DE VEHÍCULO", "").strip()
        elif "ORIGEN" in line:
            data["pais_origen"] = line.split()[-1]
        elif "COMBUSTIBLE" in line:
            data["combustible"] = line.split()[-1]
        elif "COLOR 1" in line:
            data["color_1"] = line.replace("COLOR 1", "").strip()
        elif "COLOR 2" in line:
            data["color_2"] = line.replace("COLOR 2", "").strip()
        elif "CILINDRAJE" in line:
            match = re.search(r'\b[0-9]{2,4}\b', line)
            if match:
                data["cilindraje"] = match.group()
        elif "PASAJEROS" in line:
            match = re.search(r'\b[0-9]+\b', line)
            if match:
                data["pasajeros"] = match.group()
        elif "CARROCERÍA" in line or "CARROCERIA" in line:
            data["carroceria"] = line.split()[-1]
        elif "TIPO DE PESO" in line:
            data["tipo_peso"] = line.replace("TIPO DE PESO", "").strip()

    return data
