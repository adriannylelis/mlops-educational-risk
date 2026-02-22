from fastapi import FastAPI


app = FastAPI(title="educational-risk-api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
