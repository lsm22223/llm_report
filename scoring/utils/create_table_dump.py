# ----------------------------------------------------------------------------------------------------
# 작성목적 : DB 테이블 스키마 덤프 파일 생성
# 작성일 : 2025-06-25
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-25 | 최초 구현 | 주요 테이블 스키마 덤프 파일 생성 | 이소미
# ----------------------------------------------------------------------------------------------------

from sqlalchemy import create_engine, MetaData, inspect
from datetime import datetime
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DB 연결 정보
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
metadata = MetaData()
inspector = inspect(engine)

# 덤프할 테이블 목록
TABLES = [
    'interview_result',
    'interview_category_result',
    'answer_score',
    'answer_category_result',
    'evaluation_category'
]

def get_column_definition(column):
    """컬럼 정의를 SQL 문자열로 변환"""
    sql = f"{column['name']} {column['type']}"
    
    if not column['nullable']:
        sql += " NOT NULL"
        
    if column.get('default') is not None:
        sql += f" DEFAULT {column['default']}"
        
    if column.get('autoincrement'):
        sql += " AUTO_INCREMENT"
        
    return sql

def get_primary_keys(table_name):
    """테이블의 기본키 정보 추출"""
    pk_constraint = inspector.get_pk_constraint(table_name)
    if pk_constraint and pk_constraint['constrained_columns']:
        return pk_constraint['constrained_columns']
    return []

def get_foreign_keys(table_name):
    """테이블의 외래키 정보 추출"""
    return inspector.get_foreign_keys(table_name)

def create_table_sql(table_name):
    """테이블 생성 SQL 문 생성"""
    columns = inspector.get_columns(table_name)
    pk_columns = get_primary_keys(table_name)
    fk_info = get_foreign_keys(table_name)
    
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    
    # 컬럼 정의
    column_defs = []
    for column in columns:
        column_defs.append("  " + get_column_definition(column))
    
    # 기본키 제약조건
    if pk_columns:
        column_defs.append(f"  PRIMARY KEY ({', '.join(pk_columns)})")
    
    # 외래키 제약조건
    for fk in fk_info:
        referred_table = fk['referred_table']
        constrained_cols = fk['constrained_columns']
        referred_cols = fk['referred_columns']
        fk_name = fk.get('name', f"fk_{table_name}_{referred_table}")
        
        fk_def = f"  CONSTRAINT {fk_name} FOREIGN KEY ({', '.join(constrained_cols)}) "
        fk_def += f"REFERENCES {referred_table} ({', '.join(referred_cols)})"
        column_defs.append(fk_def)
    
    sql += ",\n".join(column_defs)
    sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
    
    return sql

def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"table_schema_dump_{timestamp}.sql"
    
    with open(filename, 'w', encoding='utf-8') as f:
        # 헤더 작성
        f.write("-- 테이블 스키마 덤프 파일\n")
        f.write(f"-- 생성일시: {datetime.now()}\n\n")
        
        # SET 문 작성
        f.write("SET NAMES utf8mb4;\n")
        f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
        
        # 각 테이블별 DROP 및 CREATE 문 작성
        for table in TABLES:
            f.write(f"-- {table} 테이블 구조\n")
            f.write(f"DROP TABLE IF EXISTS {table};\n")
            f.write(create_table_sql(table) + "\n\n")
        
        # FOREIGN_KEY_CHECKS 복원
        f.write("SET FOREIGN_KEY_CHECKS=1;\n")
    
    print(f"✓ 스키마 덤프 파일이 생성되었습니다: {filename}")

if __name__ == "__main__":
    main() 