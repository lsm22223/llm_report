# ----------------------------------------------------------------------------------------------------
# 작성목적 : 키워드 추출 실행 스크립트
# 작성일 : 2025-06-23

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-23 | 최초 구현 | 키워드 추출 실행 스크립트 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from scoring.keyword.keyword_extractor import extract_and_store_keywords

def main():
    print("[🚀] 키워드 추출을 시작합니다...")
    
    # DB 연결
    db = DBConnector().SessionLocal()
    
    try:
        # 키워드 추출 및 저장
        extract_and_store_keywords(db)
        
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 