from pathlib import Path
import json


def generate_report(output_path: Path) -> None:
    report = {
        "status": "baseline",
        "features": {},
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    generate_report(Path("artifacts/drift_report.json"))
