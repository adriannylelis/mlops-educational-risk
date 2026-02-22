import json
from pathlib import Path

from src.model.train import train_and_save_artifacts


def test_train_generates_model_and_metrics(tmp_path: Path) -> None:
    artifacts_dir = tmp_path / "artifacts"

    train_and_save_artifacts(artifacts_dir)

    model_path = artifacts_dir / "model.joblib"
    metrics_path = artifacts_dir / "metrics.json"
    training_dataset_path = artifacts_dir / "training_dataset.csv"
    training_metadata_path = artifacts_dir / "training_dataset_metadata.json"

    assert model_path.exists()
    assert metrics_path.exists()
    assert training_dataset_path.exists()
    assert training_metadata_path.exists()

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    assert set(metrics.keys()) == {
        "recall",
        "precision",
        "f1",
        "rows_train",
        "rows_test",
        "positive_rate",
    }
    for value in metrics.values():
        if isinstance(value, float):
            assert 0.0 <= value <= 1.0
