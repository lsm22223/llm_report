# scoring/llm.py

import os
import sys
import openai
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import text

# backend/src를 Python path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 필요한 함수만 직접 import
from src.domain.evaluations.crud import get_evaluation_category_by_code

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_category_description(db: Session, eval_cat_cd: str) -> tuple[str, str]:
    """평가 항목 정보를 DB에서 가져옵니다.
    
    Returns:
        tuple[str, str]: (카테고리명, 상세설명) 튜플
    """
    category = get_evaluation_category_by_code(db, eval_cat_cd)
    if category:
        return (
            category.evaluation_category_name,
            category.evaluation_category_description or "상세 설명 없음"
        )
    return ("일반 역량", "")

def summarize_comments(db: Session, eval_cat_cd: str, keyword_texts: list[str]) -> str:
    cat_name, cat_desc = get_category_description(db, eval_cat_cd)
    
    prompt = (
        f"다음은 한 지원자의 '{eval_cat_cd}' 항목에 대한 평가 키워드들입니다.\n"
        f"평가 항목: {cat_name}\n"
        f"평가 설명: {cat_desc}\n\n"
        "이를 바탕으로 SK AX 채용팀 시각의 종합 코멘트를 작성해 주세요.\n"
        "해당 평가 항목의 특성을 잘 반영하여 한 문장으로 작성해 주세요.\n\n"
        "키워드 목록:\n" +
        "\n".join(f"- {txt}" for txt in keyword_texts if txt.strip()) +
        "\n\n[답변 예시]\n"
        f"이 지원자는 {cat_name} 측면에서 ~한 강점을 보였으나, ~한 부분은 보완이 필요합니다."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()


# scoring/llm.py (기존에 이어서 추가)

def extract_keywords(feedback_txts: list[str]) -> tuple[str, str]:
    prompt = (
        "다음은 한 지원자에 대한 항목별 종합 평가 피드백입니다.\n"
        "내용을 바탕으로 응시자의 특성을 명확히 드러내는 강점 키워드 6개, 약점 키워드 6개를 추출해주세요.\n\n"
        "피드백 내용:\n" +
        "\n".join(f"- {txt}" for txt in feedback_txts if txt.strip()) +
        "\n\n[출력 형식 예시]\n"
        "강점 키워드: 분석력, 소통, 주도성\n"
        "약점 키워드: 설득력, 실행력, 감정관리"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content
    strength, weakness = "", ""

    for line in content.splitlines():
        if "강점" in line:
            strength = line.split(":", 1)[-1].strip()
        elif "약점" in line:
            weakness = line.split(":", 1)[-1].strip()

    return strength, weakness

def extract_keywords_and_update_db(db: Session, feedback_txts: list[str], intv_result_id: int):
    strength, weakness = extract_keywords(feedback_txts)
    
    db.execute(text("""
        UPDATE interview_result
        SET STRENGTH_KEYWORDS = :s,
            WEAKNESS_KEYWORDS = :w,
            UPD_DTM = NOW()
        WHERE INTV_RESULT_ID = :id
    """), {
        "id": intv_result_id,
        "s": strength,
        "w": weakness
    })
