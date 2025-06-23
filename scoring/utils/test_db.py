# ----------------------------------------------------------------------------------------------------
# 작성목적 : DB 연결 테스트
# 작성일 : 2025-06-23
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-23 | 최초 구현 | DB 연결 테스트 스크립트 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def test_connection():
    print("\n[🔍] DB 연결 테스트를 시작합니다...")
    
    try:
        # DB 연결
        db = DBConnector().SessionLocal()
        
        # 간단한 쿼리 실행
        result = db.execute(text("SELECT COUNT(*) FROM interview_category_result")).scalar()
        print(f"\n[✅] DB 연결 성공! interview_category_result 테이블에 {result}개의 레코드가 있습니다.")
        
        return True
    except Exception as e:
        print(f"\n[❌] DB 연결 실패: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_connection() 