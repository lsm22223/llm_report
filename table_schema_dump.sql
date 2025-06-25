-- 테이블 스키마 덤프 파일
-- 생성일시: 2025-06-25

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

-- evaluation_category 테이블 구조
DROP TABLE IF EXISTS evaluation_category;
CREATE TABLE evaluation_category (
  EVAL_CAT_CD varchar(20) NOT NULL COMMENT '평가 항목 코드',
  CAT_NM varchar(100) NOT NULL COMMENT '평가 항목명',
  MAX_SCORE int NOT NULL DEFAULT 100 COMMENT '최대 점수',
  WEIGHT decimal(3,2) NOT NULL COMMENT '가중치',
  RGS_DTM datetime NOT NULL COMMENT '등록일시',
  UPD_DTM datetime NOT NULL COMMENT '수정일시',
  PRIMARY KEY (EVAL_CAT_CD)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='평가 항목 정보';

-- answer_score 테이블 구조
DROP TABLE IF EXISTS answer_score;
CREATE TABLE answer_score (
  ANS_SCORE_ID bigint NOT NULL AUTO_INCREMENT COMMENT '답변 점수 ID',
  INTV_ANS_ID bigint NOT NULL COMMENT '면접 답변 ID',
  EVAL_SUMMARY text COMMENT '평가 요약',
  RGS_DTM datetime NOT NULL COMMENT '등록일시',
  UPD_DTM datetime NOT NULL COMMENT '수정일시',
  PRIMARY KEY (ANS_SCORE_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='답변 점수 정보';

-- answer_category_result 테이블 구조
DROP TABLE IF EXISTS answer_category_result;
CREATE TABLE answer_category_result (
  ANS_CAT_RESULT_ID bigint NOT NULL AUTO_INCREMENT COMMENT '답변 카테고리 결과 ID',
  ANS_SCORE_ID bigint NOT NULL COMMENT '답변 점수 ID',
  EVAL_CAT_CD varchar(20) NOT NULL COMMENT '평가 항목 코드',
  ANS_CAT_SCORE decimal(5,2) NOT NULL COMMENT '항목 점수',
  STRENGTH_KEYWORD varchar(500) DEFAULT NULL COMMENT '강점 키워드',
  WEAKNESS_KEYWORD varchar(500) DEFAULT NULL COMMENT '약점 키워드',
  RGS_DTM datetime NOT NULL COMMENT '등록일시',
  UPD_DTM datetime NOT NULL COMMENT '수정일시',
  PRIMARY KEY (ANS_CAT_RESULT_ID),
  KEY FK_answer_category_result_answer_score (ANS_SCORE_ID),
  KEY FK_answer_category_result_evaluation_category (EVAL_CAT_CD),
  CONSTRAINT FK_answer_category_result_answer_score FOREIGN KEY (ANS_SCORE_ID) REFERENCES answer_score (ANS_SCORE_ID) ON DELETE CASCADE,
  CONSTRAINT FK_answer_category_result_evaluation_category FOREIGN KEY (EVAL_CAT_CD) REFERENCES evaluation_category (EVAL_CAT_CD)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='답변 카테고리별 결과';

-- interview_result 테이블 구조
DROP TABLE IF EXISTS interview_result;
CREATE TABLE interview_result (
  INTV_RESULT_ID bigint NOT NULL AUTO_INCREMENT COMMENT '면접 결과 ID',
  APL_ID bigint NOT NULL COMMENT '지원자 ID',
  INTV_PROC_ID bigint NOT NULL COMMENT '면접 프로세스 ID',
  OVERALL_SCORE decimal(5,2) DEFAULT NULL COMMENT '종합 점수',
  OVERALL_GRADE varchar(2) DEFAULT NULL COMMENT '등급',
  OVERALL_RANK int DEFAULT NULL COMMENT '순위',
  STRENGTH_KEYWORD varchar(500) DEFAULT NULL COMMENT '강점 키워드',
  WEAKNESS_KEYWORD varchar(500) DEFAULT NULL COMMENT '약점 키워드',
  RGS_DTM datetime NOT NULL COMMENT '등록일시',
  UPD_DTM datetime NOT NULL COMMENT '수정일시',
  PRIMARY KEY (INTV_RESULT_ID),
  KEY IDX_interview_result_APL_ID (APL_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='면접 결과 정보';

-- interview_category_result 테이블 구조
DROP TABLE IF EXISTS interview_category_result;
CREATE TABLE interview_category_result (
  INTV_CAT_RESULT_ID bigint NOT NULL AUTO_INCREMENT COMMENT '면접 카테고리 결과 ID',
  INTV_RESULT_ID bigint NOT NULL COMMENT '면접 결과 ID',
  EVAL_CAT_CD varchar(20) NOT NULL COMMENT '평가 항목 코드',
  FEEDBACK_TXT text COMMENT '피드백 내용',
  RGS_DTM datetime NOT NULL COMMENT '등록일시',
  UPD_DTM datetime NOT NULL COMMENT '수정일시',
  PRIMARY KEY (INTV_CAT_RESULT_ID),
  KEY FK_interview_category_result_interview_result (INTV_RESULT_ID),
  KEY FK_interview_category_result_evaluation_category (EVAL_CAT_CD),
  CONSTRAINT FK_interview_category_result_interview_result FOREIGN KEY (INTV_RESULT_ID) REFERENCES interview_result (INTV_RESULT_ID) ON DELETE CASCADE,
  CONSTRAINT FK_interview_category_result_evaluation_category FOREIGN KEY (EVAL_CAT_CD) REFERENCES evaluation_category (EVAL_CAT_CD)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='면접 카테고리별 결과';

SET FOREIGN_KEY_CHECKS=1; 