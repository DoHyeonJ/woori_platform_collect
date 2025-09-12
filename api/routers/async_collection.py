"""
비동기 데이터 수집 API 엔드포인트
외부에서 호출하여 백그라운드에서 데이터 수집을 실행하고 진행 상황을 추적할 수 있습니다.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from api.services.async_task_manager import task_manager, TaskType
from api.services.async_collection_service import AsyncCollectionService
from api.services.callback_service import callback_service

router = APIRouter(prefix="/async-collection", tags=["비동기 수집"])

# 요청 모델들
class BabitalkCollectionRequest(BaseModel):
    """바비톡 수집 요청 모델"""
    target_date: str = Field(..., description="수집할 날짜 (YYYY-MM-DD)")
    categories: Optional[List[str]] = Field(["reviews", "talks", "event_ask_memos"], description="수집할 카테고리")
    callback_url: Optional[str] = Field(None, description="수집 완료 시 호출할 콜백 URL")

class GangnamunniCollectionRequest(BaseModel):
    """강남언니 수집 요청 모델"""
    target_date: str = Field(..., description="수집할 날짜 (YYYY-MM-DD)")
    categories: Optional[List[str]] = Field(
        ["hospital_question", "surgery_question", "free_chat", "review", "ask_doctor"],
        description="수집할 카테고리"
    )
    save_as_reviews: Optional[bool] = Field(False, description="후기로 저장할지 여부")
    token: Optional[str] = Field(None, description="강남언니 API 토큰 (None이면 기본값 사용)")
    callback_url: Optional[str] = Field(None, description="수집 완료 시 호출할 콜백 URL")

class NaverCollectionRequest(BaseModel):
    """네이버 수집 요청 모델"""
    cafe_id: str = Field(..., description="카페 ID")
    target_date: Optional[str] = Field(None, description="수집할 날짜 (YYYY-MM-DD), None이면 최신 게시글")
    menu_id: Optional[str] = Field("", description="게시판 ID (빈 문자열이면 모든 게시판)")
    per_page: Optional[int] = Field(20, description="페이지당 게시글 수")
    naver_cookies: Optional[str] = Field("", description="네이버 쿠키")
    callback_url: Optional[str] = Field(None, description="수집 완료 시 호출할 콜백 URL")

class TaskResponse(BaseModel):
    """작업 응답 모델"""
    task_id: str
    message: str

# API 엔드포인트들

@router.post("/babitalk/start", response_model=TaskResponse)
async def start_babitalk_collection(request: BabitalkCollectionRequest):
    """
    바비톡 데이터 수집 시작
    
    백그라운드에서 바비톡 데이터를 비동기로 수집합니다.
    """
    try:
        # 작업 생성
        task_id = task_manager.create_task(
            TaskType.BABITALK_COLLECT,
            {
                "target_date": request.target_date,
                "categories": request.categories
            }
        )
        
        # 작업 시작
        success = task_manager.start_task(
            task_id,
            AsyncCollectionService.collect_babitalk_data,
            request.target_date,
            request.categories,
            request.callback_url
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="작업 시작에 실패했습니다")
        
        return TaskResponse(
            task_id=task_id,
            message=f"바비톡 데이터 수집이 시작되었습니다. 작업 ID: {task_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 생성 실패: {str(e)}")

@router.post("/gangnamunni/start", response_model=TaskResponse)
async def start_gangnamunni_collection(request: GangnamunniCollectionRequest):
    """
    강남언니 데이터 수집 시작
    
    백그라운드에서 강남언니 데이터를 비동기로 수집합니다.
    """
    import time
    start_time = time.time()
    
    # 로깅을 위한 카테고리명 매핑
    category_names = {
        "hospital_question": "병원질문",
        "surgery_question": "시술/수술질문",
        "free_chat": "자유수다",
        "review": "발품후기",
        "ask_doctor": "의사에게 물어보세요"
    }
    
    # 카테고리명 변환
    category_display_names = [category_names.get(cat, cat) for cat in request.categories]
    
    print(f"🚀 강남언니 비동기 데이터 수집 시작...")
    print(f"📅 수집 날짜: {request.target_date}")
    print(f"📂 수집 카테고리: {', '.join(category_display_names)}")
    print(f"💾 저장 방식: {'후기' if request.save_as_reviews else '게시글'}")
    print(f"🔑 토큰: {'사용자 지정' if request.token else '기본값'}")
    
    try:
        # 작업 생성
        task_id = task_manager.create_task(
            TaskType.GANGNAMUNNI_COLLECT,
            {
                "target_date": request.target_date,
                "categories": request.categories,
                "save_as_reviews": request.save_as_reviews,
                "token": request.token
            }
        )
        
        # 작업 시작
        success = task_manager.start_task(
            task_id,
            AsyncCollectionService.collect_gangnamunni_data,
            request.target_date,
            request.categories,
            request.save_as_reviews,
            request.token,
            request.callback_url
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="작업 시작에 실패했습니다")
        
        setup_time = time.time() - start_time
        print(f"✅ 강남언니 비동기 수집 작업 시작 완료!")
        print(f"🆔 작업 ID: {task_id}")
        print(f"⏱️  작업 설정 소요시간: {setup_time:.2f}초")
        
        return TaskResponse(
            task_id=task_id,
            message=f"강남언니 데이터 수집이 시작되었습니다. 작업 ID: {task_id}"
        )
        
    except Exception as e:
        setup_time = time.time() - start_time
        print(f"❌ 강남언니 비동기 수집 작업 시작 실패!")
        print(f"📋 오류 내용: {str(e)}")
        print(f"⏱️  실패까지 소요시간: {setup_time:.2f}초")
        raise HTTPException(status_code=500, detail=f"작업 생성 실패: {str(e)}")

@router.post("/naver/start", response_model=TaskResponse)
async def start_naver_collection(request: NaverCollectionRequest):
    """
    네이버 카페 데이터 수집 시작
    
    백그라운드에서 네이버 카페 데이터를 비동기로 수집합니다.
    """
    try:
        # 작업 생성
        task_id = task_manager.create_task(
            TaskType.NAVER_COLLECT,
            {
                "cafe_id": request.cafe_id,
                "target_date": request.target_date,
                "menu_id": request.menu_id,
                "per_page": request.per_page,
                "naver_cookies": request.naver_cookies
            }
        )
        
        # 작업 시작
        success = task_manager.start_task(
            task_id,
            AsyncCollectionService.collect_naver_data,
            request.cafe_id,
            request.target_date,
            request.menu_id,
            request.per_page,
            request.naver_cookies,
            request.callback_url
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="작업 시작에 실패했습니다")
        
        return TaskResponse(
            task_id=task_id,
            message=f"네이버 카페 데이터 수집이 시작되었습니다. 작업 ID: {task_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 생성 실패: {str(e)}")

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    작업 상태 조회
    
    특정 작업의 진행 상황과 결과를 조회합니다.
    """
    task_status = task_manager.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    return task_status

@router.get("/tasks")
async def get_all_tasks():
    """
    모든 작업 상태 조회
    
    현재 진행 중이거나 완료된 모든 작업의 상태를 조회합니다.
    """
    return task_manager.get_all_tasks()

@router.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """
    작업 취소
    
    진행 중인 작업을 취소합니다.
    """
    success = task_manager.cancel_task(task_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="작업을 취소할 수 없습니다")
    
    return {"message": f"작업 {task_id}가 취소되었습니다"}

@router.post("/cleanup")
async def cleanup_old_tasks(max_age_hours: int = 24):
    """
    오래된 작업 정리
    
    완료된 오래된 작업들을 정리합니다.
    """
    task_manager.cleanup_old_tasks(max_age_hours)
    return {"message": f"{max_age_hours}시간 이상 된 완료된 작업들이 정리되었습니다"}

@router.get("/status/summary")
async def get_status_summary():
    """
    전체 작업 현황 요약
    
    현재 실행 중인 작업 수, 완료된 작업 수 등의 요약 정보를 제공합니다.
    """
    all_tasks = task_manager.get_all_tasks()
    
    summary = {
        "total_tasks": len(all_tasks),
        "pending": len([t for t in all_tasks.values() if t["status"] == "pending"]),
        "running": len([t for t in all_tasks.values() if t["status"] == "running"]),
        "completed": len([t for t in all_tasks.values() if t["status"] == "completed"]),
        "failed": len([t for t in all_tasks.values() if t["status"] == "failed"]),
        "cancelled": len([t for t in all_tasks.values() if t["status"] == "cancelled"]),
        "timestamp": datetime.now().isoformat()
    }
    
    return summary
