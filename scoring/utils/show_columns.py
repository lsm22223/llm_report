# ----------------------------------------------------------------------------------------------------
# 작성목적 : answer_category_result와 answer_score 테이블의 컬럼명 조회
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | 컬럼명 조회 스크립트 작성 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def show_columns():
    db = DBConnector()
    
    # MySQL의 경우
    columns_query = """
    SELECT TABLE_NAME, COLUMN_NAME 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME IN ('answer_category_result', 'answer_score')
    ORDER BY TABLE_NAME, ORDINAL_POSITION;
    """
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(columns_query))
            
            current_table = None
            for row in result:
                if current_table != row[0]:
                    current_table = row[0]
                    print(f"\n[{current_table}] 컬럼 목록:")
                    print("-" * 50)
                
                print(f"- {row[1]}")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    show_columns() 