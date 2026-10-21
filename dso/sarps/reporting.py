"""Module 5 - Reporting: summaries and CSV export for faculty mentors."""
import pandas as pd


def summary(res: pd.DataFrame) -> dict:
    counts = res["risk_level"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
    return {"total": len(res), **counts.to_dict()}


def export_csv(res: pd.DataFrame) -> bytes:
    out = res.copy()
    out["reasons"] = out["reasons"].map("; ".join)
    out["suggested_actions"] = out["suggested_actions"].map("; ".join)
    return out.to_csv(index=False).encode()
