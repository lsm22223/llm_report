# ----------------------------------------------------------------------------------------------------
# 작성목적 : answer_category_result와 answer_score 테이블의 NULL 값 체크
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | NULL 값 체크 스크립트 작성 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def check_null_values():
    db = DBConnector()
    
    # answer_category_result 테이블 NULL 체크
    cat_result_query = """
    SELECT 
        'answer_category_result' as table_name,
        COUNT(*) as total_rows,
        SUM(CASE WHEN ANS_CAT_RESULT_ID IS NULL THEN 1 ELSE 0 END) as "ANS_CAT_RESULT_ID",
        SUM(CASE WHEN EVAL_CAT_CD IS NULL THEN 1 ELSE 0 END) as "EVAL_CAT_CD",
        SUM(CASE WHEN ANS_SCORE_ID IS NULL THEN 1 ELSE 0 END) as "ANS_SCORE_ID",
        SUM(CASE WHEN ANS_CAT_SCORE IS NULL THEN 1 ELSE 0 END) as "ANS_CAT_SCORE",
        SUM(CASE WHEN STRENGTH_KEYWORD IS NULL THEN 1 ELSE 0 END) as "STRENGTH_KEYWORD",
        SUM(CASE WHEN WEAKNESS_KEYWORD IS NULL THEN 1 ELSE 0 END) as "WEAKNESS_KEYWORD",
        SUM(CASE WHEN RGS_DTM IS NULL THEN 1 ELSE 0 END) as "RGS_DTM",
        SUM(CASE WHEN UPD_DTM IS NULL THEN 1 ELSE 0 END) as "UPD_DTM"
    FROM answer_category_result;
    """
    
    # answer_score 테이블 NULL 체크
    ans_score_query = """
    SELECT 
        'answer_score' as table_name,
        COUNT(*) as total_rows,
        SUM(CASE WHEN ANS_SCORE_ID IS NULL THEN 1 ELSE 0 END) as "ANS_SCORE_ID",
        SUM(CASE WHEN INTV_ANS_ID IS NULL THEN 1 ELSE 0 END) as "INTV_ANS_ID",
        SUM(CASE WHEN ANS_SUMMARY IS NULL THEN 1 ELSE 0 END) as "ANS_SUMMARY",
        SUM(CASE WHEN EVAL_SUMMARY IS NULL THEN 1 ELSE 0 END) as "EVAL_SUMMARY",
        SUM(CASE WHEN INCOMPLETE_ANSWER IS NULL THEN 1 ELSE 0 END) as "INCOMPLETE_ANSWER",
        SUM(CASE WHEN INSUFFICIENT_CONTENT IS NULL THEN 1 ELSE 0 END) as "INSUFFICIENT_CONTENT",
        SUM(CASE WHEN SUSPECTED_COPYING IS NULL THEN 1 ELSE 0 END) as "SUSPECTED_COPYING",
        SUM(CASE WHEN SUSPECTED_IMPERSONATION IS NULL THEN 1 ELSE 0 END) as "SUSPECTED_IMPERSONATION",
        SUM(CASE WHEN RGS_DTM IS NULL THEN 1 ELSE 0 END) as "RGS_DTM",
        SUM(CASE WHEN UPD_DTM IS NULL THEN 1 ELSE 0 END) as "UPD_DTM"
    FROM answer_score;
    """
    
    try:
        with db.engine.connect() as conn:
            # answer_category_result 테이블 체크
            cat_result = conn.execute(text(cat_result_query)).fetchone()
            print("\n[answer_category_result] NULL 값 현황:")
            print("-" * 100)
            print(f"전체 레코드 수: {cat_result[1]}")
            print("-" * 100)
            for i, col in enumerate(cat_result._mapping.keys()):
                if i > 1:  # table_name과 total_rows 제외
                    null_count = cat_result[i]
                    if null_count > 0:
                        print(f"{col}: {null_count}개의 NULL 값")
            
            # answer_score 테이블 체크
            ans_score = conn.execute(text(ans_score_query)).fetchone()
            print("\n[answer_score] NULL 값 현황:")
            print("-" * 100)
            print(f"전체 레코드 수: {ans_score[1]}")
            print("-" * 100)
            for i, col in enumerate(ans_score._mapping.keys()):
                if i > 1:  # table_name과 total_rows 제외
                    null_count = ans_score[i]
                    if null_count > 0:
                        print(f"{col}: {null_count}개의 NULL 값")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    check_null_values() 