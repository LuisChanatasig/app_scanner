import sys
import json
import pytesseract
from PIL import Image
import cv2
import numpy as np
import re

# (Tu configuración y funciones preprocess_image, clean_text, parse_ocr_text quedan igual)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def preprocess_image(pil_image: Image.Image) -> Image.Image:
    image = np.array(pil_image.convert('RGB'))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(bw)

def clean_text(text: str) -> str:
    replacements = {
        "GASOLNA": "GASOLINA",
        "COLOUB": "COLOMBIA",
        "COLOMB": "COLOMBIA",
        "OMGEN": "ORIGEN",
        "ORICEN": "ORIGEN",
        "ECUASOR": "ECUADOR",
        "MOVTIAD": "MOVILIDAD",
        "PUBLICA 0E": "PUBLICA DE"
    }
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    return text

def parse_ocr_text(ocr_text: str) -> dict:
    ocr_text = clean_text(ocr_text)
    lines = [line.strip() for line in ocr_text.upper().splitlines() if line.strip()]

    data = {
        "placa_actual": "",
        "placa_anterior": "",
        "año": "",
        "vin": "",
        "motor": "",
        "marca": "",
        "modelo": "",
        "cilindraje": "",
        "clase": "",
        "tipo_vehiculo": "",
        "pais_origen": "",
        "combustible": "",
        "color_1": "",
        "color_2": "",
        "pasajeros": "",
        "carroceria": "",
        "tipo_peso": "",
        "año_modelo": "",
        "observaciones": ""
    }

    # VIN (17 caracteres alfanum), quitando espacios
    vin_candidates = re.findall(r'([A-HJ-NPR-Z0-9]{17})', ocr_text.replace(" ", ""))
    if vin_candidates:
        data["vin"] = vin_candidates[0]

    # Placas estilo ECUADOR: 2–3 letras + 3–4 dígitos
    placas = re.findall(r'\b[A-Z]{2,3}[0-9]{3,4}\b', ocr_text)
    if placas:
        data["placa_actual"] = placas[0]
        if len(placas) > 1:
            data["placa_anterior"] = placas[1]

    # Año fabricación
    año_match = re.search(r'A[ÑN]O[\s:\-]*([0-9]{4})', ocr_text)
    if año_match:
        data["año"] = año_match.group(1)

    # Año modelo
    modelo_match = re.search(r'A[ÑN]O MODELO[\s:\-]*([0-9]{4})', ocr_text)
    if modelo_match:
        data["año_modelo"] = modelo_match.group(1)

    for line in lines:
        if any(make in line for make in ["CHEVROLET", "TOYOTA", "HYUNDAI", "KIA", "FORD", "MAZDA"]):
            parts = line.split()
            data["marca"] = parts[0]
            data["modelo"] = " ".join(parts[1:]) if len(parts) > 1 else ""
            continue

        if "GASOLINA" in line or "DIESEL" in line or "ELECTRICO" in line:
            data["combustible"] = ("GASOLINA" if "GASOLINA" in line 
                                   else "DIESEL" if "DIESEL" in line 
                                   else "ELECTRICO")
            continue

        if any(c in line for c in ["COLOMBIA", "JAPON", "ECUADOR", "ALEMANIA"]):
            data["pais_origen"] = line
            continue

        if "SEDAN" in line or "JEEP" in line:
            data["tipo_vehiculo"] = line
        if "AUTOMOVIL" in line or "MOTOCICLETA" in line:
            data["clase"] = line
        if "GRAVAMEN" in line:
            data["observaciones"] = line
        if re.fullmatch(r"[0-9]{3,4}", line) and not data["cilindraje"]:
            data["cilindraje"] = line
        if "METALICA" in line or "FIBRA" in line:
            data["carroceria"] = line
        if "LIVIANO" in line or "PESADO" in line:
            data["tipo_peso"] = line
        if any(col in line for col in ["PLATA", "NEGRO", "BLANCO", "PLOMO", "GRIS"]):
            if not data["color_1"]:
                data["color_1"] = line
            elif not data["color_2"]:
                data["color_2"] = line
        if re.fullmatch(r"\d+", line):
            data["pasajeros"] = line
        if re.match(r'[A-Z0-9]{8,}', line) and not data["motor"] and "CHASIS" not in line:
            data["motor"] = line

    return data

def extract_plate_data(image: Image.Image) -> dict:
    # opcional: image = preprocess_image(image)
    ocr_text = pytesseract.image_to_string(image, lang='spa')
    return parse_ocr_text(ocr_text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python ocr_plate.py ruta/a/la/imagen.png")
        sys.exit(1)

    img_path = sys.argv[1]
    img = Image.open(img_path)
    # img = preprocess_image(img)   # descomenta si quieres aplicar binarización
    resultado = extract_plate_data(img)

    # Imprime JSON bonito en consola
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
