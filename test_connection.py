# ----------------------------------------------------------------------------------------------------
# 작성목적 : DB 연결 테스트
# 작성일 : 2024-01-01
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-01-01 | 최초 구현 | DB 연결 테스트 구현 | AI Assistant
# ----------------------------------------------------------------------------------------------------

from scoring.db_connector import DBConnector
from sqlalchemy import text

def test_connection():
    try:
        print("\n🔍 DB 연결 테스트 시작...")
        db = DBConnector()
        
        # 1. 기본 연결 테스트
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            if result[0] == 1:
                print("✅ 기본 연결 성공")
            
            # 2. 테이블 존재 여부 확인
            tables = [
                "interview_result",
                "interview_category",
                "interview_category_result",
                "answer_category_result",
                "evaluation_category",
                "answer_score"
            ]
            
            print("\n📋 테이블 존재 여부 확인:")
            for table in tables:
                try:
                    conn.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    print(f"  ✅ {table}: 존재함")
                except Exception as e:
                    print(f"  ❌ {table}: 존재하지 않음 ({str(e)})")
            
            # 3. 데이터 샘플 확인
            print("\n📊 데이터 샘플 확인:")
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM interview_result")).fetchone()
                print(f"  ✅ interview_result 테이블 레코드 수: {result[0]}")
            except Exception as e:
                print(f"  ❌ 데이터 조회 실패: {str(e)}")
                
        print("\n✨ 테스트 완료")
        return True
        
    except Exception as e:
        print(f"\n❌ DB 연결 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 