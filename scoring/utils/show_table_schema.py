# ----------------------------------------------------------------------------------------------------
# 작성목적 : 테이블 스키마 확인
# 작성일 : 2025-06-24

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-24 | 최초 구현 | 테이블 스키마 확인 스크립트 작성 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scoring.core.db_connector import DBConnector
import pandas as pd

def show_table_schema():
    """테이블 스키마를 확인합니다."""
    print("\n[🔍] 테이블 스키마 확인")
    
    db = DBConnector().SessionLocal()
    
    try:
        # 테이블 목록 조회
        tables = pd.read_sql("""
            SHOW TABLES
        """, db.bind)
        
        for table_name in tables.iloc[:, 0]:
            print(f"\n[📋] {table_name} 테이블 스키마:")
            schema = pd.read_sql(f"DESCRIBE {table_name}", db.bind)
            print(schema.to_string())
            
    finally:
        db.close()

if __name__ == "__main__":
    show_table_schema() 