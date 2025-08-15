# 🚀 우리 플랫폼 데이터 수집 시스템

다양한 플랫폼(강남언니, 바비톡, 네이버)에서 데이터를 수집하고 관리하는 통합 시스템입니다.

## 📋 목차

- [시스템 개요](#시스템-개요)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 실행](#설치-및-실행)
- [데이터베이스 설정](#데이터베이스-설정)
- [API 문서](#api-문서)
- [플랫폼별 수집기](#플랫폼별-수집기)
- [사용 예시](#사용-예시)
- [문제 해결](#문제-해결)
- [기여 가이드](#기여-가이드)

## 🎯 시스템 개요

이 시스템은 다음과 같은 플랫폼에서 데이터를 수집합니다:

- **강남언니**: 성형 관련 게시글, 후기, 댓글
- **바비톡**: 시술후기, 발품후기, 자유톡, 댓글
- **네이버**: 카페 게시글, 댓글

### 주요 기능

- 🔄 **자동화된 데이터 수집**: 스케줄링 및 실시간 수집
- 📊 **통합 데이터 관리**: SQLite 기반 중앙 집중식 저장
- 🎯 **정확한 날짜 필터링**: 요청한 날짜에 맞는 데이터만 수집
- 💬 **댓글 자동 수집**: 게시글과 함께 댓글도 자동으로 수집
- 🚨 **오류 처리 및 복구**: 404 오류 시 자동 재시도 및 복구
- 📝 **상세한 로깅**: 파일 기반 로깅 시스템

## 🛠️ 기술 스택

- **Backend**: FastAPI (Python 3.8+)
- **Database**: SQLite3
- **HTTP Client**: aiohttp, requests
- **HTML Parsing**: BeautifulSoup4
- **Logging**: Python logging module
- **Async Support**: asyncio
- **API Documentation**: Swagger/OpenAPI

## 📁 프로젝트 구조

```
woori_platform_collect/
├── api/                          # FastAPI 애플리케이션
│   ├── main.py                  # 메인 애플리케이션
│   ├── models.py                # Pydantic 모델
│   └── routers/                 # API 라우터
│       ├── data_collection.py   # 데이터 수집 API
│       └── data_viewer.py       # 데이터 조회 API
├── collectors/                   # 데이터 수집기
│   ├── gannamunni_collector.py  # 강남언니 수집기
│   ├── babitalk_collector.py    # 바비톡 수집기
│   └── naver_collector.py       # 네이버 수집기
├── platforms/                    # 플랫폼별 API 클라이언트
│   ├── gannamunni.py           # 강남언니 API
│   ├── babitalk.py             # 바비톡 API
│   └── naver.py                # 네이버 API
├── database/                     # 데이터베이스 관리
│   └── models.py                # 데이터베이스 모델 및 매니저
├── scripts/                      # 유틸리티 스크립트
│   ├── migrate_comments_table.py # 댓글 테이블 마이그레이션
│   ├── add_naver_community.py   # 네이버 커뮤니티 추가
│   └── test_naver_collector.py  # 네이버 수집기 테스트
├── utils/                        # 유틸리티 모듈
│   └── logger.py                # 로깅 시스템
├── data/                         # 데이터 저장소
│   └── collect_data.db          # SQLite 데이터베이스
├── logs/                         # 로그 파일
├── docs/                         # 문서
├── requirements.txt              # Python 의존성
└── run_api.py                   # API 서버 실행 스크립트
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# Python 3.8+ 설치 확인
python --version

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 초기화

```bash
# 네이버 커뮤니티 추가
python scripts/add_naver_community.py

# 댓글 테이블 마이그레이션 (필요시)
python scripts/migrate_comments_table.py
```

### 4. API 서버 실행

```bash
# 개발 모드
python run_api.py

# 또는 직접 실행
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 접속 확인

- **API 서버**: http://localhost:8000
- **Swagger 문서**: http://localhost:8000/docs
- **ReDoc 문서**: http://localhost:8000/redoc

## 🗄️ 데이터베이스 설정

### 데이터베이스 구조

#### 1. communities 테이블
```sql
CREATE TABLE communities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
CREATE INDEX idx_communities_name ON communities(name);
```

**현재 등록된 커뮤니티**:
- **ID 1**: 바비톡 - 바비톡 시술 후기 커뮤니티
- **ID 2**: 강남언니 - 강남언니 커뮤니티  
- **ID 3**: 네이버 - 네이버 카페 데이터 수집을 위한 커뮤니티

**기본 데이터**:
- ID 1: 강남언니
- ID 2: 바비톡
- ID 3: 네이버

#### 2. articles 테이블
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_id TEXT NOT NULL,           -- 'gangnamunni', 'babitalk', 'naver'
    community_article_id TEXT NOT NULL,  -- 플랫폼별 게시글 ID
    community_id INTEGER NOT NULL,       -- 커뮤니티 ID
    title TEXT,                          -- 게시글 제목
    content TEXT NOT NULL,               -- 게시글 내용
    images TEXT,                         -- 이미지 정보 (JSON)
    writer_nickname TEXT NOT NULL,       -- 작성자 닉네임
    writer_id TEXT NOT NULL,             -- 작성자 ID
    like_count INTEGER DEFAULT 0,        -- 좋아요 수
    comment_count INTEGER DEFAULT 0,     -- 댓글 수
    view_count INTEGER DEFAULT 0,        -- 조회수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 게시글 생성일
    category_name TEXT,                  -- 카테고리명
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 수집 시간
    FOREIGN KEY (community_id) REFERENCES communities (id),
    UNIQUE(platform_id, community_article_id)
);
CREATE INDEX idx_articles_community_id ON articles(community_id);
CREATE INDEX idx_articles_created_at ON articles(created_at);
```

#### 3. comments 테이블
```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,         -- 게시글 ID (articles 테이블의 id)
    content TEXT NOT NULL,               -- 댓글 내용
    writer_nickname TEXT NOT NULL,       -- 작성자 닉네임
    writer_id TEXT NOT NULL,             -- 작성자 ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 댓글 생성일
    parent_comment_id INTEGER,           -- 부모 댓글 ID (대댓글)
    collected_at TIMESTAMP,              -- 수집 시간
    FOREIGN KEY (article_id) REFERENCES articles (id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments (id)
);
CREATE INDEX idx_comments_article_id ON comments(article_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_comment_id);
```

#### 4. reviews 테이블
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_id TEXT NOT NULL,           -- 플랫폼 ID (gangnamunni, babitalk)
    platform_review_id TEXT NOT NULL,    -- 플랫폼별 후기 ID
    community_id INTEGER NOT NULL,       -- 커뮤니티 ID
    title TEXT,                          -- 후기 제목
    content TEXT NOT NULL,               -- 후기 내용
    images TEXT,                         -- 이미지 정보 (JSON)
    writer_nickname TEXT NOT NULL,       -- 작성자 닉네임
    writer_id TEXT NOT NULL,             -- 작성자 ID
    like_count INTEGER DEFAULT 0,        -- 좋아요 수
    rating INTEGER DEFAULT 0,            -- 평점
    price INTEGER DEFAULT 0,             -- 가격
    categories TEXT,                     -- 카테고리 (JSON)
    sub_categories TEXT,                 -- 서브 카테고리 (JSON)
    surgery_date TEXT,                   -- 수술 날짜
    hospital_name TEXT,                  -- 병원명
    doctor_name TEXT,                    -- 담당의명
    is_blind BOOLEAN DEFAULT FALSE,      -- 블라인드 여부
    is_image_blur BOOLEAN DEFAULT FALSE, -- 이미지 블러 여부
    is_certificated_review BOOLEAN DEFAULT FALSE, -- 인증 후기 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 후기 생성일
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 수집 시간
    FOREIGN KEY (community_id) REFERENCES communities (id),
    UNIQUE(platform_id, platform_review_id)
);
CREATE INDEX idx_reviews_platform_id ON reviews(platform_id);
CREATE INDEX idx_reviews_platform_review_id ON reviews(platform_review_id);
CREATE INDEX idx_reviews_community_id ON reviews(community_id);
CREATE INDEX idx_reviews_created_at ON reviews(created_at);
```

### 마이그레이션 스크립트

#### 1. 네이버 커뮤니티 추가
```bash
python scripts/add_naver_community.py
```

#### 2. 댓글 테이블 구조 변경
```bash
python scripts/migrate_comments_table.py
```

### 주요 변경사항

#### comments 테이블 구조 변경
- **이전**: `platform_id`, `community_article_id`, `community_comment_id` 필드 사용
- **현재**: `article_id` 필드로 단순화 (articles 테이블의 id 참조)
- **이유**: 기존 데이터베이스 구조와의 호환성 유지

#### 외래키 관계
- `comments.article_id` → `articles.id`
- `comments.parent_comment_id` → `comments.id` (대댓글)
- `articles.community_id` → `communities.id`
- `reviews.community_id` → `communities.id`
- `excluded_articles.client_id` → `clients.id`
- `excluded_articles.article_id` → `articles.id`

#### 인덱스 정보
- **communities**: `idx_communities_name` (name 필드)
- **articles**: `idx_articles_community_id`, `idx_articles_created_at`
- **comments**: `idx_comments_article_id`, `idx_comments_parent_id`
- **reviews**: `idx_reviews_platform_id`, `idx_reviews_platform_review_id`, `idx_reviews_community_id`, `idx_reviews_created_at`

## 📡 API 문서

### 기본 URL
- **Base URL**: `http://localhost:8000/api/v1`

### 1. 데이터 수집 API

#### 강남언니 데이터 수집
```http
POST /collection/collect/gannamunni
```

**요청 본문**:
```json
{
    "category": "article",
    "limit": 20,
    "target_date": "2025-08-15"
}
```

**카테고리 옵션**:
- `article`: 일반 게시글
- `review`: 후기 게시글

#### 바비톡 데이터 수집
```http
POST /collection/collect/babitalk
```

**요청 본문**:
```json
{
    "category": "surgery_review",
    "limit": 20,
    "target_date": "2025-08-15"
}
```

**카테고리 옵션**:
- `surgery_review`: 시술후기
- `event_ask_memo`: 발품후기
- `talk`: 자유톡 (댓글 자동 수집)

#### 네이버 데이터 수집
```http
POST /collection/collect/naver
```

**요청 본문**:
```json
{
    "cafe_id": "12285441",
    "target_date": "2025-08-15",
    "menu_id": "38",
    "limit": 20,
    "cookies": ""
}
```

**기본값**:
- `cafe_id`: "12285441" (A+여우야★성형카페)
- `target_date`: 오늘 날짜
- `menu_id`: "38"
- `limit`: 20
- `cookies`: 빈 값

**특별 기능**:
- `limit = 0`: 해당 날짜의 모든 게시글 수집 (제한 없음)
- `limit > 0`: 지정된 수만큼만 수집

### 2. 데이터 조회 API

#### 게시글 목록 조회
```http
GET /viewer/articles?platform_id=naver&limit=20&offset=0
```

#### 댓글 목록 조회
```http
GET /viewer/comments?platform_id=naver&limit=20&offset=0
```

#### 통계 조회
```http
GET /viewer/statistics/summary
```

### 3. 게시판 정보 API

#### 네이버 게시판 목록
```http
GET /boards/naver/{cafe_id}
```

#### 네이버 게시판 내용
```http
GET /content/naver/{cafe_id}?menu_id=38&per_page=20
```

## 🔌 플랫폼별 수집기

### 1. 강남언니 수집기

**특징**:
- 404 오류 시 15분 대기 후 재시도
- 게시글과 댓글 동시 수집
- 수집 시간 자동 기록

**지원 카테고리**:
- 일반 게시글
- 후기 게시글

### 2. 바비톡 수집기

**특징**:
- 시술후기, 발품후기, 자유톡 통합 수집
- 자유톡 수집 시 댓글 자동 수집
- 페이지네이션 자동 처리 (50개 초과 시 2페이지까지)

**지원 카테고리**:
- `surgery_review`: 시술후기
- `event_ask_memo`: 발품후기
- `talk`: 자유톡

### 3. 네이버 수집기

**특징**:
- 날짜별 정확한 필터링
- 댓글 자동 수집
- 쿠키 기반 인증 지원
- 게시판별 수집 지원

**지원 카페**:
- 여우야 (10912875)
- A+여우야 (12285441) - 기본값
- 성형위키백과 (11498714)
- 여생남정 (13067396)
- 시크먼트 (23451561)
- 가아사 (15880379)
- 파우더룸 (10050813)

## 💡 사용 예시

### 1. 네이버 오늘 게시글 수집

```bash
curl -X POST "http://localhost:8000/api/v1/collection/collect/naver" \
  -H "Content-Type: application/json" \
  -d '{
    "cafe_id": "12285441",
    "target_date": "2025-08-15",
    "limit": 20
  }'
```

### 2. 바비톡 시술후기 수집

```bash
curl -X POST "http://localhost:8000/api/v1/collection/collect/babitalk" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "surgery_review",
    "limit": 50
  }'
```

### 3. 강남언니 후기 수집

```bash
curl -X POST "http://localhost:8000/api/v1/collection/collect/gannamunni" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "review",
    "limit": 30
  }'
```

## 🔧 문제 해결

### 1. 일반적인 문제

#### 데이터베이스 연결 오류
```bash
# 데이터베이스 파일 권한 확인
ls -la data/collect_data.db

# 데이터베이스 파일 재생성
rm data/collect_data.db
python -c "from database.models import DatabaseManager; DatabaseManager()"
```

#### 댓글 저장 오류
```bash
# 댓글 테이블 마이그레이션 실행
python scripts/migrate_comments_table.py
```

#### 네이버 커뮤니티 ID 오류
```bash
# 네이버 커뮤니티 추가
python scripts/add_naver_community.py
```

### 2. 로그 확인

```bash
# 최신 로그 확인
tail -f logs/$(date +%Y-%m-%d).log

# 특정 플랫폼 로그 확인
grep "naver" logs/$(date +%Y-%m-%d).log
```

### 3. 데이터베이스 상태 확인

```bash
# SQLite 접속
sqlite3 data/collect_data.db

# 테이블 상태 확인
.tables
.schema articles
SELECT COUNT(*) FROM articles WHERE platform_id = 'naver';
```

## 🤝 기여 가이드

### 1. 개발 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd woori_platform_collect

# 가상환경 생성
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 개발 의존성 설치
pip install -r requirements-dev.txt
```

### 2. 코드 스타일

- **Python**: PEP 8 준수
- **문서화**: 모든 함수와 클래스에 docstring 작성
- **로깅**: 적절한 로그 레벨 사용
- **에러 처리**: 구체적인 예외 처리

### 3. 테스트

```bash
# 단위 테스트 실행
python -m pytest tests/

# 특정 테스트 실행
python -m pytest tests/test_naver_collector.py -v
```

### 4. 커밋 메시지

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 업데이트
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 프로세스 또는 보조 도구 변경
```

## 📞 지원 및 문의

### 문제 신고
- GitHub Issues를 통해 버그 리포트
- 상세한 오류 로그와 함께 문제 상황 설명

### 기능 요청
- 새로운 플랫폼 추가 요청
- 기존 기능 개선 제안
- API 확장 요청

### 기술 지원
- 개발 관련 질문
- 배포 및 운영 관련 문의
- 성능 최적화 가이드

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

- FastAPI 커뮤니티
- SQLite 개발팀
- 각 플랫폼의 API 제공자

---

**마지막 업데이트**: 2025년 8월 15일
**버전**: 1.0.0
