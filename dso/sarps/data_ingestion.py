"""Module 1 - Data Ingestion & Privacy.
Loads student records (CSV) or generates a synthetic dataset, validates the
schema, and pseudonymises identifiers so no personal data enters the model."""
import hashlib
import os
import numpy as np
import pandas as pd

REQUIRED = ["student_id", "attendance_pct", "internal_marks", "assignment_completion",
            "prev_sem_gpa", "lms_logins_per_week", "backlogs", "study_hours_per_week"]
FEATURES = REQUIRED[1:]
# Secret salt comes from the environment in production; the default is for local demo only.
SALT = os.environ.get("SARPS_SALT", "sarps-demo-salt")


def pseudonymise(student_id: str) -> str:
    """One-way salted hash: model/dashboard never see the real roll number."""
    return "S" + hashlib.sha256((SALT + str(student_id)).encode()).hexdigest()[:8].upper()


def generate_synthetic(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    """Synthetic cohort (no real student data used -> privacy by design)."""
    rng = np.random.default_rng(seed)
    ability = rng.normal(0, 1, n)
    df = pd.DataFrame({
        "student_id": [f"R{i:04d}" for i in range(n)],
        "attendance_pct": np.clip(75 + 9 * ability + rng.normal(0, 8, n), 30, 100),
        "internal_marks": np.clip(60 + 10 * ability + rng.normal(0, 9, n), 5, 100),
        "assignment_completion": np.clip(78 + 10 * ability + rng.normal(0, 12, n), 0, 100),
        "prev_sem_gpa": np.clip(6.8 + 1.0 * ability + rng.normal(0, 0.6, n), 3, 10),
        "lms_logins_per_week": np.clip(np.round(8 + 3 * ability + rng.normal(0, 3, n)), 0, 30),
        "backlogs": np.clip(np.round(1.0 - 1.1 * ability + rng.normal(0, 1, n)), 0, 8),
        "study_hours_per_week": np.clip(10 + 3 * ability + rng.normal(0, 3.5, n), 0, 40),
    })
    score = (-0.06 * (df.attendance_pct - 70) - 0.05 * (df.internal_marks - 55)
             - 0.025 * (df.assignment_completion - 70) - 0.5 * (df.prev_sem_gpa - 6.5)
             + 0.45 * df.backlogs - 0.04 * (df.study_hours_per_week - 9)
             - 0.03 * (df.lms_logins_per_week - 7) + rng.normal(0, 0.9, n))
    df["at_risk"] = (score > np.quantile(score, 0.72)).astype(int)
    return df


def validate_and_hash(df: pd.DataFrame) -> pd.DataFrame:
    """Check required columns, keep only needed ones, hash IDs."""
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    keep = REQUIRED + (["at_risk"] if "at_risk" in df.columns else [])
    df = df[keep].copy()              # drop any extra (possibly personal) columns
    df["student_id"] = df["student_id"].map(pseudonymise)
    return df


def load_data(path: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(path) if path else generate_synthetic()
    return validate_and_hash(df)
