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
        "selection_metric",
        "selection_tie_breaker",
        "selected_model",
        "selected_metrics",
        "candidates",
        "rows_train",
        "rows_test",
        "positive_rate",
    }
    assert metrics["selection_metric"] == "recall"
    assert metrics["selection_tie_breaker"] == "f1"
    assert metrics["selected_model"] in {"logistic_regression", "random_forest"}

    candidates = metrics["candidates"]
    assert set(candidates.keys()) == {"logistic_regression", "random_forest"}

    for candidate_metrics in candidates.values():
        assert set(candidate_metrics.keys()) == {"recall", "precision", "f1", "pr_auc"}
        for value in candidate_metrics.values():
            assert 0.0 <= value <= 1.0

    assert metrics["selected_metrics"] == candidates[metrics["selected_model"]]
    assert metrics["rows_train"] > 0
    assert metrics["rows_test"] > 0
    assert 0.0 <= metrics["positive_rate"] <= 1.0
