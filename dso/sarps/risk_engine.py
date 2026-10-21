"""Module 4 - Risk Engine: probability -> risk band + explainable reasons + advice."""
import pandas as pd
from .data_ingestion import FEATURES

LOW, HIGH = 0.35, 0.65
# Plain-language rules used to explain a prediction (transparency / ethics).
THRESHOLDS = {
    "attendance_pct": ("below", 75, "Attendance is below 75%"),
    "internal_marks": ("below", 50, "Internal marks are below 50"),
    "assignment_completion": ("below", 60, "Assignment completion is below 60%"),
    "prev_sem_gpa": ("below", 6.0, "Previous semester GPA is below 6.0"),
    "lms_logins_per_week": ("below", 4, "Low LMS engagement (<4 logins/week)"),
    "backlogs": ("above", 2, "More than 2 backlogs"),
    "study_hours_per_week": ("below", 6, "Study time below 6 hrs/week"),
}
ADVICE = {
    "attendance_pct": "Mentor meeting to discuss attendance barriers",
    "internal_marks": "Assign peer tutoring / remedial session",
    "assignment_completion": "Set up assignment tracking with deadlines",
    "prev_sem_gpa": "Academic counselling on study strategy",
    "lms_logins_per_week": "Encourage regular use of course LMS",
    "backlogs": "Backlog clearance plan with faculty advisor",
    "study_hours_per_week": "Time-management workshop",
}


def band(p: float) -> str:
    return "High" if p >= HIGH else "Medium" if p >= LOW else "Low"


def _triggered(row):
    return [f for f, (d, t, _) in THRESHOLDS.items()
            if (d == "below" and row[f] < t) or (d == "above" and row[f] > t)]


def reasons(row) -> list[str]:
    return [THRESHOLDS[f][2] for f in _triggered(row)]


def assess(model, df: pd.DataFrame) -> pd.DataFrame:
    res = df[["student_id"]].copy()
    res["risk_probability"] = model.predict_proba(df[FEATURES])[:, 1].round(3)
    res["risk_level"] = res["risk_probability"].map(band)
    res["reasons"] = [reasons(r) for _, r in df.iterrows()]
    res["suggested_actions"] = [[ADVICE[f] for f in _triggered(r)] for _, r in df.iterrows()]
    return res
