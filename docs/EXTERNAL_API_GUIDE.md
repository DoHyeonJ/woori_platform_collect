# 외부 API 사용 가이드

이 문서는 외부 서버에서 우리 데이터 수집 서버의 API를 사용하는 방법을 상세히 설명합니다.

## 📋 목차

1. [서버 정보](#서버-정보)
2. [서버 시작하기](#서버-시작하기)
3. [비동기 데이터 수집](#비동기-데이터-수집)
4. [수집 상태 확인](#수집-상태-확인)
5. [데이터 조회](#데이터-조회)
6. [동기 데이터 수집](#동기-데이터-수집)
7. [에러 처리](#에러-처리)
8. [예제 코드](#예제-코드)
9. [API 문서](#api-문서)

## 🖥️ 서버 정보

### 기본 정보
- **서버 주소**: `http://localhost:8000` (개발 환경)
- **API 버전**: v1
- **인증**: 현재 인증 없음 (추후 JWT 토큰 기반 인증 예정)

### 주요 엔드포인트
- **비동기 수집**: `/api/v1/async-collection/*`
- **수집 상태**: `/api/v1/async-collection/status/*`
- **데이터 조회**: `/api/v1/data/*`
- **동기 수집**: `/api/v1/collection/*`

## 🚀 비동기 데이터 수집

비동기 수집은 서버를 블로킹하지 않고 백그라운드에서 데이터를 수집합니다.

### 1. 바비톡 데이터 수집

#### 시술후기 수집
```http
POST /api/v1/async-collection/babitalk/start
Content-Type: application/json

{
  "target_date": "2024-01-15",
  "categories": ["reviews"],
  "limit": 50
}
```

#### 발품후기 수집
```http
POST /api/v1/async-collection/babitalk/start
Content-Type: application/json

{
  "target_date": "2024-01-15",
  "categories": ["event_ask_memos"],
  "limit": 30
}
```

#### 자유톡 수집
```http
POST /api/v1/async-collection/babitalk/start
Content-Type: application/json

{
  "target_date": "2024-01-15",
  "categories": ["talks"],
  "limit": 20
}
```

#### 복합 수집 (여러 카테고리 동시)
```http
POST /api/v1/async-collection/babitalk/start
Content-Type: application/json

{
  "target_date": "2024-01-15",
  "categories": ["reviews", "event_ask_memos", "talks"],
  "limit": 30
}
```

**응답 예시:**
```json
{
  "task_id": "babitalk_20240115_123456",
  "status": "started",
  "message": "바비톡 데이터 수집이 시작되었습니다.",
  "estimated_duration": "5-10분",
  "started_at": "2024-01-15T10:30:00Z"
}
```

### 2. 강남언니 데이터 수집

```http
POST /api/v1/async-collection/gangnamunni/start
Content-Type: application/json

{
  "target_date": "2024-01-15",
  "categories": ["hospital_question", "surgery_question", "free_chat", "review", "ask_doctor"],
  "save_as_reviews": true,
  "limit": 50
}
```

**응답 예시:**
```json
{
  "task_id": "gangnamunni_20240115_123456",
  "status": "started",
  "message": "강남언니 데이터 수집이 시작되었습니다.",
  "estimated_duration": "3-5분",
  "started_at": "2024-01-15T10:30:00Z"
}
```

### 3. 네이버 카페 데이터 수집

```http
POST /api/v1/async-collection/naver/start
Content-Type: application/json

{
  "cafe_id": "12285441",
  "target_date": "2024-01-15",
  "menu_id": "38",
  "per_page": 30,
  "naver_cookies": "NID_AUT=...; NID_SES=..."
}
```

**응답 예시:**
```json
{
  "task_id": "naver_20240115_123456",
  "status": "started",
  "message": "네이버 카페 데이터 수집이 시작되었습니다.",
  "estimated_duration": "2-3분",
  "started_at": "2024-01-15T10:30:00Z"
}
```

## 📊 수집 상태 확인

### 1. 특정 작업 상태 확인

```http
GET /api/v1/async-collection/status/{task_id}
```

**응답 예시 (진행 중):**
```json
{
  "task_id": "babitalk_20240115_123456",
  "status": "running",
  "progress": {
    "current": 15,
    "total": 50,
    "percentage": 30
  },
  "current_category": "reviews",
  "started_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:35:00Z"
}
```

**응답 예시 (완료):**
```json
{
  "task_id": "babitalk_20240115_123456",
  "status": "completed",
  "progress": {
    "current": 50,
    "total": 50,
    "percentage": 100
  },
  "results": {
    "total_reviews": 24,
    "total_memos": 15,
    "total_talks": 11
  },
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:35:00Z",
  "execution_time": 300.5
}
```

**응답 예시 (실패):**
```json
{
  "task_id": "babitalk_20240115_123456",
  "status": "failed",
  "error": "API 호출 실패: 429 Too Many Requests",
  "started_at": "2024-01-15T10:30:00Z",
  "failed_at": "2024-01-15T10:32:00Z"
}
```

### 2. 모든 작업 상태 확인

```http
GET /api/v1/async-collection/tasks
```

**응답 예시:**
```json
{
  "active_tasks": [
    {
      "task_id": "babitalk_20240115_123456",
      "status": "running",
      "progress": 30,
      "started_at": "2024-01-15T10:30:00Z"
    }
  ],
  "recent_tasks": [
    {
      "task_id": "gangnamunni_20240115_123456",
      "status": "completed",
      "completed_at": "2024-01-15T10:25:00Z"
    }
  ]
}
```

## 📖 데이터 조회

### 1. 후기 데이터 조회

#### 플랫폼별 후기 조회
```http
GET /api/v1/data/reviews?platform=babitalk&limit=20&offset=0
```

#### 날짜별 후기 조회
```http
GET /api/v1/data/reviews?date=2024-01-15&limit=20&offset=0
```

#### 필터링된 후기 조회
```http
GET /api/v1/data/reviews?platform=babitalk&category=reviews&hospital_name=강남성형외과&limit=20&offset=0
```

**응답 예시:**
```json
{
  "data": [
    {
      "id": 1,
      "platform_id": "babitalk",
      "platform_review_id": "12345",
      "title": "코수술 후기",
      "content": "코수술 잘 받았습니다...",
      "writer_nickname": "익명123",
      "hospital_name": "강남성형외과",
      "doctor_name": "김의사",
      "rating": 5,
      "price": 3000000,
      "created_at": "2024-01-15T09:00:00Z",
      "collected_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "total_pages": 8,
  "has_next": true,
  "has_prev": false
}
```

### 2. 게시글 데이터 조회

```http
GET /api/v1/data/articles?platform=gangnamunni&limit=20&offset=0
```

### 3. 댓글 데이터 조회

```http
GET /api/v1/data/comments?platform=naver&limit=20&offset=0
```

### 4. 통계 데이터 조회

#### 전체 통계
```http
GET /api/v1/data/statistics
```

#### 플랫폼별 통계
```http
GET /api/v1/data/statistics?platform=babitalk
```

#### 날짜별 통계
```http
GET /api/v1/data/statistics?date=2024-01-15
```

## ⚡ 동기 데이터 수집

동기 수집은 즉시 결과를 반환하지만 서버를 블로킹할 수 있습니다.

### 1. 바비톡 동기 수집

```http
POST /api/v1/collection/babitalk
Content-Type: application/json

{
  "category": "reviews",
  "target_date": "2024-01-15",
  "limit": 10
}
```

### 2. 강남언니 동기 수집

```http
POST /api/v1/collection/gangnamunni
Content-Type: application/json

{
  "category": "hospital_question",
  "target_date": "2024-01-15",
  "save_as_reviews": false,
  "limit": 10
}
```

### 3. 네이버 동기 수집

```http
POST /api/v1/collection/naver
Content-Type: application/json

{
  "cafe_id": "12285441",
  "target_date": "2024-01-15",
  "menu_id": "38",
  "limit": 10,
  "cookies": "NID_AUT=...; NID_SES=..."
}
```

## 🚨 에러 처리

### HTTP 상태 코드

- **200**: 성공
- **400**: 잘못된 요청 (파라미터 오류)
- **404**: 리소스 없음
- **429**: 요청 한도 초과
- **500**: 서버 내부 오류

### 에러 응답 형식

```json
{
  "error": "Bad Request",
  "message": "target_date는 YYYY-MM-DD 형식이어야 합니다.",
  "details": {
    "field": "target_date",
    "value": "2024/01/15",
    "expected_format": "YYYY-MM-DD"
  }
}
```

### 일반적인 에러 상황

1. **날짜 형식 오류**
   ```json
   {
     "error": "Invalid date format",
     "message": "target_date는 YYYY-MM-DD 형식이어야 합니다."
   }
   ```

2. **플랫폼 API 오류**
   ```json
   {
     "error": "External API Error",
     "message": "바비톡 API 호출 실패: 429 Too Many Requests"
   }
   ```

3. **데이터베이스 오류**
   ```json
   {
     "error": "Database Error",
     "message": "데이터베이스 연결 실패"
   }
   ```

## 💻 예제 코드

### Python 예제

```python
import requests
import time
import json

class DataCollectionClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def start_babitalk_collection(self, target_date, categories, limit=30):
        """바비톡 비동기 수집 시작"""
        url = f"{self.base_url}/api/v1/async-collection/babitalk/start"
        data = {
            "target_date": target_date,
            "categories": categories,
            "limit": limit
        }
        
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def check_task_status(self, task_id):
        """작업 상태 확인"""
        url = f"{self.base_url}/api/v1/async-collection/status/{task_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, task_id, timeout=600):
        """작업 완료까지 대기"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.check_task_status(task_id)
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"작업 실패: {status.get('error', 'Unknown error')}")
            
            print(f"진행률: {status.get('progress', {}).get('percentage', 0)}%")
            time.sleep(10)  # 10초마다 확인
        
        raise TimeoutError("작업 완료 시간 초과")
    
    def get_reviews(self, platform=None, date=None, limit=20, offset=0):
        """후기 데이터 조회"""
        url = f"{self.base_url}/api/v1/data/reviews"
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if platform:
            params["platform"] = platform
        if date:
            params["date"] = date
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

# 사용 예제
def main():
    client = DataCollectionClient()
    
    # 1. 바비톡 데이터 수집 시작
    print("바비톡 데이터 수집 시작...")
    result = client.start_babitalk_collection(
        target_date="2024-01-15",
        categories=["reviews", "event_ask_memo"],
        limit=50
    )
    
    task_id = result["task_id"]
    print(f"작업 ID: {task_id}")
    
    # 2. 완료까지 대기
    print("수집 완료까지 대기 중...")
    final_result = client.wait_for_completion(task_id)
    
    print(f"수집 완료! 결과: {final_result['results']}")
    
    # 3. 수집된 데이터 조회
    print("수집된 데이터 조회...")
    reviews = client.get_reviews(platform="babitalk", limit=10)
    
    for review in reviews["data"]:
        print(f"- {review['title']} ({review['writer_nickname']})")

if __name__ == "__main__":
    main()
```

### JavaScript/Node.js 예제

```javascript
const axios = require('axios');

class DataCollectionClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 30000
        });
    }
    
    async startBabitalkCollection(targetDate, categories, limit = 30) {
        const response = await this.client.post('/api/v1/async-collection/babitalk/start', {
            target_date: targetDate,
            categories: categories,
            limit: limit
        });
        return response.data;
    }
    
    async checkTaskStatus(taskId) {
        const response = await this.client.get(`/api/v1/async-collection/status/${taskId}`);
        return response.data;
    }
    
    async waitForCompletion(taskId, timeout = 600000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const status = await this.checkTaskStatus(taskId);
            
            if (status.status === 'completed') {
                return status;
            } else if (status.status === 'failed') {
                throw new Error(`작업 실패: ${status.error || 'Unknown error'}`);
            }
            
            console.log(`진행률: ${status.progress?.percentage || 0}%`);
            await new Promise(resolve => setTimeout(resolve, 10000)); // 10초 대기
        }
        
        throw new Error('작업 완료 시간 초과');
    }
    
    async getReviews(platform = null, date = null, limit = 20, offset = 0) {
        const params = { limit, offset };
        if (platform) params.platform = platform;
        if (date) params.date = date;
        
        const response = await this.client.get('/api/v1/data/reviews', { params });
        return response.data;
    }
}

// 사용 예제
async function main() {
    const client = new DataCollectionClient();
    
    try {
        // 1. 바비톡 데이터 수집 시작
        console.log('바비톡 데이터 수집 시작...');
        const result = await client.startBabitalkCollection(
            '2024-01-15',
            ['reviews', 'event_ask_memo'],
            50
        );
        
        const taskId = result.task_id;
        console.log(`작업 ID: ${taskId}`);
        
        // 2. 완료까지 대기
        console.log('수집 완료까지 대기 중...');
        const finalResult = await client.waitForCompletion(taskId);
        
        console.log(`수집 완료! 결과:`, finalResult.results);
        
        // 3. 수집된 데이터 조회
        console.log('수집된 데이터 조회...');
        const reviews = await client.getReviews('babitalk', null, 10);
        
        reviews.data.forEach(review => {
            console.log(`- ${review.title} (${review.writer_nickname})`);
        });
        
    } catch (error) {
        console.error('오류 발생:', error.message);
    }
}

main();
```

### cURL 예제

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# 1. 바비톡 데이터 수집 시작
echo "바비톡 데이터 수집 시작..."
TASK_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/async-collection/babitalk/start" \
  -H "Content-Type: application/json" \
  -d '{
    "target_date": "2024-01-15",
    "categories": ["reviews", "event_ask_memos"],
    "limit": 50
  }')

TASK_ID=$(echo $TASK_RESPONSE | jq -r '.task_id')
echo "작업 ID: $TASK_ID"

# 2. 완료까지 대기
echo "수집 완료까지 대기 중..."
while true; do
  STATUS_RESPONSE=$(curl -s "$BASE_URL/api/v1/async-collection/status/$TASK_ID")
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
  PROGRESS=$(echo $STATUS_RESPONSE | jq -r '.progress.percentage // 0')
  
  echo "진행률: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ]; then
    echo "수집 완료!"
    echo $STATUS_RESPONSE | jq '.results'
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "수집 실패!"
    echo $STATUS_RESPONSE | jq '.error'
    exit 1
  fi
  
  sleep 10
done

# 3. 수집된 데이터 조회
echo "수집된 데이터 조회..."
curl -s "$BASE_URL/api/v1/data/reviews?platform=babitalk&limit=10" | jq '.data[] | {title: .title, writer: .writer_nickname}'
```

## 🔧 고급 사용법

### 1. 배치 수집

여러 날짜의 데이터를 순차적으로 수집:

```python
def batch_collect_dates(client, dates, categories, limit=30):
    """여러 날짜의 데이터를 순차적으로 수집"""
    results = []
    
    for date in dates:
        print(f"날짜 {date} 수집 시작...")
        
        # 수집 시작
        result = client.start_babitalk_collection(date, categories, limit)
        task_id = result["task_id"]
        
        # 완료 대기
        final_result = client.wait_for_completion(task_id)
        results.append({
            "date": date,
            "task_id": task_id,
            "results": final_result["results"]
        })
        
        print(f"날짜 {date} 수집 완료: {final_result['results']}")
    
    return results

# 사용 예제
dates = ["2024-01-15", "2024-01-16", "2024-01-17"]
results = batch_collect_dates(client, dates, ["reviews"], 20)
```

### 2. 실시간 모니터링

```python
def monitor_collection(client, task_id):
    """수집 진행 상황을 실시간으로 모니터링"""
    import time
    
    while True:
        status = client.check_task_status(task_id)
        
        if status["status"] == "completed":
            print("✅ 수집 완료!")
            break
        elif status["status"] == "failed":
            print("❌ 수집 실패!")
            break
        
        progress = status.get("progress", {})
        current = progress.get("current", 0)
        total = progress.get("total", 0)
        percentage = progress.get("percentage", 0)
        
        print(f"📊 진행률: {current}/{total} ({percentage}%)")
        
        if "current_category" in status:
            print(f"📝 현재 카테고리: {status['current_category']}")
        
        time.sleep(5)  # 5초마다 업데이트
```

### 3. 에러 복구

```python
def robust_collection(client, target_date, categories, max_retries=3):
    """에러 발생 시 재시도하는 견고한 수집"""
    for attempt in range(max_retries):
        try:
            print(f"시도 {attempt + 1}/{max_retries}")
            
            result = client.start_babitalk_collection(target_date, categories)
            task_id = result["task_id"]
            
            final_result = client.wait_for_completion(task_id)
            return final_result
            
        except Exception as e:
            print(f"시도 {attempt + 1} 실패: {e}")
            
            if attempt < max_retries - 1:
                print("5초 후 재시도...")
                time.sleep(5)
            else:
                raise Exception(f"최대 재시도 횟수 초과: {e}")
```

## 📝 주의사항

1. **API 호출 제한**: 각 플랫폼별로 API 호출 제한이 있으므로 적절한 간격을 두고 호출하세요.

2. **데이터 크기**: 대량의 데이터 수집 시 메모리 사용량을 고려하세요.

3. **네트워크 안정성**: 네트워크 연결이 불안정한 환경에서는 재시도 로직을 구현하세요.

4. **날짜 형식**: 모든 날짜는 `YYYY-MM-DD` 형식을 사용해야 합니다.

5. **쿠키 관리**: 네이버 카페 수집 시 쿠키가 만료되면 갱신이 필요합니다.

## 🆘 문제 해결

### 자주 발생하는 문제

1. **연결 거부 오류**
   - 서버가 실행 중인지 확인
   - 방화벽 설정 확인
   - 포트 번호 확인

2. **타임아웃 오류**
   - 네트워크 연결 상태 확인
   - 서버 리소스 사용량 확인
   - 타임아웃 값 증가

3. **데이터 없음**
   - 날짜 형식 확인
   - 플랫폼별 데이터 존재 여부 확인
   - 수집 범위 확인

### 로그 확인

서버 로그를 확인하여 문제를 진단할 수 있습니다:

```bash
# 서버 로그 확인
tail -f logs/$(date +%Y-%m-%d).log

# 특정 작업 로그 확인
grep "task_id" logs/$(date +%Y-%m-%d).log
```

## 📞 지원

문제가 발생하거나 추가 기능이 필요한 경우:

1. **로그 파일** 확인
2. **API 응답** 검토
3. **네트워크 상태** 확인
4. **서버 리소스** 확인

---

이 가이드를 통해 외부 서버에서 우리 데이터 수집 서버를 효과적으로 활용할 수 있습니다. 추가 질문이나 개선 사항이 있으면 언제든 문의해 주세요.
