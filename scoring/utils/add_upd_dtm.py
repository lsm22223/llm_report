# ----------------------------------------------------------------------------------------------------
# 작성목적 : answer_category_result 테이블에 UPD_DTM 컬럼 추가
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | UPD_DTM 컬럼 추가 및 RGS_DTM 값으로 초기화 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def add_upd_dtm_column():
    db = DBConnector()
    
    # 1. UPD_DTM 컬럼 추가
    add_column_query = """
    ALTER TABLE answer_category_result
    ADD COLUMN UPD_DTM TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """
    
    # 2. UPD_DTM 값을 RGS_DTM 값으로 초기화
    update_values_query = """
    UPDATE answer_category_result
    SET UPD_DTM = RGS_DTM;
    """
    
    try:
        with db.engine.connect() as conn:
            # 컬럼 추가
            conn.execute(text(add_column_query))
            print("UPD_DTM 컬럼 추가 완료!")
            
            # 값 초기화
            conn.execute(text(update_values_query))
            conn.commit()
            print("UPD_DTM 값 초기화 완료!")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    add_upd_dtm_column() 