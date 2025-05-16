import cv2
import pytesseract
import json

# Ruta de tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Función para extraer texto de una región
def ocr_region(img, coords, nombre=""):
    y, x, h, w = coords
    recorte = img[y:y+h, x:x+w]
    texto = pytesseract.image_to_string(recorte, lang='spa', config='--psm 7')
    return texto.strip()

# Cargar imagen original sin perspectiva
image = cv2.imread("Anverso_Matricula.jpg")
if image is None:
    print("Error: imagen no encontrada.")
    exit()

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Diccionario de coordenadas de campos: (y, x, alto, ancho)
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

# Colores distintos para cada campo (predefinidos)
colores = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 0, 128),
    (255, 165, 0),
    (0, 128, 255),
    (128, 255, 0),
    (255, 0, 128),
    (0, 100, 0),
    (100, 0, 100),
    (100, 100, 0),
    (0, 0, 128),
    (139, 69, 19),
    (70, 130, 180),
    (199, 21, 133),
    (220, 20, 60),
    (0, 191, 255),
    (154, 205, 50),
    (0, 0, 0),
    (255, 105, 180)  

]



# Extraer cada campo
datos = {}
for campo, coords in zonas.items():
    texto = ocr_region(gray, coords, campo)
    datos[campo] = texto

# Mostrar resultado
print("\n✅ JSON estructurado:\n")
print(json.dumps(datos, indent=4, ensure_ascii=False))

# Guardar JSON
with open("matricula_segmentada.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, indent=4, ensure_ascii=False)

# Mostrar imagen recortada con colores únicos
for (campo, coords), color in zip(zonas.items(), colores):
    y, x, h, w = coords
    cv2.rectangle(image, (x, y), (x + w, y + h), color, 1)
    cv2.putText(image, campo, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

cv2.imshow("Zonas detectadas", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
