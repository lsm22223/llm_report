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
    # 1. 평가 카테고리 추가
    with db.engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO evaluation_category 
            (EVAL_CAT_CD, CAT_NM, MAX_SCORE, WEIGHT, RGS_DTM, UPD_DTM) 
            VALUES 
            ('ENGLISH_FLUENCY', '영어 유창성', 100, 0.5, :now, :now),
            ('ENGLISH_GRAMMAR', '영어 문법', 100, 0.5, :now, :now)
        """), {'now': now})
        
        # 2. 테스트용 답변 데이터 추가
        conn.execute(text("""
            INSERT INTO answer_score 
            (INTV_ANS_ID, ANS_SCORE_ID, RGS_DTM, UPD_DTM) 
            VALUES 
            (301, 1001, :now, :now)
        """), {'now': now})
        
        # 3. 답변 카테고리 결과 추가
        conn.execute(text("""
            INSERT INTO answer_category_result 
            (ANS_SCORE_ID, EVAL_CAT_CD, ANS_CAT_SCORE, STRENGTH_KEYWORD, WEAKNESS_KEYWORD, RGS_DTM, UPD_DTM) 
            VALUES 
            (1001, 'ENGLISH_FLUENCY', 80, '발음이 정확함|자연스러운 표현 사용', '전문 용어 부족', :now, :now),
            (1001, 'ENGLISH_GRAMMAR', 70, '기본 문법 이해도 높음', '복잡한 문장 구성 미흡', :now, :now)
        """), {'now': now})
        
        # 변경사항 커밋
        conn.commit()
        print('테스트 데이터 추가 완료')
    
except Exception as e:
    print(f'오류 발생: {str(e)}')
    if 'conn' in locals():
        conn.rollback() 
        