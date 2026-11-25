from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from transcription.router import router as transcription_router
from subtitle_editor.router import router as subtitle_editor_router
from video_renderer.router import router as video_renderer_router
from jobs.router import router as jobs_router


app = FastAPI(title="CapGen API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(transcription_router)
app.include_router(subtitle_editor_router)
app.include_router(video_renderer_router)
app.include_router(jobs_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
