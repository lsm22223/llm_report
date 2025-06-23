# scoring/score_calculator.py

from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.precision', 2)

def process_scores(db: Session):
    print("\n[📊] 면접 결과 분석 과정:")
    
    # 0단계: 테이블 구조 확인
    print("\n[0단계] 테이블 구조 확인")
    
    # interview_result 샘플
    result_sample = pd.read_sql("""
        SELECT * FROM interview_result LIMIT 5
    """, db.bind)
    print("\n📊 interview_result 샘플:")
    print(result_sample.to_string())
    
    # interview_answer 샘플
    answer_sample = pd.read_sql("""
        SELECT * FROM interview_answer LIMIT 5
    """, db.bind)
    print("\n📊 interview_answer 샘플:")
    print(answer_sample.to_string())
    
    # answer_category_result 샘플
    category_sample = pd.read_sql("""
        SELECT * FROM answer_category_result LIMIT 5
    """, db.bind)
    print("\n📊 answer_category_result 샘플:")
    print(category_sample.to_string())
    
    # 테이블별 레코드 수
    table_counts = pd.read_sql("""
        SELECT 
            (SELECT COUNT(*) FROM interview_result) as RESULT_COUNT,
            (SELECT COUNT(*) FROM interview_answer) as ANSWER_COUNT,
            (SELECT COUNT(*) FROM answer_category_result) as CAT_RESULT_COUNT,
            (SELECT COUNT(DISTINCT INTV_PROC_ID) FROM interview_result) as PROC_COUNT
    """, db.bind)
    print("\n📊 테이블별 레코드 수:")
    print(table_counts.to_string())
    
    # 0단계: 전체 지원자 수 확인
    print("\n[0단계] 전체 지원자 수 확인")
    total_count = pd.read_sql("""
        SELECT COUNT(DISTINCT r.APL_ID) as TOTAL_COUNT
        FROM interview_result r
    """, db.bind)
    print(f"\n📊 전체 지원자 수: {total_count.iloc[0]['TOTAL_COUNT']}명")
    
    # 1단계: 평가 항목별 평균 점수 계산 (APL_ID 기준)
    print("\n[1단계] 지원자별 평가 항목 평균 점수")
    print("- 지원자(APL_ID)별로 각 평가 항목의 평균 점수 계산")
    
    category_scores = pd.read_sql("""
        WITH CategoryScores AS (
            SELECT 
                r.APL_ID,
                ac.EVAL_CAT_CD,
                AVG(ac.ANS_CAT_SCORE) as AVG_SCORE
            FROM interview_result r
            LEFT JOIN answer_category_result ac ON r.INTV_RESULT_ID = ac.ANS_SCORE_ID
            WHERE ac.ANS_CAT_SCORE IS NOT NULL
            GROUP BY r.APL_ID, ac.EVAL_CAT_CD
        )
        SELECT 
            APL_ID,
            MAX(CASE WHEN EVAL_CAT_CD = 'ATTITUDE' THEN AVG_SCORE END) as '면접태도',
            MAX(CASE WHEN EVAL_CAT_CD = 'COMM_SKILL' THEN AVG_SCORE END) as '의사소통력',
            MAX(CASE WHEN EVAL_CAT_CD = 'ACADEMIC' THEN AVG_SCORE END) as '학우학업도',
            MAX(CASE WHEN EVAL_CAT_CD = 'ORG_FIT' THEN AVG_SCORE END) as '조직적합도',
            MAX(CASE WHEN EVAL_CAT_CD = 'PROB_SOLVE' THEN AVG_SCORE END) as '문제해결력',
            MAX(CASE WHEN EVAL_CAT_CD = 'COMPETENCY' THEN AVG_SCORE END) as '보유역량',
            MAX(CASE WHEN EVAL_CAT_CD = 'ENGLISH' THEN AVG_SCORE END) as '영어능력'
        FROM CategoryScores
        GROUP BY APL_ID
        ORDER BY APL_ID
    """, db.bind)
    
    if not category_scores.empty:
        print("\n📊 지원자별 평가 항목 평균 점수:")
        print(category_scores.to_string())
        print(f"\n총 {len(category_scores)}명의 평가 결과")
        
        # 평가 항목별 전체 평균 계산
        print("\n📊 평가 항목별 전체 평균:")
        category_means = category_scores.mean(numeric_only=True)
        print(category_means.to_string())
    
    # 2단계: 가중치 정보 조회 (모든 평가 항목)
    print("\n[2단계] 평가 항목별 가중치")
    weights = pd.read_sql("""
        SELECT EVAL_CAT_CD, WEIGHT
        FROM evaluation_category
        WHERE EVAL_CAT_CD IN (
            'ATTITUDE',      -- 면접태도
            'COMM_SKILL',    -- 의사소통력
            'ACADEMIC',      -- 학우학업도
            'ORG_FIT',      -- 조직적합도
            'PROB_SOLVE',    -- 문제해결력
            'COMPETENCY',    -- 보유역량
            'ENGLISH'        -- 영어능력
        )
    """, db.bind)
    
    if not weights.empty:
        print("\n📊 평가 항목 가중치:")
        print(weights.to_string())
    
    # 3단계: 가중치 적용하여 종합 점수 계산
    print("\n[3단계] 가중치 적용 종합 점수 계산")
    print("- 평가 항목별 평균 점수 × 가중치")
    
    # 가중치를 딕셔너리로 변환
    weight_dict = weights.set_index('EVAL_CAT_CD')['WEIGHT'].to_dict()
    
    # 면접자별로 그룹화하여 가중 평균 계산
    final_scores = []
    for intv_id in category_scores['APL_ID'].unique():
        intv_scores = category_scores[category_scores['APL_ID'] == intv_id]
        weighted_sum = 0
        total_weight = 0
        
        for _, row in intv_scores.iterrows():
            for cat_cd, score in row.items():
                if cat_cd in weight_dict:
                    weighted_sum += score * weight_dict[cat_cd]
                    total_weight += weight_dict[cat_cd]
        
        if total_weight > 0:
            final_scores.append({
                'APL_ID': intv_id,
                'OVERALL_SCORE': weighted_sum / total_weight
            })
    
    final_df = pd.DataFrame(final_scores)
    if not final_df.empty:
        # 순위와 등급 계산
        final_df['RANK'] = final_df['OVERALL_SCORE'].rank(method='min', ascending=False).astype(int)
        final_df['PERCENTILE'] = final_df['RANK'] / len(final_df)
        
        def assign_grade(p):
            if p <= 0.01: return "S"      # 상위 1%
            elif p <= 0.05: return "A+"    # 상위 5%
            elif p <= 0.10: return "A"     # 상위 10%
            elif p <= 0.20: return "A-"    # 상위 20%
            elif p <= 0.30: return "B+"    # 상위 30%
            elif p <= 0.50: return "B"     # 상위 50%
            else: return "C"               # 나머지
        
        final_df['GRADE'] = final_df['PERCENTILE'].apply(assign_grade)
        final_df = final_df.sort_values('OVERALL_SCORE', ascending=False)
        
        print("\n📊 최종 결과 (상위 10명):")
        print(final_df.head(10).to_string())
        
        # 등급 분포 출력
        print("\n📊 등급 분포:")
        grade_dist = final_df['GRADE'].value_counts().sort_index()
        print(grade_dist.to_string())
    else:
        print("계산할 데이터가 없습니다.")

    print("\n[📊] 데이터 현황 분석:")
    
    # 1. interview_result 전체 데이터 확인
    print("\n1. interview_result 전체 데이터:")
    result_data = pd.read_sql("""
        SELECT 
            INTV_RESULT_ID,
            APL_ID,
            INTV_PROC_ID,
            OVERALL_SCORE,
            OVERALL_GRADE,
            OVERALL_RANK
        FROM interview_result
        ORDER BY INTV_RESULT_ID
    """, db.bind)
    print("\n📊 면접 결과 데이터:")
    print(result_data.to_string())
    
    # 2. answer_category_result 데이터 확인
    print("\n2. answer_category_result 데이터:")
    category_data = pd.read_sql("""
        SELECT 
            ANS_CAT_RESULT_ID,
            EVAL_CAT_CD,
            ANS_SCORE_ID,
            ANS_CAT_SCORE
        FROM answer_category_result
        ORDER BY ANS_SCORE_ID, EVAL_CAT_CD
    """, db.bind)
    print("\n📊 카테고리별 점수 데이터:")
    print(category_data.to_string())
    
    # 3. 데이터 매칭 현황
    print("\n3. 데이터 매칭 현황:")
    matching_data = pd.read_sql("""
        SELECT 
            r.INTV_RESULT_ID,
            r.APL_ID,
            r.INTV_PROC_ID,
            COUNT(DISTINCT ac.EVAL_CAT_CD) as CATEGORY_COUNT,
            GROUP_CONCAT(DISTINCT ac.EVAL_CAT_CD) as CATEGORIES
        FROM interview_result r
        LEFT JOIN answer_category_result ac ON r.INTV_RESULT_ID = ac.ANS_SCORE_ID
        GROUP BY r.INTV_RESULT_ID, r.APL_ID, r.INTV_PROC_ID
        ORDER BY r.INTV_RESULT_ID
    """, db.bind)
    print("\n📊 데이터 매칭 현황:")
    print(matching_data.to_string())
    
    # 4. 평가 카테고리 분포
    print("\n4. 평가 카테고리 분포:")
    category_dist = pd.read_sql("""
        SELECT 
            EVAL_CAT_CD,
            COUNT(*) as COUNT,
            COUNT(DISTINCT ANS_SCORE_ID) as UNIQUE_ANSWERS
        FROM answer_category_result
        GROUP BY EVAL_CAT_CD
        ORDER BY EVAL_CAT_CD
    """, db.bind)
    print("\n📊 카테고리별 평가 수:")
    print(category_dist.to_string())
