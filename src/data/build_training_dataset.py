from pathlib import Path
import json
import re

import pandas as pd


# Features comuns disponíveis nos anos 2020, 2021 e 2022.
# Usadas como base do dataset longitudinal (panel) para um modelo ano-agnóstico.
COMMON_INDEX_FEATURES = ["INDE", "IAA", "IAN", "IDA", "IEG", "IPP", "IPS", "IPV"]
COMMON_CATEGORICAL_FEATURES = ["PEDRA"]
COMMON_BOOLEAN_FEATURES = ["PONTO_VIRADA"]
COMMON_FEATURES = COMMON_INDEX_FEATURES + COMMON_CATEGORICAL_FEATURES + COMMON_BOOLEAN_FEATURES


def _extract_nivel_number(series: pd.Series) -> pd.Series:
    """Extrai o número da fase/nível do texto.

    Exemplos:
        'Nível 3 (7o e 8o ano)' -> 3
        'Fase 2 (5º e 6º ano)'  -> 2
    """
    return series.astype(str).str.extract(r"(\d+)")[0].pipe(pd.to_numeric, errors="coerce")


def _normalize_boolean_col(series: pd.Series) -> pd.Series:
    """Converte coluna booleana/texto para int (1/0), com NaN → -1 como sentinela.

    Aceita: True/False, 'Sim'/'Não', '1'/'0'.
    """
    mapping = {True: 1, False: 0, "Sim": 1, "Não": 0, "sim": 1, "não": 0, "1": 1, "0": 0}
    return series.map(mapping).fillna(-1).astype(int)


def _build_period(
    source_df: pd.DataFrame,
    year_features: int,
    target_series: pd.Series,
) -> pd.DataFrame:
    """Constrói um período do dataset panel.

    Args:
        source_df: DataFrame bruto do CSV.
        year_features: Ano das features de entrada (ex: 2020 para prever 2021).
        target_series: Série com o valor numérico de defasagem do ano seguinte.

    Returns:
        DataFrame com features normalizadas (sem sufixo de ano) e target binário.
    """
    rows: dict[str, pd.Series] = {}

    for feat in COMMON_INDEX_FEATURES:
        col = f"{feat}_{year_features}"
        rows[feat] = pd.to_numeric(
            source_df[col] if col in source_df.columns else pd.Series(pd.NA, index=source_df.index),
            errors="coerce",
        )

    for feat in COMMON_CATEGORICAL_FEATURES:
        col = f"{feat}_{year_features}"
        raw = source_df[col] if col in source_df.columns else pd.Series(pd.NA, index=source_df.index)
        # Garante tipo string uniforme — sem mistura float NaN + str
        rows[feat] = raw.fillna("<AUSENTE>").astype(str)

    for feat in COMMON_BOOLEAN_FEATURES:
        col = f"{feat}_{year_features}"
        raw = source_df[col] if col in source_df.columns else pd.Series(pd.NA, index=source_df.index)
        # Converte para int (1/0/-1) eliminando tipo misto
        rows[feat] = _normalize_boolean_col(raw)

    # FASE: em 2020 o nome é FASE_TURMA_2020; nos demais é FASE_<ano>
    fase_col = f"FASE_TURMA_{year_features}" if year_features == 2020 else f"FASE_{year_features}"
    rows["FASE"] = pd.to_numeric(
        source_df.get(fase_col, pd.Series(pd.NA, index=source_df.index)), errors="coerce"
    )

    rows["ANO_REFERENCIA"] = year_features

    target_numeric = pd.to_numeric(target_series, errors="coerce")
    rows["target_risco_defasagem"] = (target_numeric < 0).astype("Int64")

    period_df = pd.DataFrame(rows, index=source_df.index)

    # Mantém apenas linhas com target válido
    valid = target_numeric.notna()
    return period_df.loc[valid].reset_index(drop=True)


def build_training_dataset(
    input_csv_path: Path,
    output_dataset_path: Path,
    output_metadata_path: Path,
) -> pd.DataFrame:
    """Constrói dataset longitudinal (panel) com dois períodos:
    - 2020 → 2021: features de 2020, target = DEFASAGEM_2021 < 0
    - 2021 → 2022: features de 2021, target = DEFASAGEM_2022 < 0 (computado)

    Isso aproximadamente dobra o volume de dados e torna o modelo ano-agnóstico.
    """
    source_df = pd.read_csv(input_csv_path, sep=";", encoding="utf-8-sig")

    # --- Período 2020 → 2021 ---
    defasagem_2021 = pd.to_numeric(source_df["DEFASAGEM_2021"], errors="coerce")
    period_2020 = _build_period(source_df, 2020, defasagem_2021)

    # --- Período 2021 → 2022 ---
    # DEFASAGEM_2022 não está explícita: derivada de FASE_2022 - numero(NIVEL_IDEAL_2022)
    nivel_2022_num = _extract_nivel_number(source_df["NIVEL_IDEAL_2022"])
    fase_2022 = pd.to_numeric(source_df["FASE_2022"], errors="coerce")
    defasagem_2022 = fase_2022 - nivel_2022_num
    period_2021 = _build_period(source_df, 2021, defasagem_2022)

    # --- Combina os dois períodos ---
    dataset_df = pd.concat([period_2020, period_2021], ignore_index=True)
    # Converte target para int padrão (nullable Int64 → int)
    dataset_df["target_risco_defasagem"] = dataset_df["target_risco_defasagem"].astype(int)

    output_dataset_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_df.to_csv(output_dataset_path, index=False)

    feature_columns = [c for c in dataset_df.columns if c != "target_risco_defasagem"]
    metadata = {
        "input_path": str(input_csv_path),
        "output_path": str(output_dataset_path),
        "strategy": "longitudinal_panel",
        "periods": {
            "2020_to_2021": {
                "features_year": 2020,
                "target_column_raw": "DEFASAGEM_2021",
                "target_rule": "1 quando DEFASAGEM_2021 < 0",
                "rows": int(len(period_2020)),
            },
            "2021_to_2022": {
                "features_year": 2021,
                "target_column_raw": "DEFASAGEM_2022 (computada)",
                "target_rule": "1 quando (FASE_2022 - num(NIVEL_IDEAL_2022)) < 0",
                "rows": int(len(period_2021)),
            },
        },
        "rows_total_input": int(len(source_df)),
        "rows_valid_target": int(len(dataset_df)),
        "target_column_model": "target_risco_defasagem",
        "feature_columns_used": feature_columns,
        "identifier_columns_excluded": ["NOME"],
    }
    output_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    output_metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return dataset_df


if __name__ == "__main__":
    build_training_dataset(
        Path("base_dados/PEDE_PASSOS_DATASET_FIAP.csv"),
        Path("src/artifacts/training_dataset.csv"),
        Path("src/artifacts/training_dataset_metadata.json"),
    )