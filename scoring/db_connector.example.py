# ----------------------------------------------------------------------------------------------------
# 작성목적 : 백엔드 DB 연결 및 데이터 접근 관리
# 작성일 : 2025-06-23
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-23 | 최초 구현 | DB 연결 및 데이터 접근 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import pandas as pd

# 환경 변수 로드
load_dotenv()

class DBConnector:
    def __init__(self):
        self.DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/dbname"
        self.engine = create_engine(
            self.DATABASE_URL,
            connect_args={
                'ssl': False  # SSL 연결 비활성화
            }
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_pending_interviews(self):
        """분석이 필요한 면접 데이터를 가져옵니다."""
        query = text("""
            SELECT 
                ir.INTV_RESULT_ID,
                ir.INTV_PROC_ID,
                ia.INTV_ANS_ID,
                ia.ANS_CONTENT,
                iq.QUEST_CD
            FROM interview_result ir
            JOIN interview_answer ia ON ir.INTV_PROC_ID = ia.INTV_PROC_ID
            JOIN interview_question iq ON ia.QUEST_CD = iq.QUEST_CD
            WHERE ir.OVERALL_SCORE IS NULL
            AND ia.ANS_CONTENT IS NOT NULL
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return pd.DataFrame(result.fetchall(), 
                              columns=['INTV_RESULT_ID', 'INTV_PROC_ID', 'INTV_ANS_ID', 'ANS_CONTENT', 'QUEST_CD'])

    def update_answer_scores(self, intv_ans_id: int, scores: dict):
        """답변별 점수를 업데이트합니다."""
        query = text("""
            INSERT INTO answer_category_result 
                (INTV_ANS_ID, EVAL_CAT_CD, ANS_CAT_SCORE, RGS_DTM, UPD_DTM)
            VALUES 
                (:ans_id, :cat_cd, :score, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                ANS_CAT_SCORE = :score,
                UPD_DTM = NOW()
        """)
        
        with self.engine.connect() as conn:
            for cat_cd, score in scores.items():
                conn.execute(query, {
                    'ans_id': intv_ans_id,
                    'cat_cd': cat_cd,
                    'score': score
                })
            conn.commit()

    def update_interview_result(self, intv_result_id: int, overall_data: dict):
        """면접 결과를 업데이트합니다."""
        query = text("""
            UPDATE interview_result
            SET 
                OVERALL_SCORE = :score,
                OVERALL_RANK = :rank,
                OVERALL_GRADE = :grade,
                STRENGTH_KEYWORDS = :strength,
                WEAKNESS_KEYWORDS = :weakness,
                UPD_DTM = NOW()
            WHERE INTV_RESULT_ID = :id
        """)
        
        with self.engine.connect() as conn:
            conn.execute(query, {
                'id': intv_result_id,
                'score': overall_data.get('score'),
                'rank': overall_data.get('rank'),
                'grade': overall_data.get('grade'),
                'strength': overall_data.get('strength'),
                'weakness': overall_data.get('weakness')
            })
            conn.commit()

    def get_evaluation_categories(self):
        """평가 카테고리 정보를 가져옵니다."""
        query = text("""
            SELECT EVAL_CAT_CD, WEIGHT
            FROM evaluation_category
            WHERE USE_YN = 'Y'
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return {row[0]: row[1] for row in result.fetchall()} 