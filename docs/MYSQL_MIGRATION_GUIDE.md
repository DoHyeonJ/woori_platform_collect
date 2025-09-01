# MySQL 마이그레이션 가이드

## 📋 개요

이 가이드는 기존 SQLite 데이터베이스를 MySQL로 전환하는 방법을 설명합니다.

## 🛠️ 준비사항

### 1. MySQL 설치 및 설정

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server

# macOS (Homebrew)
brew install mysql

# Windows: MySQL Installer 사용
```

### 2. MySQL 데이터베이스 생성

```sql
-- MySQL에 로그인
mysql -u root -p

-- 데이터베이스 생성
CREATE DATABASE woori_platform_collect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 및 권한 부여 (선택사항)
CREATE USER 'woori_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON woori_platform_collect.* TO 'woori_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Python 패키지 설치

```bash
# 프로젝트 루트에서 실행
pip install -r requirements.txt

# 또는 개별 설치
pip install sqlalchemy pymysql cryptography alembic
```

## ⚙️ 환경 설정

### 1. .env 파일 생성

```bash
# 프로젝트 루트에 .env 파일 생성
cp .env.example .env  # 또는 직접 생성
```

### 2. .env 파일 설정

```env
# 애플리케이션 환경 설정
APPS_ENV=local  # local, development, staging, production (기본값: local)

# 데이터베이스 설정
DB_TYPE=sqlite  # 마이그레이션 전에는 sqlite로 설정

# MySQL 설정
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=woori_platform_collect

# API 서버 설정
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_LOG_LEVEL=info

# 환경 설정
ENVIRONMENT=development
```

## 🔄 마이그레이션 실행

### 1. 마이그레이션 스크립트 실행

```bash
# 프로젝트 루트에서 실행
python scripts/migrate_to_mysql.py
```

### 2. 마이그레이션 과정

스크립트는 다음 순서로 데이터를 마이그레이션합니다:

1. **커뮤니티 데이터** - 플랫폼별 커뮤니티 정보
2. **클라이언트 데이터** - 병원 정보
3. **게시글 데이터** - 수집된 게시글
4. **댓글 데이터** - 게시글에 달린 댓글
5. **후기 데이터** - 플랫폼별 후기 정보

### 3. 마이그레이션 확인

```bash
# MySQL에 접속하여 데이터 확인
mysql -u your_username -p woori_platform_collect

# 테이블 목록 확인
SHOW TABLES;

# 데이터 수 확인
SELECT COUNT(*) FROM articles;
SELECT COUNT(*) FROM comments;
SELECT COUNT(*) FROM reviews;
```

## 🔧 시스템 전환

### 1. 환경 변수 변경

마이그레이션 완료 후 `.env` 파일에서:

```env
# 변경 전
DB_TYPE=sqlite

# 변경 후
DB_TYPE=mysql
```

### 2. API 서버 재시작

```bash
# API 서버 재시작
python run_api.py
```

### 3. 동작 확인

```bash
# API 엔드포인트 테스트
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/statistics
```

## 🛡️ 환경별 테이블 생성 정책

### 자동 테이블 생성 조건

테이블 자동 생성은 **APPS_ENV=local**일 때만 실행됩니다:

| 환경 | APPS_ENV 값 | 테이블 자동 생성 | 설명 |
|------|-------------|------------------|------|
| **로컬 개발** | `local` (기본값) | ✅ **자동 생성** | 개발 편의성을 위해 자동 생성 |
| **개발 서버** | `development` | ❌ 수동 생성 필요 | 안정성을 위해 수동 관리 |
| **스테이징** | `staging` | ❌ 수동 생성 필요 | 프로덕션과 동일한 환경 |
| **프로덕션** | `production` | ❌ 수동 생성 필요 | 데이터 안전성 최우선 |

### 프로덕션 환경에서 테이블 생성

프로덕션 환경에서는 다음 방법 중 하나를 사용하세요:

#### 방법 1: 마이그레이션 스크립트 사용
```bash
# 환경 변수 설정
export APPS_ENV=production
export DB_TYPE=mysql

# 마이그레이션 실행
python scripts/migrate_to_mysql.py
```

#### 방법 2: 수동 SQL 실행
```sql
-- MySQL에 직접 접속하여 테이블 생성
-- (SQLAlchemy 모델에서 생성된 DDL 사용)
```

#### 방법 3: Alembic 마이그레이션 (권장)
```bash
# Alembic 초기화 (한 번만)
alembic init migrations

# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 실행
alembic upgrade head
```

## 📊 데이터베이스 스키마 비교

### SQLite vs MySQL 주요 차이점

| 항목 | SQLite | MySQL |
|------|--------|-------|
| 자동 증가 | `AUTOINCREMENT` | `AUTO_INCREMENT` |
| 텍스트 크기 제한 | 무제한 | `TEXT`, `VARCHAR(255)` |
| 불린 타입 | 정수 (0/1) | `BOOLEAN` |
| 날짜 타입 | 텍스트 | `DATETIME` |
| 외래키 제약 | 기본 비활성화 | 기본 활성화 |

### 새로운 SQLAlchemy 모델 특징

- 🔄 **데이터베이스 독립적**: SQLite, MySQL, PostgreSQL 지원
- 🔗 **관계 매핑**: 테이블 간 관계 자동 처리
- 📝 **타입 안전성**: Python 타입 힌트 지원
- 🚀 **성능 최적화**: 인덱스 및 쿼리 최적화

## 🛡️ 백업 및 복구

### 1. SQLite 백업

```bash
# 마이그레이션 전 SQLite 백업
cp data/collect_data.db data/collect_data_backup.db
```

### 2. MySQL 백업

```bash
# MySQL 데이터 백업
mysqldump -u username -p woori_platform_collect > backup.sql

# 백업에서 복구
mysql -u username -p woori_platform_collect < backup.sql
```

## 🔧 문제 해결

### 1. 연결 오류

```
Error: Can't connect to MySQL server
```

**해결 방법:**
- MySQL 서버가 실행 중인지 확인
- 호스트, 포트, 사용자명, 비밀번호 확인
- 방화벽 설정 확인

### 2. 권한 오류

```
Error: Access denied for user
```

**해결 방법:**
```sql
-- MySQL에서 권한 확인 및 부여
SHOW GRANTS FOR 'username'@'localhost';
GRANT ALL PRIVILEGES ON woori_platform_collect.* TO 'username'@'localhost';
```

### 3. 문자 인코딩 오류

```
Error: Incorrect string value
```

**해결 방법:**
- 데이터베이스와 테이블을 `utf8mb4` 인코딩으로 설정
- MySQL 설정에서 `character-set-server=utf8mb4` 추가

### 4. 마이그레이션 중단

**해결 방법:**
```bash
# MySQL 데이터 초기화 후 재시도
mysql -u username -p -e "DROP DATABASE woori_platform_collect; CREATE DATABASE woori_platform_collect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 마이그레이션 재실행
python scripts/migrate_to_mysql.py
```

## 🎯 성능 최적화 팁

### 1. MySQL 설정 최적화

```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
```

### 2. 인덱스 활용

SQLAlchemy 모델에는 다음 인덱스가 자동 생성됩니다:

- `articles`: `platform_id`, `community_article_id` 복합 인덱스
- `comments`: `platform_id`, `community_article_id` 복합 인덱스
- `reviews`: `platform_id`, `platform_review_id` 복합 인덱스

### 3. 연결 풀링

```python
# database/config.py에서 연결 풀 설정
engine = create_engine(
    database_url,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

## 📈 모니터링

### 1. 성능 모니터링

```sql
-- 느린 쿼리 확인
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';

-- 프로세스 목록 확인
SHOW PROCESSLIST;
```

### 2. 로그 확인

```bash
# MySQL 에러 로그
tail -f /var/log/mysql/error.log

# 애플리케이션 로그
tail -f logs/$(date +%Y-%m-%d).log
```

## 🔄 롤백 계획

문제 발생 시 SQLite로 되돌리는 방법:

1. `.env` 파일에서 `DB_TYPE=sqlite`로 변경
2. API 서버 재시작
3. SQLite 백업 파일 복원 (필요시)

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. 로그 파일 (`logs/` 디렉토리)
2. MySQL 에러 로그
3. 환경 변수 설정
4. 네트워크 연결 상태

---

**참고**: 이 가이드는 개발 환경 기준으로 작성되었습니다. 프로덕션 환경에서는 추가적인 보안 설정이 필요할 수 있습니다.
