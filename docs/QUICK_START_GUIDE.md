# API 빠른 시작 가이드

이 가이드는 우리 플랫폼 수집 API를 빠르게 시작하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 서버 확인
API 서버가 실행 중인지 확인하세요:
```bash
curl -X GET "http://localhost:8000/api/v1/data/statistics/summary"
```

### 2. 기본 조회
가장 간단한 요청으로 데이터를 확인해보세요:

```bash
# 게시글 목록 조회 (첫 5개)
curl -X GET "http://localhost:8000/api/v1/data/articles?page=1&limit=5"

# 댓글 목록 조회 (첫 5개)
curl -X GET "http://localhost:8000/api/v1/data/comments?page=1&limit=5"

# 통계 확인
curl -X GET "http://localhost:8000/api/v1/data/statistics/summary"
```

## 📊 현재 데이터 현황

- **게시글**: 1,463개 (바비톡 자유톡)
- **댓글**: 5,153개 (바비톡 자유톡)
- **후기**: 0개

## 🔍 자주 사용하는 쿼리

### 바비톡 데이터만 조회
```bash
# 바비톡 게시글
curl -X GET "http://localhost:8000/api/v1/data/articles?platform=babitalk_talk&page=1&limit=10"

# 바비톡 댓글
curl -X GET "http://localhost:8000/api/v1/data/comments?platform=babitalk_talk&page=1&limit=10"
```

### 특정 게시글의 댓글 조회
```bash
# 게시글 ID 7388807의 댓글들
curl -X GET "http://localhost:8000/api/v1/data/comments?article_id=7388807&page=1&limit=20"
```

### 특정 게시글 상세 조회
```bash
# 게시글 ID 1의 상세 정보
curl -X GET "http://localhost:8000/api/v1/data/articles/1"
```

## 💻 프로그래밍 언어별 예시

### JavaScript
```javascript
// 게시글 조회
fetch('http://localhost:8000/api/v1/data/articles?page=1&limit=5')
  .then(response => response.json())
  .then(data => console.log(data));

// 바비톡 댓글 조회
fetch('http://localhost:8000/api/v1/data/comments?platform=babitalk_talk&page=1&limit=10')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python
```python
import requests

# 게시글 조회
response = requests.get('http://localhost:8000/api/v1/data/articles?page=1&limit=5')
data = response.json()
print(data)

# 바비톡 댓글 조회
response = requests.get('http://localhost:8000/api/v1/data/comments?platform=babitalk_talk&page=1&limit=10')
data = response.json()
print(data)
```

### PHP
```php
<?php
// 게시글 조회
$response = file_get_contents('http://localhost:8000/api/v1/data/articles?page=1&limit=5');
$data = json_decode($response, true);
print_r($data);

// 바비톡 댓글 조회
$response = file_get_contents('http://localhost:8000/api/v1/data/comments?platform=babitalk_talk&page=1&limit=10');
$data = json_decode($response, true);
print_r($data);
?>
```

## 🛠️ 유용한 팁

### 1. 페이지네이션 활용
```bash
# 첫 번째 페이지
curl -X GET "http://localhost:8000/api/v1/data/articles?page=1&limit=20"

# 두 번째 페이지
curl -X GET "http://localhost:8000/api/v1/data/articles?page=2&limit=20"
```

### 2. 응답 구조 이해
모든 목록 조회 API는 다음과 같은 구조로 응답합니다:
```json
{
  "data": [...],           // 실제 데이터 배열
  "total": 1463,          // 전체 데이터 수
  "page": 1,              // 현재 페이지
  "limit": 20,            // 페이지당 데이터 수
  "total_pages": 74,      // 전체 페이지 수
  "has_next": true,       // 다음 페이지 존재 여부
  "has_prev": false       // 이전 페이지 존재 여부
}
```

### 3. 에러 처리
```bash
# 존재하지 않는 게시글 조회 (404 에러)
curl -X GET "http://localhost:8000/api/v1/data/articles/99999"

# 잘못된 플랫폼 필터 (422 에러)
curl -X GET "http://localhost:8000/api/v1/data/articles?platform=invalid_platform"
```

## 📚 더 자세한 정보

- [API 사용 가이드](./API_USAGE_GUIDE.md) - 상세한 사용법
- [API 상세 참조](./API_REFERENCE_DETAILED.md) - 완전한 API 스펙
- [프로젝트 구조](./PROJECT_STRUCTURE.md) - 시스템 구조 이해

## ❓ 문제 해결

### 서버가 응답하지 않는 경우
1. API 서버가 실행 중인지 확인
2. 포트 8000이 사용 가능한지 확인
3. 방화벽 설정 확인

### 데이터가 없는 경우
1. 통계 API로 현재 데이터 현황 확인
2. 올바른 플랫폼 ID 사용 확인
3. 페이지 번호가 올바른지 확인

### 에러가 발생하는 경우
1. 요청 URL이 올바른지 확인
2. 파라미터 값이 유효한지 확인
3. 서버 로그 확인
