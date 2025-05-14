from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import io
from utils import preprocess_image, extract_plate_data

app = FastAPI()

@app.post("/scan")
async def scan_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        original = Image.open(io.BytesIO(contents)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Imagen no válida o corrupta")

    # Procesar imagen
    processed = preprocess_image(original)

    # Extraer datos y texto OCR usando EasyOCR
    result = extract_plate_data(processed)

    return JSONResponse(content=result)
