from fastapi import FastAPI

app = FastAPI(title="SIH 2026 DMS API")

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "DMS API"}