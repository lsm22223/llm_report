# ----------------------------------------------------------------------------------------------------
# 작성목적 : 테이블 데이터 확인
# 작성일 : 2025-06-24

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-24 | 최초 구현 | 테이블 데이터 확인 기능 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
import pandas as pd

def check_tables():
    # DB 연결
    db_connector = DBConnector()
    db = db_connector.SessionLocal()
    
    try:
        # 1. answer_score 테이블 확인
        print("\n[1] answer_score 테이블 데이터:")
        answer_scores = pd.read_sql("""
            SELECT * FROM answer_score LIMIT 5
        """, db.bind)
        print(answer_scores.to_string())
        
        answer_count = pd.read_sql("""
            SELECT COUNT(*) as count FROM answer_score
        """, db.bind)
        print(f"\n총 {answer_count.iloc[0]['count']}개의 answer_score 데이터")
        
        # 2. answer_category_result 테이블 확인
        print("\n[2] answer_category_result 테이블 데이터:")
        category_results = pd.read_sql("""
            SELECT * FROM answer_category_result LIMIT 5
        """, db.bind)
        print(category_results.to_string())
        
        category_count = pd.read_sql("""
            SELECT COUNT(*) as count FROM answer_category_result
        """, db.bind)
        print(f"\n총 {category_count.iloc[0]['count']}개의 answer_category_result 데이터")
        
        # 3. evaluation_category 테이블 확인
        print("\n[3] evaluation_category 테이블 데이터:")
        categories = pd.read_sql("""
            SELECT * FROM evaluation_category
        """, db.bind)
        print(categories.to_string())
        
    finally:
        db.close()

if __name__ == "__main__":
    check_tables() 