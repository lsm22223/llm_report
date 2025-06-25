# ----------------------------------------------------------------------------------------------------
# 작성목적 : 테스트 데이터 생성
# 작성일 : 2025-06-25
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-25 | 최초 구현 | 통합된 평가 카테고리에 맞춘 테스트 데이터 생성 | 이소미
# ----------------------------------------------------------------------------------------------------

from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scoring.core.db_connector import DBConnector
from datetime import datetime

# DB 연결
db = DBConnector().SessionLocal()
now = datetime.now()

try:
    # 1. 평가 카테고리 추가
    print("\n[1단계] 평가 카테고리 추가")
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
    
    # 2. 테스트용 답변 데이터 추가
    print("\n[2단계] 테스트 데이터 추가")
    # 3명의 지원자에 대한 데이터 생성
    for apl_id in range(1, 4):
        # answer_score 추가
        db.execute(text("""
            INSERT INTO answer_score 
            (INTV_ANS_ID, ANS_SCORE_ID, RGS_DTM, UPD_DTM) 
            VALUES 
            (:ans_id, :score_id, :now, :now)
        """), {
            'ans_id': f"{apl_id}01",  # 101, 201, 301
            'score_id': apl_id * 1000 + 1,  # 1001, 2001, 3001
            'now': now
        })
        
        # 각 카테고리별 점수 추가
        scores = {
            'ENGLISH_ABILITY': (85 if apl_id == 1 else 75 if apl_id == 2 else 65),
            'COMM_SKILL': (90 if apl_id == 1 else 80 if apl_id == 2 else 70),
            'PROB_SOLVE': (95 if apl_id == 1 else 85 if apl_id == 2 else 75),
            'TECH_SKILL': (88 if apl_id == 1 else 78 if apl_id == 2 else 68),
            'JOB_COMPATIBILITY': (92 if apl_id == 1 else 82 if apl_id == 2 else 72),
            'ORG_FIT': (87 if apl_id == 1 else 77 if apl_id == 2 else 67)
        }
        
        for cat_cd, score in scores.items():
            db.execute(text("""
                INSERT INTO answer_category_result 
                (ANS_SCORE_ID, EVAL_CAT_CD, ANS_CAT_SCORE, STRENGTH_KEYWORD, WEAKNESS_KEYWORD, RGS_DTM, UPD_DTM) 
                VALUES 
                (:score_id, :cat_cd, :cat_score, :strength, :weakness, :now, :now)
            """), {
                'score_id': apl_id * 1000 + 1,
                'cat_cd': cat_cd,
                'cat_score': score,
                'strength': '우수한 실력|체계적인 접근' if score >= 85 else '기본기가 탄탄함|성장 가능성',
                'weakness': '심화 지식 필요' if score < 85 else '완벽주의 성향',
                'now': now
            })
    
    # 변경사항 커밋
    db.commit()
    print('✓ 테스트 데이터 추가 완료')
    
    # 3. 현재 평가 카테고리 조회
    result = db.execute(text('SELECT EVAL_CAT_CD, CAT_NM, MAX_SCORE, WEIGHT FROM evaluation_category'))
    print('\n현재 평가 카테고리:')
    for row in result:
        print(f"{row.EVAL_CAT_CD}: {row.CAT_NM} (최대점수: {row.MAX_SCORE}, 가중치: {row.WEIGHT})")

except Exception as e:
    print(f'오류 발생: {str(e)}')
    db.rollback()
finally:
    db.close() 
        