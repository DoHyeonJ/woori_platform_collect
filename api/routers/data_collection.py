from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Header, Query, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import asyncio
import time
from datetime import datetime
import logging

from api.models import (
    CollectionResult, PlatformType,
    GangnamUnniCollectionRequest, BabitalkCollectionRequest, NaverCollectionRequest,
    NaverBoardListResponse
)
from api.dependencies import get_database_manager
from database.models import DatabaseManager

# 수집기 import
from collectors.gannamunni_collector import GangnamUnniDataCollector
from collectors.babitalk_collector import BabitalkDataCollector
from collectors.naver_collector import NaverDataCollector

# 로거 설정
logger = logging.getLogger(__name__)

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
            },
            "naver": {
                "description": "네이버 카페 데이터 수집",
                "endpoints": {
                    "GET /boards/naver/{cafe_id}": "게시판 목록 조회 (쿠키 불필요)",
                    "GET /content/naver/{cafe_id}": "게시글 제목과 내용 조회 (쿠키 불필요)",
                    "POST /collect/naver": "게시글 수집 및 저장 (쿠키 필요)",
                    "POST /collect/naver/detailed": "상세 내용과 함께 게시글 수집 (쿠키 필요)"
                },
                "supported_cafes": [
                    "여우야 (10912875)", "A+여우야 (12285441)", "성형위키백과 (11498714)",
                    "여생남정 (13067396)", "시크먼트 (23451561)", "가아사 (15880379)", "파우더룸 (10050813)"
                ]
            }
        },
        "api_endpoints": {
            "강남언니": "/collect/gannamunni",
            "바비톡": "/collect/babitalk",
            "네이버": "/collect/naver",
            "네이버 게시판 목록": "/boards/naver/{cafe_id}"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/boards/naver/{cafe_id}", response_model=NaverBoardListResponse)
async def get_naver_board_list(
    cafe_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """네이버 카페 게시판 목록 조회 (쿠키 불필요)"""
    try:
        from platforms.naver import NaverCafeAPI
        
        # 기본 쿠키로 API 생성 (게시판 목록은 공개 정보)
        api = NaverCafeAPI()
        boards = await api.get_board_list(cafe_id)
        
        if boards:
            return NaverBoardListResponse(
                cafe_id=cafe_id,
                boards=boards,
                total=len(boards)
            )
        else:
            return NaverBoardListResponse(
                cafe_id=cafe_id,
                boards=[],
                total=0
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"게시판 목록 조회 실패: {str(e)}"
        )

@router.get("/content/naver/{cafe_id}", response_model=Dict[str, Any])
async def get_naver_board_content(
    cafe_id: str,
    menu_id: str = Query("", description="게시판 ID (비워두면 전체)"),
    per_page: int = Query(5, ge=1, le=20, description="가져올 게시글 수 (1-20)")
):
    """네이버 카페 게시글 제목과 내용 조회 (쿠키 불필요)"""
    try:
        from platforms.naver import NaverCafeAPI
        
        api = NaverCafeAPI()
        result = await api.get_board_title_and_content(cafe_id, menu_id, per_page)
        
        return {
            "cafe_id": cafe_id,
            "menu_id": menu_id,
            "per_page": per_page,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"게시글 내용 조회 실패: {str(e)}"
        )



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

@router.post("/collect/naver", response_model=CollectionResult)
async def collect_naver_data(
    request: NaverCollectionRequest,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    네이버 카페 데이터를 수집합니다.
    target_date가 지정되면 해당 날짜의 게시글을, 비워두면 오늘 날짜의 게시글을 수집합니다.
    limit이 0이면 제한없이 수집하고, 1-100이면 지정된 수만큼 수집합니다.
    
    기본값:
    - cafe_id: 12285441 (A+여우야★성형카페)
    - target_date: 오늘 날짜
    - menu_id: 38
    - limit: 20
    - cookies: 빈 값 (공개 정보만 수집)
    """
    start_time = time.time()
    
    try:
        # 기본값 설정
        cafe_id = request.cafe_id or "12285441"
        target_date = request.target_date or datetime.now().strftime("%Y-%m-%d")
        menu_id = request.menu_id or "38"
        limit = request.limit if request.limit > 0 else 20
        cookies = request.cookies or ""
        
        # 로깅
        logger.info(f"네이버 수집 시작 - 카페: {cafe_id}, 날짜: {target_date}, 게시판: {menu_id}, 제한: {limit}")
        
        # 수집기 생성
        collector = NaverDataCollector(db.db_path, cookies)
        
        # target_date가 지정된 경우 날짜별 수집
        if target_date:
            if request.limit == 0:
                # 날짜별 전체 게시글 수집 (댓글 포함)
                result = await collector.collect_articles_by_date_with_comments(
                    cafe_id=cafe_id,
                    target_date=target_date,
                    menu_id=menu_id
                )
                
                execution_time = time.time() - start_time
                
                return CollectionResult(
                    platform=PlatformType.NAVER,
                    category="by_date",
                    target_date=target_date,
                    total_articles=result.get('saved', 0),
                    total_comments=result.get('comments_saved', 0),
                    total_reviews=0,
                    execution_time=execution_time,
                    status="success",
                    message=f"네이버 카페 {cafe_id} {target_date} 날짜별 전체 수집 완료 (게시글: {result.get('saved', 0)}개, 댓글: {result.get('comments_saved', 0)}개)",
                    timestamp=datetime.now()
                )
            else:
                # 날짜별 제한 수집 (댓글 포함)
                result = await collector.collect_articles_with_content_and_comments(
                    cafe_id=cafe_id,
                    menu_id=menu_id,
                    per_page=limit,
                    target_date=target_date
                )
                
                execution_time = time.time() - start_time
                
                return CollectionResult(
                    platform=PlatformType.NAVER,
                    category="by_date",
                    target_date=target_date,
                    total_articles=result.get('saved', 0),
                    total_comments=result.get('comments_saved', 0),
                    total_reviews=0,
                    execution_time=execution_time,
                    status="success",
                    message=f"네이버 카페 {cafe_id} {target_date} 날짜별 제한 수집 완료 (게시글: {result.get('saved', 0)}개, 댓글: {result.get('comments_saved', 0)}개)",
                    timestamp=datetime.now()
                )
        else:
            # target_date가 없는 경우 최신 게시글 수집
            if request.menu_id:
                # 특정 게시판 수집
                result = await collector.collect_articles_with_content_and_comments(
                    cafe_id=cafe_id,
                    menu_id=request.menu_id,
                    per_page=request.limit if request.limit > 0 else 100,
                    target_date=request.target_date
                )
                
                execution_time = time.time() - start_time
                
                return CollectionResult(
                    platform=PlatformType.NAVER,
                    category="specific_board",
                    target_date=request.target_date,
                    total_articles=result.get('saved', 0),
                    total_comments=result.get('comments_saved', 0),
                    total_reviews=0,
                    execution_time=execution_time,
                    status="success",
                    message=f"네이버 카페 {cafe_id} 게시판 {request.menu_id} 최신 수집 완료 (게시글: {result.get('saved', 0)}개, 댓글: {result.get('comments_saved', 0)}개)",
                    timestamp=datetime.now()
                )
            else:
                # 전체 게시판 수집
                results = await collector.collect_all_boards_articles(
                    cafe_id=cafe_id,
                    per_page=limit
                )
                
                total_articles = sum(results.values())
                execution_time = time.time() - start_time
                
                return CollectionResult(
                    platform=PlatformType.NAVER,
                    category="all_boards",
                    target_date=datetime.now().strftime("%Y-%m-%d"),
                    total_articles=total_articles,
                    total_comments=0,
                    total_reviews=0,
                    execution_time=execution_time,
                    status="success",
                    message=f"네이버 카페 {cafe_id} 전체 게시판 최신 수집 완료 (총 {total_articles}개)",
                    timestamp=datetime.now()
                )
            
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"네이버 데이터 수집 실패: {str(e)}"
        )

 