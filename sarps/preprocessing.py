"""Module 2 - Preprocessing: cleaning, range validation, scaling."""
import pandas as pd
from sklearn.preprocessing import StandardScaler
from .data_ingestion import FEATURES

RANGES = {"attendance_pct": (0, 100), "internal_marks": (0, 100), "assignment_completion": (0, 100),
          "prev_sem_gpa": (0, 10), "lms_logins_per_week": (0, 100), "backlogs": (0, 20),
          "study_hours_per_week": (0, 80)}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset="student_id").copy()
    for c in FEATURES:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df[c] = df[c].fillna(df[c].median())
        lo, hi = RANGES[c]
        df[c] = df[c].clip(lo, hi)
    return df


def fit_scaler(df: pd.DataFrame) -> StandardScaler:
    return StandardScaler().fit(df[FEATURES])
