# ----------------------------------------------------------------------------------------------------
# 작성목적 : 면접 결과 분석 실행
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | 면접 결과 분석 실행 파일 생성 | 이소미
# ----------------------------------------------------------------------------------------------------

from db_connector import DBConnector
from score_calculator import process_scores

def main():
    print("[🚀] 면접 결과 분석을 시작합니다...")
    
    # DB 연결
    db = DBConnector().SessionLocal()
    
    try:
        # 점수 계산 및 등급 산정
        print("\n[1/1] 점수 계산 중...")
        process_scores(db)
        print("\n[✅] 분석이 완료되었습니다!")
        
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 