import io
import pytest
from app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app(); app.config["TESTING"] = True
    return app.test_client()


def csv_bytes(extra_col=False, drop=None):
    cols = ["student_id", "attendance_pct", "internal_marks", "assignment_completion", "prev_sem_gpa",
            "lms_logins_per_week", "backlogs", "study_hours_per_week"]
    if drop: cols.remove(drop)
    head = ",".join(cols + (["student_name"] if extra_col else []))
    row = ",".join(["R1", "55", "40", "45", "5.2", "3", "4", "4"][:len(cols)] + (["Secret Name"] if extra_col else []))
    return (head + "\n" + row + "\n").encode()


def test_home_ok(client):
    r = client.get("/"); assert r.status_code == 200 and b"Risk Dashboard" in r.data


def test_health(client):
    assert client.get("/health").get_json()["status"] == "ok"


def test_api_summary_totals(client):
    s = client.get("/api/summary").get_json(); assert s["total"] == s["High"] + s["Medium"] + s["Low"]


def test_security_headers(client):
    h = client.get("/").headers
    assert "default-src 'self'" in h["Content-Security-Policy"]
    assert h["X-Content-Type-Options"] == "nosniff" and h["X-Frame-Options"] == "DENY"


def test_upload_valid_and_ids_hashed(client):
    r = client.post("/analyze", data={"file": (io.BytesIO(csv_bytes()), "s.csv")}, content_type="multipart/form-data")
    assert r.status_code == 200 and b"R1" not in r.data and b"High" in r.data


def test_upload_drops_extra_personal_columns(client):
    r = client.post("/analyze", data={"file": (io.BytesIO(csv_bytes(extra_col=True)), "s.csv")}, content_type="multipart/form-data")
    assert r.status_code == 200 and b"Secret Name" not in r.data


def test_upload_missing_column_rejected(client):
    r = client.post("/analyze", data={"file": (io.BytesIO(csv_bytes(drop="backlogs")), "s.csv")}, content_type="multipart/form-data")
    assert r.status_code == 400 and b"Missing required columns" in r.data


def test_upload_wrong_extension_rejected(client):
    r = client.post("/analyze", data={"file": (io.BytesIO(b"x"), "evil.exe")}, content_type="multipart/form-data")
    assert r.status_code == 400


def test_upload_too_large_rejected(client):
    r = client.post("/analyze", data={"file": (io.BytesIO(b"a" * (1024 * 1024 + 10)), "big.csv")}, content_type="multipart/form-data")
    assert r.status_code == 413


def test_no_file_rejected(client):
    assert client.post("/analyze", data={}, content_type="multipart/form-data").status_code == 400


def test_html_is_escaped(client):
    row = csv_bytes().replace(b"R1", b"<script>alert(1)</script>")
    r = client.post("/analyze", data={"file": (io.BytesIO(row), "s.csv")}, content_type="multipart/form-data")
    assert b"<script>alert(1)</script>" not in r.data
