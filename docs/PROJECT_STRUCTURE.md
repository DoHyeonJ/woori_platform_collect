# 프로젝트 구조

## 📁 디렉토리 구조

```
woori_platform_collect/
├── api/                          # FastAPI 관련 파일들
│   ├── __init__.py
│   ├── main.py                   # FastAPI 앱 메인 파일
│   ├── models.py                 # API 요청/응답 모델
│   ├── dependencies.py           # 의존성 주입
│   └── routers/                  # API 라우터들
│       ├── __init__.py
│       ├── data_collection.py    # 데이터 수집 API
│       ├── data_viewer.py        # 데이터 조회 API
│       └── statistics.py         # 통계 API
├── collectors/                   # 데이터 수집기들
│   ├── __init__.py
│   ├── babitalk_collector.py     # 바비톡 데이터 수집기
│   └── gannamunni_collector.py   # 강남언니 데이터 수집기
├── platforms/                    # 플랫폼별 API 클라이언트
│   ├── __init__.py
│   ├── babitalk.py              # 바비톡 API 클라이언트
│   └── gannamunni.py            # 강남언니 API 클라이언트
├── database/                     # 데이터베이스 관련
│   ├── __init__.py
│   └── models.py                # 데이터베이스 모델
├── scripts/                      # 유틸리티 스크립트들
│   ├── __init__.py
│   ├── migrate_database.py      # 데이터베이스 마이그레이션
│   ├── db_viewer.py             # 데이터베이스 조회 도구
│   └── run_collector.py         # 수집기 실행 스크립트
├── data/                         # 데이터 파일들
│   └── collect_data.db          # SQLite 데이터베이스
├── docs/                         # 문서들
│   ├── README.md                # 프로젝트 README
│   ├── README_API.md            # API 문서
│   └── PROJECT_STRUCTURE.md     # 이 파일
├── run_api.py                    # API 서버 실행 스크립트
└── requirements.txt              # Python 의존성 파일
```

## 🔧 주요 컴포넌트

### API 서버 (`api/`)
- **main.py**: FastAPI 앱의 진입점
- **routers/**: API 엔드포인트들을 기능별로 분리
  - `data_collection.py`: 데이터 수집 API
  - `data_viewer.py`: 데이터 조회 API
  - `statistics.py`: 통계 API

### 데이터 수집기 (`collectors/`)
- **babitalk_collector.py**: 바비톡 플랫폼 데이터 수집
- **gannamunni_collector.py**: 강남언니 플랫폼 데이터 수집

### 플랫폼 API (`platforms/`)
- **babitalk.py**: 바비톡 API 클라이언트
- **gannamunni.py**: 강남언니 API 클라이언트

### 데이터베이스 (`database/`)
- **models.py**: SQLAlchemy 모델 정의

### 유틸리티 (`scripts/`)
- **migrate_database.py**: 데이터베이스 스키마 마이그레이션
- **db_viewer.py**: 데이터베이스 내용 조회 도구
- **run_collector.py**: 수집기 실행 스크립트

## 🚀 실행 방법

### API 서버 실행
```bash
python run_api.py
```

### 데이터베이스 마이그레이션
```bash
python scripts/migrate_database.py
```

### 데이터 수집기 실행
```bash
python scripts/run_collector.py
```

## 📊 API 엔드포인트

- **GET /**: API 서버 상태 확인
- **GET /health**: 헬스 체크
- **GET /docs**: Swagger UI 문서
- **GET /redoc**: ReDoc 문서

### 데이터 수집 API
- **POST /api/v1/collection/collect**: 단일 플랫폼 데이터 수집
- **POST /api/v1/collection/collect/batch**: 배치 데이터 수집
- **GET /api/v1/collection/status**: 수집 상태 확인

### 데이터 조회 API
- **GET /api/v1/data/articles**: 게시글 목록 조회
- **GET /api/v1/data/reviews**: 후기 목록 조회
- **GET /api/v1/data/comments**: 댓글 목록 조회

### 통계 API
- **GET /api/v1/statistics/overview**: 전체 통계
- **GET /api/v1/statistics/platforms**: 플랫폼별 통계
- **GET /api/v1/statistics/reviews**: 후기 통계

## 🔄 변경 사항

### 제거된 파일들
- `data_collector.py`: 구버전 수집기 (새로운 collector들로 대체)
- `data/collect_data.db`: 메인 데이터베이스

### 이동된 파일들
- 수집기들: `collectors/` 디렉토리로 이동
- 플랫폼 API들: `platforms/` 디렉토리로 이동
- 데이터베이스: `data/` 디렉토리로 이동
- 문서들: `docs/` 디렉토리로 이동

### 업데이트된 import 경로
- 모든 import 문이 새로운 디렉토리 구조에 맞게 수정됨
- 데이터베이스 경로가 `data/collect_data.db`로 변경됨 