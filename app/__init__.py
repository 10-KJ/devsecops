"""SARPS web application (Flask) - DevSecOps edition."""
import io
import logging
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sarps import data_ingestion as di, preprocessing as pp, model as mdl, risk_engine as re_, reporting as rp

MAX_UPLOAD_BYTES = 1 * 1024 * 1024   # 1 MB upload cap
MAX_ROWS = 5000                      # row cap to prevent resource exhaustion
SHOW_ROWS = 300                      # rows rendered in the table (highest risk first)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    try:
        model = mdl.load()
    except FileNotFoundError:
        model, *_ = mdl.train(pp.clean(di.load_data()))
        mdl.save(model)
    demo_df = pp.clean(di.load_data())

    def analyse(df):
        res = re_.assess(model, df)
        res = res.sort_values("risk_probability", ascending=False).reset_index(drop=True)
        return res, rp.summary(res)

    def render_result(res, summary, source):
        rows = res.head(SHOW_ROWS).to_dict("records")   # keep the page light
        return render_template("index.html", rows=rows, s=summary, source=source, cap=SHOW_ROWS)

    @app.after_request
    def secure_headers(resp):
        resp.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; form-action 'self'"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.get("/")
    def index():
        res, s = analyse(demo_df)
        return render_result(res, s, "Synthetic demo cohort (1,500 students)")

    @app.post("/analyze")
    def analyze():
        f = request.files.get("file")
        if not f or not f.filename:
            return render_template("error.html", message="Please choose a CSV file."), 400
        if not f.filename.lower().endswith(".csv"):
            return render_template("error.html", message="Only .csv files are accepted."), 400
        try:
            raw = pd.read_csv(io.BytesIO(f.read()), nrows=MAX_ROWS + 1)
            if len(raw) > MAX_ROWS:
                raise ValueError(f"File has more than {MAX_ROWS} rows.")
            tmp = di.validate_and_hash(raw)
        except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as e:
            return render_template("error.html", message=f"Invalid file: {e}"), 400
        res, s = analyse(pp.clean(tmp))
        return render_result(res, s, "Uploaded file (processed in memory, not stored)")

    @app.get("/about")
    def about():
        return render_template("about.html")

    @app.get("/health")
    def health():
        return jsonify(status="ok", model_loaded=True)

    @app.get("/api/summary")
    def api_summary():
        _, s = analyse(demo_df)
        return jsonify(s)

    @app.errorhandler(413)
    def too_large(_):
        return render_template("error.html", message="File too large (max 1 MB)."), 413

    return app
