from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .resume_parser import extract_text
from .llm_client import analyze_resume
from .schemas import ResumeInsightsResponse

app = FastAPI(title="Resume Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/process-resume", response_model=ResumeInsightsResponse)
async def process_resume(
    api_key: str = Form(..., description="OpenAI API key"),
    file: UploadFile = File(..., description="Resume file (.pdf or .docx)"),
) -> ResumeInsightsResponse:
    try:
        resume_text = extract_text(file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read resume: {exc}") from exc
    finally:
        await file.close()

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume appears to be empty")

    try:
        insights = analyze_resume(api_key=api_key, resume_text=resume_text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Model error: {exc}") from exc

    return ResumeInsightsResponse.from_dataclass(insights)
