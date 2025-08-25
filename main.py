import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import whisper

app = FastAPI(title="Whisper Transcriber")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
CACHE_DIR = os.getenv("WHISPER_CACHE", "/tmp")
MODEL = None

def get_model():
    global MODEL
    if MODEL is None:
        MODEL = whisper.load_model(WHISPER_MODEL, download_root=CACHE_DIR)
    return MODEL

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), language: str | None = None, task: str = "transcribe"):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    suffix = os.path.splitext(file.filename)[1] or ".bin"

    # Save upload to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        model = get_model()
        result = model.transcribe(tmp_path, language=language, task=task, verbose=False)
        segments = [
            {"start": float(s["start"]), "end": float(s["end"]), "text": s["text"]}
            for s in result.get("segments", [])
        ]
        return JSONResponse({
            "language": result.get("language"),
            "text": result.get("text"),
            "segments": segments  # <- time => subtitle payload
        })
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
