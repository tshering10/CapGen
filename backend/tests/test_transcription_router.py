from io import BytesIO

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_rejects_unsupported_video_format():
    response = client.post(
        "/api/transcription/transcribe",
        files={"video": ("sample.txt", BytesIO(b"not a video"), "text/plain")},
    )

    assert response.status_code == 415
