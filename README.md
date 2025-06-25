# 🎯 AI 면접 분석 서버

FastAPI 백엔드에서 수집된 면접 데이터를 분석하여 다음 항목들을 자동으로 계산 및 저장합니다:

- 면접자별 평가 항목 점수 평균
- 가중치 기반 최종 점수 및 등급 산정
- 항목별 평가 코멘트 요약 (LLM)
- 면접자별 강점/약점 키워드 추출 (LLM)

---

## 📁 폴더 구조 및 기능 설명

```
final_report/
├── scoring/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── db_connector.py    # DB 연결 및 세션 관리
│   │   └── db_session.py      # DB 세션 설정
│   ├── score/
│   │   ├── __init__.py
│   │   ├── score_calculator.py # 점수 계산 및 등급 산정
│   │   └── run_scoring.py     # 점수 계산 실행
│   ├── comment/
│   │   ├── __init__.py
│   │   ├── comment_generator.py # 평가 코멘트 생성
│   │   └── llm.py             # LLM 관련 유틸리티
│   ├── keyword/
│   │   ├── __init__.py
│   │   ├── keyword_extractor.py # 키워드 추출
│   │   ├── run_keyword_extractor.py # 키워드 추출 실행
│   │   └── show_keywords.py   # 추출된 키워드 조회
│   └── utils/
│       ├── __init__.py
│       ├── check_tables.py    # DB 테이블 구조 확인
│       └── test_db.py         # DB 연결 테스트
├── run_all.py                 # 전체 프로세스 실행
└── show_results.py            # 분석 결과 조회
```

### 📊 주요 모듈 설명

#### 1. 점수 계산 (`score/score_calculator.py`)
- 평가 항목별 평균 점수 계산
- 가중치 적용하여 최종 점수 계산
- 상대 등급 산정 (A+, A, B+, B, C+, C 등)
- 순위 계산 및 DB 저장

#### 2. 코멘트 생성 (`comment/comment_generator.py`)
- 평가 항목별 피드백 수집
- GPT-4를 사용한 코멘트 자동 생성
- 평가 항목의 특성을 반영한 맞춤형 코멘트
- 생성된 코멘트 DB 저장

#### 3. 키워드 추출 (`keyword/keyword_extractor.py`)
- 면접자별 피드백 수집
- GPT-4를 사용한 강점/약점 키워드 추출
- 추출된 키워드 DB 저장

### 🔄 실행 방법

1. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. .env 설정
```bash
cp .env.example .env
# 에디터로 아래 값들을 설정:
# - DATABASE_URL: MySQL 연결 정보
# - OPENAI_API_KEY: GPT-4 API 키
```

3. 실행 옵션

a. 전체 프로세스 실행:
```bash
python run_all.py
```

b. 개별 기능 실행:
```bash
# 점수 계산만 실행
python -m scoring.score.run_scoring

# 결과 조회
python show_results.py
```

### 📚 데이터베이스 구조

1. `interview_result`: 면접 결과 정보
   - INTV_RESULT_ID: 면접 결과 ID (PK)
   - APL_ID: 지원자 ID
   - INTV_PROC_ID: 면접 프로세스 ID
   - OVERALL_SCORE: 종합 점수
   - OVERALL_GRADE: 등급
   - OVERALL_RANK: 순위
   - STRENGTH_KEYWORD: 강점 키워드
   - WEAKNESS_KEYWORD: 약점 키워드

2. `answer_category_result`: 평가 항목별 점수
   - ANS_CAT_RESULT_ID: 결과 ID (PK)
   - EVAL_CAT_CD: 평가 항목 코드
   - ANS_SCORE_ID: 답변 점수 ID
   - ANS_CAT_SCORE: 항목 점수

3. `evaluation_category`: 평가 항목 정보
   - EVAL_CAT_CD: 평가 항목 코드 (PK)
   - WEIGHT: 가중치

### 🔍 주요 평가 항목
- COMM_SKILL: 의사소통력
- ENGLISH: 영어 능력
- PROB_SOLVE: 문제해결력
- SPECIAL: 조직 적합도
- TECH_SKILL: 보유 역량

### 💡 주요 로직 및 주의사항

#### 1. 데이터 처리 방식
- 각 함수는 DB 세션을 통해 데이터 처리
- 면접자 ID를 따로 전달할 필요 없음 (전체 데이터 자동 처리)
- 각 함수는 독립적으로 실행 가능

#### 2. 데이터 흐름
```
1. 점수 계산 (score_calculator.py)
interview_result + answer_category_result
↓
최종 점수 및 등급
↓
interview_result 업데이트

2. 결과 조회 (show_results.py)
- 전체 면접 결과 요약
- 평가 항목별 점수
- 통계 정보 (등급 분포, 항목별 평균/최저/최고)
```

#### 3. 실행 순서 (`run_all.py`)
1. 분석이 필요한 데이터 확인
2. 점수 계산 (`process_scores`)
3. 코멘트 생성 (`generate_all_comments`)
4. 키워드 추출 (`extract_and_store_keywords`)

### 📝 변경 내역

#### 2025-06-24
1. 영어 평가 항목 통합
   - ENGLISH_FLUENCY와 ENGLISH_GRAMMAR를 ENGLISH_ABILITY로 통합
   - 관련 DB 스키마 및 코드 수정

2. 면접 결과 ID 부여 방식 개선
   - INTV_RESULT_ID가 APL_ID를 따라가지 않고 순차적으로 부여되도록 수정 (1,2,3...)
   - 점수 순으로 정렬되어 ID 부여

3. 평가 등급 체계 단순화
   - interview_category_result 테이블에서 CAT_GRADE 컬럼 제거
   - 가중치를 반영한 전체 등급만 표시하도록 변경
   - 관련 코드 정리 및 최적화

### 🧪 테스트 및 유틸리티 스크립트

#### 1. 테스트 데이터 관리
- `test_data.py`: 기본 테스트 데이터 생성
- `test_english.py`: 영어 평가 관련 테스트 데이터 생성
- `update_categories.py`: 평가 카테고리 업데이트 및 초기화

#### 2. 유틸리티 스크립트 (`scoring/utils/`)
- `add_upd_dtm.py`: 데이터 수정일시 자동 업데이트
- `backup_and_migrate.py`: DB 백업 및 마이그레이션
- `check_eval_categories.py`: 평가 카테고리 유효성 검사
- `check_null_columns.py`: NULL 값 검사
- `check_tables.py`: 테이블 구조 검사
- `dump_table_schema.py`: 테이블 스키마 덤프
- `migrate_ans_score.py`: 답변 점수 마이그레이션
- `migrate_category_result.py`: 카테고리 결과 마이그레이션
- `show_columns.py`: 컬럼 정보 조회
- `show_table_schema.py`: 테이블 스키마 조회
- `update_table_structure.py`: 테이블 구조 업데이트

### 🔒 제외 대상 (.gitignore)
- Python 관련: `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`, `build/`, `dist/`, `*.egg-info/`
- 환경 설정: `.env` (`.env.example` 제외)
- IDE 설정: `.idea/`, `.vscode/`
- 로그 파일: `*.log`
- 가상환경: `venv/`, `ENV/`
- 데이터 파일: `*.csv`
- 백엔드 폴더: `backend/`

### 📋 코드 작성 규칙
1. 모든 파일 최상단에 작성 목적과 변경 이력을 주석으로 기록
```python
# ----------------------------------------------------------------------------------------------------
# 작성목적 : [파일의 주요 기능 설명]
# 작성일 : YYYY-MM-DD
# 
# 변경사항 내역 (날짜 | 변경목적 | 변경내용 | 작성자 순으로 기입)
# YYYY-MM-DD | 최초 구현 | 상세 구현 내용 | 작성자
# ----------------------------------------------------------------------------------------------------
```

2. 주요 함수와 클래스에 상세한 docstring 작성
3. 변수명과 함수명은 명확하고 이해하기 쉽게 작성
4. 에러 처리는 try-except 구문으로 명확하게 처리
5. DB 연결은 `DBConnector` 클래스를 통해 일관되게 관리

### 🔄 데이터베이스 작업 시 주의사항
1. 모든 테이블에 `RGS_DTM`(등록일시)와 `UPD_DTM`(수정일시) 필수
2. FK 관계가 있는 테이블 삭제 시 자식 테이블부터 삭제
3. 데이터 변경 전 반드시 백업
4. 트랜잭션 처리 필수 (commit/rollback)
5. 대용량 데이터 처리 시 배치 처리 권장
