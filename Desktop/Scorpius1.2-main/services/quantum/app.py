from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

app = FastAPI(title="Quantum Service")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "quantum", "status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "quantum"}
