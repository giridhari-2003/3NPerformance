import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
from fastapi.encoders import jsonable_encoder
from Quaity_evaluater import analyze_document_quality_file,summarize_quality_report

app = FastAPI(title="Document Quality API", version="1.0")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Runing analysis
        detailed_report = analyze_document_quality_file(str(file_path))
        print(detailed_report)
        summary = summarize_quality_report(detailed_report)

        return JSONResponse(content=summary)

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        if file_path.exists():
            os.remove(file_path)

@app.post("/analyze_with_score") 
async def analyze_document(file: UploadFile = File(...)): 
    try: 
        # Save uploaded file 
        file_path = UPLOAD_DIR / file.filename 
        with open(file_path, "wb") as buffer: 
            shutil.copyfileobj(file.file, buffer) # Run analysis 
            report = analyze_document_quality_file(str(file_path)) 
            report = jsonable_encoder(report) 
            return JSONResponse(content=report) 
    except Exception as e: 
        return JSONResponse(content={"error": str(e)}, status_code=500) 
    finally: 
        if file_path.exists(): 
            os.remove(file_path)

@app.post("/analyze_folder")
async def analyze_document_folder(folder_path: str = Form(...)):
    try:
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return JSONResponse(content={"error": f"Folder does not exist: {folder_path}"}, status_code=400)

        results = []
        for file_path in folder.glob("*"):
            if file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp", ".pdf"]:
                try:
                    # Use your existing functions (unchanged)
                    detailed_report = analyze_document_quality_file(str(file_path))
                    summary = summarize_quality_report(detailed_report)

                    results.append({
                        "file": str(file_path),
                        "summary": summary
                    })
                except Exception as e:
                    results.append({
                        "file": str(file_path),
                        "summary": {"quality_checker": "fail", "reason": str(e)}
                    })

        return JSONResponse(content={"results": results})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
async def root():
    return {"message": "Document Quality API is running"}
