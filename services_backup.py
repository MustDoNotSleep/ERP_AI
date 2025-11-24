from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from models import RecommendationRequest

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_recommendations(request: RecommendationRequest):
    candidates_text = ""
    for emp in request.candidates:
        avg_score = (emp.workAttitude + emp.goalAchievement + emp.collaboration) / 3
        candidates_text += f"- 이름: {emp.name}, 팀명: {emp.teamName}, 근무태도: {emp.workAttitude}, 목표달성: {emp.goalAchievement}, 협업점수: {emp.collaboration}, 평균점수: {avg_score:.2f}, 평가: {emp.comment}\n"

    system_prompt = """
    당신은 공정한 인사 평가 전문가입니다.
    제공된 직원의 근무 평가 데이터를 분석하여 '최우수 사원 3명'을 선정하세요.

    [선정 기준]
    1. 근무태도, 목표달성, 협업점수의 평균점수가 높은 순서대로 우선순위를 둡니다.
    2. 평가 코멘트가 긍정적이고 구체적인 직원을 우대합니다.

    [응답 형식]
    반드시 아래와 같은 JSON 배열(List) 형태로만 답변하세요. 코드블록(```json)이나 다른 말은 절대 쓰지 마세요.
    [
        {"rank": 1, "name": "이름", "teamName": "팀명", "reason": "추천 이유(한 문장 요약)"},
        {"rank": 2, "name": "이름", "teamName": "팀명", "reason": "추천 이유(한 문장 요약)"},
        {"rank": 3, "name": "이름", "teamName": "팀명", "reason": "추천 이유(한 문장 요약)"}
    ]
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 후보자들 중에서 추천해주세요:\n{candidates_text}"}
        ],
        temperature=0.7
    )
    ai_response = response.choices[0].message.content
    clean_response = ai_response.replace("```json", "").replace("```", "").strip()
    result_list = json.loads(clean_response)
    return result_list
