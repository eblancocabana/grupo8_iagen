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

