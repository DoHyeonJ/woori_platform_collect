# API 사용 가이드

이 문서는 우리 플랫폼 수집 API의 사용 방법을 설명합니다.

## 기본 정보

- **Base URL**: `http://localhost:8000/api/v1/data`
- **Content-Type**: `application/json`
- **인증**: 현재 인증이 필요하지 않습니다.

## 공통 응답 형식

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

### 에러 응답
```json
{
  "detail": "오류 메시지"
}
```

## 엔드포인트 목록

### 1. 게시글 조회

#### 1.1 게시글 목록 조회
**GET** `/articles`

게시글 목록을 페이지네이션과 함께 조회합니다.

**쿼리 파라미터:**
- `platform` (선택): 플랫폼 필터
  - `babitalk_talk`: 바비톡 자유톡
  - `babitalk_event_ask`: 바비톡 발품후기
  - `gangnamunni`: 강남언니
  - `naver`: 네이버 카페
- `category` (선택): 카테고리 필터
- `page` (기본값: 1): 페이지 번호 (1 이상)
- `limit` (기본값: 20): 페이지당 데이터 수 (1-100)

**요청 예시:**
```bash
# 전체 게시글 조회
curl -X GET "http://localhost:8000/api/v1/data/articles?page=1&limit=20"

# 바비톡 자유톡 게시글만 조회
curl -X GET "http://localhost:8000/api/v1/data/articles?platform=babitalk_talk&page=1&limit=10"

# 특정 카테고리 게시글 조회
curl -X GET "http://localhost:8000/api/v1/data/articles?category=성형&page=1&limit=20"
```

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

#### 1.2 특정 게시글 조회
**GET** `/articles/{article_id}`

특정 게시글의 상세 정보를 조회합니다.

**경로 파라미터:**
- `article_id` (필수): 게시글 ID (정수)

**요청 예시:**
```bash
curl -X GET "http://localhost:8000/api/v1/data/articles/1"
```

**응답 예시:**
```json
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
```

### 2. 후기 조회

#### 2.1 후기 목록 조회
**GET** `/reviews`

후기 목록을 페이지네이션과 함께 조회합니다.

**쿼리 파라미터:**
- `platform` (선택): 플랫폼 필터
- `category` (선택): 카테고리 필터
- `page` (기본값: 1): 페이지 번호
- `limit` (기본값: 20): 페이지당 데이터 수

**요청 예시:**
```bash
# 전체 후기 조회
curl -X GET "http://localhost:8000/api/v1/data/reviews?page=1&limit=20"

# 바비톡 후기만 조회
curl -X GET "http://localhost:8000/api/v1/data/reviews?platform=babitalk&page=1&limit=10"
```

**응답 예시:**
```json
{
  "data": [
    {
      "id": 1,
      "platform_id": "babitalk",
      "platform_review_id": "12345",
      "community_id": 1,
      "title": "눈 성형 후기",
      "content": "성형 후기 내용...",
      "writer_nickname": "사용자1",
      "writer_id": "user123",
      "like_count": 5,
      "rating": 5,
      "price": 2000000,
      "images": "[]",
      "categories": "눈",
      "sub_categories": "쌍꺼풀",
      "surgery_date": "2025-01-01",
      "hospital_name": "ABC성형외과",
      "doctor_name": "김의사",
      "is_blind": false,
      "is_image_blur": false,
      "is_certificated_review": true,
      "created_at": "2025-09-01T10:00:00",
      "collected_at": "2025-09-02T22:02:06"
    }
  ],
  "total": 0,
  "page": 1,
  "limit": 20,
  "total_pages": 0,
  "has_next": false,
  "has_prev": false
}
```

#### 2.2 특정 후기 조회
**GET** `/reviews/{review_id}`

특정 후기의 상세 정보를 조회합니다.

**경로 파라미터:**
- `review_id` (필수): 후기 ID (정수)

**요청 예시:**
```bash
curl -X GET "http://localhost:8000/api/v1/data/reviews/1"
```

### 3. 댓글 조회

#### 3.1 댓글 목록 조회
**GET** `/comments`

댓글 목록을 페이지네이션과 함께 조회합니다.

**쿼리 파라미터:**
- `platform` (선택): 플랫폼 필터
- `article_id` (선택): 게시글 ID 필터 (커뮤니티 게시글 ID)
- `page` (기본값: 1): 페이지 번호
- `limit` (기본값: 20): 페이지당 데이터 수

**요청 예시:**
```bash
# 전체 댓글 조회
curl -X GET "http://localhost:8000/api/v1/data/comments?page=1&limit=20"

# 바비톡 댓글만 조회
curl -X GET "http://localhost:8000/api/v1/data/comments?platform=babitalk_talk&page=1&limit=10"

# 특정 게시글의 댓글 조회
curl -X GET "http://localhost:8000/api/v1/data/comments?article_id=7388807&page=1&limit=20"
```

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

#### 3.2 특정 댓글 조회
**GET** `/comments/{comment_id}`

특정 댓글의 상세 정보를 조회합니다.

**경로 파라미터:**
- `comment_id` (필수): 댓글 ID (정수)

**요청 예시:**
```bash
curl -X GET "http://localhost:8000/api/v1/data/comments/220"
```

### 4. 통계 조회

#### 4.1 데이터 수집 통계 요약
**GET** `/statistics/summary`

전체 데이터 수집 통계를 조회합니다.

**요청 예시:**
```bash
curl -X GET "http://localhost:8000/api/v1/data/statistics/summary"
```

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

## 사용 예시

### JavaScript (Fetch API)
```javascript
// 게시글 목록 조회
async function getArticles(page = 1, limit = 20, platform = null) {
  const url = new URL('http://localhost:8000/api/v1/data/articles');
  url.searchParams.append('page', page);
  url.searchParams.append('limit', limit);
  if (platform) {
    url.searchParams.append('platform', platform);
  }
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}

// 사용 예시
getArticles(1, 10, 'babitalk_talk').then(data => {
  console.log('게시글 목록:', data);
});
```

### Python (requests)
```python
import requests

def get_articles(page=1, limit=20, platform=None):
    url = 'http://localhost:8000/api/v1/data/articles'
    params = {
        'page': page,
        'limit': limit
    }
    if platform:
        params['platform'] = platform
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return None

# 사용 예시
articles = get_articles(page=1, limit=10, platform='babitalk_talk')
if articles:
    print(f"총 {articles['total']}개의 게시글")
    for article in articles['data']:
        print(f"- {article['title']}")
```

### cURL 예시
```bash
# 바비톡 자유톡 게시글 조회 (첫 5개)
curl -X GET "http://localhost:8000/api/v1/data/articles?platform=babitalk_talk&page=1&limit=5" \
  -H "accept: application/json"

# 특정 게시글의 댓글 조회
curl -X GET "http://localhost:8000/api/v1/data/comments?article_id=7388807&page=1&limit=10" \
  -H "accept: application/json"

# 통계 조회
curl -X GET "http://localhost:8000/api/v1/data/statistics/summary" \
  -H "accept: application/json"
```

## 에러 코드

- **200**: 성공
- **404**: 리소스를 찾을 수 없음
- **422**: 요청 파라미터 오류
- **500**: 서버 내부 오류

## 주의사항

1. **페이지네이션**: 대량의 데이터를 조회할 때는 `limit` 파라미터를 적절히 설정하세요.
2. **플랫폼 ID**: 정확한 플랫폼 ID를 사용하세요 (`babitalk_talk`, `gangnamunni`, `naver` 등).
3. **날짜 형식**: 모든 날짜는 ISO 8601 형식으로 반환됩니다.
4. **이미지 데이터**: `images` 필드는 JSON 문자열로 저장되어 있습니다.

## 현재 데이터 현황

- **전체 게시글**: 1,463개 (모두 `babitalk_talk`)
- **전체 댓글**: 5,153개 (모두 `babitalk_talk`)
- **전체 후기**: 0개

## 추가 정보

더 자세한 정보는 다음 문서를 참고하세요:
- [API 참조 문서](./API_REFERENCE.md)
- [프로젝트 구조](./PROJECT_STRUCTURE.md)
- [비동기 수집 가이드](./ASYNC_COLLECTION_GUIDE.md)
