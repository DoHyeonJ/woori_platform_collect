from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio
import time
from datetime import datetime

from api.models import (
    CollectionResult, PlatformType,
    GangnamUnniCollectionRequest, BabitalkCollectionRequest
)
from api.dependencies import get_database_manager
from database.models import DatabaseManager

# 수집기 import
from collectors.gannamunni_collector import GangnamUnniDataCollector
from collectors.babitalk_collector import BabitalkDataCollector

router = APIRouter()

@router.get("/status")
async def get_collection_status():
    """
    데이터 수집 상태를 확인합니다.
    """
    return {
        "status": "available",
        "supported_platforms": {
            "gangnamunni": {
                "name": "강남언니",
                "categories": {
                    "hospital_question": "병원질문",
                    "surgery_question": "시술/수술질문",
                    "free_chat": "자유수다",
                    "review": "발품후기",
                    "ask_doctor": "의사에게 물어보세요"
                }
            },
            "babitalk": {
                "name": "바비톡",
                "categories": {
                    "surgery_review": "시술 후기",
                    "event_ask_memo": "발품후기 (카테고리 ID 필요)",
                    "talk": "자유톡 (서비스 ID 필요, 댓글 자동 수집)"
                },
                "event_ask_categories": {
                    3000: "눈",
                    3100: "코",
                    3200: "지방흡입/이식",
                    3300: "안면윤곽/양악",
                    3400: "가슴",
                    3500: "남자성형",
                    3600: "기타"
                },
                "talk_services": {
                    79: "성형",
                    71: "쁘띠/피부",
                    72: "일상"
                }
            }
        },
        "api_endpoints": {
            "강남언니": "/collect/gannamunni",
            "바비톡": "/collect/babitalk"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.post("/collect/gannamunni", response_model=CollectionResult)
async def collect_gannamunni_data(
    request: GangnamUnniCollectionRequest,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    강남언니 데이터를 수집합니다.
    """
    start_time = time.time()
    
    try:
        collector = GangnamUnniDataCollector(db.db_path)
        
        # 강남언니 데이터 수집
        result = await collector.collect_articles_by_date(
            target_date=request.target_date,
            category=request.category,
            save_as_reviews=request.save_as_reviews
        )
        
        execution_time = time.time() - start_time
        
        return CollectionResult(
            platform=PlatformType.GANGNAMUNNI,
            category=request.category,
            target_date=request.target_date,
            total_articles=result,
            total_comments=0,
            total_reviews=result if request.save_as_reviews else 0,
            execution_time=execution_time,
            status="success",
            message=f"강남언니 {request.category} 데이터 수집 완료",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"강남언니 데이터 수집 실패: {str(e)}"
        )

@router.post("/collect/babitalk", response_model=CollectionResult)
async def collect_babitalk_data(
    request: BabitalkCollectionRequest,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    바비톡 데이터를 수집합니다.
    카테고리에 따라 시술후기, 발품후기, 자유톡을 수집하며,
    자유톡 수집 시 댓글도 자동으로 수집됩니다.
    """
    start_time = time.time()
    
    try:
        collector = BabitalkDataCollector(db.db_path)
        
        if request.category == "surgery_review":
            # 시술후기 수집
            result = await collector.collect_reviews_by_date(
                target_date=request.target_date,
                limit=request.limit
            )
            
            execution_time = time.time() - start_time
            
            return CollectionResult(
                platform=PlatformType.BABITALK,
                category=request.category,
                target_date=request.target_date,
                total_articles=0,
                total_comments=0,
                total_reviews=result,
                execution_time=execution_time,
                status="success",
                message="바비톡 시술후기 수집 완료",
                timestamp=datetime.now()
            )
            
        elif request.category == "event_ask_memo":
            # 발품후기 수집 (카테고리 ID 필요)
            if not request.category_id:
                raise HTTPException(
                    status_code=400,
                    detail="발품후기 수집 시에는 category_id가 필요합니다."
                )
            
            result = await collector.collect_event_ask_memos_by_date(
                target_date=request.target_date,
                category_id=request.category_id,
                limit_per_page=request.limit
            )
            
            execution_time = time.time() - start_time
            
            return CollectionResult(
                platform=PlatformType.BABITALK,
                category=request.category,
                target_date=request.target_date,
                total_articles=0,
                total_comments=0,
                total_reviews=result,
                execution_time=execution_time,
                status="success",
                message=f"바비톡 발품후기 수집 완료 (카테고리: {request.category_id})",
                timestamp=datetime.now()
            )
            
        elif request.category == "talk":
            # 자유톡 수집 (서비스 ID 필요, 댓글 자동 수집)
            if not request.service_id:
                raise HTTPException(
                    status_code=400,
                    detail="자유톡 수집 시에는 service_id가 필요합니다."
                )
            
            # 자유톡 수집
            talks_result = await collector.collect_talks_by_date(
                target_date=request.target_date,
                service_id=request.service_id,
                limit_per_page=request.limit
            )
            
            # 자유톡에 대한 댓글 자동 수집
            comments_result = await collector.collect_comments_for_talks_by_date(
                target_date=request.target_date,
                service_id=request.service_id,
                limit_per_page=request.limit
            )
            
            execution_time = time.time() - start_time
            
            return CollectionResult(
                platform=PlatformType.BABITALK,
                category=request.category,
                target_date=request.target_date,
                total_articles=talks_result,
                total_comments=comments_result,
                total_reviews=0,
                execution_time=execution_time,
                status="success",
                message=f"바비톡 자유톡 수집 완료 (서비스: {request.service_id}), 댓글 {comments_result}개 자동 수집",
                timestamp=datetime.now()
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 바비톡 카테고리: {request.category}"
            )
            
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"바비톡 데이터 수집 실패: {str(e)}"
        )

 