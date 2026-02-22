from pathlib import Path
import json

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
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

    model = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    metrics = {
        "recall": float(recall_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions)),
        "f1": float(f1_score(y_test, predictions)),
        "rows_train": int(len(x_train)),
        "rows_test": int(len(x_test)),
        "positive_rate": float(target.mean()),
    }

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifacts_dir / "model.joblib"
    metrics_path = artifacts_dir / "metrics.json"

    joblib.dump(model, model_path)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    train_and_save_artifacts(Path("artifacts"))
