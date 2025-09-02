# 비동기 데이터 수집 가이드

## 개요

이 가이드는 외부에서 API를 통해 데이터 수집을 비동기로 실행하고, 진행 상황을 추적하는 방법을 설명합니다.

## 특징

- **비동기 처리**: 데이터 수집이 백그라운드에서 실행되어 서버가 다른 요청을 처리할 수 있습니다
- **진행 상황 추적**: 실시간으로 수집 진행률과 상태를 확인할 수 있습니다
- **작업 관리**: 작업 취소, 상태 조회, 결과 확인이 가능합니다
- **멀티 플랫폼**: 바비톡, 강남언니, 네이버 카페 모두 지원합니다

## API 엔드포인트

### 1. 바비톡 데이터 수집 시작

```bash
POST /api/v1/async-collection/babitalk/start
```

**요청 본문:**
```json
{
  "target_date": "2025-01-01",
  "categories": ["reviews", "talks", "event_ask_memos"],
  "limit": 24
}
```

**응답:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "바비톡 데이터 수집이 시작되었습니다. 작업 ID: 550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. 강남언니 데이터 수집 시작

```bash
POST /api/v1/async-collection/gangnamunni/start
```

**요청 본문:**
```json
{
  "target_date": "2025-01-01",
  "categories": ["hospital_question", "surgery_question", "free_chat", "review", "ask_doctor"],
  "save_as_reviews": false,
  "limit": 0
}
```

### 3. 네이버 카페 데이터 수집 시작

```bash
POST /api/v1/async-collection/naver/start
```

**요청 본문:**
```json
{
  "cafe_id": "10912875",
  "target_date": "2025-01-01",
  "menu_id": "",
  "per_page": 20,
  "naver_cookies": "your_cookies_here"
}
```

### 4. 작업 상태 조회

```bash
GET /api/v1/async-collection/task/{task_id}
```

**응답:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "babitalk_collect",
  "status": "running",
  "progress": 15,
  "total": 50,
  "current_step": "시술후기 수집 중...",
  "created_at": "2025-01-01T10:00:00",
  "started_at": "2025-01-01T10:00:01",
  "completed_at": null,
  "error": null,
  "result_summary": {},
  "logs": [
    "[10:00:01] 바비톡 데이터 수집 시작",
    "[10:00:05] 시술후기 수집 중... (15/50)"
  ]
}
```

### 5. 모든 작업 상태 조회

```bash
GET /api/v1/async-collection/tasks
```

### 6. 작업 취소

```bash
DELETE /api/v1/async-collection/task/{task_id}
```

### 7. 전체 현황 요약

```bash
GET /api/v1/async-collection/status/summary
```

**응답:**
```json
{
  "total_tasks": 10,
  "pending": 2,
  "running": 3,
  "completed": 4,
  "failed": 1,
  "cancelled": 0,
  "timestamp": "2025-01-01T10:30:00"
}
```

## 작업 상태 설명

- **pending**: 대기 중 (아직 시작되지 않음)
- **running**: 실행 중
- **completed**: 완료됨
- **failed**: 실패함
- **cancelled**: 취소됨

## 사용 예시

### Python을 사용한 예시

```python
import requests
import time

# 1. 바비톡 데이터 수집 시작
response = requests.post('http://localhost:8000/api/v1/async-collection/babitalk/start', json={
    "target_date": "2025-01-01",
    "categories": ["reviews", "talks"],
    "limit": 24
})

task_id = response.json()['task_id']
print(f"작업 시작됨: {task_id}")

# 2. 진행 상황 모니터링
while True:
    status_response = requests.get(f'http://localhost:8000/api/v1/async-collection/task/{task_id}')
    status = status_response.json()
    
    print(f"상태: {status['status']}, 진행률: {status['progress']}/{status['total']}")
    print(f"현재 단계: {status['current_step']}")
    
    if status['status'] in ['completed', 'failed', 'cancelled']:
        print("작업 완료!")
        print(f"결과: {status['result_summary']}")
        break
    
    time.sleep(5)  # 5초마다 상태 확인
```

### JavaScript를 사용한 예시

```javascript
// 1. 강남언니 데이터 수집 시작
const startResponse = await fetch('http://localhost:8000/api/v1/async-collection/gangnamunni/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        target_date: '2025-01-01',
        categories: ['hospital_question', 'review'],
        save_as_reviews: true
    })
});

const { task_id } = await startResponse.json();
console.log(`작업 시작됨: ${task_id}`);

// 2. 진행 상황 모니터링
const checkStatus = async () => {
    const statusResponse = await fetch(`http://localhost:8000/api/v1/async-collection/task/${task_id}`);
    const status = await statusResponse.json();
    
    console.log(`상태: ${status.status}, 진행률: ${status.progress}/${status.total}`);
    
    if (['completed', 'failed', 'cancelled'].includes(status.status)) {
        console.log('작업 완료!', status.result_summary);
        return;
    }
    
    setTimeout(checkStatus, 5000); // 5초 후 다시 확인
};

checkStatus();
```

## 주의사항

1. **쿠키 관리**: 네이버 카페 수집 시 유효한 쿠키가 필요합니다
2. **API 제한**: 각 플랫폼의 API 제한을 고려하여 적절한 딜레이를 설정했습니다
3. **메모리 관리**: 완료된 작업은 24시간 후 자동으로 정리됩니다
4. **동시 실행**: 최대 10개의 작업이 동시에 실행될 수 있습니다

## 문제 해결

### 작업이 시작되지 않는 경우
- 요청 데이터가 올바른지 확인
- 서버 로그 확인

### 작업이 실패하는 경우
- `error` 필드에서 실패 원인 확인
- 네트워크 연결 상태 확인
- 플랫폼별 접근 제한 확인

### 진행률이 업데이트되지 않는 경우
- 작업이 아직 대기 중일 수 있음
- 서버 로그에서 상세 정보 확인

## 로그 확인

서버 로그에서 더 자세한 정보를 확인할 수 있습니다:

```bash
# 개발 환경
python api/main.py

# 프로덕션 환경
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
