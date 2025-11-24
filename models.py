from pydantic import BaseModel

class EvaluationData(BaseModel):
    name: str
    teamName: str
    workAttitude: int
    goalAchievement: int
    collaboration: int
    comment: str

class RecommendationRequest(BaseModel):
    candidates: list[EvaluationData]
