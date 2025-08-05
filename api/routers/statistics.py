from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime

from api.models import StatisticsResponse, PlatformType
from api.dependencies import get_database_manager
from database.models import DatabaseManager

router = APIRouter()

@router.get("/overview", response_model=StatisticsResponse)
async def get_statistics_overview(
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    전체 통계 정보를 조회합니다.
    """
    try:
        # 기본 통계 정보 조회
        stats = db.get_statistics()
        
        return StatisticsResponse(
            total_communities=stats.get("total_communities", 0),
            total_articles=stats.get("total_articles", 0),
            total_reviews=stats.get("total_reviews", 0),
            total_comments=stats.get("total_comments", 0),
            platform_statistics=stats.get("platform_statistics", {}),
            review_statistics=stats.get("review_statistics", {}),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 실패: {str(e)}"
        )

@router.get("/platform/{platform}")
async def get_platform_statistics(
    platform: PlatformType,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    특정 플랫폼의 통계 정보를 조회합니다.
    """
    try:
        # 플랫폼별 통계 조회
        platform_stats = db.get_platform_statistics(platform.value)
        
        return {
            "platform": platform.value,
            "statistics": platform_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"플랫폼 통계 조회 실패: {str(e)}"
        )

@router.get("/daily")
async def get_daily_statistics(
    date: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    특정 날짜의 통계 정보를 조회합니다.
    """
    try:
        # 날짜별 통계 조회
        daily_stats = db.get_daily_statistics(date)
        
        return {
            "date": date,
            "statistics": daily_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"일별 통계 조회 실패: {str(e)}"
        )

@router.get("/trends")
async def get_trend_statistics(
    days: int = 7,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    최근 N일간의 트렌드 통계를 조회합니다.
    """
    try:
        # 트렌드 통계 조회
        trend_stats = db.get_trend_statistics(days)
        
        return {
            "period_days": days,
            "trends": trend_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"트렌드 통계 조회 실패: {str(e)}"
        ) 