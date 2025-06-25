# ----------------------------------------------------------------------------------------------------
# 작성목적 : 평가 카테고리 업데이트 및 초기화
# 작성일 : 2025-06-25
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-25 | 기능 개선 | ENGLISH_FLUENCY와 ENGLISH_GRAMMAR를 ENGLISH_ABILITY로 통합 | 이소미
# ----------------------------------------------------------------------------------------------------

from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scoring.core.db_connector import DBConnector
from datetime import datetime

def init_categories():
    """평가 카테고리를 초기화합니다."""
    db = DBConnector().SessionLocal()
    now = datetime.now()

    try:
        # 1. 기존 데이터 삭제 (순서 중요: 자식 테이블부터 삭제)
        print("\n[1단계] 기존 데이터 삭제")
        db.execute(text("DELETE FROM pdf_report"))
        print("✓ pdf_report 테이블 데이터 삭제 완료")
        
        db.execute(text("DELETE FROM interview_category_result"))
        print("✓ interview_category_result 테이블 데이터 삭제 완료")
        
        db.execute(text("DELETE FROM interview_result"))
        print("✓ interview_result 테이블 데이터 삭제 완료")
        
        db.execute(text("DELETE FROM answer_category_result"))
        print("✓ answer_category_result 테이블 데이터 삭제 완료")
        
        db.execute(text("DELETE FROM answer_score"))
        print("✓ answer_score 테이블 데이터 삭제 완료")
        
        db.execute(text("DELETE FROM evaluation_category"))
        print("✓ evaluation_category 테이블 데이터 삭제 완료")
        
        # 2. 평가 카테고리 추가
        print("\n[2단계] 평가 카테고리 추가")
        db.execute(text("""
            INSERT INTO evaluation_category 
            (EVAL_CAT_CD, CAT_NM, MAX_SCORE, WEIGHT, RGS_DTM, UPD_DTM) 
            VALUES 
            ('ENGLISH_ABILITY', '영어 능력', 100, 0.2, :now, :now),
            ('COMM_SKILL', '의사소통력', 100, 0.1, :now, :now),
            ('PROB_SOLVE', '문제해결력', 100, 0.2, :now, :now),
            ('TECH_SKILL', '기술역량', 100, 0.2, :now, :now),
            ('JOB_COMPATIBILITY', '직무적합도', 100, 0.15, :now, :now),
            ('ORG_FIT', '조직적합도', 100, 0.15, :now, :now)
        """), {'now': now})
        print("✓ 평가 카테고리 추가 완료")
        
        # 3. 현재 평가 카테고리 조회
        result = db.execute(text('SELECT EVAL_CAT_CD, CAT_NM, MAX_SCORE, WEIGHT FROM evaluation_category'))
        print('\n현재 평가 카테고리:')
        for row in result:
            print(f"{row.EVAL_CAT_CD}: {row.CAT_NM} (최대점수: {row.MAX_SCORE}, 가중치: {row.WEIGHT})")
        
        # 변경사항 커밋
        db.commit()
        print("\n✓ 모든 작업이 완료되었습니다.")

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_categories() 