# ----------------------------------------------------------------------------------------------------
# 작성목적 : DB 테이블 생성 스크립트
# 작성일 : 2025-06-25
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-25 | 최초 구현 | SQLAlchemy를 사용한 테이블 생성 | 이소미
# ----------------------------------------------------------------------------------------------------

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import text
from datetime import datetime
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DB 연결 정보
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# 평가 카테고리 테이블
evaluation_category = Table(
    'evaluation_category', 
    metadata,
    Column('EVAL_CAT_CD', String(20), primary_key=True, comment='평가 항목 코드'),
    Column('CAT_NM', String(100), nullable=False, comment='평가 항목명'),
    Column('MAX_SCORE', Integer, nullable=False, server_default=text('100'), comment='최대 점수'),
    Column('WEIGHT', Float(precision=3, scale=2), nullable=False, comment='가중치'),
    Column('RGS_DTM', DateTime, nullable=False, comment='등록일시'),
    Column('UPD_DTM', DateTime, nullable=False, comment='수정일시'),
    comment='평가 항목 정보'
)

# 답변 점수 테이블
answer_score = Table(
    'answer_score', 
    metadata,
    Column('ANS_SCORE_ID', Integer, primary_key=True, autoincrement=True, comment='답변 점수 ID'),
    Column('INTV_ANS_ID', Integer, nullable=False, comment='면접 답변 ID'),
    Column('EVAL_SUMMARY', Text, comment='평가 요약'),
    Column('RGS_DTM', DateTime, nullable=False, comment='등록일시'),
    Column('UPD_DTM', DateTime, nullable=False, comment='수정일시'),
    comment='답변 점수 정보'
)

# 답변 카테고리 결과 테이블
answer_category_result = Table(
    'answer_category_result', 
    metadata,
    Column('ANS_CAT_RESULT_ID', Integer, primary_key=True, autoincrement=True, comment='답변 카테고리 결과 ID'),
    Column('ANS_SCORE_ID', Integer, ForeignKey('answer_score.ANS_SCORE_ID', ondelete='CASCADE'), nullable=False, comment='답변 점수 ID'),
    Column('EVAL_CAT_CD', String(20), ForeignKey('evaluation_category.EVAL_CAT_CD'), nullable=False, comment='평가 항목 코드'),
    Column('ANS_CAT_SCORE', Float(precision=5, scale=2), nullable=False, comment='항목 점수'),
    Column('STRENGTH_KEYWORD', String(500), comment='강점 키워드'),
    Column('WEAKNESS_KEYWORD', String(500), comment='약점 키워드'),
    Column('RGS_DTM', DateTime, nullable=False, comment='등록일시'),
    Column('UPD_DTM', DateTime, nullable=False, comment='수정일시'),
    comment='답변 카테고리별 결과'
)

# 면접 결과 테이블
interview_result = Table(
    'interview_result', 
    metadata,
    Column('INTV_RESULT_ID', Integer, primary_key=True, autoincrement=True, comment='면접 결과 ID'),
    Column('APL_ID', Integer, nullable=False, index=True, comment='지원자 ID'),
    Column('INTV_PROC_ID', Integer, nullable=False, comment='면접 프로세스 ID'),
    Column('OVERALL_SCORE', Float(precision=5, scale=2), comment='종합 점수'),
    Column('OVERALL_GRADE', String(2), comment='등급'),
    Column('OVERALL_RANK', Integer, comment='순위'),
    Column('STRENGTH_KEYWORD', String(500), comment='강점 키워드'),
    Column('WEAKNESS_KEYWORD', String(500), comment='약점 키워드'),
    Column('RGS_DTM', DateTime, nullable=False, comment='등록일시'),
    Column('UPD_DTM', DateTime, nullable=False, comment='수정일시'),
    comment='면접 결과 정보'
)

# 면접 카테고리 결과 테이블
interview_category_result = Table(
    'interview_category_result', 
    metadata,
    Column('INTV_CAT_RESULT_ID', Integer, primary_key=True, autoincrement=True, comment='면접 카테고리 결과 ID'),
    Column('INTV_RESULT_ID', Integer, ForeignKey('interview_result.INTV_RESULT_ID', ondelete='CASCADE'), nullable=False, comment='면접 결과 ID'),
    Column('EVAL_CAT_CD', String(20), ForeignKey('evaluation_category.EVAL_CAT_CD'), nullable=False, comment='평가 항목 코드'),
    Column('FEEDBACK_TXT', Text, comment='피드백 내용'),
    Column('RGS_DTM', DateTime, nullable=False, comment='등록일시'),
    Column('UPD_DTM', DateTime, nullable=False, comment='수정일시'),
    comment='면접 카테고리별 결과'
)

def create_tables():
    """테이블을 생성합니다."""
    try:
        # 기존 테이블 삭제 (역순)
        metadata.drop_all(engine, tables=[
            interview_category_result,
            interview_result,
            answer_category_result,
            answer_score,
            evaluation_category
        ])
        print("✓ 기존 테이블 삭제 완료")
        
        # 새 테이블 생성
        metadata.create_all(engine)
        print("✓ 새 테이블 생성 완료")
        
        print("\n테이블 생성이 완료되었습니다.")
        print("다음 단계: python update_categories.py 실행")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    create_tables() 