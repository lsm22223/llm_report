# ----------------------------------------------------------------------------------------------------
# 작성목적 : 면접 결과 분석 실행 스크립트
# 작성일 : 2025-06-23
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-23 | 최초 구현 | 분석 프로세스 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.db_connector import DBConnector
from scoring.score_calculator import process_scores
from scoring.comment_generator import generate_all_comments
from scoring.keyword_extractor import extract_and_store_keywords
from sqlalchemy import text

def main():
    # DB 커넥터 초기화
    db = DBConnector().SessionLocal()
    
    try:
        print("\n🔍 분석이 필요한 면접 데이터 확인 중...")
        
        # 기존 interview_result 테이블의 데이터만 가져오기
        results = db.execute(text("""
            SELECT DISTINCT INTV_RESULT_ID 
            FROM interview_result 
            ORDER BY INTV_RESULT_ID
        """)).fetchall()
        
        if not results:
            print("📭 분석할 데이터가 없습니다.")
            return
            
        print(f"📋 총 {len(results)} 개의 답변 분석 시작")
        
        # 1. 점수 계산
        print("\n1️⃣ 점수 계산")
        process_scores(db)
        
        # 2. 코멘트 생성
        print("\n2️⃣ 평가 코멘트 생성")
        generate_all_comments(db)
        
        # 3. 키워드 추출
        print("\n3️⃣ 키워드 추출")
        extract_and_store_keywords(db)
        
        print("\n✅ 모든 분석이 완료되었습니다!")
            
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
    finally:
        db.close()
        print("\n👋 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
