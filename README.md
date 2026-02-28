# TransVolt — Voltage Time-Series Analysis Dashboard

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-6366f1?style=flat-square)

A Flask web application that performs automated analysis of voltage time-series data. Upload a CSV file and instantly get interactive plots, statistical summaries, and downloadable results — all in a dark-themed dashboard.

---

## Features

- **Upload or sample data** — drop in any CSV with `Timestamp` / `Values` columns, or click Analyze to run the built-in sample dataset
- **5-point moving average** — smoothed trend overlay on the raw signal
- **Peak & trough detection** — scipy `find_peaks` identifies all local maxima and minima
- **Low-voltage flagging** — highlights every reading where voltage falls below 20 V
- **Downward-acceleration points** — finds the steepest-slope moment in each downward voltage cycle
- **5 Matplotlib plots** rendered server-side and displayed in a responsive grid
- **Downloadable CSV** of acceleration points
- **Dark-theme dashboard** with stat cards, scrollable data tables, and a tech-stack footer

---

## Tech Stack

| Layer       | Library / Tool             |
|-------------|---------------------------|
| Web server  | Flask 3, Gunicorn          |
| Data        | pandas, NumPy              |
| Signal DSP  | SciPy (`find_peaks`)       |
| Plotting    | Matplotlib (Agg backend)   |
| Frontend    | Vanilla HTML/CSS           |
| Deploy      | Heroku (Procfile)          |

---

## Screenshots

> _Run the app locally and upload `data/Sample_Data.csv` to see the dashboard._

---

## Installation

```bash
# 1. Clone
git clone https://github.com/<your-username>/transvolt-mobility-webapp.git
cd transvolt-mobility-webapp

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py
```

Open **http://localhost:8000** in your browser.

---

## Usage

1. Open the dashboard.
2. Optionally choose a CSV file with the file picker.
3. Click **Analyze**.
4. Review the stat cards, plots, and data tables.
5. Click **Download Downward Acceleration Points (CSV)** to export results.

---

## Expected CSV Format

| Column      | Format                | Example               |
|-------------|----------------------|-----------------------|
| `Timestamp` | `%d/%m/%y %H:%M`     | `01/06/23 08:30`      |
| `Values`    | numeric (float/int)   | `23.7`                |

A sample file is included at `data/Sample_Data.csv`.

---

## Project Structure

```
transvolt-mobility-webapp/
├── app.py                        # Flask routes
├── analysis.py                   # Original analysis module (kept)
├── core/
│   ├── __init__.py
│   └── analysis.py               # Active analysis module (imported by app.py)
├── static/
│   └── css/
│       └── style.css             # Dark-theme dashboard styles
├── templates/
│   └── index.html                # Jinja2 template
├── data/
│   └── Sample_Data.csv           # Built-in sample dataset
├── Procfile                      # Heroku process declaration
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## Deploy to Heroku

```bash
heroku create
git push heroku main
heroku open
```

The `Procfile` is already configured for Gunicorn.

---

## License

MIT © 2026 Sarthak. See [LICENSE](LICENSE) for details.
