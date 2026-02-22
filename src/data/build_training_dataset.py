from pathlib import Path
import json

import pandas as pd


def build_training_dataset(
    input_csv_path: Path,
    output_dataset_path: Path,
    output_metadata_path: Path,
) -> pd.DataFrame:
    source_df = pd.read_csv(input_csv_path, sep=";", encoding="utf-8-sig")

    target_column = "DEFASAGEM_2021"
    identifier_columns = ["NOME"]
    feature_columns = [column for column in source_df.columns if column.endswith("_2020")]
    future_columns = [
        column for column in source_df.columns if column.endswith("_2021") or column.endswith("_2022")
    ]

    target_numeric = pd.to_numeric(source_df[target_column], errors="coerce")
    valid_rows = target_numeric.notna()

    dataset_df = source_df.loc[valid_rows, feature_columns].copy()
    dataset_df["target_risco_defasagem"] = (target_numeric.loc[valid_rows] < 0).astype(int)

    output_dataset_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_df.to_csv(output_dataset_path, index=False)

    metadata = {
        "input_path": str(input_csv_path),
        "output_path": str(output_dataset_path),
        "rows_total_input": int(len(source_df)),
        "rows_valid_target": int(len(dataset_df)),
        "target_column_raw": target_column,
        "target_column_model": "target_risco_defasagem",
        "target_rule": "1 quando DEFASAGEM_2021 < 0, 0 caso contrário",
        "feature_columns_used": feature_columns,
        "identifier_columns_excluded": identifier_columns,
        "future_columns_excluded": future_columns,
    }
    output_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    output_metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return dataset_df


if __name__ == "__main__":
    build_training_dataset(
        Path("base_dados/PEDE_PASSOS_DATASET_FIAP.csv"),
        Path("artifacts/training_dataset.csv"),
        Path("artifacts/training_dataset_metadata.json"),
    )