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


class RetrievedContext(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    year: int
    section: str
    topic: str
    text: str
    score: float


class SourceReference(BaseModel):
    doc_id: str
    title: str
    year: int
    chunk_id: str | None = None
    section: str | None = None


class ExerciseEntry(BaseModel):
    name: str
    movement_pattern: str
    sets: int = Field(ge=1, le=8)
    reps: str
    target_intensity: str
    rest_seconds: int = Field(ge=30, le=300)
    tempo_optional: str | None = None
    substitution_options: list[str] = Field(default_factory=list)
    restriction_flags: list[str] = Field(default_factory=list)
    equipment_required: list[str] = Field(default_factory=list)
    notes_optional: str | None = None


class TrainingSession(BaseModel):
    day: str
    session_goal: str
    estimated_duration_min: int = Field(ge=10, le=180)
    warmup_notes: list[str] = Field(default_factory=list)
    exercises: list[ExerciseEntry] = Field(default_factory=list)
    session_notes: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def non_empty_exercises(self) -> "TrainingSession":
        if not self.exercises:
            raise ValueError("Each session must include at least one exercise.")
        return self


class PlanWeek(BaseModel):
    week_number: int = Field(ge=1, le=4)
    focus: str
    sessions: list[TrainingSession]


class ValidationIssue(BaseModel):
    code: str
    severity: Literal["warning", "error"]
    message: str
    location: str | None = None


class ValidationReport(BaseModel):
    status: Literal["passed", "passed_with_warnings", "failed"]
    issues: list[ValidationIssue] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    repair_attempted: bool = False
    repair_actions: list[str] = Field(default_factory=list)

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]


class TrainingPlan(BaseModel):
    user_summary: str
    safety_notes: list[str]
    plan_duration_weeks: int = Field(default=4, ge=1, le=12)
    weekly_schedule: list[PlanWeek]
    sources_used: list[SourceReference] = Field(default_factory=list)
    validation_status: str = "pending"
    validation_warnings: list[str] = Field(default_factory=list)
    generation_mode: ExperimentMode
    repair_applied: bool = False
    retrieval_query: str | None = None
    retrieved_context: list[RetrievedContext] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def four_week_default(self) -> "TrainingPlan":
        if self.plan_duration_weeks != len(self.weekly_schedule):
            raise ValueError("plan_duration_weeks must match weekly_schedule length.")
        return self

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)


class GenerationTrace(BaseModel):
    prompt: str
    raw_output: str
    retrieval_query: str | None = None
    repaired_output: str | None = None
    used_fallback_generator: bool = False
    model_used: str | None = None


class PipelineResult(BaseModel):
    profile: UserProfile
    mode: ExperimentMode
    plan: TrainingPlan
    validation: ValidationReport
    trace: GenerationTrace

    def to_log_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.model_dump(mode="json"),
            "mode": self.mode.value,
            "plan": self.plan.model_dump(mode="json"),
            "validation": self.validation.model_dump(mode="json"),
            "trace": self.trace.model_dump(mode="json"),
        }


def extract_json_object(raw_text: str) -> str:
    raw_text = raw_text.strip()
    if not raw_text:
        raise ValueError("The model returned empty output.")
    if raw_text.startswith("{") and raw_text.endswith("}"):
        return raw_text
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")
    candidate = raw_text[start : end + 1]
    json.loads(candidate)
    return candidate

