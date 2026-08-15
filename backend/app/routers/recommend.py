from fastapi import APIRouter

router = APIRouter()


@router.get("/recommend/diseases")
def recommend_diseases():
    return {"recommendations": ["Rest", "Hydration", "OTC decongestant"]}
