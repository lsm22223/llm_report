# ----------------------------------------------------------------------------------------------------
# 작성목적 : 면접 답변 점수 계산 및 저장
# 작성일 : 2025-06-24

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-24 | 기능 개선 | 불필요한 테이블 조회 제거 및 로직 단순화 | 이소미
# 2025-06-24 | 기능 추가 | 메인 실행 블록 추가 | 이소미
# 2025-06-24 | 버그 수정 | DB 세션 생성 방식 수정 | 이소미
# 2025-06-24 | 버그 수정 | 테이블명 및 컬럼명 수정 | 이소미
# 2025-06-24 | 기능 추가 | 데이터 분석 기능 추가 | 이소미
# 2025-06-24 | 버그 수정 | evaluation_category 테이블 컬럼명 수정 | 이소미
# 2025-06-24 | 버그 수정 | import 경로 수정 | 이소미
# 2025-06-24 | 기능 개선 | 지원자별 카테고리 평균 점수 계산 로직 추가 | 이소미
# 2025-06-24 | 버그 수정 | INTV_ANS_ID 처리 방식 수정 | 이소미
# 2025-06-24 | 버그 수정 | result_id 생성 로직 수정 | 이소미
# 2025-06-24 | 버그 수정 | 테이블 컬럼명 수정 | 이소미
# 2025-06-24 | 버그 수정 | 기존 데이터 삭제 로직 추가 | 이소미
# 2025-06-24 | 버그 수정 | 데이터 삭제 순서 수정 | 이소미
# 2025-06-24 | 버그 수정 | result_id 관리 방식 수정 | 이소미
# 2025-06-24 | 버그 수정 | analyze_scores 함수 컬럼명 수정 | 이소미
# 2025-06-25 | 기능 추가 | ENGLISH_FLUENCY와 ENGLISH_GRAMMAR를 ENGLISH_ABILITY로 통합하는 예외처리 추가 | 이소미
# 2025-06-25 | 버그 수정 | 영어 관련 카테고리 처리 로직 수정 | 이소미
# 2025-06-25 | 기능 개선 | CAT_GRADE 컬럼 제거 및 전체 등급만 계산하도록 수정 | 이소미
# ----------------------------------------------------------------------------------------------------

from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scoring.core.db_connector import DBConnector
import pandas as pd
import numpy as np
from datetime import datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.precision', 2)

def analyze_scores(db: Session):
    """
    면접 답변 점수를 분석합니다.
    
    Args:
        db (Session): 데이터베이스 세션
    """
    print("\n[📊] 면접 답변 점수 분석을 시작합니다...")
    
    try:
        # 1. 평가 카테고리 가중치 조회
        weights = pd.read_sql("""
            SELECT EVAL_CAT_CD, WEIGHT
            FROM evaluation_category
        """, db.bind)
        
        # 2. 지원자별 상세 점수와 가중치 반영한 평균
        detailed_scores = pd.read_sql("""
            SELECT 
                r.INTV_RESULT_ID,
                r.APL_ID,
                c.EVAL_CAT_CD,
                c.CAT_SCORE,
                c.FEEDBACK_TXT,
                e.WEIGHT
            FROM interview_result r
            JOIN interview_category_result c ON r.INTV_RESULT_ID = c.INTV_RESULT_ID
            JOIN evaluation_category e ON c.EVAL_CAT_CD = e.EVAL_CAT_CD
            ORDER BY r.INTV_RESULT_ID, c.EVAL_CAT_CD
        """, db.bind)
        
        # 3. 지원자별 가중 평균 점수 계산
        applicant_scores = []
        for intv_id in detailed_scores['INTV_RESULT_ID'].unique():
            app_scores = detailed_scores[detailed_scores['INTV_RESULT_ID'] == intv_id]
            
            # 가중 평균 계산
            weighted_sum = (app_scores['CAT_SCORE'] * app_scores['WEIGHT']).sum()
            total_weight = app_scores['WEIGHT'].sum()
            weighted_avg = weighted_sum / total_weight if total_weight > 0 else 0
            
            # 전체 등급 계산
            overall_grade = calculate_grade(weighted_avg)
            
            applicant_scores.append({
                'INTV_RESULT_ID': intv_id,
                'APL_ID': app_scores.iloc[0]['APL_ID'],
                'weighted_avg': weighted_avg,
                'overall_grade': overall_grade,
                'cat_count': len(app_scores)
            })
        
        # 점수순으로 정렬
        applicant_scores = pd.DataFrame(applicant_scores).sort_values('weighted_avg', ascending=False)
        
        # 지원자별로 결과 출력
        for idx, applicant in applicant_scores.iterrows():
            print(f"\n\n📌 지원자 {int(applicant['APL_ID'])} 평가 결과")
            print(f"INTV_RESULT_ID: {int(applicant['INTV_RESULT_ID'])}")
            print(f"종합 순위: {idx + 1}위")
            print(f"가중 평균 점수: {applicant['weighted_avg']:.2f}")
            print(f"전체 등급: {applicant['overall_grade']}")
            print("\n카테고리별 평가:")
            
            # 해당 지원자의 카테고리별 점수
            app_scores = detailed_scores[detailed_scores['INTV_RESULT_ID'] == applicant['INTV_RESULT_ID']]
            for _, score in app_scores.iterrows():
                print(f"\n• {score['EVAL_CAT_CD']} (가중치: {score['WEIGHT']})")
                print(f"  - 점수: {score['CAT_SCORE']:.2f}")
                if pd.notna(score['FEEDBACK_TXT']):
                    print(f"  - 코멘트: {score['FEEDBACK_TXT']}")
            print("-" * 100)
            
    except Exception as e:
        print(f"\n[❌] 데이터 분석 중 오류가 발생했습니다: {str(e)}")
        raise

def process_scores(db: Session):
    print("\n[🔄] 면접 결과 점수 계산 및 저장을 시작합니다...")
    
    try:
        # 1. 평가 카테고리별 가중치 조회
        print("\n[1단계] 평가 카테고리 가중치 조회")
        weights = pd.read_sql("""
            SELECT EVAL_CAT_CD, WEIGHT
            FROM evaluation_category
        """, db.bind)
        print(f"✓ {len(weights)}개 카테고리 가중치 조회 완료")
        
        # 2. 답변별 카테고리 점수 조회
        print("\n[2단계] 답변별 카테고리 점수 조회")
        scores = pd.read_sql("""
            SELECT 
                s.INTV_ANS_ID,
                CAST(SUBSTRING(s.INTV_ANS_ID, 1, 1) AS UNSIGNED) as APL_ID,
                r.EVAL_CAT_CD,
                r.ANS_CAT_SCORE,
                r.STRENGTH_KEYWORD,
                r.WEAKNESS_KEYWORD
            FROM answer_score s
            JOIN answer_category_result r ON s.ANS_SCORE_ID = r.ANS_SCORE_ID
        """, db.bind)
        print(f"✓ {len(scores)}개 카테고리 점수 조회 완료")
        
        # 3. 지원자별 카테고리 점수 계산
        print("\n[3단계] 지원자별 카테고리 점수 계산")
        
        # 기존 데이터 삭제 (순서 중요: 자식 테이블부터 삭제)
        print("\n[3-1] 기존 데이터 삭제")
        db.execute(text("DELETE FROM pdf_report"))
        print("✓ pdf_report 테이블 데이터 삭제 완료")
        
        db.execute(text("DELETE FROM interview_category_result"))
        print("✓ interview_category_result 테이블 데이터 삭제 완료")
        
        db.execute(text("DELETE FROM interview_result"))
        print("✓ interview_result 테이블 데이터 삭제 완료")
        
        # 결과 ID 카운터 초기화
        result_id = 1
        cat_result_id = 1
        
        # 지원자별로 처리
        print("\n[3-2] 지원자별 데이터 처리")
        for intv_id in scores['APL_ID'].unique():
            # 지원자의 모든 답변
            intv_scores = scores[scores['APL_ID'] == intv_id]
            
            # 먼저 interview_result 테이블에 기본 정보 저장
            insert_result_query = text("""
                INSERT INTO interview_result (
                    INTV_RESULT_ID,
                    APL_ID,
                    INTV_PROC_ID,
                    RGS_DTM,
                    UPD_DTM
                ) VALUES (
                    :result_id,
                    :apl_id,
                    :proc_id,
                    :rgs_dtm,
                    :upd_dtm
                )
            """)
            
            db.execute(insert_result_query, {
                'result_id': result_id,
                'apl_id': int(intv_id),
                'proc_id': int(intv_id),
                'rgs_dtm': datetime.now(),
                'upd_dtm': datetime.now()
            })
            
            # 영어 능력 관련 카테고리 통합을 위한 변수
            english_scores = []
            english_strengths = []
            english_weaknesses = []
            
            # 카테고리별로 평균 점수 계산
            for cat_cd in weights['EVAL_CAT_CD'].unique():
                cat_scores = intv_scores[intv_scores['EVAL_CAT_CD'] == cat_cd]
                
                # 영어 관련 카테고리인 경우 따로 처리
                if cat_cd in ['ENGLISH_FLUENCY', 'ENGLISH_GRAMMAR']:
                    if not cat_scores.empty:
                        english_scores.extend(cat_scores['ANS_CAT_SCORE'].tolist())
                        strengths = [s for s in cat_scores['STRENGTH_KEYWORD'].dropna() if pd.notna(s)]
                        weaknesses = [w for w in cat_scores['WEAKNESS_KEYWORD'].dropna() if pd.notna(w)]
                        english_strengths.extend(strengths)
                        english_weaknesses.extend(weaknesses)
                    continue
                
                if not cat_scores.empty:
                    # 평균 점수 계산
                    avg_score = cat_scores['ANS_CAT_SCORE'].mean()
                    
                    # 강점과 약점 키워드 결합
                    strengths = [s for s in cat_scores['STRENGTH_KEYWORD'].dropna() if pd.notna(s)]
                    weaknesses = [w for w in cat_scores['WEAKNESS_KEYWORD'].dropna() if pd.notna(w)]
                    
                    # 피드백 생성
                    feedback = ""
                    if strengths:
                        feedback += "강점: " + " | ".join(strengths)
                    if weaknesses:
                        if feedback:
                            feedback += "\n"
                        feedback += "약점: " + " | ".join(weaknesses)
                    
                    # 결과 저장
                    insert_query = text("""
                        INSERT INTO interview_category_result (
                            INTV_CAT_RESULT_ID,
                            INTV_RESULT_ID,
                            EVAL_CAT_CD,
                            CAT_SCORE,
                            FEEDBACK_TXT,
                            RGS_DTM,
                            UPD_DTM
                        ) VALUES (
                            :cat_result_id,
                            :intv_result_id,
                            :eval_cat_cd,
                            :cat_score,
                            :feedback,
                            :rgs_dtm,
                            :upd_dtm
                        )
                    """)
                    
                    db.execute(insert_query, {
                        'cat_result_id': cat_result_id,
                        'intv_result_id': result_id,
                        'eval_cat_cd': cat_cd,
                        'cat_score': float(avg_score),  # numpy.float64를 float로 변환
                        'feedback': feedback,
                        'rgs_dtm': datetime.now(),
                        'upd_dtm': datetime.now()
                    })
                    
                    cat_result_id += 1
            
            # 영어 관련 점수가 있는 경우 ENGLISH_ABILITY로 통합하여 저장
            if english_scores:
                avg_english_score = sum(english_scores) / len(english_scores)
                
                # 피드백 생성
                feedback = ""
                if english_strengths:
                    feedback += "강점: " + " | ".join(english_strengths)
                if english_weaknesses:
                    if feedback:
                        feedback += "\n"
                    feedback += "약점: " + " | ".join(english_weaknesses)
                
                # ENGLISH_ABILITY로 통합하여 저장
                insert_query = text("""
                    INSERT INTO interview_category_result (
                        INTV_CAT_RESULT_ID,
                        INTV_RESULT_ID,
                        EVAL_CAT_CD,
                        CAT_SCORE,
                        FEEDBACK_TXT,
                        RGS_DTM,
                        UPD_DTM
                    ) VALUES (
                        :cat_result_id,
                        :intv_result_id,
                        'ENGLISH_ABILITY',
                        :cat_score,
                        :feedback,
                        :rgs_dtm,
                        :upd_dtm
                    )
                """)
                
                db.execute(insert_query, {
                    'cat_result_id': cat_result_id,
                    'intv_result_id': result_id,
                    'cat_score': float(avg_english_score),  # numpy.float64를 float로 변환
                    'feedback': feedback,
                    'rgs_dtm': datetime.now(),
                    'upd_dtm': datetime.now()
                })
                
                cat_result_id += 1
            
            # 지원자 결과 ID 증가
            result_id += 1
            print(f"✓ 지원자 {intv_id} 처리 완료")
        
        # 변경사항 커밋
        db.commit()
        print("\n[✅] 모든 데이터 처리 및 저장이 완료되었습니다!")
        
        # 4. 저장된 데이터 확인
        print("\n[4단계] 저장된 데이터 확인")
        results = pd.read_sql("""
            SELECT 
                r.INTV_RESULT_ID,
                r.APL_ID,
                c.EVAL_CAT_CD,
                c.CAT_SCORE,
                c.FEEDBACK_TXT
            FROM interview_result r
            JOIN interview_category_result c ON r.INTV_RESULT_ID = c.INTV_RESULT_ID
            ORDER BY r.INTV_RESULT_ID, c.EVAL_CAT_CD
        """, db.bind)
        
        print("\n📊 저장된 카테고리별 결과:")
        print(results.to_string())
        print(f"\n총 {len(results)}개의 카테고리 평가 결과가 저장되었습니다.")
        
    except Exception as e:
        print(f"\n[❌] 데이터 처리 중 오류가 발생했습니다: {str(e)}")
        db.rollback()
        raise
    
    # 분석 결과 출력
    analyze_scores(db)

def calculate_grade(score: float) -> str:
    """점수를 등급으로 변환"""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B+'
    elif score >= 60:
        return 'B'
    elif score >= 50:
        return 'C+'
    else:
        return 'C'

if __name__ == "__main__":
    # DB 연결
    db = DBConnector()
    
    # 점수 계산 및 저장 실행
    process_scores(db)
