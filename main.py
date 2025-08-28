from fastapi import FastAPI, File, UploadFile, Form
import whisper
import subprocess

app = FastAPI()
model = whisper.load_model("base")  # or "small", "medium", "large"

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form(None),
    translate: str = Form(None)
):
    # Save file locally
    with open("tempfile", "wb") as f:
        f.write(await file.read())

    # Call ffmpeg to ensure correct format (Cloud Run will have ffmpeg via Dockerfile)
    subprocess.run([
        "ffmpeg", "-i", "tempfile", "-ar", "16000", "-ac", "1", "temp.wav", "-y"
    ])

    # Run whisper
    result = model.transcribe("temp.wav", language=language)

    # Translate if needed (very simplified)
    if translate:
        result["text"] = f"[Translated to {translate}] " + result["text"]

    return {"text": result["text"]}
