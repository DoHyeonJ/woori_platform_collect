"""
비동기 데이터 수집 서비스
각 플랫폼별 데이터 수집을 비동기로 처리하는 서비스 함수들
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable

from collectors.babitalk_collector import BabitalkDataCollector
from collectors.gannamunni_collector import GangnamUnniDataCollector
from collectors.naver_collector import NaverDataCollector


class AsyncCollectionService:
    """비동기 데이터 수집 서비스"""
    
    @staticmethod
    async def collect_babitalk_data(
        target_date: str,
        categories: list = None,
        limit: int = 24,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        바비톡 데이터 비동기 수집
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD)
            categories: 수집할 카테고리 목록 ["reviews", "talks", "event_ask_memos"]
            limit: 페이지당 수집할 데이터 수
            progress_callback: 진행률 콜백 함수
            
        Returns:
            Dict[str, Any]: 수집 결과
        """
        if categories is None:
            categories = ["reviews", "talks", "event_ask_memos"]
        
        collector = BabitalkDataCollector()
        
        results = {
            "target_date": target_date,
            "total_articles": 0,
            "total_comments": 0,
            "total_reviews": 0,
            "category_results": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        total_categories = len(categories)
        completed_categories = 0
        
        try:
            if progress_callback:
                progress_callback(0, total_categories, "바비톡 데이터 수집 시작")
            
            # 1. 시술후기 수집
            if "reviews" in categories:
                if progress_callback:
                    progress_callback(completed_categories, total_categories, "시술후기 수집 중...")
                
                review_count = await collector.collect_reviews_by_date(target_date, limit_per_page=limit)
                results["total_reviews"] += review_count
                results["category_results"]["reviews"] = review_count
                completed_categories += 1
                
                await asyncio.sleep(1)  # API 호출 간격 조절
            
            # 2. 발품후기 수집
            if "event_ask_memos" in categories:
                if progress_callback:
                    progress_callback(completed_categories, total_categories, "발품후기 수집 중...")
                
                memo_results = await collector.collect_all_event_ask_memos_by_date(target_date, limit_per_page=limit)
                memo_total = sum(memo_results.values())
                results["total_articles"] += memo_total
                results["category_results"]["event_ask_memos"] = memo_results
                completed_categories += 1
                
                await asyncio.sleep(1)
            
            # 3. 자유톡 수집
            if "talks" in categories:
                if progress_callback:
                    progress_callback(completed_categories, total_categories, "자유톡 수집 중...")
                
                talk_results = await collector.collect_all_talks_by_date(target_date, limit_per_page=limit)
                talk_total = sum(talk_results.values())
                results["total_articles"] += talk_total
                results["category_results"]["talks"] = talk_results
                completed_categories += 1
                
                # 댓글 수집
                if progress_callback:
                    progress_callback(completed_categories - 0.5, total_categories, "자유톡 댓글 수집 중...")
                
                # 각 서비스별 댓글 수집
                comment_total = 0
                for service_id in collector.api.TALK_SERVICE_CATEGORIES.keys():
                    comments_count = await collector.collect_comments_for_talks_by_date(target_date, service_id, limit_per_page=limit)
                    comment_total += comments_count
                
                results["total_comments"] += comment_total
            
            if progress_callback:
                progress_callback(total_categories, total_categories, "바비톡 데이터 수집 완료")
            
            results["end_time"] = datetime.now().isoformat()
            results["status"] = "success"
            
            return results
            
        except Exception as e:
            results["end_time"] = datetime.now().isoformat()
            results["status"] = "error"
            results["error"] = str(e)
            return results
    
    @staticmethod
    async def collect_gangnamunni_data(
        target_date: str,
        categories: list = None,
        save_as_reviews: bool = False,
        limit: int = 0,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        강남언니 데이터 비동기 수집
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD)
            categories: 수집할 카테고리 목록
            save_as_reviews: 후기로 저장할지 여부
            limit: 수집할 최대 개수
            progress_callback: 진행률 콜백 함수
            
        Returns:
            Dict[str, Any]: 수집 결과
        """
        if categories is None:
            categories = ["hospital_question", "surgery_question", "free_chat", "review", "ask_doctor"]
        
        collector = GangnamUnniDataCollector()
        
        results = {
            "target_date": target_date,
            "total_articles": 0,
            "category_results": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        total_categories = len(categories)
        completed_categories = 0
        
        try:
            if progress_callback:
                progress_callback(0, total_categories, "강남언니 데이터 수집 시작")
            
            for category in categories:
                if progress_callback:
                    progress_callback(completed_categories, total_categories, f"{category} 카테고리 수집 중...")
                
                count = await collector.collect_articles_by_date(target_date, category, save_as_reviews)
                results["total_articles"] += count
                results["category_results"][category] = count
                completed_categories += 1
                
                await asyncio.sleep(2)  # API 호출 간격 조절
            
            if progress_callback:
                progress_callback(total_categories, total_categories, "강남언니 데이터 수집 완료")
            
            results["end_time"] = datetime.now().isoformat()
            results["status"] = "success"
            
            return results
            
        except Exception as e:
            results["end_time"] = datetime.now().isoformat()
            results["status"] = "error"
            results["error"] = str(e)
            return results
    
    @staticmethod
    async def collect_naver_data(
        cafe_id: str,
        target_date: str = None,
        menu_id: str = "",
        per_page: int = 20,
        naver_cookies: str = "",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        네이버 카페 데이터 비동기 수집
        
        Args:
            cafe_id: 카페 ID
            target_date: 수집할 날짜 (YYYY-MM-DD) - None이면 최신 게시글
            menu_id: 게시판 ID (빈 문자열이면 모든 게시판)
            per_page: 페이지당 게시글 수
            naver_cookies: 네이버 쿠키
            progress_callback: 진행률 콜백 함수
            
        Returns:
            Dict[str, Any]: 수집 결과
        """
        collector = NaverDataCollector(naver_cookies)
        
        results = {
            "cafe_id": cafe_id,
            "target_date": target_date,
            "total_articles": 0,
            "total_comments": 0,
            "board_results": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        try:
            if progress_callback:
                progress_callback(0, 1, "네이버 카페 데이터 수집 시작")
            
            if target_date:
                # 특정 날짜의 게시글과 댓글 수집
                if progress_callback:
                    progress_callback(0, 1, f"{target_date} 날짜 게시글 및 댓글 수집 중...")
                
                result = await collector.collect_articles_by_date_with_comments(cafe_id, target_date, menu_id)
                results["total_articles"] = result.get("saved", 0)
                results["total_comments"] = result.get("comments_saved", 0)
                results["details"] = result.get("details", [])
                
            else:
                # 최신 게시글 수집
                if menu_id:
                    # 특정 게시판
                    if progress_callback:
                        progress_callback(0, 1, f"게시판 {menu_id} 최신 게시글 수집 중...")
                    
                    count = await collector.collect_articles_by_menu(cafe_id, menu_id, per_page)
                    results["total_articles"] = count
                    results["board_results"][menu_id] = count
                else:
                    # 모든 게시판
                    if progress_callback:
                        progress_callback(0, 1, "모든 게시판 최신 게시글 수집 중...")
                    
                    board_results = await collector.collect_all_boards_articles(cafe_id, per_page)
                    results["total_articles"] = sum(board_results.values())
                    results["board_results"] = board_results
            
            if progress_callback:
                progress_callback(1, 1, "네이버 카페 데이터 수집 완료")
            
            results["end_time"] = datetime.now().isoformat()
            results["status"] = "success"
            
            return results
            
        except Exception as e:
            results["end_time"] = datetime.now().isoformat()
            results["status"] = "error"
            results["error"] = str(e)
            return results
