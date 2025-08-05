# 데이터 수집 플랫폼 API 서버

강남언니, 바비톡 등 다양한 플랫폼의 데이터를 수집하고 관리하는 RESTful API 서버입니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. API 서버 실행

```bash
python run_api.py
```

또는 직접 uvicorn으로 실행:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. API 문서 확인

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health

## 📚 API 엔드포인트

### 데이터 수집 API

#### 1. 단일 카테고리 수집
```http
POST /api/v1/collection/collect
```

**요청 예시:**
```json
{
  "platform": "gangnamunni",
  "category": "hospital_question",
  "target_date": "2025-01-15",
  "save_as_reviews": false,
  "limit": 24
}
```

#### 2. 배치 수집 (전체 카테고리)
```http
POST /api/v1/collection/collect/batch
```

**요청 예시:**
```json
{
  "platform": "babitalk",
  "target_date": "2025-01-15",
  "save_as_reviews": true,
  "limit": 24
}
```

#### 3. 수집 상태 확인
```http
GET /api/v1/collection/status
```

### 데이터 조회 API

#### 1. 게시글 목록 조회
```http
GET /api/v1/data/articles?platform=gangnamunni&page=1&limit=20
```

#### 2. 후기 목록 조회
```http
GET /api/v1/data/reviews?platform=babitalk&page=1&limit=20
```

#### 3. 댓글 목록 조회
```http
GET /api/v1/data/comments?article_id=123&page=1&limit=20
```

#### 4. 특정 게시글 조회
```http
GET /api/v1/data/articles/{article_id}
```

#### 5. 특정 후기 조회
```http
GET /api/v1/data/reviews/{review_id}
```

#### 6. 게시글의 댓글 조회
```http
GET /api/v1/data/articles/{article_id}/comments
```

### 통계 API

#### 1. 전체 통계
```http
GET /api/v1/statistics/overview
```

#### 2. 플랫폼별 통계
```http
GET /api/v1/statistics/platform/{platform}
```

#### 3. 일별 통계
```http
GET /api/v1/statistics/daily?date=2025-01-15
```

#### 4. 트렌드 통계
```http
GET /api/v1/statistics/trends?days=7
```

## 🔧 환경 변수

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `API_HOST` | `0.0.0.0` | 서버 호스트 |
| `API_PORT` | `8000` | 서버 포트 |
| `API_RELOAD` | `true` | 자동 재시작 여부 |
| `API_LOG_LEVEL` | `info` | 로그 레벨 |
| `DB_PATH` | `test_collect_data.db` | 데이터베이스 파일 경로 |

## 📋 지원하는 플랫폼 및 카테고리

### 강남언니 (gangnamunni)
- `hospital_question`: 병원질문
- `surgery_question`: 시술/수술질문
- `free_chat`: 자유수다
- `review`: 발품후기
- `ask_doctor`: 의사에게 물어보세요

### 바비톡 (babitalk)
- `surgery_review`: 시술후기
- `event_ask_memo`: 발품후기
- `talk`: 자유톡

## 🔍 응답 형식

### 성공 응답
```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### 에러 응답
```json
{
  "error": "Internal Server Error",
  "message": "데이터베이스 연결 실패",
  "timestamp": "2025-01-15T10:30:00"
}
```

## 🛠️ 개발

### 프로젝트 구조
```
api/
├── main.py              # FastAPI 앱 메인
├── dependencies.py      # 의존성 주입
├── models.py           # Pydantic 모델
└── routers/
    ├── data_collection.py  # 데이터 수집 API
    ├── data_viewer.py      # 데이터 조회 API
    └── statistics.py       # 통계 API
```

### 새로운 엔드포인트 추가

1. `api/models.py`에 요청/응답 모델 추가
2. `api/routers/`에 해당 라우터 추가
3. `api/main.py`에 라우터 등록

## 🔒 보안

현재 버전은 개발용으로 CORS가 모든 도메인에 대해 허용되어 있습니다. 프로덕션 환경에서는 다음을 고려하세요:

- CORS 설정 제한
- 인증/인가 추가
- Rate Limiting 적용
- HTTPS 사용

## 📝 로그

API 서버는 다음 로그를 제공합니다:

- **Access Log**: HTTP 요청/응답 로그
- **Application Log**: 애플리케이션 로그
- **Error Log**: 에러 로그

## 🚀 배포

### Docker 사용
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 시스템 서비스로 등록
```bash
# systemd 서비스 파일 생성
sudo nano /etc/systemd/system/data-collector-api.service
```

```ini
[Unit]
Description=Data Collector API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 활성화 및 시작
sudo systemctl enable data-collector-api
sudo systemctl start data-collector-api
``` 