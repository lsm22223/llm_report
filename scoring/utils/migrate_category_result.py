# ----------------------------------------------------------------------------------------------------
# 작성목적 : answer_category_result 데이터 마이그레이션
# 작성일 : 2025-06-24

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-24 | 최초 구현 | CSV 데이터를 DB로 마이그레이션 | 이소미
# 2025-06-24 | 버그 수정 | CSV 파일 경로 수정 | 이소미
# 2025-06-24 | 버그 수정 | nan 값 처리 추가 | 이소미
# ----------------------------------------------------------------------------------------------------

from scoring.core.db_connector import DBConnector
import pandas as pd
import numpy as np
from sqlalchemy import text
from datetime import datetime
import os

def migrate_category_result():
    print("\n[🔄] answer_category_result 데이터 마이그레이션을 시작합니다...")
    
    # DB 연결
    db_connector = DBConnector()
    db = db_connector.SessionLocal()
    
    try:
        # CSV 파일 읽기
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'answer_category_result_202506231719.csv')
        df = pd.read_csv(csv_path)
        print(f"✓ CSV 파일에서 {len(df)}개의 데이터를 읽었습니다.")
        
        # nan 값을 None으로 변환
        df = df.replace({np.nan: None})
        
        # 기존 데이터 삭제
        db.execute(text("DELETE FROM answer_category_result"))
        print("✓ 기존 answer_category_result 데이터 삭제 완료")
        
        # 데이터 삽입
        for _, row in df.iterrows():
            insert_query = text("""
                INSERT INTO answer_category_result (
                    ANS_CAT_RESULT_ID,
                    EVAL_CAT_CD,
                    ANS_SCORE_ID,
                    ANS_CAT_SCORE,
                    STRENGTH_KEYWORD,
                    WEAKNESS_KEYWORD,
                    RGS_DTM,
                    UPD_DTM
                ) VALUES (
                    :result_id,
                    :cat_cd,
                    :score_id,
                    :cat_score,
                    :strength,
                    :weakness,
                    :rgs_dtm,
                    :upd_dtm
                )
            """)
            
            db.execute(insert_query, {
                'result_id': row['ANS_CAT_RESULT_ID'],
                'cat_cd': row['EVAL_CAT_CD'],
                'score_id': row['ANS_SCORE_ID'],
                'cat_score': row['ANS_CAT_SCORE'],
                'strength': row['STRENGTH_KEYWORD'],
                'weakness': row['WEAKNESS_KEYWORD'],
                'rgs_dtm': datetime.now(),
                'upd_dtm': datetime.now()
            })
            
            print(f"✓ ANS_CAT_RESULT_ID {row['ANS_CAT_RESULT_ID']} 데이터 삽입 완료")
        
        # 변경사항 커밋
        db.commit()
        print("\n[✅] answer_category_result 데이터 마이그레이션이 완료되었습니다!")
        
    except Exception as e:
        print(f"\n[❌] 오류가 발생했습니다: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_category_result() 