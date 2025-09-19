# Bulk Get API 사양서

## 개요

Bulk Get API는 여러 개의 ID를 한 번에 전달하여 해당하는 데이터를 효율적으로 조회할 수 있는 API입니다. Article, Review, Comment 세 가지 데이터 타입에 대해 각각 제공됩니다.

## 기본 정보

- **Base URL**: `http://localhost:8000/api/v1/data`
- **Content-Type**: `application/json`
- **Method**: `POST`

## 공통 요청/응답 모델

### BulkGetRequest
```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

| 필드 | 타입 | 필수 | 설명 | 제약사항 |
|------|------|------|------|----------|
| ids | List[int] | ✅ | 조회할 ID 목록 | 1-100개 |

### BulkGetResponse
```json
{
  "data": [...],
  "total": 3,
  "requested_ids": [1, 2, 3],
  "found_ids": [1, 2, 3],
  "missing_ids": []
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| data | List[Any] | 조회된 데이터 목록 |
| total | int | 조회된 데이터 총 개수 |
| requested_ids | List[int] | 요청된 ID 목록 |
| found_ids | List[int] | 실제 조회된 ID 목록 |
| missing_ids | List[int] | 조회되지 않은 ID 목록 |

## API 엔드포인트

### 1. 게시글 Bulk 조회

#### 엔드포인트
```
POST /api/v1/data/articles/bulk
```

#### 요청 예시
```bash
curl -X POST "http://localhost:8000/api/v1/data/articles/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [47079, 47080, 47081]
  }'
```

#### 응답 예시
```json
{
  "data": [
    {
      "id": 47079,
      "platform_id": "gangnamunni",
      "community_article_id": "3558390",
      "community_id": 2,
      "title": "강남언니 게시글 3558390",
      "content": "게시글 내용...",
      "writer_nickname": "사용자닉네임",
      "writer_id": "12345",
      "like_count": 5,
      "comment_count": 3,
      "view_count": 100,
      "images": "[]",
      "created_at": "2025-09-19T10:30:00",
      "category_name": "hospital_question",
      "collected_at": "2025-09-19T18:30:00"
    }
  ],
  "total": 1,
  "requested_ids": [47079, 47080, 47081],
  "found_ids": [47079],
  "missing_ids": [47080, 47081]
}
```

### 2. 후기 Bulk 조회

#### 엔드포인트
```
POST /api/v1/data/reviews/bulk
```

#### 요청 예시
```bash
curl -X POST "http://localhost:8000/api/v1/data/reviews/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [2918, 2919, 2920]
  }'
```

#### 응답 예시
```json
{
  "data": [
    {
      "id": 2918,
      "platform_id": "gangnamunni_review",
      "platform_review_id": "102125125",
      "community_id": 2,
      "title": "얼굴 - 레이저리프팅",
      "content": "후기 내용...",
      "writer_nickname": "사용자닉네임",
      "writer_id": "12345",
      "like_count": 10,
      "rating": 5,
      "price": 500000,
      "images": "{\"beforePhotos\": [], \"afterPhotos\": []}",
      "categories": "[\"피부\"]",
      "sub_categories": "[\"레이저리프팅\"]",
      "surgery_date": "2025-09-18T15:00:00Z",
      "hospital_name": "얀클리닉",
      "doctor_name": "최원탁",
      "is_blind": false,
      "is_image_blur": false,
      "is_certificated_review": true,
      "created_at": "2025-09-19T10:30:00",
      "collected_at": "2025-09-19T18:30:00"
    }
  ],
  "total": 1,
  "requested_ids": [2918, 2919, 2920],
  "found_ids": [2918],
  "missing_ids": [2919, 2920]
}
```

### 3. 댓글 Bulk 조회

#### 엔드포인트
```
POST /api/v1/data/comments/bulk
```

#### 요청 예시
```bash
curl -X POST "http://localhost:8000/api/v1/data/comments/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [132979, 132978, 132977]
  }'
```

#### 응답 예시
```json
{
  "data": [
    {
      "id": 132979,
      "platform_id": "gangnamunni",
      "community_article_id": "3558390",
      "community_id": 2,
      "comment_id": "123456",
      "parent_comment_id": null,
      "content": "댓글 내용...",
      "writer_nickname": "햄부기가죠아요",
      "writer_id": "67890",
      "like_count": 0,
      "created_at": "2025-09-19T10:30:00",
      "collected_at": "2025-09-19T18:30:00"
    }
  ],
  "total": 1,
  "requested_ids": [132979, 132978, 132977],
  "found_ids": [132979],
  "missing_ids": [132978, 132977]
}
```

## 에러 응답

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "type": "too_short",
      "loc": ["body", "ids"],
      "msg": "List should have at least 1 item after validation, not 0",
      "input": [],
      "ctx": {
        "field_type": "List",
        "min_length": 1,
        "actual_length": 0
      }
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "게시글 bulk 조회 실패: 오류 메시지"
}
```

## 사용 사례

### 1. 대시보드 데이터 로딩
```javascript
// 최근 게시글 10개 ID로 상세 정보 조회
const response = await fetch('/api/v1/data/articles/bulk', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ids: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] })
});
const data = await response.json();
```

### 2. 검색 결과 상세 조회
```javascript
// 검색 결과에서 선택된 후기들의 상세 정보 조회
const selectedReviewIds = [2918, 2919, 2920];
const response = await fetch('/api/v1/data/reviews/bulk', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ids: selectedReviewIds })
});
const reviews = await response.json();
```

### 3. 댓글 스레드 로딩
```javascript
// 특정 게시글의 댓글들 상세 조회
const commentIds = [132979, 132978, 132977];
const response = await fetch('/api/v1/data/comments/bulk', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ids: commentIds })
});
const comments = await response.json();
```

## 성능 고려사항

### 1. ID 개수 제한
- **최대 100개**: 한 번에 조회할 수 있는 ID 개수 제한
- **최소 1개**: 빈 배열은 허용하지 않음

### 2. 데이터베이스 최적화
- `IN` 쿼리 사용으로 효율적인 조회
- 인덱스 활용으로 빠른 검색

### 3. 메모리 사용량
- 대량 데이터 조회 시 메모리 사용량 고려
- 필요에 따라 페이지네이션과 함께 사용 권장

## 주의사항

1. **존재하지 않는 ID**: `missing_ids`에 포함되어 반환됨
2. **중복 ID**: 중복된 ID는 자동으로 제거됨
3. **순서 보장**: 요청한 ID 순서와 응답 순서는 다를 수 있음
4. **데이터 일관성**: 조회 시점의 데이터 스냅샷 제공

## 관련 API

- [일반 조회 API](./API_REFERENCE.md#데이터-조회)
- [검색 API](./API_REFERENCE.md#키워드-검색)
- [페이지네이션 API](./API_REFERENCE.md#페이지네이션)

## 변경 이력

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 1.0.0 | 2025-09-19 | 초기 버전 릴리스 |
