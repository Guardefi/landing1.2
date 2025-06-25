"""
Test server to isolate import issues
"""

import os
import sys

from fastapi import FastAPI
from modules.recon_vault import ReconVault

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
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
