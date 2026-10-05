from pathlib import Path
import json
import re
import joblib

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "ml" / "sif_classifier.joblib"
RULES_PATH = ROOT / "data" / "life_saving_rules.json"

PATTERNS = {
    "Activity": [
        ("maintenance", "Maintenance"), ("lifting", "Lifting"), ("crane", "Lifting"),
        ("hot work", "Hot Work"), ("drilling", "Drilling"), ("confined space", "Confined Space"),
        ("work at height", "Working at Height"), ("height", "Working at Height"),
        ("vehicle", "Driving / Vehicle Movement"), ("driving", "Driving / Vehicle Movement"),
        ("electrical", "Electrical Work"), ("excavation", "Excavation")
    ],
    "Hazard": [
        ("pressurised line", "Pressurised Line"), ("pressurized line", "Pressurised Line"),
        ("pressure", "Stored Pressure"), ("gas", "Gas / Vapour"), ("hydrocarbon", "Hydrocarbon"),
        ("suspended load", "Suspended Load"), ("dropped object", "Dropped Object"),
        ("fall", "Fall from Height"), ("electrical", "Electrical Energy"),
        ("rotating equipment", "Rotating Equipment"), ("line of fire", "Line of Fire"),
        ("confined space", "Confined Space")
    ],
    "Unsafe Act": [
        ("opened", "Opening equipment/line before isolation"),
        ("entered", "Entering a restricted/confined area"),
        ("stood", "Standing in a line-of-fire zone"),
        ("climbed", "Working/accessing without adequate fall protection"),
        ("bypassed", "Bypassing a safety control"),
        ("removed", "Removing a safety guard/control"),
        ("drove", "Unsafe vehicle operation"),
        ("worked", "Unsafe work activity")
    ],
    "Barrier Failure": [
        ("energy isolation was not verified", "Energy isolation not verified"),
        ("energy isolation was not", "Energy isolation not verified"),
        ("without energy isolation", "Energy isolation missing"),
        ("without isolation", "Energy isolation missing"),
        ("lockout was not verified", "Lockout/Tagout not verified"),
        ("lockout tagout was not", "Lockout/Tagout not verified"),
        ("without gas testing", "Gas testing missing"),
        ("gas testing was not", "Gas testing not verified"),
        ("without a permit", "Permit-to-work control missing"),
        ("without permit", "Permit-to-work control missing"),
        ("permit was not", "Permit-to-work control failure"),
        ("exclusion zone was not established", "Lifting exclusion zone missing"),
        ("without an exclusion zone", "Lifting exclusion zone missing"),
        ("without fall protection", "Fall protection missing"),
        ("fall arrest", "Fall protection control"),
        ("safety interlock was bypassed", "Safety interlock bypassed"),
        ("guard was removed", "Machine guarding failure"),
        ("spotter was missing", "Vehicle/pedestrian control failure"),
        ("attendant was absent", "Confined-space attendant control failure"),
        ("gas detector alarm was ignored", "Gas monitoring control failure")
    ],
    "Potential Consequence": [
        ("nearly injured", "Potential serious injury"),
        ("near miss", "Near-miss potential"),
        ("injury", "Serious injury potential"),
        ("fatal", "Fatality potential"),
        ("struck", "Struck-by injury"),
        ("hit", "Struck-by injury"),
        ("release of pressure", "Pressure-release injury"),
        ("dropped object", "Dropped-object injury"),
        ("fall", "Fall-related serious injury"),
        ("fire", "Fire / thermal injury"),
        ("explosion", "Explosion / high-consequence event"),
        ("gas exposure", "Toxic exposure")
    ]
}

HIGH_CONSEQUENCE_CUES = [
    "pressurised", "pressurized", "stored pressure", "confined space",
    "hot work", "suspended load", "dropped object", "line of fire",
    "working at height", "fall arrest", "hydrocarbon", "gas exposure",
    "energy isolation", "lockout", "bypassed", "exclusion zone",
    "fatal", "nearly injured", "serious injury"
]

BARRIER_FAILURE_CUES = [
    "without", "not verified", "not established", "missing", "absent",
    "ignored", "bypassed", "removed", "failed", "failure"
]

REPORT_TYPES = {
    "Unsafe Act": ["worker", "operator", "contractor", "entered", "opened", "stood", "worked", "bypassed"],
    "Unsafe Condition": ["condition", "leak", "damaged", "unguarded", "exposed", "blocked", "defective"],
    "Near Miss": ["near miss", "nearly", "almost", "close call"],
    "Incident": ["injury", "injured", "fatal", "fire", "explosion", "collision", "incident"]
}

def ensure_model():
    if not MODEL_PATH.exists():
        from ml.train_model import train
        train()

def first_matches(text, patterns):
    low = text.lower()
    values = []
    for phrase, label in patterns:
        if phrase in low and label not in values:
            values.append(label)
    return values

def classify_report_type(text):
    low = text.lower()
    scores = {name: sum(1 for cue in cues if cue in low) for name, cues in REPORT_TYPES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Safety Observation"

def analyse(text):
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return {"valid": False, "message": "Please enter a safety report."}

    low = text.lower()
    relevant = any(
        term in low for term in [
            "worker", "operator", "contractor", "maintenance", "safety", "hazard",
            "permit", "isolation", "lockout", "gas", "lifting", "crane", "hot work",
            "confined", "height", "vehicle", "incident", "near miss", "injury",
            "equipment", "pressure", "ppe", "guard", "barrier", "unsafe"
        ]
    )
    if len(text.split()) < 3:
        return {
            "valid": False,
            "message": "The report is too short. Enter a complete workplace safety observation."
        }
    if not relevant:
        return {
            "valid": False,
            "message": "This text does not contain enough workplace-safety context for SIF analysis."
        }

    ensure_model()
    model = joblib.load(MODEL_PATH)
    ml_prob = float(model.predict_proba([text])[0][1])

    entities = {group: first_matches(text, patterns) for group, patterns in PATTERNS.items()}
    matched_cues = [cue for cue in HIGH_CONSEQUENCE_CUES if cue in low]
    barrier_cues = [cue for cue in BARRIER_FAILURE_CUES if cue in low]

    # Transparent hybrid prototype score:
    # ML probability + explicit high-consequence/barrier evidence.
    evidence_score = min(1.0, 0.12 * len(set(matched_cues)) + 0.10 * len(set(barrier_cues)))
    hybrid_score = min(0.99, 0.65 * ml_prob + 0.35 * evidence_score)

    # Explicit critical barrier failures should not be hidden by a weak tiny demo model.
    critical_barrier = any(
        phrase in low for phrase in [
            "without isolation", "without energy isolation",
            "energy isolation was not verified", "pressurised line",
            "pressurized line", "without gas testing", "suspended load",
            "line of fire", "without fall protection", "safety interlock was bypassed"
        ]
    )
    if critical_barrier:
        hybrid_score = max(hybrid_score, 0.82)

    if hybrid_score >= 0.60:
        label = "SIF Potential"
    elif hybrid_score >= 0.45:
        label = "Needs HSE Review"
    else:
        label = "Non-SIF"

    if entities["Potential Consequence"]:
        consequence = entities["Potential Consequence"]
    elif label == "SIF Potential":
        consequence = ["Potential serious injury / fatality"]
    else:
        consequence = ["No high-consequence consequence detected"]

    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    matched_rules = []
    for name, words in rules.items():
        if any(w in low for w in words):
            matched_rules.append(name)

    action_advice = []
    low_action_map = {
        "energy isolation": "Verify zero-energy state and independent LOTO verification before breaking containment.",
        "gas testing": "Require atmospheric testing and continuous monitoring where the task demands it.",
        "permit": "Confirm the permit-to-work is valid, understood, displayed and matches the actual task.",
        "exclusion zone": "Establish and enforce a controlled exclusion zone before lifting or dropped-object exposure.",
        "fall protection": "Verify compliant fall protection, anchorage and edge protection before work at height.",
        "interlock": "Restore and function-test safety interlocks; prohibit bypass without authorized engineered control.",
        "guard": "Restore machine guarding and verify the protective function before operation.",
        "line of fire": "Remove personnel from the line of fire and define a controlled work zone.",
    }
    for cue, advice in low_action_map.items():
        if cue in low:
            action_advice.append(advice)
    if not action_advice and label == "SIF Potential":
        action_advice.append("Escalate for HSE review, verify critical controls, and document preventive actions.")

    root_cause_hints = []
    if entities["Barrier Failure"]:
        root_cause_hints += ["Why was the critical control missing or bypassed?", "Was the procedure adequate and understood?", "Was supervision/verification effective?"]
    if entities["Unsafe Act"]:
        root_cause_hints.append("Check competency, task planning, workload and supervision as possible contributing factors.")

    explanation = []
    if entities["Hazard"]:
        explanation.append("A high-consequence hazard was detected: " + ", ".join(entities["Hazard"]) + ".")
    if entities["Barrier Failure"]:
        explanation.append("A safety barrier/control issue was detected: " + ", ".join(entities["Barrier Failure"]) + ".")
    if matched_rules:
        explanation.append("The detected hazard/control issue maps to: " + ", ".join(matched_rules) + ".")
    if not explanation:
        explanation.append("The prediction is based primarily on the trained text classifier and should be reviewed by HSE personnel.")

    return {
        "valid": True,
        "label": label,
        "confidence": round(hybrid_score * 100, 2),
        "sif_probability": round(hybrid_score * 100, 2),
        "ml_probability": round(ml_prob * 100, 2),
        "report_type": classify_report_type(text),
        "entities": entities,
        "life_saving_rules": matched_rules or ["Needs expert mapping"],
        "matched_cues": matched_cues,
        "explanation": explanation,
        "evidence_count": len(set(matched_cues + barrier_cues)),
        "action_advice": action_advice,
        "root_cause_hints": root_cause_hints,
        "potential_consequence": consequence,
    }
