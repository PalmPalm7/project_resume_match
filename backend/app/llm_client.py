"""Client helpers for sending resume text to the LLM."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openai import OpenAI

SYSTEM_PROMPT = """You are an assistant that performs resume parsing for HR teams.
Return valid JSON that follows the schema provided in the user message. Do not include
any additional commentary.
"""

USER_PROMPT_TEMPLATE = """
You will be given the text extracted from a candidate resume. Extract structured
information and rate the candidate's strengths and weaknesses.

Return JSON using this schema:
{
  "candidate_name": string,
  "headline": string,
  "contact_information": string,
  "education": [
    {
      "institution": string,
      "degree": string,
      "start_year": string,
      "end_year": string,
      "highlights": [string]
    }
  ],
  "experience": [
    {
      "company": string,
      "role": string,
      "start_date": string,
      "end_date": string,
      "highlights": [string],
      "skills_demonstrated": [string]
    }
  ],
  "skills": {
      "core": [string],
      "tools": [string]
  },
  "strengths": [string],
  "weaknesses": [string],
  "overall_summary": string
}

Resume text:
"""


@dataclass(slots=True)
class ResumeInsights:
    candidate_name: str
    headline: str
    contact_information: str
    education: list[dict[str, Any]]
    experience: list[dict[str, Any]]
    skills: dict[str, list[str]]
    strengths: list[str]
    weaknesses: list[str]
    overall_summary: str


def analyze_resume(api_key: str, resume_text: str, model: str = "gpt-4o-mini") -> ResumeInsights:
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE + resume_text,
            },
        ],
        temperature=0.2,
    )

    if not response.output:
        raise RuntimeError("No response from language model")

    message_content = response.output[0].content[0].text

    import json

    payload = json.loads(message_content)
    return ResumeInsights(**payload)
