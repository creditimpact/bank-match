from fastapi import FastAPI

app = FastAPI(title="bank-match API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"name": "bank-match", "version": "0.1.0"}
