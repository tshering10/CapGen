from fastapi import FastAPI

from transcription.router import router as transcription_router
from subtitle_editor.router import router as subtitle_editor_router


app = FastAPI(title="CapGen API", version="0.1.0")
app.include_router(transcription_router)
app.include_router(subtitle_editor_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
