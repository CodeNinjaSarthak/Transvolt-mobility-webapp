# tests/test_analysis.py
import io
import os
import pytest
import pandas as pd

from core.analysis import (
    load_df,
    find_extrema,
    below_20,
    find_downward_acceleration,
    run_analysis,
)

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "Sample_Data.csv")


@pytest.fixture
def sample_df():
    return load_df(csv_path=SAMPLE_CSV)


@pytest.fixture
def sample_bytes():
    with open(SAMPLE_CSV, "rb") as f:
        return f.read()


# ── TestLoadDf ─────────────────────────────────────────────────────────────────

class TestLoadDf:
    def test_loads_from_path(self):
        df = load_df(csv_path=SAMPLE_CSV)
        assert "Timestamp" in df.columns
        assert "Values" in df.columns
        assert len(df) > 0

    def test_loads_from_bytes(self, sample_bytes):
        df = load_df(uploaded_bytes=sample_bytes)
        assert len(df) > 0

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_df(csv_path="/nonexistent/path/file.csv")

    def test_raises_on_bad_columns(self, tmp_path):
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("A,B\n1,2\n3,4\n")
        with pytest.raises(ValueError, match="Timestamp"):
            load_df(csv_path=str(bad_csv))

    def test_timestamp_sorted(self, sample_df):
        assert sample_df["Timestamp"].is_monotonic_increasing

    def test_moving_average_length(self, sample_df):
        assert len(sample_df["5_day_MA"]) == len(sample_df)


# ── TestFindExtrema ────────────────────────────────────────────────────────────

class TestFindExtrema:
    def test_returns_dataframes(self, sample_df):
        peaks_df, troughs_df, _, _ = find_extrema(sample_df)
        assert isinstance(peaks_df, pd.DataFrame)
        assert isinstance(troughs_df, pd.DataFrame)

    def test_columns(self, sample_df):
        peaks_df, troughs_df, _, _ = find_extrema(sample_df)
        assert list(peaks_df.columns) == ["Timestamp", "Value"]
        assert list(troughs_df.columns) == ["Timestamp", "Value"]

    def test_peaks_are_local_maxima(self, sample_df):
        _, _, peaks_idx, _ = find_extrema(sample_df)
        values = sample_df["Values"].to_numpy()
        for i in peaks_idx:
            assert values[i] > values[i - 1], f"Peak at {i} not > left neighbor"
            assert values[i] > values[i + 1], f"Peak at {i} not > right neighbor"


# ── TestBelow20 ────────────────────────────────────────────────────────────────

class TestBelow20:
    def test_all_below_threshold(self, sample_df):
        result = below_20(sample_df)
        assert (result["Value"] < 20).all()

    def test_columns(self, sample_df):
        result = below_20(sample_df)
        assert list(result.columns) == ["Timestamp", "Value"]


# ── TestDownwardAcceleration ───────────────────────────────────────────────────

class TestDownwardAcceleration:
    def test_returns_dataframe(self, sample_df):
        result = find_downward_acceleration(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_columns(self, sample_df):
        result = find_downward_acceleration(sample_df)
        for col in ["Index", "Timestamp", "Value"]:
            assert col in result.columns


# ── TestRunAnalysis ────────────────────────────────────────────────────────────

class TestRunAnalysis:
    def test_end_to_end(self, tmp_path):
        result = run_analysis(csv_path=SAMPLE_CSV, out_dir=str(tmp_path))
        for key in ("df", "peaks_df", "troughs_df", "below_df", "accel_df", "accel_csv_path"):
            assert key in result

    def test_plots_generated(self, tmp_path):
        run_analysis(csv_path=SAMPLE_CSV, out_dir=str(tmp_path))
        expected = [
            "plot_1_original.png",
            "plot_2_ma.png",
            "plot_3_peaks_troughs.png",
            "plot_4_below20.png",
            "plot_5_acceleration.png",
        ]
        for fname in expected:
            assert (tmp_path / fname).exists(), f"{fname} not generated"

    def test_csv_generated(self, tmp_path):
        result = run_analysis(csv_path=SAMPLE_CSV, out_dir=str(tmp_path))
        assert os.path.exists(result["accel_csv_path"])
