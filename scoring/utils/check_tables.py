# ----------------------------------------------------------------------------------------------------
# 작성목적 : DB 테이블 존재 여부 확인
# 작성일 : 2025-06-23

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-23 | 최초 구현 | DB 테이블 존재 여부 확인 기능 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def check_tables():
    """DB 테이블 존재 여부를 확인합니다."""
    print("[🔍] DB 테이블 구조를 확인합니다...")
    
    db = DBConnector().SessionLocal()
    try:
        # interview_result 테이블 구조 확인
        result = db.execute(text("DESCRIBE interview_result")).fetchall()
        print("\n[📋] interview_result 테이블 구조:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
            
        # interview_answer 테이블 구조 확인
        result = db.execute(text("DESCRIBE interview_answer")).fetchall()
        print("\n[📋] interview_answer 테이블 구조:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
            
        # answer_category_result 테이블 구조 확인
        result = db.execute(text("DESCRIBE answer_category_result")).fetchall()
        print("\n[📋] answer_category_result 테이블 구조:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
            
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_tables() 