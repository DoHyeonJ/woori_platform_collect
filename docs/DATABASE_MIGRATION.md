# 🗄️ 데이터베이스 마이그레이션 가이드

이 문서는 우리 플랫폼 데이터 수집 시스템의 데이터베이스 마이그레이션 과정을 상세히 설명합니다.

## 📋 목차

- [개요](#개요)
- [마이그레이션 전 준비사항](#마이그레이션-전-준비사항)
- [필수 마이그레이션](#필수-마이그레이션)
- [선택적 마이그레이션](#선택적-마이그레이션)
- [마이그레이션 순서](#마이그레이션-순서)
- [문제 해결](#문제-해결)
- [롤백 방법](#롤백-방법)

## 🎯 개요

데이터베이스 마이그레이션은 기존 데이터베이스 구조를 새로운 요구사항에 맞게 변경하는 과정입니다. 이 시스템에서는 다음과 같은 변경사항이 적용됩니다:

### 주요 변경사항

1. **Comment 테이블 구조 변경**
   - `article_id` → `platform_id`, `community_article_id`, `community_comment_id`
   - 외래키 관계 개선

2. **네이버 커뮤니티 추가**
   - `community_id = 3`으로 설정
   - 네이버 데이터 수집 지원

3. **ID 필드 타입 변경**
   - 모든 ID 필드를 `TEXT` 타입으로 통일
   - 플랫폼 간 호환성 향상

## ⚠️ 마이그레이션 전 준비사항

### 1. 데이터 백업

```bash
# 데이터베이스 파일 백업
cp data/collect_data.db data/collect_data_backup_$(date +%Y%m%d_%H%M%S).db

# 또는 SQL 덤프 생성
sqlite3 data/collect_data.db .dump > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. 시스템 중지

```bash
# API 서버 중지
# 실행 중인 수집 프로세스 중지
# 데이터베이스 연결 확인
```

### 3. 권한 확인

```bash
# 데이터베이스 파일 쓰기 권한 확인
ls -la data/collect_data.db

# 필요시 권한 수정
chmod 644 data/collect_data.db
```

## 🔧 필수 마이그레이션

### 1. 네이버 커뮤니티 추가

#### 목적
네이버 데이터 수집을 위한 커뮤니티를 추가하고 `community_id = 3`으로 설정합니다.

#### 실행 방법
```bash
python scripts/add_naver_community.py
```

#### 예상 출력
```
🔧 네이버 커뮤니티 추가 시작: data/collect_data.db
📋 현재 커뮤니티 목록:
  - ID: 1, 이름: 강남언니, 생성일: 2025-08-15 10:00:00
  - ID: 2, 이름: 바비톡, 생성일: 2025-08-15 10:00:00
📝 네이버 커뮤니티 추가 중...
✅ 네이버 커뮤니티를 ID 3으로 추가 완료

📋 최종 커뮤니티 목록:
  - ID: 1, 이름: 강남언니, 생성일: 2025-08-15 10:00:00
  - ID: 2, 이름: 바비톡, 생성일: 2025-08-15 10:00:00
  - ID: 3, 이름: 네이버, 생성일: 2025-08-15 10:30:00

✅ 네이버 커뮤니티 설정 완료:
  - ID: 3
  - 이름: 네이버
  - 생성일: 2025-08-15 10:30:00
  - 설명: 네이버 카페 데이터 수집을 위한 커뮤니티

🎉 네이버 커뮤니티 설정 완료!
```

#### 확인 방법
```sql
-- SQLite 접속
sqlite3 data/collect_data.db

-- 커뮤니티 목록 확인
SELECT * FROM communities ORDER BY id;

-- 네이버 커뮤니티 확인
SELECT * FROM communities WHERE name = '네이버';
```

---

### 2. 댓글 테이블 구조 변경

#### 목적
기존 `comments` 테이블의 구조를 새로운 요구사항에 맞게 변경합니다.

#### 실행 방법
```bash
python scripts/migrate_comments_table.py
```

#### 예상 출력
```
🔧 comments 테이블 마이그레이션 시작: data/collect_data.db
현재 comments 테이블 컬럼: ['id', 'article_id', 'content', 'writer_nickname', 'writer_id', 'created_at', 'parent_comment_id', 'collected_at']
📋 새로운 구조의 임시 테이블 생성 중...
🔄 기존 데이터 마이그레이션 중...
기존 댓글 수: 45개
✅ 45개 댓글 마이그레이션 완료
🔄 테이블 교체 중...
📊 인덱스 생성 중...
🔗 외래키 제약 조건 추가 중...
✅ 마이그레이션 완료! 최종 comments 테이블 컬럼: ['id', 'platform_id', 'community_article_id', 'community_comment_id', 'content', 'writer_nickname', 'writer_id', 'created_at', 'parent_comment_id', 'collected_at']
📊 최종 댓글 수: 45개
🎉 comments 테이블 마이그레이션 완료!
```

#### 변경 전후 구조 비교

**변경 전**:
```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    writer_nickname TEXT NOT NULL,
    writer_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parent_comment_id INTEGER,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles (id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments (id)
);
```

**변경 후**:
```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_id TEXT NOT NULL,
    community_article_id TEXT NOT NULL,
    community_comment_id TEXT NOT NULL,
    content TEXT NOT NULL,
    writer_nickname TEXT NOT NULL,
    writer_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parent_comment_id TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (platform_id, community_article_id) REFERENCES articles (platform_id, community_article_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments (community_comment_id)
);
```

#### 확인 방법
```sql
-- 테이블 구조 확인
PRAGMA table_info(comments);

-- 인덱스 확인
SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='comments';

-- 외래키 제약 조건 확인
PRAGMA foreign_key_list(comments);

-- 데이터 샘플 확인
SELECT * FROM comments LIMIT 5;
```

---

## 🔄 선택적 마이그레이션

### 1. ID 필드 타입 변경

#### 목적
모든 ID 필드를 `TEXT` 타입으로 통일하여 플랫폼 간 호환성을 향상시킵니다.

#### 실행 방법
```bash
python scripts/migrate_id_to_string.py
```

#### 변경 대상
- `articles.community_article_id`
- `reviews.platform_review_id`
- `comments.community_comment_id`

#### 확인 방법
```sql
-- articles 테이블 확인
PRAGMA table_info(articles);

-- reviews 테이블 확인
PRAGMA table_info(reviews);

-- comments 테이블 확인
PRAGMA table_info(comments);
```

---

### 2. collected_at 필드 추가

#### 목적
모든 테이블에 `collected_at` 필드를 추가하여 데이터 수집 시간을 기록합니다.

#### 실행 방법
```bash
python scripts/migrate_collected_at.py
```

#### 변경 대상
- `articles` 테이블
- `comments` 테이블
- `reviews` 테이블

#### 확인 방법
```sql
-- collected_at 필드 확인
SELECT id, created_at, collected_at FROM articles LIMIT 5;
SELECT id, created_at, collected_at FROM comments LIMIT 5;
SELECT id, created_at, collected_at FROM reviews LIMIT 5;
```

---

## 📋 마이그레이션 순서

### 권장 실행 순서

1. **데이터 백업** (필수)
   ```bash
   cp data/collect_data.db data/collect_data_backup_$(date +%Y%m%d_%H%M%S).db
   ```

2. **네이버 커뮤니티 추가** (필수)
   ```bash
   python scripts/add_naver_community.py
   ```

3. **댓글 테이블 구조 변경** (필수)
   ```bash
   python scripts/migrate_comments_table.py
   ```

4. **ID 필드 타입 변경** (선택)
   ```bash
   python scripts/migrate_id_to_string.py
   ```

5. **collected_at 필드 추가** (선택)
   ```bash
   python scripts/migrate_collected_at.py
   ```

6. **마이그레이션 완료 확인**
   ```bash
   python -c "from database.models import DatabaseManager; print('✅ 마이그레이션 완료')"
   ```

### 실행 시간 예상

| 마이그레이션 | 예상 시간 | 데이터 크기에 따른 영향 |
|-------------|----------|----------------------|
| 네이버 커뮤니티 추가 | 1-2초 | 없음 |
| 댓글 테이블 구조 변경 | 5-30초 | 댓글 수에 비례 |
| ID 필드 타입 변경 | 10-60초 | 전체 레코드 수에 비례 |
| collected_at 필드 추가 | 5-20초 | 전체 레코드 수에 비례 |

---

## 🚨 문제 해결

### 1. 일반적인 오류

#### 권한 오류
```bash
# 오류 메시지
❌ 마이그레이션 실패: [Errno 13] Permission denied

# 해결 방법
chmod 644 data/collect_data.db
chmod 755 data/
```

#### 데이터베이스 잠금 오류
```bash
# 오류 메시지
❌ 마이그레이션 실패: database is locked

# 해결 방법
# 1. 모든 SQLite 연결 종료
# 2. API 서버 중지
# 3. 수집 프로세스 중지
# 4. 마이그레이션 재시도
```

#### 외래키 제약 조건 오류
```bash
# 오류 메시지
❌ 마이그레이션 실패: FOREIGN KEY constraint failed

# 해결 방법
# 1. 데이터 무결성 확인
# 2. 고아 레코드 정리
# 3. 마이그레이션 재시도
```

### 2. 데이터 무결성 확인

#### 고아 댓글 확인
```sql
-- 고아 댓글 조회
SELECT c.* FROM comments c
LEFT JOIN articles a ON c.platform_id = a.platform_id 
    AND c.community_article_id = a.community_article_id
WHERE a.id IS NULL;

-- 고아 댓글 수
SELECT COUNT(*) FROM comments c
LEFT JOIN articles a ON c.platform_id = a.platform_id 
    AND c.community_article_id = a.community_article_id
WHERE a.id IS NULL;
```

#### 고아 댓글 정리
```sql
-- 고아 댓글 삭제 (주의: 데이터 손실 가능)
DELETE FROM comments WHERE id IN (
    SELECT c.id FROM comments c
    LEFT JOIN articles a ON c.platform_id = a.platform_id 
        AND c.community_article_id = a.community_article_id
    WHERE a.id IS NULL
);
```

### 3. 성능 최적화

#### 인덱스 최적화
```sql
-- 인덱스 상태 확인
SELECT name, sql FROM sqlite_master WHERE type='index';

-- 불필요한 인덱스 제거
DROP INDEX IF EXISTS idx_unused;

-- 새로운 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_articles_platform_date 
ON articles(platform_id, created_at);
```

#### 통계 업데이트
```sql
-- SQLite 통계 업데이트
ANALYZE;

-- 특정 테이블 통계 업데이트
ANALYZE articles;
ANALYZE comments;
ANALYZE reviews;
```

---

## 🔙 롤백 방법

### 1. 전체 롤백

```bash
# 백업 파일에서 복원
cp data/collect_data_backup_YYYYMMDD_HHMMSS.db data/collect_data.db

# 권한 복원
chmod 644 data/collect_data.db
```

### 2. 부분 롤백

#### 댓글 테이블 롤백
```sql
-- 기존 구조로 복원 (주의: 데이터 손실 가능)
DROP TABLE comments;
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    writer_nickname TEXT NOT NULL,
    writer_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parent_comment_id INTEGER,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles (id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments (id)
);
```

#### 네이버 커뮤니티 롤백
```sql
-- 네이버 커뮤니티 삭제
DELETE FROM communities WHERE name = '네이버';

-- 관련 데이터 정리
DELETE FROM articles WHERE platform_id = 'naver';
DELETE FROM comments WHERE platform_id = 'naver';
```

### 3. 롤백 후 확인

```bash
# 데이터베이스 상태 확인
python -c "from database.models import DatabaseManager; print('✅ 롤백 완료')"

# 테이블 구조 확인
sqlite3 data/collect_data.db ".schema"
```

---

## 📊 마이그레이션 완료 확인

### 1. 기본 확인사항

```bash
# 모든 마이그레이션 스크립트 실행 확인
ls -la scripts/migrate_*.py

# 데이터베이스 파일 상태 확인
ls -la data/collect_data.db

# 데이터베이스 연결 테스트
python -c "from database.models import DatabaseManager; print('✅ 연결 성공')"
```

### 2. 상세 확인사항

#### 테이블 구조 확인
```sql
-- 모든 테이블 목록
.tables

-- 각 테이블 구조 확인
.schema communities
.schema articles
.schema comments
.schema reviews
```

#### 데이터 샘플 확인
```sql
-- 커뮤니티 확인
SELECT * FROM communities ORDER BY id;

-- 게시글 샘플 확인
SELECT id, platform_id, community_article_id, title FROM articles LIMIT 5;

-- 댓글 샘플 확인
SELECT id, platform_id, community_article_id, content FROM comments LIMIT 5;
```

#### 외래키 관계 확인
```sql
-- 외래키 제약 조건 확인
PRAGMA foreign_key_list(articles);
PRAGMA foreign_key_list(comments);
PRAGMA foreign_key_list(reviews);
```

### 3. 기능 테스트

```bash
# 네이버 수집기 테스트
python scripts/test_naver_collector.py

# API 서버 테스트
python run_api.py
# 브라우저에서 http://localhost:8000/docs 접속
```

---

## 📞 지원 및 문의

### 마이그레이션 관련 문제

- **GitHub Issues**: 마이그레이션 오류 리포트
- **로그 분석**: 상세한 오류 로그와 함께 문제 상황 설명
- **데이터 샘플**: 문제가 발생한 데이터 샘플 제공

### 권장사항

1. **테스트 환경에서 먼저 실행**: 프로덕션 환경 적용 전 테스트
2. **충분한 백업**: 여러 시점의 백업 파일 보관
3. **단계별 실행**: 한 번에 하나씩 마이그레이션 실행
4. **검증 단계**: 각 단계 후 데이터 무결성 확인

---

**마지막 업데이트**: 2025년 8월 15일  
**문서 버전**: 1.0.0  
**적용 버전**: 시스템 v1.0.0
