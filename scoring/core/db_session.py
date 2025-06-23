# ----------------------------------------------------------------------------------------------------
# 작성목적 : 운영 DB 연결 설정
# 작성일 : 2025-06-23

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2025-06-23 | 최초 구현 | 운영 DB 연결 설정 추가 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os
from scoring.core.db_connector import DBConnector

# DB 세션 생성
def get_db():
    db = DBConnector().SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DB 엔진 직접 사용
def get_engine():
    return DBConnector().engine 