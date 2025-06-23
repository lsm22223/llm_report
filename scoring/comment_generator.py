# ----------------------------------------------------------------------------------------------------
# 작성목적 : 평가 코멘트 생성
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | 평가 코멘트 생성 기능 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

import os
from sqlalchemy import text
from scoring.db_connector import DBConnector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_category_info(db, eval_cat_cd: str) -> tuple[str, str]:
    """평가 항목 정보를 DB에서 가져옵니다."""
    result = db.execute(text("""
        SELECT 
            CAT_NM,
            CAT_DESC
        FROM evaluation_category
        WHERE EVAL_CAT_CD = :code
    """), {"code": eval_cat_cd}).first()
    
    if result:
        return (result[0], result[1] or "상세 설명 없음")
    return ("일반 역량", "")

def summarize_comments(db, eval_cat_cd: str, keyword_texts: list[str]) -> str:
    """GPT를 사용해 키워드를 바탕으로 코멘트를 생성합니다."""
    cat_name, cat_desc = get_category_info(db, eval_cat_cd)
    
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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

def generate_all_comments(db):
    print("\n[📝] 평가 코멘트 생성을 시작합니다...")
    
    # 1. INTV_RESULT_ID + EVAL_CAT_CD 별로 키워드 수집
    print("\n[1/3] 키워드 데이터 수집 중...")
    rows = db.execute(text("""
        SELECT 
            r.INTV_RESULT_ID,
            ac.EVAL_CAT_CD,
            ac.STRENGTH_KEYWORD,
            ac.WEAKNESS_KEYWORD
        FROM interview_result r
        JOIN answer_category_result ac ON r.INTV_RESULT_ID = ac.ANS_SCORE_ID
        WHERE (ac.STRENGTH_KEYWORD IS NOT NULL AND ac.STRENGTH_KEYWORD != '')
           OR (ac.WEAKNESS_KEYWORD IS NOT NULL AND ac.WEAKNESS_KEYWORD != '')
    """)).fetchall()

    # 2. 항목별 그룹핑
    print("\n[2/3] 데이터 그룹화 중...")
    from collections import defaultdict
    grouped = defaultdict(lambda: defaultdict(list))  # {INTV_RESULT_ID: {EVAL_CAT_CD: [(strength, weakness), ...]}}

    for row in rows:
        intv_result_id = row[0]
        eval_cat_cd = row[1]
        strength = row[2] or ""
        weakness = row[3] or ""
        grouped[intv_result_id][eval_cat_cd].append((strength, weakness))

    # 3. 항목별 LLM 호출 및 FEEDBACK_TXT 저장
    print("\n[3/3] 코멘트 생성 및 저장 중...")
    for intv_result_id, cat_dict in grouped.items():
        for eval_cat_cd, keyword_pairs in cat_dict.items():
            try:
                # 키워드 쌍을 문자열로 변환
                keyword_texts = []
                for strength, weakness in keyword_pairs:
                    if strength:
                        keyword_texts.append(f"강점: {strength}")
                    if weakness:
                        keyword_texts.append(f"약점: {weakness}")
                
                feedback = summarize_comments(db, eval_cat_cd, keyword_texts)
                
                db.execute(text("""
                    INSERT INTO interview_category_result (
                        INTV_RESULT_ID, EVAL_CAT_CD, FEEDBACK_TXT, RGS_DTM, UPD_DTM
                    ) VALUES (:id, :cat_cd, :txt, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE 
                        FEEDBACK_TXT = :txt,
                        UPD_DTM = NOW()
                """), {
                    "id": intv_result_id,
                    "cat_cd": eval_cat_cd,
                    "txt": feedback
                })
                print(f"[🗨️] {intv_result_id}-{eval_cat_cd} 코멘트 저장 완료")
            except Exception as e:
                print(f"[❌] {intv_result_id}-{eval_cat_cd} LLM 요약 실패: {e}")

    db.commit()
    print("\n[✅] 모든 코멘트 생성이 완료되었습니다!")

def main():
    print("[🚀] 평가 코멘트 생성을 시작합니다...")
    
    # DB 연결
    db = DBConnector().SessionLocal()
    
    try:
        # 코멘트 생성
        generate_all_comments(db)
        
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
