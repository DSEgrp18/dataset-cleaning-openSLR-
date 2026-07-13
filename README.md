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

## What the cleaner does

1. **Drops weak clips** — removes mostly-quiet / low-energy recordings  
2. **Trims silence** — cuts leading and trailing quiet (`top_db=25`)  
3. **Peak-normalizes** — scales each clip to ~0.95 peak  
4. **Writes copies only** — output goes to `dataset_clean/`; originals are never overwritten  

On a typical extract of this corpus (~2064 WAVs), the run kept **2061** clips and removed **3** weak files. See `clean_report.json`.

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
