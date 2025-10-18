import os
from functools import lru_cache
from typing import Any, Dict
import importlib.util

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv()

_openai_spec = importlib.util.find_spec("openai")
if _openai_spec is not None:  # pragma: no branch - module availability check
    from openai import OpenAI
else:  # pragma: no cover - dependency guard
    OpenAI = None  # type: ignore


class MissingOpenAIClient(RuntimeError):
    """Raised when the OpenAI client is unavailable."""


def create_client() -> "OpenAI":
    """Create a cached OpenAI client instance.

    Raises:
        MissingOpenAIClient: If the OpenAI package is unavailable.
        RuntimeError: If the API key is missing.
    """

    if OpenAI is None:
        raise MissingOpenAIClient(
            "The openai package is required. Install dependencies with 'pip install -r requirements.txt'."
        )

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable not set. "
            "Set it before starting the server."
        )

    return OpenAI(api_key=api_key)


@lru_cache(maxsize=1)
def get_client() -> "OpenAI":
    """Return a cached OpenAI client."""

    return create_client()


def build_prompt(resume_text: str, job_description: str | None) -> str:
    """Build the instruction prompt for the language model."""

    jd_section = f"\nJob Description:\n{job_description.strip()}" if job_description else ""
    return (
        "You are an assistant that evaluates resumes for hiring teams. "
        "Extract the most relevant skills, strengths, weaknesses, and readiness for the role. "
        "Return JSON only, matching this schema strictly: \n"
        "{\n"
        "  \"candidate_name\": string | null,\n"
        "  \"overall_summary\": string,\n"
        "  \"tags\": [ { \"label\": string, \"score\": number (0-5), \"status\": \"strong\"|\"medium\"|\"weak\" } ],\n"
        "  \"skills\": [ { \"category\": string, \"strengths\": [string], \"weaknesses\": [string], \"score\": number (0-5) } ],\n"
        "  \"recommendations\": [string]\n"
        "}\n"
        "Scores should be numbers. Provide at most 6 tags and 8 skill categories. "
        "Do not include any additional text.\n\n"
        "Resume:\n"
        f"{resume_text.strip()}"
        f"{jd_section}\n"
    )


def parse_resume(resume_text: str, job_description: str | None = None) -> Dict[str, Any]:
    """Send the resume to the OpenAI API and parse the JSON response."""

    client = get_client()
    prompt = build_prompt(resume_text, job_description)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        response_format={"type": "json_object"},
    )

    content = response.output[0].content[0].text  # type: ignore[index]

    import json

    return json.loads(content)


def create_app() -> Flask:
    """Application factory for easier testing."""

    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    @app.post("/api/parse_resume")
    def api_parse_resume():
        payload = request.get_json(silent=True) or {}
        resume_text = payload.get("resumeText", "").strip()
        job_description = payload.get("jobDescription", "").strip() or None

        if not resume_text:
            return jsonify({"error": "Resume text is required."}), 400

        try:
            parsed = parse_resume(resume_text, job_description)
        except MissingOpenAIClient as exc:  # pragma: no cover - runtime guard
            return jsonify({"error": str(exc)}), 500
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 500
        except Exception as exc:  # pragma: no cover - unexpected errors
            return jsonify({"error": f"Failed to parse resume: {exc}"}), 500

        return jsonify(parsed)

    return app


if __name__ == "__main__":  # pragma: no cover
    create_app().run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
