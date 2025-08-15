#!/usr/bin/env python3
"""
네이버 카페 데이터 수집기
"""
import os
import sys
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

# utils 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import LoggedClass
from platforms.naver import NaverCafeAPI, NaverCafeMenu, NaverCafeArticle
from database.models import DatabaseManager, Article

class NaverDataCollector(LoggedClass):
    """네이버 카페 데이터 수집기"""
    
    def __init__(self, db_path: str, naver_cookies: str = ""):
        super().__init__()
        self.db_path = db_path
        self.naver_cookies = naver_cookies
        self.api = NaverCafeAPI(naver_cookies)
        self.db = DatabaseManager(db_path)
        
        # 네이버 커뮤니티 ID (기본값)
        self.naver_community_id = 1  # 데이터베이스에 미리 설정된 값
    
    async def collect_board_list(self, cafe_id: str) -> List[NaverCafeMenu]:
        """게시판 목록 수집"""
        try:
            self.log_info(f"게시판 목록 수집 시작 (카페 ID: {cafe_id})")
            
            boards = await self.api.get_board_list(cafe_id)
            
            if boards:
                self.log_info(f"게시판 {len(boards)}개 수집 완료")
                for board in boards:
                    self.log_info(f"  - {board.menu_name} (ID: {board.menu_id}, 타입: {board.menu_type})")
            else:
                self.log_warning("수집된 게시판이 없습니다")
            
            return boards
            
        except Exception as e:
            self.log_error(f"게시판 목록 수집 실패: {str(e)}")
            return []
    
    async def collect_articles_by_menu(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> int:
        """특정 게시판의 게시글 수집"""
        try:
            self.log_info(f"게시글 수집 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id})")
            
            # 게시글과 내용 함께 조회
            articles = await self.api.get_articles_with_content(cafe_id, menu_id, per_page)
            
            if not articles:
                self.log_warning("수집된 게시글이 없습니다")
                return 0
            
            # 데이터베이스에 저장
            saved_count = 0
            for article in articles:
                try:
                    if await self._save_article(cafe_id, article):
                        saved_count += 1
                except Exception as e:
                    self.log_error(f"게시글 {article.article_id} 저장 실패: {str(e)}")
                    continue
            
            self.log_info(f"게시글 수집 완료: {saved_count}/{len(articles)}개 저장")
            return saved_count
            
        except Exception as e:
            self.log_error(f"게시글 수집 실패: {str(e)}")
            return 0
    
    async def collect_articles_by_date(self, cafe_id: str, target_date: str, menu_id: str = "", per_page: int = 20) -> int:
        """특정 날짜의 게시글 수집"""
        try:
            self.log_info(f"날짜별 게시글 수집 시작 (카페 ID: {cafe_id}, 날짜: {target_date})")
            
            # 게시글과 내용 함께 조회
            articles = await self.api.get_articles_with_content(cafe_id, menu_id, per_page)
            
            if not articles:
                self.log_warning("수집된 게시글이 없습니다")
                return 0
            
            # 날짜 필터링 (필요시 구현)
            # 현재는 모든 게시글을 수집
            
            # 데이터베이스에 저장
            saved_count = 0
            for article in articles:
                try:
                    if await self._save_article(cafe_id, article):
                        saved_count += 1
                except Exception as e:
                    self.log_error(f"게시글 {article.article_id} 저장 실패: {str(e)}")
                    continue
            
            self.log_info(f"날짜별 게시글 수집 완료: {saved_count}/{len(articles)}개 저장")
            return saved_count
            
        except Exception as e:
            self.log_error(f"날짜별 게시글 수집 실패: {str(e)}")
            return 0
    
    async def collect_all_boards_articles(self, cafe_id: str, per_page: int = 20) -> Dict[str, int]:
        """모든 게시판의 게시글 수집"""
        try:
            self.log_info(f"전체 게시판 게시글 수집 시작 (카페 ID: {cafe_id})")
            
            # 게시판 목록 조회
            boards = await self.collect_board_list(cafe_id)
            
            if not boards:
                self.log_warning("수집할 게시판이 없습니다")
                return {}
            
            results = {}
            
            # 각 게시판별로 게시글 수집
            for board in boards:
                try:
                    self.log_info(f"게시판 '{board.menu_name}' 게시글 수집 시작")
                    
                    count = await self.collect_articles_by_menu(cafe_id, board.menu_id, per_page)
                    results[board.menu_name] = count
                    
                    # API 호출 간격 조절
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.log_error(f"게시판 '{board.menu_name}' 게시글 수집 실패: {str(e)}")
                    results[board.menu_name] = 0
                    continue
            
            total_articles = sum(results.values())
            self.log_info(f"전체 게시판 게시글 수집 완료: 총 {total_articles}개")
            
            return results
            
        except Exception as e:
            self.log_error(f"전체 게시판 게시글 수집 실패: {str(e)}")
            return {}
    
    async def _save_article(self, cafe_id: str, article: NaverCafeArticle) -> bool:
        """게시글을 데이터베이스에 저장"""
        try:
            # 카페 이름 조회
            cafe_name = self.api.get_cafe_name_by_id(cafe_id)
            if not cafe_name:
                cafe_name = f"카페_{cafe_id}"
            
            # 이미 저장된 게시글인지 확인
            existing = self.db.get_article_by_platform_id_and_community_article_id("naver", article.article_id)
            if existing:
                self.log_info(f"게시글 {article.article_id}는 이미 저장되어 있습니다")
                return False
            
            # Article 객체 생성
            db_article = Article(
                id=None,
                platform_id="naver",
                community_article_id=str(article.article_id),
                community_id=self.naver_community_id,
                title=article.subject,
                content=article.content or "",
                images="[]",  # 네이버 카페는 이미지 정보를 별도로 처리하지 않음
                writer_nickname=article.writer_nickname,
                writer_id=article.writer_id,
                like_count=article.like_count or 0,
                comment_count=article.comment_count or 0,
                view_count=article.view_count or 0,
                created_at=article.created_at,
                category_name=cafe_name,
                collected_at=datetime.now()
            )
            
            # 데이터베이스에 저장
            article_id = self.db.insert_article(db_article)
            
            if article_id:
                self.log_info(f"게시글 {article.article_id} 저장 완료 (DB ID: {article_id})")
                return True
            else:
                self.log_error(f"게시글 {article.article_id} 저장 실패")
                return False
                
        except Exception as e:
            self.log_error(f"게시글 저장 중 오류 발생: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """수집 통계 조회"""
        try:
            # 네이버 게시글 수
            naver_articles = self.db.get_articles_count_by_filters({"platform_id": "naver"})
            
            # 카페별 통계
            cafe_stats = {}
            for cafe_name, cafe_id in self.api.list_cafes().items():
                cafe_articles = self.db.get_articles_count_by_filters({
                    "platform_id": "naver",
                    "category_name": cafe_name
                })
                cafe_stats[cafe_name] = cafe_articles
            
            return {
                "total_articles": naver_articles,
                "by_cafe": cafe_stats,
                "supported_cafes": self.api.list_cafes(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log_error(f"통계 조회 실패: {str(e)}")
            return {}
    
    async def test_collection(self, cafe_id: str = "10912875") -> Dict[str, Any]:
        """수집 테스트"""
        try:
            self.log_info(f"네이버 수집 테스트 시작 (카페 ID: {cafe_id})")
            
            # 게시판 목록 조회 테스트
            boards = await self.collect_board_list(cafe_id)
            
            # 첫 번째 게시판의 게시글 수집 테스트
            test_result = {}
            if boards:
                first_board = boards[0]
                test_result["board_test"] = {
                    "board_name": first_board.menu_name,
                    "board_id": first_board.menu_id,
                    "board_type": first_board.menu_type
                }
                
                # 게시글 5개만 테스트 수집
                articles_count = await self.collect_articles_by_menu(
                    cafe_id=cafe_id,
                    menu_id=str(first_board.menu_id),  # int를 str로 변환
                    per_page=5
                )
                test_result["articles_test"] = {
                    "requested": 5,
                    "collected": articles_count
                }
            
            # 통계 조회
            stats = self.get_collection_stats()
            test_result["stats"] = stats
            
            self.log_info("네이버 수집 테스트 완료")
            return test_result
            
        except Exception as e:
            self.log_error(f"네이버 수집 테스트 실패: {str(e)}")
            return {"error": str(e)}
