# ----------------------------------------------------------------------------------------------------
# 작성목적 : 평가 카테고리 재설정
# 작성일 : 2025-06-24

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-24 | 최초 구현 | 엑셀 파일 기준으로 평가 카테고리 재설정 | 이소미
# 2025-06-24 | 버그 수정 | answer_category_result 테이블 데이터 삭제 추가 | 이소미
# 2025-06-24 | 버그 수정 | answer_score 테이블 데이터 삭제 추가 | 이소미
# 2025-06-24 | 버그 수정 | interview_category_result 테이블 데이터 삭제 추가 | 이소미
# 2025-06-24 | 버그 수정 | question_evaluation 테이블 데이터 삭제 추가 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def update_categories():
    """평가 카테고리를 엑셀 파일 기준으로 재설정합니다."""
    print("[🔄] 평가 카테고리 재설정을 시작합니다...")
    
    # 새로운 카테고리 정의
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
    
    try:
        # DB 연결
        db = DBConnector().SessionLocal()
        
        # answer_category_result 테이블 데이터 삭제
        try:
            delete_results_query = text("DELETE FROM answer_category_result")
            db.execute(delete_results_query)
            print("[✅] answer_category_result 테이블 데이터 삭제 완료")
        except Exception as e:
            print(f"[❌] answer_category_result 테이블 데이터 삭제 실패: {str(e)}")
            return
            
        # answer_score 테이블 데이터 삭제
        try:
            delete_scores_query = text("DELETE FROM answer_score")
            db.execute(delete_scores_query)
            print("[✅] answer_score 테이블 데이터 삭제 완료")
        except Exception as e:
            print(f"[❌] answer_score 테이블 데이터 삭제 실패: {str(e)}")
            return
            
        # interview_category_result 테이블 데이터 삭제
        try:
            delete_interview_query = text("DELETE FROM interview_category_result")
            db.execute(delete_interview_query)
            print("[✅] interview_category_result 테이블 데이터 삭제 완료")
        except Exception as e:
            print(f"[❌] interview_category_result 테이블 데이터 삭제 실패: {str(e)}")
            return
            
        # question_evaluation 테이블 데이터 삭제
        try:
            delete_question_query = text("DELETE FROM question_evaluation")
            db.execute(delete_question_query)
            print("[✅] question_evaluation 테이블 데이터 삭제 완료")
        except Exception as e:
            print(f"[❌] question_evaluation 테이블 데이터 삭제 실패: {str(e)}")
            return
        
        # 기존 카테고리 삭제
        try:
            delete_query = text("DELETE FROM evaluation_category")
            db.execute(delete_query)
            print("[✅] 기존 카테고리 삭제 완료")
        except Exception as e:
            print(f"[❌] 기존 카테고리 삭제 실패: {str(e)}")
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
                print(f"[✅] 카테고리 추가 완료: {cat['code']}")
                
            except Exception as e:
                print(f"[❌] 카테고리 추가 실패 ({cat['code']}): {str(e)}")
                continue
        
        # 변경사항 커밋
        db.commit()
        print("[✅] 모든 카테고리 재설정이 완료되었습니다!")
        
    except Exception as e:
        print(f"[❌] 오류가 발생했습니다: {str(e)}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    update_categories() 