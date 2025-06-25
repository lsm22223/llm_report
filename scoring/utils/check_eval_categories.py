# ----------------------------------------------------------------------------------------------------
# 작성목적 : answer_category_result 테이블의 평가 항목 확인
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | 평가 항목 확인 스크립트 작성 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def check_eval_categories():
    db = DBConnector().SessionLocal()
    
    try:
        # 1. 현재 사용 중인 평가 항목 코드 조회
        result = db.execute(text("""
            SELECT DISTINCT EVAL_CAT_CD, COUNT(*) as count
            FROM answer_category_result
            GROUP BY EVAL_CAT_CD
            ORDER BY EVAL_CAT_CD;
        """)).fetchall()
        
        print("\n[현재 사용 중인 평가 항목]")
        print("-" * 50)
        print(f"{'평가항목코드':<20} {'사용 건수':<10}")
        print("-" * 50)
        
        for row in result:
            print(f"{row[0]:<20} {row[1]:<10}")
            
        # 2. evaluation_category 테이블이 있는지 확인
        try:
            result = db.execute(text("""
                SELECT EVAL_CAT_CD, CAT_NM, CAT_DESC
                FROM evaluation_category
                ORDER BY EVAL_CAT_CD;
            """)).fetchall()
            
            print("\n[평가 항목 마스터 데이터]")
            print("-" * 100)
            print(f"{'평가항목코드':<20} {'항목명':<30} {'설명':<50}")
            print("-" * 100)
            
            for row in result:
                print(f"{row[0]:<20} {row[1]:<30} {(row[2] or '')[:47]+'...' if row[2] and len(row[2]) > 50 else (row[2] or ''):<50}")
                
        except Exception as e:
            print("\n[!] evaluation_category 테이블이 없거나 접근할 수 없습니다.")
            
    except Exception as e:
        print(f"[❌] 오류 발생: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_eval_categories() 