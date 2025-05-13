from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image, UnidentifiedImageError
import io
from utils import extract_plate_data, preprocess_image

app = FastAPI()

ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

@app.post("/scan")
async def scan_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado. Usa .jpg, .png, .jpeg, .bmp, .tiff")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")  # Asegura que se pueda procesar correctamente
        data = extract_plate_data(image)
        return JSONResponse(content=data)
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="No se pudo abrir la imagen. Verifica que sea un archivo válido.")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/preview")
async def preview_processed(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado. Usa .jpg, .png, .jpeg, .bmp, .tiff")

    try:
        contents = await file.read()
        original = Image.open(io.BytesIO(contents)).convert("RGB")
        processed = preprocess_image(original)

        img_bytes = io.BytesIO()
        processed.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return StreamingResponse(img_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo procesar la imagen: {str(e)}")
