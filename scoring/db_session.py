# ----------------------------------------------------------------------------------------------------
# 작성목적 : 운영 DB 연결 설정
# 작성일 : 2024-03-21

# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# 2024-03-21 | 최초 구현 | 운영 DB 연결 설정 추가 | 이소미
# ----------------------------------------------------------------------------------------------------

import sys
import os

# 프로젝트 루트 경로를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.src.core.config.database import SessionLocal, engine

# DB 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DB 엔진 직접 사용
def get_engine():
    return engine 