"""
비동기 작업 관리 모듈
외부 API 호출로부터 데이터 수집 작업을 비동기로 처리하고 진행 상황을 추적합니다.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from enum import Enum
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """작업 상태 열거형"""
    PENDING = "pending"         # 대기 중
    RUNNING = "running"         # 실행 중
    COMPLETED = "completed"     # 완료
    FAILED = "failed"          # 실패
    CANCELLED = "cancelled"     # 취소

class TaskType(Enum):
    """작업 타입 열거형"""
    BABITALK_COLLECT = "babitalk_collect"
    GANGNAMUNNI_COLLECT = "gangnamunni_collect"
    NAVER_COLLECT = "naver_collect"

class AsyncTaskManager:
    """비동기 작업 관리자"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)  # 최대 10개 동시 작업
        
    def create_task(self, task_type: TaskType, task_data: Dict[str, Any]) -> str:
        """새로운 작업 생성"""
        task_id = str(uuid.uuid4())
        
        self.tasks[task_id] = {
            "id": task_id,
            "type": task_type.value,
            "status": TaskStatus.PENDING.value,
            "progress": 0,
            "total": 0,
            "current_step": "",
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "task_data": task_data,
            "logs": []
        }
        
        logger.info(f"새로운 작업 생성: {task_id} ({task_type.value})")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 조회"""
        task = self.tasks.get(task_id)
        if not task:
            return None
            
        # 민감한 정보 제거한 상태로 반환
        return {
            "id": task["id"],
            "type": task["type"],
            "status": task["status"],
            "progress": task["progress"],
            "total": task["total"],
            "current_step": task["current_step"],
            "created_at": task["created_at"],
            "started_at": task["started_at"],
            "completed_at": task["completed_at"],
            "error": task["error"],
            "result_summary": self._get_result_summary(task["result"]),
            "logs": task["logs"][-10:]  # 최근 10개 로그만 반환
        }
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """모든 작업 상태 조회"""
        return {task_id: self.get_task_status(task_id) for task_id in self.tasks}
    
    def update_task_progress(self, task_id: str, progress: int, total: int, current_step: str = ""):
        """작업 진행률 업데이트"""
        if task_id in self.tasks:
            self.tasks[task_id]["progress"] = progress
            self.tasks[task_id]["total"] = total
            self.tasks[task_id]["current_step"] = current_step
            
            # 로그 추가
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {current_step} ({progress}/{total})"
            self.tasks[task_id]["logs"].append(log_entry)
            
            # 최대 50개 로그만 유지
            if len(self.tasks[task_id]["logs"]) > 50:
                self.tasks[task_id]["logs"] = self.tasks[task_id]["logs"][-50:]
    
    def start_task(self, task_id: str, task_func: Callable, *args, **kwargs) -> bool:
        """작업 시작"""
        if task_id not in self.tasks:
            return False
            
        if self.tasks[task_id]["status"] != TaskStatus.PENDING.value:
            return False
        
        self.tasks[task_id]["status"] = TaskStatus.RUNNING.value
        self.tasks[task_id]["started_at"] = datetime.now().isoformat()
        
        # 진행률 콜백 함수 생성
        def progress_callback(progress: int, total: int, step: str = ""):
            self.update_task_progress(task_id, progress, total, step)
        
        # 비동기 작업 실행
        asyncio.create_task(self._run_task(task_id, task_func, progress_callback, *args, **kwargs))
        
        logger.info(f"작업 시작: {task_id}")
        return True
    
    async def _run_task(self, task_id: str, task_func: Callable, progress_callback: Callable, *args, **kwargs):
        """작업 실행 (내부 메서드)"""
        try:
            # kwargs에 progress_callback 추가
            kwargs['progress_callback'] = progress_callback
            
            # 작업 실행
            result = await task_func(*args, **kwargs)
            
            # 작업 완료
            self.tasks[task_id]["status"] = TaskStatus.COMPLETED.value
            self.tasks[task_id]["result"] = result
            self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
            self.tasks[task_id]["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 작업 완료")
            
            logger.info(f"작업 완료: {task_id}")
            
        except Exception as e:
            # 작업 실패
            self.tasks[task_id]["status"] = TaskStatus.FAILED.value
            self.tasks[task_id]["error"] = str(e)
            self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
            self.tasks[task_id]["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 작업 실패: {str(e)}")
            
            logger.error(f"작업 실패: {task_id}, 오류: {str(e)}")
            logger.error(traceback.format_exc())
    
    def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        if task_id not in self.tasks:
            return False
            
        if self.tasks[task_id]["status"] in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
            return False
        
        self.tasks[task_id]["status"] = TaskStatus.CANCELLED.value
        self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
        self.tasks[task_id]["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 작업 취소됨")
        
        logger.info(f"작업 취소: {task_id}")
        return True
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """오래된 작업 정리"""
        current_time = datetime.now()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            created_at = datetime.fromisoformat(task["created_at"])
            age_hours = (current_time - created_at).total_seconds() / 3600
            
            if age_hours > max_age_hours and task["status"] in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
            logger.info(f"오래된 작업 정리: {task_id}")
    
    def _get_result_summary(self, result: Any) -> Dict[str, Any]:
        """결과 요약 정보 생성"""
        if not result:
            return {}
            
        if isinstance(result, dict):
            summary = {}
            for key, value in result.items():
                if isinstance(value, (int, float, str, bool)):
                    summary[key] = value
                elif isinstance(value, (list, dict)):
                    summary[f"{key}_count"] = len(value) if hasattr(value, '__len__') else 0
            return summary
        else:
            return {"result": str(result)}

# 전역 작업 관리자 인스턴스
task_manager = AsyncTaskManager()
