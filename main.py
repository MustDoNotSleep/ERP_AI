from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# .env 환경변수 로드
load_dotenv()

app = FastAPI()

# OpenAI 클라이언트
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# [입력 데이터 구조] Spring Boot에서 받을 데이터
class EvaluationData(BaseModel):
    name: str         # 이름
    department: str   # 부서 (TeamName)
    total_score: int  # 종합 점수
    comment: str      # 평가자 코멘트

class RecommendationRequest(BaseModel):
    candidates: list[EvaluationData]

# [AI 추천 로직]
@app.post("/ai/recommend")
def recommend_employees(request: RecommendationRequest):
    print(f"🔍 AI 분석 시작: 총 {len(request.candidates)}명의 후보 분석 중...")

    if not request.candidates:
        return {"result": []}

    # 프롬프트 데이터 구성
    candidates_text = ""
    for emp in request.candidates:
        candidates_text += f"- 이름: {emp.name}, 부서: {emp.department}, 총점: {emp.total_score}, 평가: {emp.comment}\n"

    # GPT에게 명령
    system_prompt = """
    당신은 공정한 인사 평가 전문가입니다.
    제공된 직원 데이터를 분석하여 '최우수 사원 3명'을 선정하세요.
    
    [선정 기준]
    1. 총점이 높은 순서대로 우선순위를 둡니다.
    2. 평가 코멘트가 긍정적이고 구체적인 직원을 우대합니다.
    
    [응답 형식]
    반드시 아래와 같은 JSON 배열(List) 형태로만 답변하세요. 코드블록(```json)이나 다른 말은 절대 쓰지 마세요.
    [
        {"rank": 1, "name": "이름", "department": "부서", "reason": "추천 이유(한 문장 요약)"},
        {"rank": 2, "name": "이름", "department": "부서", "reason": "추천 이유(한 문장 요약)"},
        {"rank": 3, "name": "이름", "department": "부서", "reason": "추천 이유(한 문장 요약)"}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # GPT-4o가 있다면 gpt-4o 사용 추천
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 후보자들 중에서 추천해주세요:\n{candidates_text}"}
            ],
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        print(f"🤖 AI 응답: {ai_response}")

        # JSON 파싱 (GPT가 가끔 ```json 등을 붙일 때를 대비)
        clean_response = ai_response.replace("```json", "").replace("```", "").strip()
        result_list = json.loads(clean_response)
        
        return {"status": "success", "recommendations": result_list}

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 서버 헬스 체크용
@app.get("/")
def read_root():
    return {"status": "ERP AI Server Running"}