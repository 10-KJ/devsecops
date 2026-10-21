import pandas as pd, pytest
from sarps import data_ingestion as di, preprocessing as pp, model as mdl, risk_engine as re_, reporting as rp


@pytest.fixture(scope="module")
def df():
    return pp.clean(di.load_data())


def test_pseudonymise_deterministic_and_hides_id():
    a = di.pseudonymise("R0001")
    assert a == di.pseudonymise("R0001") and "R0001" not in a and a != di.pseudonymise("R0002")


def test_missing_column_rejected(tmp_path):
    p = tmp_path / "x.csv"; pd.DataFrame({"student_id": [1]}).to_csv(p, index=False)
    with pytest.raises(ValueError):
        di.load_data(str(p))


def test_clean_fills_and_clips():
    d = di.generate_synthetic(50); d.loc[0, "attendance_pct"] = None; d.loc[1, "internal_marks"] = 400
    d = pp.clean(di.load_data.__globals__["pd"].DataFrame(d).assign(student_id=lambda x: x.student_id.map(di.pseudonymise)))
    assert d.attendance_pct.notna().all() and d.internal_marks.max() <= 100


def test_no_sensitive_features():
    for bad in ("gender", "caste", "religion", "income", "address"):
        assert bad not in di.FEATURES


def test_model_quality(df):
    _, _, res, _ = mdl.train(df)
    assert max(v["roc_auc"] for v in res.values()) > 0.9


def test_risk_band_boundaries():
    assert re_.band(0.1) == "Low" and re_.band(0.5) == "Medium" and re_.band(0.9) == "High"


def test_assess_and_reasons(df):
    m, *_ = mdl.train(df)
    r = re_.assess(m, df)
    assert len(r) == len(df) and set(r.risk_level) <= {"Low", "Medium", "High"}
    weak = df.iloc[0].copy(); weak["attendance_pct"] = 40
    assert "Attendance is below 75%" in re_.reasons(weak)


def test_export(df):
    m, *_ = mdl.train(df)
    assert b"risk_level" in rp.export_csv(re_.assess(m, df))
