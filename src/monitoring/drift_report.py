from pathlib import Path
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.data.build_training_dataset import build_training_dataset


def _psi_numeric(base: pd.Series, current: pd.Series, bins: int = 10) -> float:
    base_clean = pd.to_numeric(base, errors="coerce").dropna()
    current_clean = pd.to_numeric(current, errors="coerce").dropna()
    if base_clean.empty or current_clean.empty:
        return 0.0
    quantiles = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(base_clean, quantiles))
    if len(edges) < 3:
        return 0.0
    base_counts, _ = np.histogram(base_clean, bins=edges)
    current_counts, _ = np.histogram(current_clean, bins=edges)
    epsilon = 1e-6
    base_dist = np.clip(base_counts / max(base_counts.sum(), 1), epsilon, None)
    current_dist = np.clip(current_counts / max(current_counts.sum(), 1), epsilon, None)
    return float(np.sum((current_dist - base_dist) * np.log(current_dist / base_dist)))


def _psi_categorical(base: pd.Series, current: pd.Series) -> float:
    base_clean = base.fillna("<NA>").astype(str)
    current_clean = current.fillna("<NA>").astype(str)
    categories = sorted(set(base_clean.unique()) | set(current_clean.unique()))
    epsilon = 1e-6
    base_dist = []
    current_dist = []
    for category in categories:
        base_dist.append((base_clean == category).mean())
        current_dist.append((current_clean == category).mean())
    base_arr = np.clip(np.array(base_dist), epsilon, None)
    current_arr = np.clip(np.array(current_dist), epsilon, None)
    return float(np.sum((current_arr - base_arr) * np.log(current_arr / base_arr)))


def _drift_status(psi_value: float) -> str:
    if psi_value >= 0.2:
        return "drift"
    if psi_value >= 0.1:
        return "warning"
    return "stable"


def generate_report(
    output_path: Path,
    training_dataset_path: Path = Path("src/artifacts/training_dataset.csv"),
    source_dataset_path: Path = Path("base_dados/PEDE_PASSOS_DATASET_FIAP.csv"),
) -> None:
    if not training_dataset_path.exists():
        build_training_dataset(
            input_csv_path=source_dataset_path,
            output_dataset_path=training_dataset_path,
            output_metadata_path=Path("src/artifacts/training_dataset_metadata.json"),
        )

    dataset_df = pd.read_csv(training_dataset_path)
    feature_columns = [column for column in dataset_df.columns if column != "target_risco_defasagem"]

    split_index = int(len(dataset_df) * 0.7)
    baseline_df = dataset_df.iloc[:split_index]
    current_df = dataset_df.iloc[split_index:]

    features_report = {}
    drift_count = 0
    for column in feature_columns:
        if pd.api.types.is_numeric_dtype(dataset_df[column]):
            psi_value = _psi_numeric(baseline_df[column], current_df[column])
        else:
            psi_value = _psi_categorical(baseline_df[column], current_df[column])
        status = _drift_status(psi_value)
        if status == "drift":
            drift_count += 1
        features_report[column] = {
            "psi": round(psi_value, 6),
            "status": status,
        }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline_rows": int(len(baseline_df)),
        "current_rows": int(len(current_df)),
        "drift_features": drift_count,
        "global_status": "drift" if drift_count > 0 else "stable",
        "features": features_report,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    generate_report(Path("src/artifacts/drift_report.json"))
