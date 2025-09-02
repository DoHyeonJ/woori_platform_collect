# 키워드 검색 API 가이드

## 개요

키워드 검색 API는 수집된 게시글, 댓글, 후기 데이터에서 특정 키워드를 검색할 수 있는 통합 검색 기능을 제공합니다.

## API 엔드포인트

```
GET /api/v1/data/search
```

## 요청 파라미터

### 필수 파라미터

| 파라미터 | 타입 | 설명 | 예시 |
|---------|------|------|------|
| `keywords` | string | 검색할 키워드들 (콤마로 구분) | `"성형,눈,코"` |

### 선택 파라미터

| 파라미터 | 타입 | 기본값 | 설명 | 예시 |
|---------|------|--------|------|------|
| `platforms` | string | null | 플랫폼 필터 (콤마로 구분) | `"gangnamunni,babitalk"` |
| `data_types` | string | null | 데이터 타입 필터 (콤마로 구분) | `"article,comment,review"` |
| `start_date` | string | null | 검색 시작 날짜 (YYYY-MM-DD) | `"2024-01-01"` |
| `end_date` | string | null | 검색 종료 날짜 (YYYY-MM-DD) | `"2024-12-31"` |
| `page` | integer | 1 | 페이지 번호 (1 이상) | `1` |
| `limit` | integer | 20 | 페이지당 데이터 수 (1-1000) | `50` |

### 지원되는 플랫폼

- `gangnamunni` - 강남언니
- `babitalk` - 바비톡
- `babitalk_talk` - 바비톡 자유톡
- `babitalk_event_ask` - 바비톡 발품후기
- `naver` - 네이버 카페

### 지원되는 데이터 타입

- `article` - 게시글
- `comment` - 댓글
- `review` - 후기

## 요청 예시

### 1. 기본 키워드 검색

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형" \
  -H "accept: application/json"
```

### 2. 다중 키워드 검색

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형,눈,코" \
  -H "accept: application/json"
```

### 3. 플랫폼 필터 적용

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형&platforms=gangnamunni,babitalk" \
  -H "accept: application/json"
```

### 4. 날짜 범위 지정

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형&start_date=2024-01-01&end_date=2024-12-31" \
  -H "accept: application/json"
```

### 5. 특정 데이터 타입만 검색

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형&data_types=article,review" \
  -H "accept: application/json"
```

### 6. 모든 필터 조합

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형,눈&platforms=gangnamunni&data_types=article,comment&start_date=2024-01-01&end_date=2024-12-31&page=1&limit=50" \
  -H "accept: application/json"
```

## 응답 형식

### 성공 응답 (200 OK)

```json
{
  "articles": [
    {
      "id": 123,
      "platform_id": "gangnamunni",
      "community_article_id": "12345",
      "community_id": 1,
      "title": "성형 후기입니다",
      "content": "눈 성형을 받았는데 결과가 만족스럽습니다...",
      "writer_nickname": "익명123",
      "writer_id": "user123",
      "like_count": 15,
      "comment_count": 8,
      "view_count": 120,
      "images": "[\"image1.jpg\", \"image2.jpg\"]",
      "created_at": "2024-01-15T10:30:00",
      "category_name": "review",
      "collected_at": "2024-01-15T10:35:00"
    }
  ],
  "comments": [
    {
      "id": 456,
      "platform_id": "gangnamunni",
      "community_article_id": "12345",
      "community_id": 1,
      "comment_id": "comment123",
      "parent_comment_id": null,
      "content": "성형 결과가 정말 좋네요!",
      "writer_nickname": "익명456",
      "writer_id": "user456",
      "like_count": 3,
      "created_at": "2024-01-15T11:00:00",
      "collected_at": "2024-01-15T11:05:00"
    }
  ],
  "reviews": [
    {
      "id": 789,
      "platform_id": "babitalk",
      "platform_review_id": "review123",
      "community_id": 2,
      "title": "눈 성형 후기",
      "content": "눈 성형을 받고 만족스러운 결과를 얻었습니다...",
      "writer_nickname": "익명789",
      "writer_id": "user789",
      "like_count": 25,
      "rating": 5,
      "price": 3000000,
      "images": "[\"before.jpg\", \"after.jpg\"]",
      "categories": "[\"눈\"]",
      "sub_categories": "[\"쌍꺼풀\"]",
      "surgery_date": "2024-01-10",
      "hospital_name": "○○성형외과",
      "doctor_name": "김의사",
      "is_blind": false,
      "is_image_blur": false,
      "is_certificated_review": true,
      "created_at": "2024-01-15T09:00:00",
      "collected_at": "2024-01-15T09:05:00"
    }
  ],
  "total_counts": {
    "articles": 150,
    "comments": 300,
    "reviews": 75
  },
  "page": 1,
  "limit": 20,
  "total_pages": 26,
  "has_next": true,
  "has_prev": false,
  "search_info": {
    "keywords": ["성형", "눈"],
    "platforms": ["gangnamunni"],
    "data_types": ["article", "comment", "review"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "total_results": 525,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### 에러 응답

#### 400 Bad Request - 잘못된 요청

```json
{
  "detail": "검색 키워드가 필요합니다."
}
```

```json
{
  "detail": "유효하지 않은 플랫폼: invalid_platform. 유효한 플랫폼: gangnamunni, babitalk, babitalk_talk, babitalk_event_ask, naver"
}
```

```json
{
  "detail": "시작 날짜는 YYYY-MM-DD 형식이어야 합니다."
}
```

#### 500 Internal Server Error - 서버 오류

```json
{
  "detail": "키워드 검색 실패: 데이터베이스 연결 오류"
}
```

## 응답 필드 설명

### 공통 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `articles` | array | 검색된 게시글 목록 |
| `comments` | array | 검색된 댓글 목록 |
| `reviews` | array | 검색된 후기 목록 |
| `total_counts` | object | 타입별 총 개수 |
| `page` | integer | 현재 페이지 번호 |
| `limit` | integer | 페이지당 데이터 수 |
| `total_pages` | integer | 전체 페이지 수 |
| `has_next` | boolean | 다음 페이지 존재 여부 |
| `has_prev` | boolean | 이전 페이지 존재 여부 |
| `search_info` | object | 검색 조건 정보 |

### 게시글 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | integer | 게시글 고유 ID |
| `platform_id` | string | 플랫폼 ID |
| `community_article_id` | string | 커뮤니티 게시글 ID |
| `community_id` | integer | 커뮤니티 ID |
| `title` | string | 게시글 제목 |
| `content` | string | 게시글 내용 |
| `writer_nickname` | string | 작성자 닉네임 |
| `writer_id` | string | 작성자 ID |
| `like_count` | integer | 좋아요 수 |
| `comment_count` | integer | 댓글 수 |
| `view_count` | integer | 조회수 |
| `images` | string | 이미지 JSON 문자열 |
| `created_at` | string | 작성 시간 (ISO 8601) |
| `category_name` | string | 카테고리명 |
| `collected_at` | string | 수집 시간 (ISO 8601) |

### 댓글 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | integer | 댓글 고유 ID |
| `platform_id` | string | 플랫폼 ID |
| `community_article_id` | string | 커뮤니티 게시글 ID |
| `community_id` | integer | 커뮤니티 ID |
| `comment_id` | string | 댓글 ID |
| `parent_comment_id` | string | 부모 댓글 ID (대댓글인 경우) |
| `content` | string | 댓글 내용 |
| `writer_nickname` | string | 작성자 닉네임 |
| `writer_id` | string | 작성자 ID |
| `like_count` | integer | 좋아요 수 |
| `created_at` | string | 작성 시간 (ISO 8601) |
| `collected_at` | string | 수집 시간 (ISO 8601) |

### 후기 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | integer | 후기 고유 ID |
| `platform_id` | string | 플랫폼 ID |
| `platform_review_id` | string | 플랫폼 후기 ID |
| `community_id` | integer | 커뮤니티 ID |
| `title` | string | 후기 제목 |
| `content` | string | 후기 내용 |
| `writer_nickname` | string | 작성자 닉네임 |
| `writer_id` | string | 작성자 ID |
| `like_count` | integer | 좋아요 수 |
| `rating` | integer | 평점 |
| `price` | integer | 가격 |
| `images` | string | 이미지 JSON 문자열 |
| `categories` | string | 카테고리 JSON 문자열 |
| `sub_categories` | string | 하위 카테고리 JSON 문자열 |
| `surgery_date` | string | 수술 날짜 |
| `hospital_name` | string | 병원명 |
| `doctor_name` | string | 담당의명 |
| `is_blind` | boolean | 블라인드 여부 |
| `is_image_blur` | boolean | 이미지 블러 여부 |
| `is_certificated_review` | boolean | 인증 후기 여부 |
| `created_at` | string | 작성 시간 (ISO 8601) |
| `collected_at` | string | 수집 시간 (ISO 8601) |

## 검색 동작 방식

### 키워드 검색

- **게시글**: 제목(`title`)과 내용(`content`)에서 키워드 검색
- **댓글**: 내용(`content`)에서만 키워드 검색 (제목 없음)
- **후기**: 제목(`title`)과 내용(`content`)에서 키워드 검색

### 다중 키워드 처리

- 콤마로 구분된 키워드들은 **OR** 조건으로 처리
- 예: `"성형,눈,코"` → "성형" OR "눈" OR "코"가 포함된 데이터 검색

### 필터 조합

- 모든 필터는 **AND** 조건으로 결합
- 예: `platforms=gangnamunni&data_types=article&start_date=2024-01-01` → 강남언니 플랫폼의 게시글 중 2024년 1월 1일 이후 작성된 것만 검색

## 사용 시나리오

### 1. 특정 병원명 검색

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=나나성형외과&data_types=article,review"
```

### 2. 특정 시술 관련 검색

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=쌍꺼풀,눈매교정&platforms=gangnamunni,babitalk"
```

### 3. 최근 1개월 데이터 검색

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형&start_date=2024-01-01&end_date=2024-01-31"
```

### 4. 특정 플랫폼의 댓글만 검색

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=만족&platforms=gangnamunni&data_types=comment"
```

## 주의사항

1. **키워드 인코딩**: URL에 한글 키워드를 포함할 때는 URL 인코딩이 필요합니다.
   - 예: `"성형"` → `"%EC%84%B1%ED%98%95"`

2. **날짜 형식**: 날짜는 반드시 `YYYY-MM-DD` 형식을 사용해야 합니다.

3. **페이지네이션**: 대용량 데이터 검색 시 `limit` 파라미터로 페이지 크기를 조절하세요.

4. **성능 고려**: 너무 많은 키워드나 넓은 날짜 범위는 검색 성능에 영향을 줄 수 있습니다.

## API 문서

Swagger UI를 통한 인터랙티브 API 문서는 다음 URL에서 확인할 수 있습니다:

```
http://localhost:8000/docs
```

## 지원 및 문의

API 사용 중 문제가 발생하거나 추가 기능이 필요한 경우, 개발팀에 문의해주세요.
