# API 상세 참조 문서

이 문서는 우리 플랫폼 수집 API의 상세한 스펙을 제공합니다.

## 기본 정보

- **Base URL**: `http://localhost:8000/api/v1/data`
- **API 버전**: v1
- **Content-Type**: `application/json`
- **인증**: 현재 인증이 필요하지 않음

## 데이터 모델

### Article (게시글)
```json
{
  "id": 1,
  "platform_id": "babitalk_talk",
  "community_article_id": "7388807",
  "community_id": 1,
  "title": "게시글 제목",
  "content": "게시글 내용",
  "writer_nickname": "작성자 닉네임",
  "writer_id": "작성자 ID",
  "like_count": 0,
  "comment_count": 0,
  "view_count": 0,
  "images": "[{\"id\": 0, \"url\": \"이미지 URL\"}]",
  "created_at": "2025-09-01T23:55:29",
  "category_name": "카테고리명",
  "collected_at": "2025-09-02T22:02:06"
}
```

### Review (후기)
```json
{
  "id": 1,
  "platform_id": "babitalk",
  "platform_review_id": "12345",
  "community_id": 1,
  "title": "후기 제목",
  "content": "후기 내용",
  "writer_nickname": "작성자 닉네임",
  "writer_id": "작성자 ID",
  "like_count": 5,
  "rating": 5,
  "price": 2000000,
  "images": "[]",
  "categories": "카테고리",
  "sub_categories": "하위 카테고리",
  "surgery_date": "2025-01-01",
  "hospital_name": "병원명",
  "doctor_name": "의사명",
  "is_blind": false,
  "is_image_blur": false,
  "is_certificated_review": true,
  "created_at": "2025-09-01T10:00:00",
  "collected_at": "2025-09-02T22:02:06"
}
```

### Comment (댓글)
```json
{
  "id": 220,
  "platform_id": "babitalk_talk",
  "community_article_id": "7388698",
  "community_id": 1,
  "comment_id": "80680379",
  "parent_comment_id": "80674982",
  "content": "댓글 내용",
  "writer_nickname": "댓글작성자",
  "writer_id": "commenter123",
  "like_count": 0,
  "created_at": "2025-09-01T12:00:00",
  "collected_at": "2025-09-02T22:02:06"
}
```

### PaginatedResponse (페이지네이션 응답)
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

## 엔드포인트 상세

### GET /articles

게시글 목록을 조회합니다.

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| platform | string | 아니오 | - | 플랫폼 필터 |
| category | string | 아니오 | - | 카테고리 필터 |
| page | integer | 아니오 | 1 | 페이지 번호 (≥1) |
| limit | integer | 아니오 | 20 | 페이지당 데이터 수 (1-100) |

**Platform 값:**
- `babitalk_talk`: 바비톡 자유톡
- `babitalk_event_ask`: 바비톡 발품후기
- `gangnamunni`: 강남언니
- `naver`: 네이버 카페

**응답:**
- **200 OK**: 성공적으로 조회됨
- **422 Unprocessable Entity**: 잘못된 파라미터
- **500 Internal Server Error**: 서버 오류

**응답 예시:**
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

### GET /articles/{article_id}

특정 게시글을 조회합니다.

**경로 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| article_id | integer | 예 | 게시글 ID |

**응답:**
- **200 OK**: 성공적으로 조회됨
- **404 Not Found**: 게시글을 찾을 수 없음
- **500 Internal Server Error**: 서버 오류

### GET /reviews

후기 목록을 조회합니다.

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| platform | string | 아니오 | - | 플랫폼 필터 |
| category | string | 아니오 | - | 카테고리 필터 |
| page | integer | 아니오 | 1 | 페이지 번호 (≥1) |
| limit | integer | 아니오 | 20 | 페이지당 데이터 수 (1-100) |

**응답:**
- **200 OK**: 성공적으로 조회됨
- **422 Unprocessable Entity**: 잘못된 파라미터
- **500 Internal Server Error**: 서버 오류

### GET /reviews/{review_id}

특정 후기를 조회합니다.

**경로 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| review_id | integer | 예 | 후기 ID |

**응답:**
- **200 OK**: 성공적으로 조회됨
- **404 Not Found**: 후기를 찾을 수 없음
- **500 Internal Server Error**: 서버 오류

### GET /comments

댓글 목록을 조회합니다.

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| platform | string | 아니오 | - | 플랫폼 필터 |
| article_id | string | 아니오 | - | 게시글 ID 필터 (커뮤니티 게시글 ID) |
| page | integer | 아니오 | 1 | 페이지 번호 (≥1) |
| limit | integer | 아니오 | 20 | 페이지당 데이터 수 (1-100) |

**응답:**
- **200 OK**: 성공적으로 조회됨
- **422 Unprocessable Entity**: 잘못된 파라미터
- **500 Internal Server Error**: 서버 오류

**응답 예시:**
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

### GET /comments/{comment_id}

특정 댓글을 조회합니다.

**경로 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| comment_id | integer | 예 | 댓글 ID |

**응답:**
- **200 OK**: 성공적으로 조회됨
- **404 Not Found**: 댓글을 찾을 수 없음
- **500 Internal Server Error**: 서버 오류

### GET /statistics/summary

데이터 수집 통계 요약을 조회합니다.

**응답:**
- **200 OK**: 성공적으로 조회됨
- **500 Internal Server Error**: 서버 오류

**응답 예시:**
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

## 에러 응답

### 400 Bad Request
```json
{
  "detail": "잘못된 요청입니다."
}
```

### 404 Not Found
```json
{
  "detail": "리소스를 찾을 수 없습니다."
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["query", "platform"],
      "msg": "Input should be 'gangnamunni', 'babitalk' or 'naver'",
      "input": "invalid_platform",
      "ctx": {
        "expected": "'gangnamunni', 'babitalk' or 'naver'"
      }
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "서버 내부 오류가 발생했습니다."
}
```

## 데이터 타입 설명

### 날짜/시간
모든 날짜와 시간은 ISO 8601 형식으로 반환됩니다:
- `2025-09-01T23:55:29` (UTC)
- `2025-09-02T22:02:06.123456` (마이크로초 포함)

### 이미지 데이터
`images` 필드는 JSON 문자열로 저장되어 있습니다:
```json
"[{\"id\": 0, \"url\": \"https://example.com/image.jpg\", \"small_url\": \"https://example.com/small_image.jpg\", \"is_after\": false, \"order\": 0, \"is_main\": true, \"is_blur\": true}]"
```

### 플랫폼 ID 매핑
- `babitalk_talk`: 바비톡 자유톡 게시글
- `babitalk_event_ask`: 바비톡 발품후기
- `gangnamunni`: 강남언니 게시글/후기
- `naver`: 네이버 카페 게시글

## 성능 고려사항

1. **페이지네이션**: 대량의 데이터를 조회할 때는 `limit`을 적절히 설정하세요.
2. **필터링**: 필요한 경우 플랫폼이나 카테고리 필터를 사용하여 데이터를 제한하세요.
3. **캐싱**: 동일한 데이터를 반복 조회하는 경우 클라이언트 측에서 캐싱을 고려하세요.

## 제한사항

1. **페이지당 최대 데이터 수**: 100개
2. **페이지 번호**: 1 이상의 정수
3. **플랫폼 필터**: 미리 정의된 값만 허용
4. **인증**: 현재 인증이 필요하지 않음 (향후 추가 예정)

## 버전 관리

현재 API 버전: v1

향후 버전 변경 시:
- URL에 버전 정보 포함: `/api/v2/data/...`
- 하위 호환성 유지
- 변경 사항은 별도 공지

## 지원

API 사용 중 문제가 발생하면:
1. 이 문서의 에러 코드 섹션을 확인하세요.
2. 요청 파라미터가 올바른지 확인하세요.
3. 서버 로그를 확인하세요.
