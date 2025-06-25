# ----------------------------------------------------------------------------------------------------
# 작성목적 : answer_category_result와 answer_score 테이블 구조 덤프 추출
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | 테이블 구조 덤프 추출 스크립트 작성 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scoring.core.db_connector import DBConnector
from sqlalchemy import text

def dump_table_schemas():
    db = DBConnector()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"table_schema_dump_{timestamp}.sql"
    
    # 테이블 생성 SQL 추출 쿼리
    show_create_queries = [
        "SHOW CREATE TABLE answer_category_result",
        "SHOW CREATE TABLE answer_score"
    ]
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            with db.engine.connect() as conn:
                # SET 문 추가
                f.write("SET NAMES utf8mb4;\n")
                f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                
                for query in show_create_queries:
                    result = conn.execute(text(query)).fetchone()
                    create_sql = result[1]  # SHOW CREATE TABLE의 두 번째 컬럼이 CREATE 문
                    
                    # DROP TABLE IF EXISTS 추가
                    table_name = result[0]
                    f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
                    f.write(f"{create_sql};\n\n")
                
                # FOREIGN KEY CHECKS 복원
                f.write("SET FOREIGN_KEY_CHECKS=1;\n")
            
        print(f"테이블 구조가 {output_file}에 성공적으로 덤프되었습니다.")
        
        # 파일 내용 출력
        print("\n생성된 덤프 파일 내용:")
        print("-" * 100)
        with open(output_file, 'r', encoding='utf-8') as f:
            print(f.read())
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    dump_table_schemas() 