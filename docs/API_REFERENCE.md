# 📡 API 상세 참조 문서

이 문서는 우리 플랫폼 데이터 수집 시스템의 모든 API 엔드포인트에 대한 상세한 설명을 제공합니다.

## 📋 목차

- [기본 정보](#기본-정보)
- [인증](#인증)
- [데이터 수집 API](#데이터-수집-api)
- [데이터 조회 API](#데이터-조회-api)
- [비동기 수집 API](#비동기-수집-api)
- [게시판 정보 API](#게시판-정보-api)
- [응답 코드](#응답-코드)
- [에러 처리](#에러-처리)
- [제한 사항](#제한-사항)

## 🌐 기본 정보

- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **API 버전**: v1
- **문서**: Swagger UI (`/docs`), ReDoc (`/redoc`)

## 🔐 인증

현재 버전에서는 인증이 필요하지 않습니다. 모든 API는 공개적으로 접근 가능합니다.

## 📚 관련 문서

- [API 사용 가이드](./API_USAGE_GUIDE.md) - 상세한 사용법과 예시
- [API 상세 참조](./API_REFERENCE_DETAILED.md) - 완전한 API 스펙
- [빠른 시작 가이드](./QUICK_START_GUIDE.md) - 빠른 시작 방법

## 📥 데이터 수집 API

### 1. 강남언니 데이터 수집

#### 엔드포인트
```http
POST /collection/collect/gannamunni
```

#### 설명
강남언니 플랫폼에서 게시글과 댓글을 수집합니다.

#### 요청 본문
```json
{
    "category": "article",
    "limit": 20,
    "target_date": "2025-08-15"
}
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `category` | string | ✅ | - | 수집할 카테고리 |
| `limit` | integer | ❌ | 20 | 수집할 게시글 수 (1-100) |
| `target_date` | string | ❌ | 오늘 | 수집할 날짜 (YYYY-MM-DD) |

#### 카테고리 옵션

| 값 | 설명 |
|----|------|
| `article` | 일반 게시글 |
| `review` | 후기 게시글 |

#### 응답 예시
```json
{
    "platform": "gangnamunni",
    "category": "article",
    "target_date": "2025-08-15",
    "total_articles": 15,
    "total_comments": 45,
    "total_reviews": 0,
    "execution_time": 12.5,
    "status": "success",
    "message": "강남언니 일반 게시글 수집 완료 (게시글: 15개, 댓글: 45개)",
    "timestamp": "2025-08-15T10:30:00"
}
```

---

### 2. 바비톡 데이터 수집

#### 엔드포인트
```http
POST /collection/collect/babitalk
```

#### 설명
바비톡 플랫폼에서 시술후기, 발품후기, 자유톡을 수집합니다. 자유톡 수집 시 댓글도 자동으로 수집됩니다.

#### 요청 본문
```json
{
    "category": "surgery_review",
    "limit": 50,
    "target_date": "2025-08-15"
}
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `category` | string | ✅ | - | 수집할 카테고리 |
| `limit` | integer | ❌ | 20 | 수집할 게시글 수 (1-100) |
| `target_date` | string | ❌ | 오늘 | 수집할 날짜 (YYYY-MM-DD) |

#### 카테고리 옵션

| 값 | 설명 | 댓글 수집 |
|----|------|-----------|
| `surgery_review` | 시술후기 | ❌ |
| `event_ask_memo` | 발품후기 | ❌ |
| `talk` | 자유톡 | ✅ (자동) |

#### 응답 예시
```json
{
    "platform": "babitalk",
    "category": "talk",
    "target_date": "2025-08-15",
    "total_articles": 30,
    "total_comments": 120,
    "total_reviews": 0,
    "execution_time": 25.3,
    "status": "success",
    "message": "바비톡 자유톡 수집 완료 (게시글: 30개, 댓글: 120개)",
    "timestamp": "2025-08-15T10:30:00"
}
```

---

### 3. 네이버 데이터 수집

#### 엔드포인트
```http
POST /collection/collect/naver
```

#### 설명
네이버 카페에서 게시글과 댓글을 수집합니다. 날짜별 정확한 필터링을 지원하며, 댓글도 자동으로 수집됩니다.

#### 요청 본문
```json
{
    "cafe_id": "12285441",
    "target_date": "2025-08-15",
    "menu_id": "38",
    "limit": 20,
    "cookies": ""
}
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `cafe_id` | string | ❌ | "12285441" | 카페 ID |
| `target_date` | string | ❌ | 오늘 | 수집할 날짜 (YYYY-MM-DD) |
| `menu_id` | string | ❌ | "38" | 특정 게시판 ID |
| `limit` | integer | ❌ | 20 | 수집할 게시글 수 (0: 제한없음, 1-100: 지정된 수) |
| `cookies` | string | ❌ | "" | 네이버 로그인 쿠키 |

#### 지원 카페 ID

| 카페명 | 카페 ID | 설명 |
|--------|---------|------|
| A+여우야★성형카페 | 12285441 | 기본값 |
| 여우야 | 10912875 | - |
| 성형위키백과 | 11498714 | - |
| 여생남정 | 13067396 | - |
| 시크먼트 | 23451561 | - |
| 가아사 | 15880379 | - |
| 파우더룸 | 10050813 | - |

#### 특별 기능

- **`limit = 0`**: 해당 날짜의 모든 게시글을 제한 없이 수집
- **`limit > 0`**: 지정된 수만큼만 수집
- **날짜 필터링**: 정확한 날짜에 맞는 게시글만 수집

#### 응답 예시
```json
{
    "platform": "naver",
    "category": "by_date",
    "target_date": "2025-08-15",
    "total_articles": 25,
    "total_comments": 89,
    "total_reviews": 0,
    "execution_time": 18.7,
    "status": "success",
    "message": "네이버 카페 12285441 2025-08-15 날짜별 전체 수집 완료 (게시글: 25개, 댓글: 89개)",
    "timestamp": "2025-08-15T10:30:00"
}
```

---

## 📤 데이터 조회 API

### 1. 게시글 목록 조회

#### 엔드포인트
```http
GET /data/articles
```

#### 설명
수집된 게시글 목록을 페이지네이션과 함께 조회합니다.

#### 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `platform` | string | ❌ | - | 플랫폼 필터 (babitalk_talk, gangnamunni, naver 등) |
| `category` | string | ❌ | - | 카테고리 필터 |
| `page` | integer | ❌ | 1 | 페이지 번호 (≥1) |
| `limit` | integer | ❌ | 20 | 페이지당 데이터 수 (1-100) |

#### 응답 예시
```json
{
    "data": [
        {
            "id": 1,
            "platform_id": "babitalk_talk",
            "community_article_id": "7388807",
            "community_id": 1,
            "title": "절개+눈교+앞트임 6개월",
            "content": "위버스성형외과 김렬우 원장님께 받았어요...",
            "writer_nickname": "쿼카3yXhq",
            "writer_id": "16876410",
            "like_count": 0,
            "comment_count": 0,
            "view_count": 0,
            "images": "[{\"id\": 0, \"url\": \"https://images.babitalk.com/...\"}]",
            "created_at": "2025-09-01T23:55:29",
            "category_name": "성형",
            "collected_at": "2025-09-02T22:02:06"
        }
    ],
    "total": 1463,
    "page": 1,
    "limit": 20,
    "total_pages": 74,
    "has_next": true,
    "has_prev": false
}
```

### 2. 특정 게시글 조회

#### 엔드포인트
```http
GET /data/articles/{article_id}
```

#### 설명
특정 게시글의 상세 정보를 조회합니다.

#### 경로 파라미터
- `article_id` (integer, 필수): 게시글 ID

---

### 3. 후기 목록 조회

#### 엔드포인트
```http
GET /data/reviews
```

#### 설명
수집된 후기 목록을 페이지네이션과 함께 조회합니다.

#### 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `platform` | string | ❌ | - | 플랫폼 필터 |
| `category` | string | ❌ | - | 카테고리 필터 |
| `page` | integer | ❌ | 1 | 페이지 번호 (≥1) |
| `limit` | integer | ❌ | 20 | 페이지당 데이터 수 (1-100) |

### 4. 특정 후기 조회

#### 엔드포인트
```http
GET /data/reviews/{review_id}
```

#### 설명
특정 후기의 상세 정보를 조회합니다.

#### 경로 파라미터
- `review_id` (integer, 필수): 후기 ID

---

### 5. 댓글 목록 조회

#### 엔드포인트
```http
GET /data/comments
```

#### 설명
수집된 댓글 목록을 페이지네이션과 함께 조회합니다.

#### 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `platform` | string | ❌ | - | 플랫폼 필터 |
| `article_id` | string | ❌ | - | 게시글 ID 필터 (커뮤니티 게시글 ID) |
| `page` | integer | ❌ | 1 | 페이지 번호 (≥1) |
| `limit` | integer | ❌ | 20 | 페이지당 데이터 수 (1-100) |

#### 응답 예시
```json
{
    "data": [
        {
            "id": 220,
            "platform_id": "babitalk_talk",
            "community_article_id": "7388698",
            "community_id": 1,
            "comment_id": "80680379",
            "parent_comment_id": "80674982",
            "content": "댓글 내용...",
            "writer_nickname": "댓글작성자",
            "writer_id": "commenter123",
            "like_count": 0,
            "created_at": "2025-09-01T12:00:00",
            "collected_at": "2025-09-02T22:02:06"
        }
    ],
    "total": 5153,
    "page": 1,
    "limit": 20,
    "total_pages": 258,
    "has_next": true,
    "has_prev": false
}
```

### 6. 특정 댓글 조회

#### 엔드포인트
```http
GET /data/comments/{comment_id}
```

#### 설명
특정 댓글의 상세 정보를 조회합니다.

#### 경로 파라미터
- `comment_id` (integer, 필수): 댓글 ID

---

### 7. 통계 조회

#### 엔드포인트
```http
GET /data/statistics/summary
```

#### 설명
전체 시스템의 통계 정보를 조회합니다.

#### 응답 예시
```json
{
    "total": {
        "articles": 1463,
        "reviews": 0,
        "comments": 5153
    },
    "by_platform": {
        "gangnamunni": {
            "articles": 0,
            "reviews": 0
        },
        "babitalk": {
            "articles": 0,
            "reviews": 0
        }
    },
    "timestamp": "2025-09-02T13:38:15.123456"
}
```

---

## 📋 게시판 정보 API

### 1. 네이버 게시판 목록

#### 엔드포인트
```http
GET /boards/naver/{cafe_id}
```

#### 설명
특정 네이버 카페의 게시판 목록을 조회합니다.

#### 경로 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `cafe_id` | string | ✅ | 카페 ID |

#### 응답 예시
```json
{
    "cafe_id": "12285441",
    "cafe_name": "A+여우야★성형카페",
    "boards": [
        {
            "menu_id": 38,
            "menu_name": "성형후기",
            "menu_type": "B",
            "board_type": "article",
            "sort": 1
        },
        {
            "menu_id": 39,
            "menu_name": "질문과답변",
            "menu_type": "B",
            "board_type": "article",
            "sort": 2
        }
    ]
}
```

---

### 2. 네이버 게시판 내용

#### 엔드포인트
```http
GET /content/naver/{cafe_id}
```

#### 설명
특정 네이버 카페 게시판의 내용을 조회합니다.

#### 경로 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `cafe_id` | string | ✅ | 카페 ID |

#### 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `menu_id` | string | ❌ | - | 특정 게시판 ID |
| `per_page` | integer | ❌ | 20 | 페이지당 게시글 수 |

#### 응답 예시
```json
{
    "cafe_id": "12285441",
    "menu_id": "38",
    "content": "게시글 1:\n제목: 성형 후기 공유합니다\n내용: 안녕하세요...\n\n게시글 2:\n제목: 질문이 있습니다\n내용: 궁금한 점이...",
    "total_articles": 2
}
```

---

## 📊 응답 코드

### HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 |
| 404 | 리소스를 찾을 수 없음 |
| 422 | 유효성 검사 실패 |
| 500 | 내부 서버 오류 |

### 응답 형식

#### 성공 응답
```json
{
    "status": "success",
    "data": { ... },
    "message": "작업이 성공적으로 완료되었습니다"
}
```

#### 에러 응답
```json
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "잘못된 파라미터입니다",
        "details": [
            {
                "field": "limit",
                "message": "limit은 1 이상 100 이하여야 합니다"
            }
        ]
    }
}
```

---

## ⚠️ 에러 처리

### 일반적인 에러

#### 1. 유효성 검사 실패 (422)
```json
{
    "detail": [
        {
            "loc": ["body", "limit"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt",
            "ctx": {"limit_value": 0}
        }
    ]
}
```

#### 2. 내부 서버 오류 (500)
```json
{
    "detail": "데이터 수집 실패: 네트워크 연결 오류"
}
```

#### 3. 리소스 없음 (404)
```json
{
    "detail": "요청한 리소스를 찾을 수 없습니다"
}
```

### 에러 해결 방법

#### 유효성 검사 오류
- 요청 본문의 파라미터 타입과 범위 확인
- 필수 파라미터 누락 여부 확인

#### 네트워크 오류
- 인터넷 연결 상태 확인
- 대상 플랫폼 서버 상태 확인
- API 호출 빈도 조절

#### 데이터베이스 오류
- 데이터베이스 파일 권한 확인
- 마이그레이션 스크립트 실행 여부 확인

---

## 🚫 제한 사항

### API 호출 제한

| 플랫폼 | 초당 요청 수 | 일일 요청 수 | 비고 |
|--------|-------------|-------------|------|
| 강남언니 | 5 | 1000 | 404 오류 시 15분 대기 |
| 바비톡 | 3 | 500 | 댓글 50개 초과 시 2페이지까지 |
| 네이버 | 2 | 200 | 쿠키 필요 시 인증 필수 |

### 데이터 크기 제한

| 항목 | 제한 | 설명 |
|------|------|------|
| 게시글 제목 | 500자 | 초과 시 자동 잘림 |
| 게시글 내용 | 10,000자 | 초과 시 자동 잘림 |
| 댓글 내용 | 1,000자 | 초과 시 자동 잘림 |
| 이미지 URL | 100개 | 초과 시 자동 잘림 |

### 파일 업로드 제한

현재 버전에서는 파일 업로드를 지원하지 않습니다.

---

## 🔄 버전 관리

### API 버전 정책

- **v1**: 현재 안정 버전
- **v2**: 향후 주요 업데이트 예정
- **v0.x**: 개발/테스트 버전

### 하위 호환성

- 기존 API 엔드포인트는 변경되지 않음
- 새로운 파라미터는 선택적으로 추가
- 응답 형식은 기존 구조 유지

---

## 📞 지원 및 문의

### 기술 지원
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **문서**: 이 문서와 README.md 참조
- **예시 코드**: 각 API별 사용 예시 제공

### 개발자 리소스
- **Swagger UI**: `/docs`에서 인터랙티브 API 테스트
- **ReDoc**: `/redoc`에서 읽기 쉬운 API 문서
- **OpenAPI 스펙**: `/openapi.json`에서 기계 읽기 가능한 스펙

---

## 📊 현재 데이터 현황

- **전체 게시글**: 1,463개 (모두 `babitalk_talk`)
- **전체 댓글**: 5,153개 (모두 `babitalk_talk`)
- **전체 후기**: 0개

## 🔗 관련 링크

- [API 사용 가이드](./API_USAGE_GUIDE.md) - 상세한 사용법과 예시
- [API 상세 참조](./API_REFERENCE_DETAILED.md) - 완전한 API 스펙
- [빠른 시작 가이드](./QUICK_START_GUIDE.md) - 빠른 시작 방법
- [비동기 수집 가이드](./ASYNC_COLLECTION_GUIDE.md) - 백그라운드 수집 방법

---

**마지막 업데이트**: 2025년 9월 2일  
**API 버전**: v1.0.0  
**문서 버전**: 1.1.0
