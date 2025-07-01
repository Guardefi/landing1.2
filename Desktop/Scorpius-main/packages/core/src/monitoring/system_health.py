"""Low‑level machine health metrics."""

import datetime

import psutil

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
async def health():
    du = psutil.disk_usage("/")
    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "cpu_load": psutil.cpu_percent(interval=0.5),
        "mem_load": psutil.virtual_memory().percent,
        "disk_free_gb": round(du.free / 1e9, 2),
    }
