# ----------------------------------------------------------------------------------------------------
# 작성목적 : 면접 결과 종합 조회
# 작성일 : 2025-06-23
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 순으로 기입)
# 2025-06-23 | 최초 구현 | 면접 결과 종합 조회 기능 구현
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from sqlalchemy import text
import pandas as pd

def show_overall_results(db):
    """전체 면접 결과 요약을 보여줍니다."""
    print("\n[📊] 전체 면접 결과 요약")
    
    results = pd.read_sql("""
        SELECT 
            r.INTV_RESULT_ID,
            r.APL_ID,
            r.OVERALL_SCORE,
            r.OVERALL_GRADE,
            r.OVERALL_RANK,
            r.STRENGTH_KEYWORD,
            r.WEAKNESS_KEYWORD
        FROM interview_result r
        ORDER BY r.OVERALL_RANK
    """, db.bind)
    
    if not results.empty:
        print("\n=== 전체 순위 ===")
        for _, row in results.iterrows():
            print(f"\n📌 지원자 ID: {row['APL_ID']}")
            print(f"🎯 종합 점수: {row['OVERALL_SCORE']:.1f}")
            print(f"📝 등급: {row['OVERALL_GRADE']}")
            print(f"🏆 순위: {row['OVERALL_RANK']}")
            print(f"💪 강점: {row['STRENGTH_KEYWORD']}")
            print(f"🔧 약점: {row['WEAKNESS_KEYWORD']}")
            print("-" * 100)

def show_category_scores(db):
    """평가 항목별 점수를 보여줍니다."""
    print("\n[📊] 평가 항목별 점수")
    
    results = pd.read_sql("""
        SELECT 
            r.INTV_RESULT_ID,
            r.APL_ID,
            ac.EVAL_CAT_CD,
            ac.ANS_CAT_SCORE,
            c.FEEDBACK_TXT
        FROM interview_result r
        JOIN answer_category_result ac ON r.INTV_RESULT_ID = ac.ANS_SCORE_ID
        LEFT JOIN interview_category_result c ON (r.INTV_RESULT_ID = c.INTV_RESULT_ID AND ac.EVAL_CAT_CD = c.EVAL_CAT_CD)
        ORDER BY r.INTV_RESULT_ID, ac.EVAL_CAT_CD
    """, db.bind)
    
    if not results.empty:
        for intv_id in results['INTV_RESULT_ID'].unique():
            intv_data = results[results['INTV_RESULT_ID'] == intv_id]
            print(f"\n📌 지원자 ID: {intv_data.iloc[0]['APL_ID']}")
            
            for _, row in intv_data.iterrows():
                print(f"\n평가항목: {row['EVAL_CAT_CD']}")
                print(f"점수: {row['ANS_CAT_SCORE']:.1f}")
                if pd.notna(row['FEEDBACK_TXT']):
                    print(f"코멘트: {row['FEEDBACK_TXT']}")
            print("-" * 100)

def show_statistics(db):
    """통계 정보를 보여줍니다."""
    print("\n[📊] 통계 정보")
    
    # 등급 분포
    grade_dist = pd.read_sql("""
        SELECT 
            OVERALL_GRADE,
            COUNT(*) as COUNT
        FROM interview_result
        GROUP BY OVERALL_GRADE
        ORDER BY OVERALL_GRADE
    """, db.bind)
    
    if not grade_dist.empty:
        print("\n=== 등급 분포 ===")
        for _, row in grade_dist.iterrows():
            print(f"{row['OVERALL_GRADE']}: {row['COUNT']}명")
    
    # 평가 항목별 평균
    cat_avg = pd.read_sql("""
        SELECT 
            ac.EVAL_CAT_CD,
            AVG(ac.ANS_CAT_SCORE) as AVG_SCORE,
            MIN(ac.ANS_CAT_SCORE) as MIN_SCORE,
            MAX(ac.ANS_CAT_SCORE) as MAX_SCORE
        FROM answer_category_result ac
        GROUP BY ac.EVAL_CAT_CD
    """, db.bind)
    
    if not cat_avg.empty:
        print("\n=== 평가 항목별 통계 ===")
        for _, row in cat_avg.iterrows():
            print(f"\n{row['EVAL_CAT_CD']}:")
            print(f"- 평균: {row['AVG_SCORE']:.1f}")
            print(f"- 최저: {row['MIN_SCORE']:.1f}")
            print(f"- 최고: {row['MAX_SCORE']:.1f}")

def main():
    print("[🚀] 면접 결과 조회를 시작합니다...")
    
    # DB 연결
    db = DBConnector().SessionLocal()
    
    try:
        # 1. 전체 결과 요약
        show_overall_results(db)
        
        # 2. 평가 항목별 점수
        show_category_scores(db)
        
        # 3. 통계 정보
        show_statistics(db)
        
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
    finally:
        db.close()
        print("\n[👋] 프로그램을 종료합니다.")

if __name__ == "__main__":
    main() 