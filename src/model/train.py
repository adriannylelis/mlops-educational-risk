from pathlib import Path
import json

import joblib
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data.build_training_dataset import build_training_dataset


def train_and_save_artifacts(
    artifacts_dir: Path,
    raw_dataset_path: Path = Path("base_dados/PEDE_PASSOS_DATASET_FIAP.csv"),
) -> None:
    dataset_path = artifacts_dir / "training_dataset.csv"
    metadata_path = artifacts_dir / "training_dataset_metadata.json"
    dataset_df = build_training_dataset(raw_dataset_path, dataset_path, metadata_path)

    target = dataset_df["target_risco_defasagem"]
    features = dataset_df.drop(columns=["target_risco_defasagem"])

    numeric_columns = features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_columns = [column for column in features.columns if column not in numeric_columns]

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_columns,
            ),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_columns,
            ),
        ],
        remainder="drop",
    )

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )

    candidate_models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            min_samples_leaf=3,
        ),
    }

    candidate_metrics = {}
    trained_candidates = {}

    for candidate_name, classifier in candidate_models.items():
        model = Pipeline(
            steps=[
                ("preprocessing", clone(preprocessing)),
                ("classifier", classifier),
            ]
        )
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        probabilities = model.predict_proba(x_test)[:, 1]

        candidate_metrics[candidate_name] = {
            "recall": float(recall_score(y_test, predictions)),
            "precision": float(precision_score(y_test, predictions)),
            "f1": float(f1_score(y_test, predictions)),
            "pr_auc": float(average_precision_score(y_test, probabilities)),
        }
        trained_candidates[candidate_name] = model

    selected_model_name = max(
        candidate_metrics,
        key=lambda model_name: (
            candidate_metrics[model_name]["recall"],
            candidate_metrics[model_name]["f1"],
        ),
    )
    selected_model = trained_candidates[selected_model_name]

    metrics = {
        "selection_metric": "recall",
        "selection_tie_breaker": "f1",
        "selected_model": selected_model_name,
        "selected_metrics": candidate_metrics[selected_model_name],
        "candidates": candidate_metrics,
        "rows_train": int(len(x_train)),
        "rows_test": int(len(x_test)),
        "positive_rate": float(target.mean()),
    }

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifacts_dir / "model.joblib"
    metrics_path = artifacts_dir / "metrics.json"

    joblib.dump(selected_model, model_path)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    train_and_save_artifacts(Path("artifacts"))
