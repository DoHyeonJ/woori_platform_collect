# Search API 스펙 문서

## 개요

Search API는 수집된 게시글, 댓글, 후기 데이터에서 키워드 검색을 수행하는 통합 검색 기능을 제공합니다. 네이버 카페 필터링 기능이 추가되어 특정 카페의 데이터만 검색할 수 있습니다.

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
| `platforms` | string | null | 플랫폼 필터 (콤마로 구분) | `"gangnamunni,babitalk,naver"` |
| `data_types` | string | null | 데이터 타입 필터 (콤마로 구분) | `"article,comment,review"` |
| `naver_cafes` | string | null | 네이버 카페 필터 (콤마로 구분, 카페명 또는 카페ID) | `"여우야,A+여우야"` 또는 `"10912875,12285441"` |
| `start_date` | string | null | 검색 시작 날짜 (YYYY-MM-DD) | `"2024-01-01"` |
| `end_date` | string | null | 검색 종료 날짜 (YYYY-MM-DD) | `"2024-12-31"` |
| `page` | integer | 1 | 페이지 번호 (1 이상) | `1` |
| `limit` | integer | 20 | 페이지당 데이터 수 (1-1000) | `50` |

## 지원되는 플랫폼

| 플랫폼 ID | 플랫폼명 | 설명 |
|----------|----------|------|
| `gangnamunni` | 강남언니 | 강남언니 커뮤니티 |
| `babitalk` | 바비톡 | 바비톡 시술후기 |
| `babitalk_talk` | 바비톡 자유톡 | 바비톡 자유톡 게시판 |
| `babitalk_event_ask` | 바비톡 발품후기 | 바비톡 발품후기 |
| `naver` | 네이버카페 | 네이버 카페 |

## 지원되는 데이터 타입

| 데이터 타입 | 설명 |
|------------|------|
| `article` | 게시글 |
| `comment` | 댓글 |
| `review` | 후기 |

## 지원되는 네이버 카페

| 카페명 | 카페 ID | URL ID | 설명 |
|--------|---------|--------|------|
| 여우야 | 10912875 | feko | 여우야 성형카페 |
| A+여우야 | 12285441 | fox5282 | A+여우야 성형카페 |
| 성형위키백과 | 11498714 | juliett00 | 성형위키백과 |
| 여생남정 | 13067396 | suddes | 여생남정 |
| 시크먼트 | 23451561 | parisienlook | 시크먼트 |
| 가아사 | 15880379 | luxury009 | 가아사 |
| 파우더룸 | 10050813 | cosmania | 파우더룸 |

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

### 4. 네이버 카페 필터 적용 (카페명)

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형&platforms=naver&naver_cafes=여우야,A+여우야" \
  -H "accept: application/json"
```

### 5. 네이버 카페 필터 적용 (카페ID)

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형&platforms=naver&naver_cafes=10912875,12285441" \
  -H "accept: application/json"
```

### 6. 혼합 필터 적용

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형&platforms=naver&naver_cafes=여우야,12285441&data_types=article,comment&start_date=2024-01-01&end_date=2024-12-31" \
  -H "accept: application/json"
```

### 7. 페이지네이션 적용

```bash
curl -X GET "http://localhost:8000/api/v1/data/search?keywords=성형&page=2&limit=50" \
  -H "accept: application/json"
```

## 응답 형식

### 성공 응답 (200 OK)

```json
{
  "articles": [
    {
      "id": 123,
      "platform_id": "naver",
      "community_article_id": "12345",
      "community_id": 1,
      "title": "게시글 제목",
      "content": "게시글 내용",
      "writer_nickname": "작성자닉네임",
      "writer_id": "writer123",
      "like_count": 10,
      "comment_count": 5,
      "view_count": 100,
      "images": "[]",
      "created_at": "2024-01-15T10:30:00",
      "category_name": "여우야",
      "collected_at": "2024-01-15T10:35:00",
      "article_url": "https://cafe.naver.com/feko/12345"
    }
  ],
  "comments": [
    {
      "id": 456,
      "platform_id": "naver",
      "community_article_id": "12345",
      "community_id": 1,
      "comment_id": "67890",
      "parent_comment_id": null,
      "content": "댓글 내용",
      "writer_nickname": "댓글작성자",
      "writer_id": "commenter123",
      "like_count": 0,
      "created_at": "2024-01-15T11:00:00",
      "collected_at": "2024-01-15T11:05:00",
      "comment_url": "https://cafe.naver.com/feko/12345"
    }
  ],
  "reviews": [
    {
      "id": 789,
      "platform_id": "babitalk",
      "platform_review_id": "review123",
      "community_id": 1,
      "title": "후기 제목",
      "content": "후기 내용",
      "writer_nickname": "후기작성자",
      "writer_id": "reviewer123",
      "like_count": 15,
      "rating": 5,
      "price": 2000000,
      "images": "[]",
      "categories": "눈성형",
      "sub_categories": "쌍수",
      "surgery_date": "2024-01-10",
      "hospital_name": "성형외과",
      "doctor_name": "김의사",
      "is_blind": false,
      "is_image_blur": false,
      "is_certificated_review": true,
      "created_at": "2024-01-15T09:00:00",
      "collected_at": "2024-01-15T09:05:00",
      "article_url": "https://web.babitalk.com/reviews/review123"
    }
  ],
  "total_counts": {
    "articles": 25,
    "comments": 89,
    "reviews": 12
  },
  "page": 1,
  "limit": 20,
  "total_pages": 2,
  "has_next": true,
  "has_prev": false,
  "search_info": {
    "keywords": ["성형", "눈", "코"],
    "platforms": ["naver"],
    "data_types": ["article", "comment"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "total_results": 126,
    "timestamp": "2024-01-15T12:00:00"
  }
}
```

### 에러 응답

#### 400 Bad Request - 잘못된 파라미터

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

## 필터링 동작 방식

### 1. 키워드 검색
- **게시글**: 제목(`title`)과 내용(`content`)에서 검색
- **댓글**: 내용(`content`)에서 검색
- **후기**: 제목(`title`), 내용(`content`), 병원명(`hospital_name`), 의사명(`doctor_name`)에서 검색

### 2. 플랫폼 필터
- 지정된 플랫폼의 데이터만 검색
- 여러 플랫폼을 콤마로 구분하여 지정 가능

### 3. 네이버 카페 필터
- **게시글**: `category_name` 필드로 필터링
- **댓글**: 게시글과 조인하여 `category_name` 필드로 필터링
- **후기**: `categories` 필드로 필터링
- 카페명 또는 카페ID로 지정 가능 (자동 변환)

### 4. 날짜 필터
- `start_date`: 해당 날짜 이후의 데이터
- `end_date`: 해당 날짜까지의 데이터 (23:59:59까지 포함)

### 5. 데이터 타입 필터
- `article`: 게시글만 검색
- `comment`: 댓글만 검색
- `review`: 후기만 검색

## URL 생성 규칙

### 게시글 URL
- **강남언니**: `https://www.gangnamunni.com/community/{article_id}`
- **바비톡 시술후기**: `https://web.babitalk.com/reviews/{article_id}`
- **바비톡 자유톡**: `https://web.babitalk.com/community/{article_id}`
- **바비톡 발품후기**: `https://web.babitalk.com/ask-memos/{article_id}`
- **네이버 카페**: `https://cafe.naver.com/{cafe_url_id}/{article_id}`

### 댓글 URL
- 게시글 URL과 동일 (댓글 앵커는 지원하지 않음)

### 후기 URL
- 바비톡 후기: `https://web.babitalk.com/reviews/{review_id}`

## 성능 고려사항

1. **페이지네이션**: 대량의 데이터 검색 시 `limit` 파라미터를 적절히 설정
2. **인덱스**: 데이터베이스에 적절한 인덱스가 설정되어 있어야 함
3. **캐싱**: 자주 사용되는 검색 결과는 캐싱 고려

## 주의사항

1. **네이버 카페 필터**: `platforms=naver`가 설정되지 않은 경우에도 네이버 카페 필터가 적용될 수 있음
2. **날짜 형식**: 날짜는 반드시 `YYYY-MM-DD` 형식으로 입력
3. **키워드**: 빈 문자열이나 공백만 있는 키워드는 무시됨
4. **대소문자**: 키워드 검색은 대소문자를 구분하지 않음

## 버전 히스토리

- **v1.1.0** (2024-01-15): 네이버 카페 필터링 기능 추가
- **v1.0.0** (2024-01-01): 초기 버전 릴리스
