# app.py
import os
import shutil
import time
import uuid
from flask import Flask, render_template, request, send_from_directory
from core.analysis import run_analysis

app = Flask(__name__)

STATIC_DIR = "static"
DATA_DIR = "data"
DEFAULT_CSV = os.path.join(DATA_DIR, "Sample_Data.csv")

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

RESULTS_DIR = os.path.join(STATIC_DIR, "results")
RESULT_TTL = 3600  # seconds

ALLOWED_EXTENSIONS = {".csv"}

PLOT_LABELS = [
    ("plot_1_original.png",      "Original Voltage Signal"),
    ("plot_2_ma.png",            "Voltage with 5-Point Moving Average"),
    ("plot_3_peaks_troughs.png", "Local Peaks & Troughs"),
    ("plot_4_below20.png",       "Readings Below 20 V"),
    ("plot_5_acceleration.png",  "Downward Acceleration Points"),
]


def _cleanup_old_results():
    if not os.path.isdir(RESULTS_DIR):
        return
    cutoff = time.time() - RESULT_TTL
    with os.scandir(RESULTS_DIR) as entries:
        for entry in entries:
            if entry.is_dir() and entry.stat().st_mtime < cutoff:
                shutil.rmtree(entry.path, ignore_errors=True)


def _empty_context():
    return {
        "plots": [],
        "tables": {},
        "accel_csv": None,
        "peaks_count": 0,
        "troughs_count": 0,
        "below20_count": 0,
        "accel_count": 0,
    }


@app.route("/", methods=["GET"])
def index_get():
    return render_template("index.html", **_empty_context())


@app.route("/", methods=["POST"])
def index_post():
    uploaded_bytes = None
    file = request.files.get("file")

    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            ctx = _empty_context()
            ctx["error"] = "Only .csv files are accepted."
            return render_template("index.html", **ctx), 400
        uploaded_bytes = file.read()

    _cleanup_old_results()

    request_id = uuid.uuid4().hex
    out_dir = os.path.join(RESULTS_DIR, request_id)
    os.makedirs(out_dir, exist_ok=True)

    try:
        results = run_analysis(
            csv_path=None if uploaded_bytes else DEFAULT_CSV,
            uploaded_bytes=uploaded_bytes,
            out_dir=out_dir,
        )

        plots = [
            {"filename": f"results/{request_id}/{name}", "label": label}
            for name, label in PLOT_LABELS
        ]
        accel_csv = f"results/{request_id}/downward_acceleration_points.csv"

        context = {
            "plots": plots,
            "tables": {
                "peaks":   results["peaks_df"].to_dict(orient="records"),
                "troughs": results["troughs_df"].to_dict(orient="records"),
                "below20": results["below_df"].to_dict(orient="records"),
                "accel":   results["accel_df"].to_dict(orient="records"),
            },
            "accel_csv":     accel_csv,
            "peaks_count":   len(results["peaks_df"]),
            "troughs_count": len(results["troughs_df"]),
            "below20_count": len(results["below_df"]),
            "accel_count":   len(results["accel_df"]),
        }
        return render_template("index.html", **context)

    except Exception as e:
        shutil.rmtree(out_dir, ignore_errors=True)
        ctx = _empty_context()
        ctx["error"] = str(e)
        return render_template("index.html", **ctx), 500


@app.errorhandler(413)
def file_too_large(e):
    ctx = _empty_context()
    ctx["error"] = "File is too large. Maximum upload size is 5 MB."
    return render_template("index.html", **ctx), 413


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
