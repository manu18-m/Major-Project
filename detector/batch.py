from pathlib import Path
import pandas as pd
from detector.analysis import analyse

def analyze_csv(input_path, output_path):
    df = pd.read_csv(input_path)
    if "report" not in df.columns:
        raise ValueError("CSV must contain a 'report' column.")

    records = []
    for text in df["report"].fillna("").astype(str):
        r = analyse(text)
        if not r.get("valid"):
            records.append({
                "report": text,
                "classification": "Invalid/Needs Input",
                "sif_probability": "",
                "report_type": "",
                "activity": "",
                "hazard": "",
                "barrier_failure": "",
                "potential_consequence": "",
                "life_saving_rules": "",
            })
            continue
        e = r["entities"]
        records.append({
            "report": text,
            "classification": r["label"],
            "sif_probability": r["sif_probability"],
            "report_type": r["report_type"],
            "activity": "; ".join(e["Activity"]),
            "hazard": "; ".join(e["Hazard"]),
            "barrier_failure": "; ".join(e["Barrier Failure"]),
            "potential_consequence": "; ".join(e["Potential Consequence"]),
            "life_saving_rules": "; ".join(r["life_saving_rules"]),
        })

    pd.DataFrame(records).to_csv(output_path, index=False)
    return output_path
