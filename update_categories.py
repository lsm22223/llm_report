from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scoring.core.db_connector import DBConnector
from datetime import datetime

# DB 연결
db = DBConnector()
now = datetime.now()

try:
    with db.engine.connect() as conn:
        # 1. 기존 데이터 삭제 (순서 중요: 자식 테이블부터 삭제)
        conn.execute(text("DELETE FROM pdf_report"))
        conn.execute(text("DELETE FROM interview_category_result"))
        conn.execute(text("DELETE FROM interview_result"))
        conn.execute(text("DELETE FROM answer_category_result WHERE EVAL_CAT_CD IN ('ENGLISH_FLUENCY', 'ENGLISH_GRAMMAR', 'ENGLISH_ABILITY')"))
        conn.execute(text("DELETE FROM evaluation_category WHERE EVAL_CAT_CD IN ('ENGLISH_FLUENCY', 'ENGLISH_GRAMMAR', 'ENGLISH_ABILITY')"))
        
        # 2. 통합된 영어 능력 카테고리 추가
        conn.execute(text("""
            INSERT INTO evaluation_category 
            (EVAL_CAT_CD, CAT_NM, MAX_SCORE, WEIGHT, RGS_DTM, UPD_DTM) 
            VALUES 
            ('ENGLISH_ABILITY', '영어 능력', 100, 1.0, :now, :now)
        """), {'now': now})
        
        # 3. 테스트용 답변 데이터 추가
        conn.execute(text("""
            INSERT INTO answer_score 
            (INTV_ANS_ID, ANS_SCORE_ID, RGS_DTM, UPD_DTM) 
            VALUES 
            (301, 1001, :now, :now)
        """), {'now': now})
        
        # 4. 답변 카테고리 결과 추가 (세부 평가를 위한 FLUENCY와 GRAMMAR)
        conn.execute(text("""
            INSERT INTO answer_category_result 
            (ANS_SCORE_ID, EVAL_CAT_CD, ANS_CAT_SCORE, STRENGTH_KEYWORD, WEAKNESS_KEYWORD, RGS_DTM, UPD_DTM) 
            VALUES 
            (1001, 'ENGLISH_FLUENCY', 80, '발음이 정확함|자연스러운 표현 사용', '전문 용어 부족', :now, :now),
            (1001, 'ENGLISH_GRAMMAR', 70, '기본 문법 이해도 높음', '복잡한 문장 구성 미흡', :now, :now)
        """), {'now': now})
        
        # 변경사항 커밋
        conn.commit()
        print('데이터 업데이트 완료')
        
        # 5. 현재 평가 카테고리 조회
        result = conn.execute(text('SELECT EVAL_CAT_CD, CAT_NM, MAX_SCORE, WEIGHT FROM evaluation_category'))
        print('\n현재 평가 카테고리:')
        for row in result:
            print(f"{row.EVAL_CAT_CD}: {row.CAT_NM} (최대점수: {row.MAX_SCORE}, 가중치: {row.WEIGHT})")
    
except Exception as e:
    print(f'오류 발생: {str(e)}')
    if 'conn' in locals():
        conn.rollback() 