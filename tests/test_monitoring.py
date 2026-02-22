import json
from pathlib import Path

from monitoring.drift_report import generate_report


def test_generate_drift_report(tmp_path: Path) -> None:
    output_path = tmp_path / "drift_report.json"
    training_dataset_path = Path("artifacts/training_dataset.csv")
    source_dataset_path = Path("base_dados/PEDE_PASSOS_DATASET_FIAP.csv")

    generate_report(
        output_path=output_path,
        training_dataset_path=training_dataset_path,
        source_dataset_path=source_dataset_path,
    )

    assert output_path.exists()
    report = json.loads(output_path.read_text(encoding="utf-8"))

    assert set(report.keys()) == {
        "generated_at",
        "baseline_rows",
        "current_rows",
        "drift_features",
        "global_status",
        "features",
    }
    assert report["global_status"] in {"stable", "drift"}
    assert report["baseline_rows"] > 0
    assert report["current_rows"] > 0
    assert isinstance(report["features"], dict)
    assert len(report["features"]) > 0
