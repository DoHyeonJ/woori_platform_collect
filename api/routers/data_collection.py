from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import asyncio
import time
from datetime import datetime

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
                "name": "네이버 카페",
                "categories": {
                    "all_boards": "전체 게시판",
                    "specific_board": "특정 게시판",
                    "by_date": "날짜별"
                },
                "supported_cafes": {
                    "여우야": "10912875",
                    "A+여우야": "12285441",
                    "성형위키백과": "11498714",
                    "여생남정": "13067396",
                    "시크먼트": "23451561",
                    "가아사": "15880379",
                    "파우더룸": "10050813"
                }
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
async def get_naver_boards(
    cafe_id: str
):
    """
    네이버 카페의 게시판 목록을 조회합니다.
    
    게시판 목록은 공개 정보이므로 로그인이 필요하지 않습니다.
    """
    try:
        # 기본 쿠키 설정 (게시판 목록 조회용)
        default_cookies = "NID_AUT=; NID_SES=; NID_JKL="
        
        # 수집기 생성 (데이터베이스 저장 없이 게시판 목록만 조회)
        collector = NaverDataCollector("data/collect_data.db", default_cookies)
        
        # 게시판 목록 조회
        boards = await collector.collect_board_list(cafe_id)
        
        if boards is None:
            raise HTTPException(
                status_code=500,
                detail="게시판 목록 조회에 실패했습니다."
            )
        
        # 카페 이름 조회
        cafe_name = collector.api.get_cafe_name_by_id(cafe_id)
        
        # 응답 모델 생성
        board_info_list = []
        for board in boards:
            board_info_list.append({
                "menu_id": int(board.menu_id),  # int로 확실하게 변환
                "menu_name": board.menu_name,
                "menu_type": board.menu_type,
                "board_type": board.board_type,
                "sort": board.sort
            })
        
        return NaverBoardListResponse(
            cafe_id=cafe_id,
            cafe_name=cafe_name,
            boards=board_info_list,
            total_boards=len(boards),
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"게시판 목록 조회 실패: {str(e)}"
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
    카테고리에 따라 전체 게시판, 특정 게시판, 날짜별로 수집할 수 있습니다.
    
    request의 cookies 필드에 네이버 로그인 쿠키를 포함해야 합니다.
    예: NID_AUT=...; NID_SES=...
    """
    start_time = time.time()
    
    try:
        # 네이버 쿠키 검증
        if not request.cookies:
            raise HTTPException(
                status_code=400,
                detail="네이버 쿠키가 필요합니다. cookies 필드에 네이버 로그인 쿠키를 포함해주세요."
            )
        
        collector = NaverDataCollector(db.db_path, request.cookies)
        
        if request.category == "all_boards":
            # 전체 게시판 수집
            results = await collector.collect_all_boards_articles(
                cafe_id=request.cafe_id,
                per_page=request.limit
            )
            
            total_articles = sum(results.values())
            execution_time = time.time() - start_time
            
            return CollectionResult(
                platform=PlatformType.NAVER,
                category=request.category,
                target_date=request.target_date or datetime.now().strftime("%Y-%m-%d"),
                total_articles=total_articles,
                total_comments=0,
                total_reviews=0,
                execution_time=execution_time,
                status="success",
                message=f"네이버 카페 {request.cafe_id} 전체 게시판 수집 완료 (총 {total_articles}개)",
                timestamp=datetime.now()
            )
            
        elif request.category == "specific_board":
            # 특정 게시판 수집
            if not request.menu_id:
                raise HTTPException(
                    status_code=400,
                    detail="특정 게시판 수집 시에는 menu_id가 필요합니다."
                )
            
            result = await collector.collect_articles_by_menu(
                cafe_id=request.cafe_id,
                menu_id=request.menu_id,
                per_page=request.limit
            )
            
            execution_time = time.time() - start_time
            
            return CollectionResult(
                platform=PlatformType.NAVER,
                category=request.category,
                target_date=request.target_date or datetime.now().strftime("%Y-%m-%d"),
                total_articles=result,
                total_comments=0,
                total_reviews=0,
                execution_time=execution_time,
                status="success",
                message=f"네이버 카페 {request.cafe_id} 게시판 {request.menu_id} 수집 완료 ({result}개)",
                timestamp=datetime.now()
            )
            
        elif request.category == "by_date":
            # 날짜별 수집
            if not request.target_date:
                raise HTTPException(
                    status_code=400,
                    detail="날짜별 수집 시에는 target_date가 필요합니다."
                )
            
            result = await collector.collect_articles_by_date(
                cafe_id=request.cafe_id,
                target_date=request.target_date,
                menu_id=request.menu_id or "",
                per_page=request.limit
            )
            
            execution_time = time.time() - start_time
            
            return CollectionResult(
                platform=PlatformType.NAVER,
                category=request.category,
                target_date=request.target_date,
                total_articles=result,
                total_comments=0,
                total_reviews=0,
                execution_time=execution_time,
                status="success",
                message=f"네이버 카페 {request.cafe_id} {request.target_date} 날짜별 수집 완료 ({result}개)",
                timestamp=datetime.now()
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 네이버 카테고리: {request.category}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"네이버 데이터 수집 실패: {str(e)}"
        )

 