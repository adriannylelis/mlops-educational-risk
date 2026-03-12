from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app
from src.model.train import train_and_save_artifacts


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint_returns_score_and_class() -> None:
    train_and_save_artifacts(artifacts_dir=Path("src/artifacts"))

    response = client.post("/predict", json={"features": {}})

    assert response.status_code == 200
    payload = response.json()

    assert set(payload.keys()) == {"score_risco", "classe_risco"}
    assert 0.0 <= payload["score_risco"] <= 1.0
    assert payload["classe_risco"] in {"alto", "baixo"}
