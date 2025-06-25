# ----------------------------------------------------------------------------------------------------
# 작성목적 : 면접 답변 점수 계산 실행
# 작성일 : 2025-06-24

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-24 | 기능 개선 | DB 저장 기능 추가 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from scoring.score.score_calculator import process_scores

if __name__ == "__main__":
    db = DBConnector().SessionLocal()
    try:
        process_scores(db)
    finally:
        db.close() 