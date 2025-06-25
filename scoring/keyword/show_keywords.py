# ----------------------------------------------------------------------------------------------------
# 작성목적 : 키워드 추출 결과 조회
# 작성일 : 2025-06-23

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-23 | 최초 구현 | 키워드 추출 결과 조회 기능 구현 | 이소미
# 2025-06-24 | 쿼리 수정 | 키워드 컬럼명 수정 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def main():
    print("\n[🔍] 추출된 키워드를 조회합니다...")
    
    # DB 연결
    db = DBConnector().SessionLocal()
    
    try:
        # 키워드 조회
        results = db.execute(text("""
            SELECT 
                INTV_RESULT_ID, 
                STRENGTH_KEYWORD, 
                WEAKNESS_KEYWORD,
                OVERALL_SCORE,
                OVERALL_GRADE,
                OVERALL_RANK
            FROM interview_result 
            ORDER BY INTV_RESULT_ID
        """)).fetchall()
        
        print("\n=== 면접자별 키워드 ===")
        for row in results:
            print(f"\n📌 면접진행 ID: {row[0]}")
            print(f"📊 종합 점수: {row[3]:.2f}")
            print(f"📝 전체 등급: {row[4]}")
            print(f"🏆 전체 순위: {row[5]}위")
            print(f"💪 강점: {row[1]}")
            print(f"🔧 약점: {row[2]}")
            print("-" * 80)
            
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 