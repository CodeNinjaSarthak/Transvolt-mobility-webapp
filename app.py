# app.py
import os
from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,
)
from analysis import run_analysis

app = Flask(__name__)
STATIC_DIR = "static"
DATA_DIR = "data"
DEFAULT_CSV = os.path.join(DATA_DIR, "Sample_Data.csv")


@app.route("/", methods=["GET", "POST"])
def index():
    uploaded = None
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            uploaded = file.read()

    try:
        results = run_analysis(
            csv_path=None if uploaded else DEFAULT_CSV,
            uploaded_bytes=uploaded,
            out_dir=STATIC_DIR,
        )
        context = {
            "plots": [
                "plot_1_original.png",
                "plot_2_ma.png",
                "plot_3_peaks_troughs.png",
                "plot_4_below20.png",
                "plot_5_acceleration.png",
            ],
            "tables": {
                "peaks": results["peaks_df"].to_dict(orient="records"),
                "troughs": results["troughs_df"].to_dict(orient="records"),
                "below20": results["below_df"].to_dict(orient="records"),
                "accel": results["accel_df"].to_dict(orient="records"),
            },
            "accel_csv": os.path.basename(results["accel_csv_path"]),
        }
        return render_template("index.html", **context)
    except Exception as e:
        return render_template(
            "index.html", error=str(e), plots=[], tables={}, accel_csv=None
        )


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=8000, debug=True)
