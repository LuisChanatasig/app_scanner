import cv2 
import numpy as np
import pytesseract

# Ruta del ejecutable de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ordenar_puntos(puntos):

# Leer imagen (con extensión)
image = cv2.imread('Anverso_Matricula.jpg')  # ← Cambiar según el nombre real del archivo

# Verifica si la imagen fue cargada
if image is None:
    print("Error: no se pudo cargar la imagen. Verifica el nombre o la ruta.")
else:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    canny = cv2.Canny(gray, 10, 150)
    canny = cv2.dilate(canny, None, iterations=1)

    # CORREGIDO: CHAIN_APPROX_SIMPLE
    cnts = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]

    for c in cnts:
        epsilon = 0.01 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)

        if len(approx) == 4:
            # CORREGIDO: usar 'approx' no 'aprox'
            cv2.drawContours(image, [approx], 0, (0, 255, 255), 2)

            cv2.circle(image, tuple(approx[1][0]),7,(255,0,0),2)
            cv2.circle(image, tuple(approx[0][0]),7,(0,255,0),2)
            cv2.circle(image, tuple(approx[2][0]),7,(0,0,255),2)
            cv2.circle(image, tuple(approx[3][0]),7,(255,255,0),2)

            pts1 = np.float32([approx[1][0],approx[0][0],approx[2][0],approx[3][0]])
            pts2 = np.float32([[0,0],[270,0],[0,310],[270,310]])
            M = cv2.getPerspectiveTransform(pts1,pts2)
            dst = cv2.warpPerspective(gray,M,(270,310))
            cv2.imshow('dst',dst)



    cv2.imshow('Imagen Original', image)
    cv2.imshow('Bordes - Canny', canny)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
