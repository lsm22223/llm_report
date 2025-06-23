# ----------------------------------------------------------------------------------------------------
# 작성목적 : 추출된 키워드 조회
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | 키워드 조회 스크립트 생성 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.db_connector import DBConnector
from sqlalchemy import text

def main():
    print("\n[🔍] 추출된 키워드를 조회합니다...")
    
    # DB 연결
    db = DBConnector().SessionLocal()
    
    try:
        # 키워드 조회
        results = db.execute(text("""
            SELECT INTV_RESULT_ID, STRENGTH_KEYWORD, WEAKNESS_KEYWORD 
            FROM interview_result 
            ORDER BY INTV_RESULT_ID
        """)).fetchall()
        
        print("\n=== 면접자별 키워드 ===")
        for row in results:
            print(f"\n📌 면접자 ID: {row[0]}")
            print(f"💪 강점: {row[1]}")
            print(f"🔧 약점: {row[2]}")
            print("-" * 50)
            
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 