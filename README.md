# SIH 26165 — AI/NLP Engine to Detect SIF Precursors

This project is a review-ready prototype inspired by the structure of the earlier
SafeShe project document supplied for reference.

## Problem
Analyse free-text Unsafe Act (UA), Unsafe Condition (UC), Near-Miss and incident
reports to identify Serious Injury & Fatality (SIF) potential and extract precursor
information.

## Prototype modules
1. Report input
2. NLP preprocessing
3. SIF / Non-SIF classification
4. Hazard / barrier / activity keyword extraction
5. IOGP Life-Saving Rule category mapping
6. Precursor analytics dashboard
7. CSV report dataset
8. Model training script
9. Project report

## Important dataset note
`data/sif_reports.csv` is a SYNTHETIC demonstration dataset. It is not OIL confidential
data and must not be represented as OIL's real dataset.

## Technology
- Python
- Django
- scikit-learn
- pandas
- TF-IDF
- Logistic Regression
- SQLite
- HTML/CSS/JavaScript

## Run
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
python ml/train_model.py
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Prototype limitations
The classifier is trained on synthetic demonstration examples. For the actual SIH
solution, authorised OIL data and expert labels are required. SIF predictions should
support, not replace, HSE expert review.


## Enhanced prototype features
- Hybrid AI + explicit safety-evidence scoring
- SIF Potential / Needs HSE Review / Non-SIF
- Report type detection
- Activity, hazard, unsafe-act, barrier-failure and consequence extraction
- Life-Saving Rule category mapping
- Explainable evidence panel
- Batch CSV analysis at `/batch/`
- Precursor analytics dashboard at `/dashboard/`
- Demonstration model evaluation with `python ml/evaluate_model.py`

### Important
The supplied dataset is synthetic demonstration data. Do not present its results as
OIL operational statistics. Production deployment requires authorised data, expert
labels, security controls, calibration and HSE validation.


## FINAL ONE-COMMAND STARTUP

### Requirements
- Python 3.10+ (Python 3.11 recommended)
- Internet access on the first run only, so the launcher can install Python packages.

### Start the application
From the project root, run only:

```powershell
python manage.py runserver
```

You do NOT need to manually:
- create a virtual environment
- install requirements
- train the model
- run migrations

The launcher handles those steps automatically.

After the first successful startup, use the same command every time:

```powershell
python manage.py runserver
```

Then open http://127.0.0.1:8000/

### Important
The included dataset is synthetic demonstration data. It is not OIL operational data.
The SIF score is a prototype decision-support signal and is not a calibrated probability.
Final deployment requires authorised OIL data, expert labels, validation, security controls,
and HSE expert review.


## Expanded HSE workflow

This release extends the SIF NLP engine with structured incident/near-miss intake, 5x5 risk screening, CAPA/action tracking, critical-control verification, safety inspections, 5-Why RCA, preventive analytics, and CSV export. These features are intentionally implemented as a local demonstration workflow and do not connect to OIL operational systems.
