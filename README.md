# 다중 플랫폼 여론모니터링 시스템

여러 커뮤니티 플랫폼의 게시글과 댓글을 수집하고 SQLite 데이터베이스에 저장하여 분석할 수 있는 시스템입니다.

현재 지원 플랫폼:
- **강남언니** (gangnamunni.com)

## 📁 파일 구조

```
woori_platform_collect/
├── gannamunni.py           # 강남언니 API 클래스
├── database/
│   ├── __init__.py          # 데이터베이스 패키지 초기화
│   └── models.py            # 데이터베이스 모델 및 관리자
├── data_collector.py        # 데이터 수집 및 DB 저장 클래스
├── db_viewer.py            # 데이터베이스 뷰어 (대화형)
├── run_collector.py        # 데이터 수집 실행 스크립트
├── migrate_database.py     # 데이터베이스 마이그레이션 스크립트
├── collect_data.db         # SQLite 데이터베이스 파일
└── README.md               # 프로젝트 설명서
```

## 🗄️ 데이터베이스 구조

### 테이블 구조

#### 1. communities (커뮤니티)
- `id`: 고유 ID (PK)
- `name`: 커뮤니티 명칭 (UNIQUE)
- `created_at`: 등록일
- `description`: 설명

#### 2. clients (클라이언트)
- `id`: 고유 ID (PK)
- `hospital_name`: 병원명
- `created_at`: 등록일
- `description`: 설명

#### 3. articles (게시글)
- `id`: 고유 ID (PK)
- `platform_id`: 플랫폼 ID
- `community_article_id`: 커뮤니티 게시글 ID
- `community_id`: 커뮤니티 ID (FK)
- `title`: 제목
- `content`: 내용
- `images`: 이미지 URL (JSON)
- `writer_nickname`: 작성자 닉네임
- `writer_id`: 작성자 ID
- `like_count`: 좋아요 수
- `comment_count`: 댓글 수
- `view_count`: 조회수
- `created_at`: 작성시간
- `category_name`: 카테고리명

#### 4. comments (댓글)
- `id`: 고유 ID (PK)
- `article_id`: 게시글 ID (FK)
- `content`: 내용
- `writer_nickname`: 작성자 닉네임
- `writer_id`: 작성자 ID
- `created_at`: 작성시간
- `parent_comment_id`: 부모 댓글 ID (대댓글용)

#### 5. excluded_articles (제외 게시글)
- `id`: 고유 ID (PK)
- `client_id`: 클라이언트 ID (FK)
- `article_id`: 게시글 ID (FK)
- `created_at`: 등록일

## 📂 수집 카테고리

- **병원질문** (ID: 11)
- **시술/수술질문** (ID: 2)
- **자유수다** (ID: 1)
- **발품후기** (ID: 5)
- **의사에게 물어보세요** (ID: 13)

## 🚀 사용법

### 1. 데이터 수집

```bash
python run_collector.py
```

수집 옵션:
- 오늘 데이터 수집
- 어제 데이터 수집
- 특정 날짜 데이터 수집
- 최근 7일 데이터 수집

### 2. 데이터베이스 뷰어

```bash
python db_viewer.py
```

뷰어 기능:
- 📊 전체 통계 보기
- 📋 최근 게시글 보기
- 📅 특정 날짜 게시글 보기
- 📂 카테고리별 게시글 보기
- 📝 게시글 상세 보기
- 🔍 게시글 검색
- 📊 일별 요약 보기

### 3. 데이터베이스 마이그레이션

```bash
python migrate_database.py
```

마이그레이션 옵션:
- 기존 데이터베이스 백업 후 초기화
- 기존 데이터베이스 삭제 후 초기화 (백업 없음)
- 취소

### 4. 프로그래밍 방식 사용

```python
from data_collector import DataCollector
from db_viewer import DatabaseViewer

# 데이터 수집
collector = DataCollector()
categories = {
    "hospital_question": "병원질문",
    "surgery_question": "시술/수술질문",
    "free_chat": "자유수다",
    "review": "발품후기",
    "ask_doctor": "의사에게 물어보세요"
}

# 특정 날짜 데이터 수집
articles_count, comments_count = await collector.collect_and_save_articles("2025-08-03", categories)

# 통계 조회
stats = collector.get_statistics()
print(f"전체 게시글: {stats['total_articles']}개")

# 데이터베이스 뷰어
viewer = DatabaseViewer()
viewer.show_statistics()
viewer.show_articles_by_date("2025-08-03")
```

## 📊 주요 기능

### 데이터 수집
- ✅ 모든 카테고리 자동 수집
- ✅ 게시글과 댓글 동시 수집
- ✅ 대댓글 지원
- ✅ 중복 게시글 방지
- ✅ 에러 처리 및 재시도

### 데이터 저장
- ✅ SQLite 데이터베이스 사용
- ✅ 인덱스 최적화
- ✅ 외래키 제약조건
- ✅ JSON 형태 이미지 저장

### 데이터 조회
- ✅ 날짜별 조회
- ✅ 카테고리별 조회
- ✅ 키워드 검색
- ✅ 통계 정보
- ✅ 상세 정보 조회

## 🔧 설치 및 설정

### 필수 패키지

```bash
pip install aiohttp
```

### 데이터베이스 초기화

데이터베이스는 자동으로 생성되며, `collect_data.db` 파일이 생성됩니다.

기존 데이터베이스를 초기화하려면:
```bash
python migrate_database.py
```

## 📈 성능 최적화

- **비동기 처리**: aiohttp를 사용한 비동기 API 호출
- **인덱스**: 자주 조회되는 컬럼에 인덱스 생성
- **중복 방지**: UNIQUE 제약조건으로 중복 데이터 방지
- **배치 처리**: 페이지 단위로 데이터 수집

## 🛡️ 에러 처리

- API 호출 실패 시 재시도
- 댓글 수집 실패 시 게시글 수집은 계속 진행
- 데이터베이스 연결 오류 처리
- 잘못된 날짜 형식 검증

## 📝 로그 및 모니터링

- 수집 진행 상황 실시간 출력
- 카테고리별 수집 결과 표시
- 에러 메시지 상세 출력
- 통계 정보 자동 생성

## 🔄 확장 가능성

- 다른 플랫폼 추가 가능 (현재 강남언니 지원)
- 추가 카테고리 지원
- 실시간 모니터링 기능
- 웹 인터페이스 추가
- 데이터 내보내기 기능
- 다중 플랫폼 통합 분석

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요. 