# ----------------------------------------------------------------------------------------------------
# 작성목적 : 데이터베이스 백업 및 마이그레이션
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | 백업 및 마이그레이션 기능 구현 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from sqlalchemy import text
import pandas as pd
import numpy as np
from datetime import datetime
import os

def backup_and_migrate():
    """데이터베이스 백업 후 새로운 데이터로 마이그레이션합니다."""
    print("[🔄] 데이터베이스 백업 및 마이그레이션을 시작합니다...")
    
    # 백업 시간을 파일명에 사용
    backup_time = datetime.now().strftime("%Y%m%d_%H%M")
    
    try:
        # DB 연결
        db = DBConnector().SessionLocal()
        
        # 1. 백업 테이블 생성
        print("\n[1/3] 백업 테이블 생성 중...")
        backup_tables = [
            'answer_category_result',
            'answer_score',
            'interview_category_result',
            'question_evaluation',
            'evaluation_category'
        ]
        
        for table in backup_tables:
            try:
                backup_table = f"{table}_backup_{backup_time}"
                query = text(f"CREATE TABLE {backup_table} AS SELECT * FROM {table}")
                db.execute(query)
                print(f"[✓] {table} 테이블 백업 완료 → {backup_table}")
            except Exception as e:
                print(f"[❌] {table} 테이블 백업 실패: {str(e)}")
                return
        
        # 2. 새로운 카테고리 설정
        print("\n[2/3] 새로운 카테고리 설정 중...")
        new_categories = [
            {
                'code': 'COMMUNICATION',
                'name': '커뮤니케이션',
                'desc': '지원자의 커뮤니케이션 능력을 평가합니다.',
                'max_score': 100,
                'weight': 25.0
            },
            {
                'code': 'ORG_FIT',
                'name': '조직 적합도',
                'desc': '지원자의 조직 문화 적합도를 평가합니다.',
                'max_score': 100,
                'weight': 25.0
            },
            {
                'code': 'JOB_COMPATIBILITY',
                'name': '직무 적합도',
                'desc': '지원자의 직무 적합도를 평가합니다.',
                'max_score': 100,
                'weight': 25.0
            },
            {
                'code': 'TECH_STACK',
                'name': '기술 스택',
                'desc': '지원자의 기술적 역량을 평가합니다.',
                'max_score': 100,
                'weight': 25.0
            },
            {
                'code': 'PROBLEM_SOLVING',
                'name': '문제 해결 능력',
                'desc': '지원자의 문제 해결 능력을 평가합니다.',
                'max_score': 100,
                'weight': 25.0
            }
        ]
        
        # 기존 데이터 삭제
        for table in reversed(backup_tables):
            try:
                query = text(f"DELETE FROM {table}")
                db.execute(query)
                print(f"[✓] {table} 테이블 데이터 삭제 완료")
            except Exception as e:
                print(f"[❌] {table} 테이블 데이터 삭제 실패: {str(e)}")
                return
        
        # 새로운 카테고리 추가
        for cat in new_categories:
            try:
                query = text("""
                    INSERT INTO evaluation_category 
                        (EVAL_CAT_CD, CAT_NM, CAT_DESC, MAX_SCORE, WEIGHT, RGS_DTM, UPD_DTM)
                    VALUES 
                        (:code, :name, :desc, :max_score, :weight, NOW(), NOW())
                """)
                
                db.execute(query, {
                    'code': cat['code'],
                    'name': cat['name'],
                    'desc': cat['desc'],
                    'max_score': cat['max_score'],
                    'weight': cat['weight']
                })
                print(f"[✓] 카테고리 추가 완료: {cat['code']}")
                
            except Exception as e:
                print(f"[❌] 카테고리 추가 실패 ({cat['code']}): {str(e)}")
                return
        
        # 3. CSV 데이터 마이그레이션
        print("\n[3/3] CSV 데이터 마이그레이션 중...")
        
        # CSV 파일 읽기
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'data', 'answer_category_result_202506231719.csv')
        df = pd.read_csv(csv_path)
        print(f"[📊] 읽어온 데이터 수: {len(df)} 행")
        
        # nan 값을 None으로 변환
        df = df.replace({np.nan: None})
        
        # answer_score 테이블에 데이터 삽입
        unique_scores = df[['ANS_SCORE_ID']].drop_duplicates()
        unique_scores['INTV_ANS_ID'] = unique_scores['ANS_SCORE_ID'].apply(lambda x: int(str(x)[0]))
        
        score_query = text("""
            INSERT INTO answer_score 
                (ANS_SCORE_ID, INTV_ANS_ID, RGS_DTM)
            VALUES 
                (:score_id, :intv_ans_id, NOW())
        """)
        
        score_success = 0
        for _, row in unique_scores.iterrows():
            try:
                db.execute(score_query, {
                    'score_id': row['ANS_SCORE_ID'],
                    'intv_ans_id': row['INTV_ANS_ID']
                })
                score_success += 1
                
            except Exception as e:
                print(f"[❌] answer_score 데이터 삽입 실패 (ID: {row['ANS_SCORE_ID']}): {str(e)}")
                continue
        
        print(f"[✓] answer_score 테이블 데이터 삽입 완료! (성공: {score_success}개 / 전체: {len(unique_scores)}개)")
        
        # answer_category_result 테이블에 데이터 삽입
        result_query = text("""
            INSERT INTO answer_category_result 
                (ANS_CAT_RESULT_ID, ANS_SCORE_ID, EVAL_CAT_CD, ANS_CAT_SCORE, 
                STRENGTH_KEYWORD, WEAKNESS_KEYWORD, RGS_DTM)
            VALUES 
                (:result_id, :score_id, :cat_cd, :score, 
                :strength, :weakness, NOW())
        """)
        
        result_success = 0
        for _, row in df.iterrows():
            try:
                db.execute(result_query, {
                    'result_id': row['ANS_CAT_RESULT_ID'],
                    'score_id': row['ANS_SCORE_ID'],
                    'cat_cd': row['EVAL_CAT_CD'],
                    'score': row['ANS_CAT_SCORE'],
                    'strength': row['STRENGTH_KEYWORD'],
                    'weakness': row['WEAKNESS_KEYWORD']
                })
                result_success += 1
                
            except Exception as e:
                print(f"[❌] answer_category_result 데이터 삽입 실패 (ID: {row['ANS_CAT_RESULT_ID']}): {str(e)}")
                continue
        
        print(f"[✓] answer_category_result 테이블 데이터 삽입 완료! (성공: {result_success}개 / 전체: {len(df)}개)")
        
        # 변경사항 커밋
        db.commit()
        print("\n[✅] 모든 백업 및 마이그레이션이 완료되었습니다!")
        print(f"[💾] 백업 테이블 접두사: *_backup_{backup_time}")
        
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    backup_and_migrate() 