"""
Test server to isolate import issues
"""



sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI(title="Test Server")
recon_vault = ReconVault()


@app.get("/")
async def root():
    return {"message": "Test server running"}


@app.get("/api/recon/test")
async def test_recon():
    """Test the recon vault initialization."""
    return {
        "status": "success",
        "message": "Recon vault initialized successfully",
        "instance": str(type(recon_vault)),
import os
import sys

import uvicorn
from fastapi import FastAPI
from modules.recon_vault import ReconVault

    }


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8001)
