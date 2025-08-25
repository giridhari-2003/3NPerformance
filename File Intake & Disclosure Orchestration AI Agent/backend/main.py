import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
from fastapi.encoders import jsonable_encoder
from Quality_evaluater import analyze_document_quality_file  # import your function

app = FastAPI(title="Document Quality API", version="1.0")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run analysis
        report = analyze_document_quality_file(str(file_path))
        report = jsonable_encoder(report)

        return JSONResponse(content=report)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        # Cleanup uploaded file after processing
        if file_path.exists():
            os.remove(file_path)


@app.get("/")
async def root():
    return {"message": "Document Quality API is running"}
