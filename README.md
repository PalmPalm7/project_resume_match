# Resume Intelligence Platform

This project provides a full-stack prototype for extracting resume content (PDF or DOCX),
parsing it with OpenAI for named-entity recognition, and presenting the results on a
modern dashboard inspired by HR screening matrices.

## Project Structure

```
backend/   # FastAPI service that extracts resume text and queries OpenAI
frontend/  # React + Vite single page app for uploading resumes and visualizing results
```

## Features

- Resume text extraction using PDF/DOCX readers with optional Docling integration.
- OpenAI-powered analysis that returns structured candidate insights, including strengths
  and weaknesses.
- Responsive UI with API key input, resume upload, and rich matrix visualization.

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API exposes `POST /api/process-resume` and expects a multipart form with fields:

- `api_key`: your OpenAI API key (not stored by the server).
- `file`: PDF or DOCX resume file.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Create a `.env` file in `frontend/` if you need to change the backend base URL:

```
VITE_API_BASE_URL=http://localhost:8000
```

### Optional Docling Support

If you have [`docling`](https://github.com/OpenSourceDocling/docling) available, install
it alongside the backend requirements to enable higher-fidelity document parsing.

```bash
pip install docling
```

## OpenAI Model

The backend defaults to `gpt-4o-mini` for a balance between cost and quality. Update the
`analyze_resume` function if you prefer a different model.

## License

MIT
