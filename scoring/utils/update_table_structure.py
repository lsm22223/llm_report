# ----------------------------------------------------------------------------------------------------
# 작성목적 : interview_category_result 테이블의 CAT_GRADE 컬럼 제거
# 작성일 : 2025-06-25

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-25 | 기능 개선 | CAT_GRADE 컬럼 제거 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def update_table_structure():
    """interview_category_result 테이블에서 CAT_GRADE 컬럼을 제거합니다."""
    try:
        # DB 연결
        db = DBConnector()
        
        with db.engine.connect() as conn:
            # CAT_GRADE 컬럼 제거
            conn.execute(text("ALTER TABLE interview_category_result DROP COLUMN IF EXISTS CAT_GRADE"))
            conn.commit()
            print("[✓] CAT_GRADE 컬럼이 성공적으로 제거되었습니다.")
            
    except Exception as e:
        print(f"[❌] 테이블 구조 변경 중 오류가 발생했습니다: {str(e)}")
        raise

if __name__ == "__main__":
    update_table_structure()