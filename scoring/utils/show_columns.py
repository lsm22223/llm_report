# ----------------------------------------------------------------------------------------------------
# 작성목적 : 테이블 컬럼 정보 조회
# 작성일 : 2025-06-24

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-24 | 최초 구현 | 테이블 컬럼 정보 조회 기능 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def main():
    print("\n[🔍] 테이블 컬럼 정보를 조회합니다...")
    
    # DB 연결
    db = DBConnector().SessionLocal()
    
    try:
        tables = [
            'interview_result',
            'interview_category_result',
            'answer_score',
            'answer_category_result',
            'evaluation_category'
        ]
        
        for table in tables:
            print(f"\n=== {table} 테이블 ===")
            results = db.execute(text(f"""
                SELECT 
                    COLUMN_NAME,
                    COLUMN_TYPE,
                    IS_NULLABLE,
                    COLUMN_KEY,
                    EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = :table
                ORDER BY ORDINAL_POSITION
            """), {"table": table}).fetchall()
            
            print(f"{'컬럼명':<20} {'타입':<15} {'NULL':<6} {'키':<5} {'기타'}")
            print("-" * 60)
            for row in results:
                print(f"{row[0]:<20} {row[1]:<15} {row[2]:<6} {row[3]:<5} {row[4]}")
            
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 