from fastapi import APIRouter, HTTPException
from models import RecommendationRequest
from services import get_recommendations

router = APIRouter()

@router.post("/ai/recommend")
def recommend_employees(request: RecommendationRequest):
    try:
        result_list = get_recommendations(request)
        return {"status": "success", "recommendations": result_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
