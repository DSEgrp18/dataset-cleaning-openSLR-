# OpenSLR Sinhala (si_lk) Dataset Cleaning

Audio cleaning pipeline for the **OpenSLR Resource 30** Sinhala speech corpus (`si_lk`).

The large WAV folders are **not** stored in this repository. Download the dataset, extract it, then run the cleaner locally.

## Dataset download

Download the archive from OpenSLR:

- https://openslr.trmal.net/resources/30/si_lk.tar.gz

```bash
# Example (Windows PowerShell / Linux / macOS)
curl -L -o si_lk.tar.gz "https://openslr.trmal.net/resources/30/si_lk.tar.gz"
tar -xzf si_lk.tar.gz
```

Place the extracted WAV files in a folder named `dataset/` next to `clean_dataset.py` (or adjust the paths in the script).

## Cleaning pipeline

`clean_dataset.py` processes every `*.wav` in `dataset/` in order. Originals are never modified; cleaned files are written to `dataset_clean/`.

```text
dataset/*.wav
      │
      ▼
┌─────────────────────┐
│ 1. Load (mono)      │  librosa — keep original sample rate (48 kHz)
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 2. Weak-clip filter │  drop if RMS (int16-scale) < 200
│                     │  or quiet fraction ≥ 0.85
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 3. Trim silence     │  librosa.effects.trim(top_db=25)
│                     │  drop if empty or duration < 0.5 s
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 4. Peak normalize   │  scale so peak ≈ 0.95
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 5. Write + report   │  dataset_clean/<same name>.wav
│                     │  dataset_clean/clean_report.json
└─────────────────────┘
```

### Pipeline steps

| Step | Action | Details |
|------|--------|---------|
| 1 | Load | Mono WAV; sample rate left at source (typically 48 kHz) |
| 2 | Remove weak clips | Drop if energy is too low (`MIN_RMS = 200`) or most samples are near silence (`MAX_QUIET_FRAC = 0.85`) |
| 3 | Trim silence | Cut leading/trailing quiet with `TRIM_TOP_DB = 25`; reject clips shorter than `MIN_DUR_SEC = 0.5` after trim |
| 4 | Normalize loudness | Peak normalize to `PEAK_TARGET = 0.95` so levels are consistent |
| 5 | Save copies | Write cleaned audio to `dataset_clean/`; write a JSON report of kept/removed files |

### Tunable parameters

Defined at the top of `clean_dataset.py`:

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `TRIM_TOP_DB` | `25` | Silence trim aggressiveness |
| `PEAK_TARGET` | `0.95` | Target peak after normalization |
| `MIN_RMS` | `200` | Minimum int16-scale RMS to keep |
| `MAX_QUIET_FRAC` | `0.85` | Max fraction of near-silent samples |
| `MIN_DUR_SEC` | `0.5` | Minimum duration after trim |

### Example result

On a typical extract of this corpus (~2064 WAVs), the pipeline kept **2061** clips and removed **3** weak files. See `clean_report.json`.

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
python clean_dataset.py
```

Outputs:

| Path | Description |
|------|-------------|
| `dataset_clean/*.wav` | Cleaned audio |
| `dataset_clean/clean_report.json` | Keep/remove counts and settings |

## Project layout

```
.
├── clean_dataset.py      # Cleaning script
├── requirements.txt
├── clean_report.json     # Example report from a full run
├── dataset/              # Ignored — put downloaded WAVs here
└── dataset_clean/        # Ignored — generated cleaned WAVs
```

## Source

- OpenSLR Resource 30: [si_lk](https://openslr.trmal.net/resources/30/si_lk.tar.gz)
