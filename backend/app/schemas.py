"""Pydantic models for API responses."""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    start_year: str = ""
    end_year: str = ""
    highlights: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    company: str = ""
    role: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = Field(default_factory=list)
    skills_demonstrated: list[str] = Field(default_factory=list)


class SkillsMatrix(BaseModel):
    core: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class ResumeInsightsResponse(BaseModel):
    candidate_name: str = ""
    headline: str = ""
    contact_information: str = ""
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    skills: SkillsMatrix = Field(default_factory=SkillsMatrix)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    overall_summary: str = ""

    @classmethod
    def from_dataclass(cls, data: Any) -> "ResumeInsightsResponse":
        return cls(**data.__dict__)
