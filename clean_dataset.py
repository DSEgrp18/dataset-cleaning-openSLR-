"""
Clean Sinhala speech WAVs:
- drop mostly-quiet / weak clips
- trim leading/trailing silence
- peak-normalize loudness
- write copies to dataset_clean/ (never overwrite originals)
"""

from __future__ import annotations

import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SRC = Path(__file__).resolve().parent / "dataset"
DST = Path(__file__).resolve().parent / "dataset_clean"

# Keep original sample rate (48 kHz)
TARGET_SR = None
TRIM_TOP_DB = 25
PEAK_TARGET = 0.95
# Drop clips that remain mostly near-silence after load (matches earlier scan)
MIN_RMS = 200.0
MAX_QUIET_FRAC = 0.85
QUIET_ABS = 100 / 32768.0  # ~int16 |s|<100 in float32 [-1, 1]
MIN_DUR_SEC = 0.5


def quiet_fraction(y: np.ndarray) -> float:
    if len(y) == 0:
        return 1.0
    return float(np.mean(np.abs(y) < QUIET_ABS))


def clean_one(path: Path) -> tuple[str, str | None]:
    """Returns (status, detail). status in kept|removed|error."""
    try:
        y, sr = librosa.load(path, sr=TARGET_SR, mono=True)
    except Exception as e:
        return "error", str(e)

    rms_i16 = float(np.sqrt(np.mean(y**2)) * 32768.0) if len(y) else 0.0
    quiet_before = quiet_fraction(y)

    if rms_i16 < MIN_RMS or quiet_before >= MAX_QUIET_FRAC:
        return "removed", f"weak rms_i16={rms_i16:.1f} quiet={quiet_before:.2f}"

    y_trim, _ = librosa.effects.trim(y, top_db=TRIM_TOP_DB)
    if len(y_trim) == 0:
        return "removed", "empty after trim"

    dur = len(y_trim) / float(sr)
    if dur < MIN_DUR_SEC:
        return "removed", f"too short after trim ({dur:.3f}s)"

    peak = float(np.max(np.abs(y_trim))) or 1.0
    y_out = (PEAK_TARGET * y_trim / peak).astype(np.float32)

    out_path = DST / path.name
    sf.write(out_path, y_out, sr)
    return "kept", f"dur={dur:.3f}s peak_norm={peak:.4f}"


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"Source folder not found: {SRC}")

    DST.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("*.wav"))
    if not files:
        raise SystemExit(f"No WAV files in {SRC}")

    summary = {"kept": [], "removed": [], "error": []}
    for i, path in enumerate(files, 1):
        status, detail = clean_one(path)
        summary[status].append({"file": path.name, "detail": detail})
        if i % 200 == 0 or i == len(files):
            print(f"processed {i}/{len(files)}")

    report = {
        "source": str(SRC),
        "dest": str(DST),
        "total_input": len(files),
        "kept": len(summary["kept"]),
        "removed": len(summary["removed"]),
        "error": len(summary["error"]),
        "removed_files": summary["removed"],
        "error_files": summary["error"],
        "settings": {
            "trim_top_db": TRIM_TOP_DB,
            "peak_target": PEAK_TARGET,
            "min_rms_i16": MIN_RMS,
            "max_quiet_frac": MAX_QUIET_FRAC,
            "min_dur_sec": MIN_DUR_SEC,
            "target_sr": "original",
        },
    }
    report_path = DST / "clean_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"done: kept={report['kept']} removed={report['removed']} "
        f"error={report['error']} -> {DST}"
    )
    for item in summary["removed"]:
        print(f"  removed: {item['file']} ({item['detail']})")


if __name__ == "__main__":
    main()
