from pathlib import Path
import json

import joblib
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


def train_and_save_artifacts(artifacts_dir: Path) -> None:
    features, target = make_classification(
        n_samples=1000,
        n_features=8,
        n_informative=5,
        n_redundant=1,
        n_classes=2,
        random_state=42,
        weights=[0.65, 0.35],
    )

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    metrics = {
        "recall": float(recall_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions)),
        "f1": float(f1_score(y_test, predictions)),
    }

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifacts_dir / "model.joblib"
    metrics_path = artifacts_dir / "metrics.json"

    joblib.dump(model, model_path)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    train_and_save_artifacts(Path("artifacts"))
