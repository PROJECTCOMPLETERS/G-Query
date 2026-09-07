from fastapi import FastAPI

app = FastAPI(
    title="SatQuery API",
    description="Satellite Query and Analysis API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "satquery-backend",
    }