from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from models import RecommendationRequest

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# GPT 응답을 안전하게 JSON으로 변환하는 함수
def safe_json_parse(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except:
        # JSON 배열 부분만 추출해서 다시 시도
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
        raise ValueError("⚠️ GPT JSON 파싱 실패")


def get_recommendations(request: RecommendationRequest):
    candidates_text = ""
    for emp in request.candidates:
        avg_score = (emp.workAttitude + emp.goalAchievement + emp.collaboration) / 3
        candidates_text += (
            f"- 이름: {emp.name}, 팀명: {emp.teamName}, 근무태도: {emp.workAttitude}, "
            f"목표달성: {emp.goalAchievement}, 협업점수: {emp.collaboration}, "
            f"평균점수: {avg_score:.2f}, 평가: {emp.comment}\n"
        )

    system_prompt = """
    당신은 공정한 인사 평가 전문가입니다.
    제공된 직원의 근무 평가 데이터를 분석하여 '최우수 사원 3명'을 선정하세요.

    [선정 기준]
    1. 근무태도, 목표달성, 협업점수의 평균점수가 높은 순서대로 우선순위를 둡니다.
    2. 평가 코멘트가 긍정적이고 구체적인 직원을 우대합니다.
    3. 동일 점수일 경우, 평가 코멘트의 질을 고려하여 선정합니다.
    4. 편향되지 않고 객관적인 시각으로 평가하세요.
    5. 후보자가 3명 미만이면 가능한 인원을 추천하세요.
    6. 동일인은 표시하면 안됩니다.
    7. 추천 AI는 년도의 분기별 한번씩 보여지고, 분기별 데이터를 이용합니다.
    8. 추천 이유는 다 동일한 문구 이면 안됩니다.



    [응답 형식]
    반드시 아래와 같은 JSON 배열(List) 형태로만 답변하세요. 코드블록(```json)이나 다른 말은 절대 쓰지 마세요.
    [
        {"rank": 1, "name": "이름", "teamName": "팀명", "reason": "추천 이유(한 문장 요약)"},
        {"rank": 2, "name": "이름", "teamName": "팀명", "reason": "추천 이유(한 문장 요약)"},
        {"rank": 3, "name": "이름", "teamName": "팀명", "reason": "추천 이유(한 문장 요약)"}
    ]
    """

    # GPT API 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 후보자들 중에서 추천해주세요:\n{candidates_text}"}
        ],
        temperature=0.7
    )

    ai_response = response.choices[0].message.content

    # 개발 중 로그 확인용 (배포 시 제거 가능)
    print("📌 AI RAW RESPONSE ↓")
    print(ai_response)

    # GPT의 응답을 파싱
    result_list = safe_json_parse(ai_response)

    return result_list
