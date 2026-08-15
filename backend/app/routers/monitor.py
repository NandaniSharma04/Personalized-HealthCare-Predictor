from fastapi import APIRouter

router = APIRouter()


@router.get("/monitor/summary")
def monitor_summary():
    return {"uptime": "unknown", "model_versions": []}
