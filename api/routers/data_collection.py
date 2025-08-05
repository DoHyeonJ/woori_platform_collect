from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio
import time
from datetime import datetime

from api.models import (
    CollectionRequest, BatchCollectionRequest, CollectionResult, 
    BatchCollectionResult, PlatformType, CategoryType
)
from api.dependencies import get_database_manager
from database.models import DatabaseManager

# 수집기 import
from collectors.gannamunni_collector import GangnamUnniDataCollector
from collectors.babitalk_collector import BabitalkDataCollector

router = APIRouter()

@router.post("/collect", response_model=CollectionResult)
async def collect_data(
    request: CollectionRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    특정 플랫폼과 카테고리의 데이터를 수집합니다.
    """
    start_time = time.time()
    
    try:
        if request.platform == PlatformType.GANGNAMUNNI:
            collector = GangnamUnniDataCollector(db.db_path)
            
            # 강남언니 카테고리 매핑
            category_mapping = {
                CategoryType.HOSPITAL_QUESTION: "hospital_question",
                CategoryType.SURGERY_QUESTION: "surgery_question", 
                CategoryType.FREE_CHAT: "free_chat",
                CategoryType.REVIEW: "review",
                CategoryType.ASK_DOCTOR: "ask_doctor"
            }
            
            category = category_mapping.get(request.category, "hospital_question")
            
            # 단일 카테고리 수집
            result = await collector.collect_articles_by_date(
                target_date=request.target_date,
                category=category,
                save_as_reviews=request.save_as_reviews
            )
            
            execution_time = time.time() - start_time
            
            return CollectionResult(
                platform=request.platform,
                category=request.category,
                target_date=request.target_date,
                total_articles=result,
                total_comments=0,  # 강남언니는 댓글 수를 별도로 계산하지 않음
                total_reviews=result if request.save_as_reviews else 0,
                execution_time=execution_time,
                status="success",
                message=f"강남언니 {category} 데이터 수집 완료",
                timestamp=datetime.now()
            )
            
        elif request.platform == PlatformType.BABITALK:
            collector = BabitalkDataCollector(db.db_path)
            
            # 바비톡 카테고리별 수집
            if request.category == CategoryType.SURGERY_REVIEW:
                result = await collector.collect_reviews_by_date(
                    target_date=request.target_date,
                    limit=request.limit
                )
                
                execution_time = time.time() - start_time
                
                return CollectionResult(
                    platform=request.platform,
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
                
            elif request.category == CategoryType.EVENT_ASK_MEMO:
                result = await collector.collect_all_event_ask_memos_by_date(
                    target_date=request.target_date,
                    limit=request.limit
                )
                
                execution_time = time.time() - start_time
                
                return CollectionResult(
                    platform=request.platform,
                    category=request.category,
                    target_date=request.target_date,
                    total_articles=0,
                    total_comments=0,
                    total_reviews=result,
                    execution_time=execution_time,
                    status="success",
                    message="바비톡 발품후기 수집 완료",
                    timestamp=datetime.now()
                )
                
            elif request.category == CategoryType.TALK:
                result = await collector.collect_all_talks_by_date(
                    target_date=request.target_date,
                    limit=request.limit
                )
                
                execution_time = time.time() - start_time
                
                return CollectionResult(
                    platform=request.platform,
                    category=request.category,
                    target_date=request.target_date,
                    total_articles=result,
                    total_comments=0,
                    total_reviews=0,
                    execution_time=execution_time,
                    status="success",
                    message="바비톡 자유톡 수집 완료",
                    timestamp=datetime.now()
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"지원하지 않는 바비톡 카테고리: {request.category}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 플랫폼: {request.platform}"
            )
            
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"데이터 수집 실패: {str(e)}"
        )

@router.post("/collect/batch", response_model=BatchCollectionResult)
async def collect_batch_data(
    request: BatchCollectionRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    특정 플랫폼의 모든 카테고리 데이터를 배치로 수집합니다.
    """
    start_time = time.time()
    
    try:
        if request.platform == PlatformType.GANGNAMUNNI:
            collector = GangnamUnniDataCollector(db.db_path)
            
            # 모든 카테고리 수집
            result = await collector.collect_all_categories_by_date(
                target_date=request.target_date,
                save_as_reviews=request.save_as_reviews
            )
            
            execution_time = time.time() - start_time
            
            # 카테고리별 결과 구성
            categories = {}
            total_articles = sum(result.values())
            
            for category, count in result.items():
                categories[category] = CollectionResult(
                    platform=request.platform,
                    category=CategoryType(category),
                    target_date=request.target_date,
                    total_articles=count,
                    total_comments=0,
                    total_reviews=count if request.save_as_reviews else 0,
                    execution_time=execution_time,
                    status="success",
                    message=f"강남언니 {category} 수집 완료",
                    timestamp=datetime.now()
                )
            
            return BatchCollectionResult(
                platform=request.platform,
                target_date=request.target_date,
                categories=categories,
                total_articles=total_articles,
                total_comments=0,
                total_reviews=total_articles if request.save_as_reviews else 0,
                execution_time=execution_time,
                status="success",
                message="강남언니 전체 카테고리 수집 완료",
                timestamp=datetime.now()
            )
            
        elif request.platform == PlatformType.BABITALK:
            collector = BabitalkDataCollector(db.db_path)
            
            # 바비톡 모든 카테고리 수집
            categories = {}
            total_articles = 0
            total_reviews = 0
            
            # 시술후기 수집
            surgery_reviews = await collector.collect_reviews_by_date(
                target_date=request.target_date,
                limit=request.limit
            )
            total_reviews += surgery_reviews
            
            categories["surgery_review"] = CollectionResult(
                platform=request.platform,
                category=CategoryType.SURGERY_REVIEW,
                target_date=request.target_date,
                total_articles=0,
                total_comments=0,
                total_reviews=surgery_reviews,
                execution_time=0,
                status="success",
                message="바비톡 시술후기 수집 완료",
                timestamp=datetime.now()
            )
            
            # 발품후기 수집
            event_ask_reviews = await collector.collect_all_event_ask_memos_by_date(
                target_date=request.target_date,
                limit=request.limit
            )
            total_reviews += event_ask_reviews
            
            categories["event_ask_memo"] = CollectionResult(
                platform=request.platform,
                category=CategoryType.EVENT_ASK_MEMO,
                target_date=request.target_date,
                total_articles=0,
                total_comments=0,
                total_reviews=event_ask_reviews,
                execution_time=0,
                status="success",
                message="바비톡 발품후기 수집 완료",
                timestamp=datetime.now()
            )
            
            # 자유톡 수집
            talks = await collector.collect_all_talks_by_date(
                target_date=request.target_date,
                limit=request.limit
            )
            total_articles += talks
            
            categories["talk"] = CollectionResult(
                platform=request.platform,
                category=CategoryType.TALK,
                target_date=request.target_date,
                total_articles=talks,
                total_comments=0,
                total_reviews=0,
                execution_time=0,
                status="success",
                message="바비톡 자유톡 수집 완료",
                timestamp=datetime.now()
            )
            
            execution_time = time.time() - start_time
            
            return BatchCollectionResult(
                platform=request.platform,
                target_date=request.target_date,
                categories=categories,
                total_articles=total_articles,
                total_comments=0,
                total_reviews=total_reviews,
                execution_time=execution_time,
                status="success",
                message="바비톡 전체 카테고리 수집 완료",
                timestamp=datetime.now()
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 플랫폼: {request.platform}"
            )
            
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"배치 데이터 수집 실패: {str(e)}"
        )

@router.get("/status")
async def get_collection_status():
    """
    데이터 수집 상태를 확인합니다.
    """
    return {
        "status": "available",
        "supported_platforms": ["gangnamunni", "babitalk"],
        "supported_categories": {
            "gangnamunni": ["hospital_question", "surgery_question", "free_chat", "review", "ask_doctor"],
            "babitalk": ["surgery_review", "event_ask_memo", "talk"]
        },
        "timestamp": datetime.now().isoformat()
    } 