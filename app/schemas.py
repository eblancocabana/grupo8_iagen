from __future__ import annotations

import json
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class ExperienceLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class Goal(str, Enum):
    strength = "strength"
    hypertrophy = "hypertrophy"
    general_health = "general_health"


class EquipmentType(str, Enum):
    gym = "gym"
    home_basic = "home_basic"
    bodyweight = "bodyweight"


class MovementRestriction(str, Enum):
    avoid_deep_knee_flexion = "avoid_deep_knee_flexion"
    avoid_high_impact = "avoid_high_impact"
    avoid_loaded_lumbar_flexion = "avoid_loaded_lumbar_flexion"
    avoid_overhead_pressing = "avoid_overhead_pressing"


class ExperimentMode(str, Enum):
    baseline_no_rag = "baseline_no_rag"
    rag_only = "rag_only"
    rag_plus_validation = "rag_plus_validation"


class UserProfile(BaseModel):
    profile_id: str | None = None
    age: int = Field(ge=18, le=60)
    experience_level: ExperienceLevel
    goal: Goal
    days_per_week: int = Field(ge=1, le=6)
    session_duration_min: int = Field(ge=20, le=120)
    equipment: EquipmentType
    movement_restrictions: list[MovementRestriction] = Field(default_factory=list)
    exercise_preferences: list[str] = Field(default_factory=list)
    notes_optional: str | None = None

    @field_validator("movement_restrictions")
    @classmethod
    def unique_restrictions(cls, values: list[MovementRestriction]) -> list[MovementRestriction]:
        return list(dict.fromkeys(values))

    def short_summary(self) -> str:
        restrictions = ", ".join(item.value for item in self.movement_restrictions) or "none"
        return (
            f"{self.experience_level.value} user focused on {self.goal.value}, "
            f"{self.days_per_week} days/week, {self.session_duration_min} min sessions, "
            f"equipment={self.equipment.value}, restrictions={restrictions}"
        )


class DocumentMetadata(BaseModel):
    doc_id: str
    title: str
    year: int
    language: str
    source_type: str
    topic: str
    filepath: str
    inclusion_reason: str


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    section: str
    page: int | None = None
    text: str
    topic: str
    evidence_level: str
    title: str
    year: int


