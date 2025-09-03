# 데이터베이스 마이그레이션 가이드

## 개요
이 가이드는 localhost에서 db.hellobdd2.gabia.io로 데이터를 마이그레이션하는 방법을 설명합니다.

## 마이그레이션 대상 테이블
- `articles` - 게시글 데이터
- `comments` - 댓글 데이터  
- `reviews` - 후기 데이터
- `communities` - 커뮤니티 데이터 (참조용)

## 사전 준비

### 1. 환경 변수 설정
`.env` 파일에 다음 환경 변수를 추가하세요:

```bash
# 소스 데이터베이스 (localhost)
SOURCE_MYSQL_USER=root
SOURCE_MYSQL_PASSWORD=your_localhost_password
SOURCE_MYSQL_DATABASE=woori_collect

# 대상 데이터베이스 (db.hellobdd2.gabia.io)
TARGET_MYSQL_USER=hellobdd2
TARGET_MYSQL_PASSWORD=your_gabia_password
TARGET_MYSQL_DATABASE=hellobdd2
```

### 2. 데이터베이스 연결 확인
- localhost MySQL 서버가 실행 중인지 확인
- db.hellobdd2.gabia.io 접속 권한이 있는지 확인
- 대상 데이터베이스에 테이블이 생성되어 있는지 확인

## 마이그레이션 실행

### 1. 스크립트 실행
```bash
python scripts/migrate_localhost_to_gabia.py
```

### 2. 실행 과정
1. **연결 확인**: 소스 및 대상 데이터베이스 연결 테스트
2. **통계 조회**: 마이그레이션 전 데이터 개수 확인
3. **커뮤니티 마이그레이션**: 커뮤니티 데이터 이전
4. **게시글 마이그레이션**: articles 테이블 데이터 이전
5. **댓글 마이그레이션**: comments 테이블 데이터 이전
6. **후기 마이그레이션**: reviews 테이블 데이터 이전
7. **완료 통계**: 마이그레이션 후 데이터 개수 확인

## 마이그레이션 특징

### 중복 처리
- 모든 테이블에서 중복 데이터는 자동으로 건너뜀
- `platform_id`와 `community_article_id` 조합으로 중복 체크
- `platform_id`와 `platform_review_id` 조합으로 후기 중복 체크

### 데이터 무결성
- 외래키 관계 유지 (comments → articles)
- 댓글 마이그레이션 시 대상 DB의 게시글 ID로 매핑
- 날짜/시간 데이터 형식 유지

### 진행 상황 모니터링
- 100개 단위로 진행 상황 출력
- 실패한 레코드는 경고 로그로 기록
- 전체 통계로 마이그레이션 결과 확인

## 마이그레이션 후 작업

### 1. 애플리케이션 설정 변경
`.env` 파일에서 데이터베이스 설정을 대상 서버로 변경:

```bash
DB_TYPE=mysql
MYSQL_HOST=db.hellobdd2.gabia.io
MYSQL_PORT=3306
MYSQL_USER=hellobdd2
MYSQL_PASSWORD=your_gabia_password
MYSQL_DATABASE=hellobdd2
```

### 2. 애플리케이션 재시작
```bash
# API 서버 재시작
python run_api.py
```

### 3. 데이터 검증
- API를 통해 데이터가 정상적으로 조회되는지 확인
- 통계 API로 데이터 개수 확인
- 키워드 검색 기능 테스트

## 문제 해결

### 연결 오류
- 방화벽 설정 확인
- 데이터베이스 사용자 권한 확인
- 네트워크 연결 상태 확인

### 마이그레이션 실패
- 로그 파일 확인 (`logs/` 디렉토리)
- 실패한 레코드의 데이터 형식 확인
- 대상 데이터베이스의 테이블 구조 확인

### 성능 최적화
- 대용량 데이터의 경우 배치 크기 조정
- 네트워크 지연이 있는 경우 타임아웃 설정 조정
- 인덱스 최적화 고려

## 주의사항

1. **백업**: 마이그레이션 전 소스 데이터베이스 백업 권장
2. **테스트**: 운영 환경 적용 전 테스트 환경에서 먼저 실행
3. **모니터링**: 마이그레이션 중 시스템 리소스 모니터링
4. **롤백 계획**: 문제 발생 시 롤백 방법 준비

## 로그 확인

마이그레이션 로그는 다음 위치에서 확인할 수 있습니다:
- `logs/` 디렉토리의 최신 로그 파일
- 콘솔 출력의 실시간 진행 상황
- 오류 발생 시 상세한 스택 트레이스
