# ----------------------------------------------------------------------------------------------------
# 작성목적 : 면접 답변 키워드 추출
# 작성일 : 2025-06-23

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-23 | 최초 구현 | 면접 답변 키워드 추출 기능 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import defaultdict
from openai import OpenAI
import os
from dotenv import load_dotenv
from scoring.core.db_connector import DBConnector

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_keywords(feedbacks: list[str]) -> tuple[str, str]:
    """피드백 텍스트들에서 강점과 약점 키워드를 추출합니다."""
    prompt = (
        "다음은 한 지원자의 면접 피드백입니다. 이를 바탕으로 강점과 약점 키워드를 추출해주세요.\n\n"
        "피드백 목록:\n" +
        "\n".join(f"- {txt}" for txt in feedbacks) +
        "\n\n강점과 약점을 각각 최대 6개의 키워드로 요약해주세요. 중요한 키워드 위주로 추출하되, 의미있는 키워드만 추출하세요.\n"
        "답변 형식: '강점: 키워드1,키워드2,키워드3... | 약점: 키워드1,키워드2,키워드3...'"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    result = response.choices[0].message.content.strip()
    strength, weakness = result.split("|")
    
    strength = strength.split(":")[1].strip()
    weakness = weakness.split(":")[1].strip()
    
    return strength, weakness

def extract_and_store_keywords(db: Session):
    print("\n[📝] 키워드 추출을 시작합니다...")
    
    # 1. 면접자별 FEEDBACK_TXT 모으기
    print("\n[1/2] 피드백 데이터 수집 중...")
    rows = db.execute(text("""
        SELECT INTV_RESULT_ID, FEEDBACK_TXT
        FROM interview_category_result
        WHERE FEEDBACK_TXT IS NOT NULL AND FEEDBACK_TXT != ''
    """)).fetchall()

    grouped = defaultdict(list)  # {INTV_RESULT_ID: [txt1, txt2, ...]}

    for row in rows:
        grouped[row[0]].append(row[1])

    # 2. LLM에 전달하고 저장
    print("\n[2/2] 키워드 추출 및 저장 중...")
    for intv_result_id, feedbacks in grouped.items():
        try:
            strength, weakness = extract_keywords(feedbacks)
            db.execute(text("""
                UPDATE interview_result
                SET STRENGTH_KEYWORD = :s,
                    WEAKNESS_KEYWORD = :w,
                    UPD_DTM = NOW()
                WHERE INTV_RESULT_ID = :id
            """), {
                "id": intv_result_id,
                "s": strength,
                "w": weakness
            })
            print(f"[🔍] {intv_result_id} → 키워드 저장 완료")
        except Exception as e:
            print(f"[❌] {intv_result_id} 키워드 추출 실패: {e}")

    db.commit()
    print("\n[✅] 모든 키워드 추출이 완료되었습니다!")
