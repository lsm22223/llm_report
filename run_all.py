# ----------------------------------------------------------------------------------------------------
# 작성목적 : 면접 결과 분석 실행 스크립트
# 작성일 : 2025-06-23
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 순으로 기입)
# 2025-06-23 | 최초 구현 | 분석 프로세스 구현
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from scoring.score.score_calculator import process_scores
from scoring.comment.comment_generator import generate_all_comments
from scoring.keyword.keyword_extractor import extract_and_store_keywords
from sqlalchemy import text

def check_data_exists(db):
    """분석이 필요한 데이터가 있는지 확인합니다."""
    results = db.execute(text("""
        SELECT DISTINCT INTV_RESULT_ID 
        FROM interview_result 
        ORDER BY INTV_RESULT_ID
    """)).fetchall()
    
    return len(results) if results else 0

def main():
    try:
        print("\n🔍 분석이 필요한 면접 데이터 확인 중...")
        
        # 초기 데이터 확인
        db = DBConnector().SessionLocal()
        count = check_data_exists(db)
        db.close()
        
        if count == 0:
            print("📭 분석할 데이터가 없습니다.")
            return
            
        print(f"📋 총 {count}개의 답변 분석 시작")
        
        # 1. 점수 계산
        print("\n1️⃣ 점수 계산")
        db = DBConnector().SessionLocal()
        process_scores(db)
        db.close()
        
        # 2. 코멘트 생성
        print("\n2️⃣ 평가 코멘트 생성")
        db = DBConnector().SessionLocal()
        generate_all_comments(db)
        db.close()
        
        # 3. 키워드 추출
        print("\n3️⃣ 키워드 추출")
        db = DBConnector().SessionLocal()
        extract_and_store_keywords(db)
        db.close()
        
        print("\n✅ 모든 분석이 완료되었습니다!")
            
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
    finally:
        print("\n👋 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
