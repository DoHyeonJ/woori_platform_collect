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
        self.naver_community_id = 3  # 네이버 커뮤니티 ID
    
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
    
    async def collect_board_title_and_content(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> str:
        """게시판의 게시글 제목과 내용을 함께 조회"""
        try:
            self.log_info(f"게시글 제목과 내용 조회 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id})")
            
            # API를 통해 게시글 제목과 내용 조회
            result = await self.api.get_board_title_and_content(cafe_id, menu_id, per_page)
            
            if result:
                self.log_info(f"게시글 제목과 내용 조회 완료: {per_page}개")
                return result
            else:
                self.log_warning("게시글 제목과 내용 조회 실패")
                return "게시글 조회에 실패했습니다."
                
        except Exception as e:
            self.log_error(f"게시글 제목과 내용 조회 중 오류 발생: {str(e)}")
            return f"게시글 조회 오류: {str(e)}"
    
    async def collect_articles_with_detailed_content(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> Dict[str, Any]:
        """게시글을 상세 내용과 함께 수집하고 데이터베이스에 저장"""
        try:
            self.log_info(f"상세 내용과 함께 게시글 수집 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id})")
            
            # 게시글과 내용 함께 조회
            articles = await self.api.get_articles_with_content(cafe_id, menu_id, per_page)
            
            if not articles:
                self.log_warning("수집된 게시글이 없습니다")
                return {"total": 0, "saved": 0, "failed": 0, "details": []}
            
            # 데이터베이스에 저장
            saved_count = 0
            failed_count = 0
            details = []
            
            for i, article in enumerate(articles):
                try:
                    self.log_info(f"게시글 {i+1}/{len(articles)} 저장 중...")
                    
                    if await self._save_article(cafe_id, article):
                        saved_count += 1
                        details.append({
                            "article_id": article.article_id,
                            "title": article.subject,
                            "status": "success",
                            "content_length": len(article.content or "")
                        })
                    else:
                        failed_count += 1
                        details.append({
                            "article_id": article.article_id,
                            "title": article.subject,
                            "status": "failed",
                            "reason": "이미 저장된 게시글이거나 저장 실패"
                        })
                        
                except Exception as e:
                    failed_count += 1
                    self.log_error(f"게시글 {article.article_id} 저장 실패: {str(e)}")
                    details.append({
                        "article_id": article.article_id,
                        "title": article.subject,
                        "status": "error",
                        "reason": str(e)
                    })
                    continue
            
            result = {
                "total": len(articles),
                "saved": saved_count,
                "failed": failed_count,
                "details": details
            }
            
            self.log_info(f"상세 내용과 함께 게시글 수집 완료: {saved_count}/{len(articles)}개 저장")
            return result
            
        except Exception as e:
            self.log_error(f"상세 내용과 함께 게시글 수집 실패: {str(e)}")
            return {"total": 0, "saved": 0, "failed": 0, "details": [], "error": str(e)}
    
    async def collect_articles_with_content_and_comments(self, cafe_id: str, menu_id: str = "", per_page: int = 20, target_date: Optional[str] = None) -> Dict[str, Any]:
        """게시글을 상세 내용과 댓글과 함께 수집하고 데이터베이스에 저장"""
        try:
            self.log_info(f"상세 내용과 댓글과 함께 게시글 수집 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id}, 날짜: {target_date})")
            
            # 게시글과 댓글 함께 조회
            articles_data = await self.api.get_articles_with_content_and_comments(cafe_id, menu_id, per_page, target_date)
            
            if not articles_data:
                self.log_warning("수집된 게시글이 없습니다")
                return {"total": 0, "saved": 0, "failed": 0, "comments_saved": 0, "details": []}
            
            # 데이터베이스에 저장
            saved_count = 0
            failed_count = 0
            comments_saved_count = 0
            details = []
            
            for i, article_data in enumerate(articles_data):
                try:
                    self.log_info(f"게시글 {i+1}/{len(articles_data)} 저장 중...")
                    
                    article = article_data['article']
                    comments = article_data['comments']
                    
                    # 게시글 저장
                    if await self._save_article(cafe_id, article):
                        saved_count += 1
                        
                        # 댓글 저장
                        if comments:
                            comment_saved = await self._save_comments(cafe_id, article.article_id, comments)
                            comments_saved_count += comment_saved
                            self.log_info(f"게시글 {article.article_id} 댓글 {comment_saved}/{len(comments)}개 저장 완료")
                        
                        details.append({
                            "article_id": article.article_id,
                            "title": article.subject,
                            "status": "success",
                            "content_length": len(article.content or ""),
                            "comments_saved": len(comments)
                        })
                    else:
                        failed_count += 1
                        details.append({
                            "article_id": article.article_id,
                            "title": article.subject,
                            "status": "failed",
                            "reason": "이미 저장된 게시글이거나 저장 실패"
                        })
                        
                except Exception as e:
                    failed_count += 1
                    self.log_error(f"게시글 {article.article_id} 저장 실패: {str(e)}")
                    details.append({
                        "article_id": article.article_id,
                        "title": article.subject,
                        "status": "error",
                        "reason": str(e)
                    })
                    continue
            
            result = {
                "total": len(articles_data),
                "saved": saved_count,
                "failed": failed_count,
                "comments_saved": comments_saved_count,
                "details": details
            }
            
            self.log_info(f"상세 내용과 댓글과 함께 게시글 수집 완료: {saved_count}/{len(articles_data)}개 저장, 댓글 {comments_saved_count}개 저장")
            return result
            
        except Exception as e:
            self.log_error(f"상세 내용과 댓글과 함께 게시글 수집 실패: {str(e)}")
            return {"total": 0, "saved": 0, "failed": 0, "comments_saved": 0, "details": [], "error": str(e)}
    
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
    
    async def collect_articles_by_date_with_comments(self, cafe_id: str, target_date: str, menu_id: str = "") -> Dict[str, Any]:
        """특정 날짜의 모든 게시글을 수집하고 댓글까지 포함하여 저장"""
        try:
            self.log_info(f"날짜별 게시글과 댓글 전체 수집 시작 (카페 ID: {cafe_id}, 날짜: {target_date})")
            
            # 날짜를 datetime 객체로 변환
            from datetime import datetime
            try:
                target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
                self.log_info(f"대상 날짜: {target_datetime}")
            except ValueError as e:
                self.log_error(f"날짜 형식 오류: {target_date}, 예상 형식: YYYY-MM-DD")
                return {"total": 0, "saved": 0, "failed": 0, "comments_saved": 0, "details": [], "error": f"날짜 형식 오류: {str(e)}"}
            
            # 게시글 목록 조회 (페이지네이션 없이 모든 게시글)
            all_articles = []
            page = 1
            per_page = 100  # 한 번에 100개씩 조회
            
            while True:
                try:
                    self.log_info(f"게시글 목록 조회 중... (페이지: {page})")
                    
                    articles = await self.api.get_article_list(cafe_id, menu_id, page, per_page)
                    
                    if not articles:
                        self.log_info(f"페이지 {page}에서 더 이상 게시글이 없습니다")
                        break
                    
                    # 해당 날짜의 게시글만 필터링
                    date_filtered_articles = []
                    for article in articles:
                        if article.created_at:
                            article_date = article.created_at.date()
                            if article_date == target_datetime.date():
                                date_filtered_articles.append(article)
                    
                    if date_filtered_articles:
                        all_articles.extend(date_filtered_articles)
                        self.log_info(f"페이지 {page}에서 {len(date_filtered_articles)}개 게시글 필터링 완료")
                    
                    # 마지막 게시글의 생성일이 대상 날짜보다 이전이면 중단
                    if articles and articles[-1].created_at:
                        last_article_date = articles[-1].created_at.date()
                        if last_article_date < target_datetime.date():
                            self.log_info(f"마지막 게시글 날짜({last_article_date})가 대상 날짜({target_datetime.date()})보다 이전이므로 중단")
                            break
                    
                    page += 1
                    
                    # API 호출 간격 조절
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.log_error(f"페이지 {page} 조회 실패: {str(e)}")
                    break
            
            if not all_articles:
                self.log_warning(f"{target_date} 날짜에 해당하는 게시글이 없습니다")
                return {"total": 0, "saved": 0, "failed": 0, "comments_saved": 0, "details": [], "message": "해당 날짜의 게시글이 없습니다"}
            
            self.log_info(f"총 {len(all_articles)}개 게시글 필터링 완료")
            
            # 각 게시글의 내용과 댓글 조회
            saved_count = 0
            failed_count = 0
            comments_saved_count = 0
            details = []
            
            for i, article in enumerate(all_articles):
                try:
                    self.log_info(f"게시글 {i+1}/{len(all_articles)} 처리 중... (ID: {article.article_id})")
                    
                    # 게시글 내용 조회
                    content_html, created_at = await self.api.get_article_content(cafe_id, article.article_id)
                    if content_html:
                        article.content = self.api.parse_content_html(content_html)
                        self.log_info(f"게시글 {article.article_id} 내용 파싱 완료")
                        
                        # 생성일이 없는 경우 내용 조회에서 얻은 정보로 업데이트
                        if not article.created_at and created_at:
                            article.created_at = created_at
                            self.log_info(f"게시글 {article.article_id} 생성일 업데이트: {created_at}")
                    else:
                        self.log_warning(f"게시글 {article.article_id} 내용 조회 실패")
                        article.content = ""
                    
                    # 댓글 조회
                    comments = await self.api.get_article_comments(cafe_id, article.article_id)
                    self.log_info(f"게시글 {article.article_id} 댓글 {len(comments)}개 조회 완료")
                    
                    # 게시글 저장
                    if await self._save_article(cafe_id, article):
                        saved_count += 1
                        
                        # 댓글 저장
                        if comments:
                            comment_saved = await self._save_comments(cafe_id, article.article_id, comments)
                            comments_saved_count += comment_saved
                            self.log_info(f"게시글 {article.article_id} 댓글 {comment_saved}/{len(comments)}개 저장 완료")
                        
                        details.append({
                            "article_id": article.article_id,
                            "title": article.subject,
                            "status": "success",
                            "content_length": len(article.content or ""),
                            "comments_saved": len(comments),
                            "created_at": article.created_at.isoformat() if article.created_at else None
                        })
                    else:
                        failed_count += 1
                        details.append({
                            "article_id": article.article_id,
                            "title": article.subject,
                            "status": "failed",
                            "reason": "이미 저장된 게시글이거나 저장 실패"
                        })
                    
                    # API 호출 간격 조절
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    failed_count += 1
                    self.log_error(f"게시글 {article.article_id} 처리 실패: {str(e)}")
                    details.append({
                        "article_id": article.article_id,
                        "title": article.subject,
                        "status": "error",
                        "reason": str(e)
                    })
                    continue
            
            result = {
                "total": len(all_articles),
                "saved": saved_count,
                "failed": failed_count,
                "comments_saved": comments_saved_count,
                "target_date": target_date,
                "details": details
            }
            
            self.log_info(f"날짜별 게시글과 댓글 전체 수집 완료: {saved_count}/{len(all_articles)}개 저장, 댓글 {comments_saved_count}개 저장")
            return result
            
        except Exception as e:
            self.log_error(f"날짜별 게시글과 댓글 전체 수집 실패: {str(e)}")
            return {"total": 0, "saved": 0, "failed": 0, "comments_saved": 0, "details": [], "error": str(e)}
    
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
    
    async def _save_comments(self, cafe_id: str, article_id: str, comments: List[Dict[str, Any]]) -> int:
        """댓글을 데이터베이스에 저장"""
        try:
            saved_count = 0
            
            # article_id는 articles 테이블의 id 필드여야 함
            # 먼저 네이버 게시글 ID로 articles 테이블의 id를 찾아야 함
            db_article = self.db.get_article_by_platform_id_and_community_article_id("naver", article_id)
            if not db_article:
                self.log_error(f"게시글 {article_id}를 데이터베이스에서 찾을 수 없습니다")
                return 0
            
            db_article_id = db_article['id']
            self.log_info(f"게시글 {article_id}의 DB ID: {db_article_id}")
            
            for comment in comments:
                try:
                    # 이미 저장된 댓글인지 확인 (기존 테이블 구조 사용)
                    existing = self.db.get_comment_by_article_id_and_comment_id(str(db_article_id), comment['comment_id'])
                    if existing:
                        self.log_info(f"댓글 {comment['comment_id']}는 이미 저장되어 있습니다")
                        continue
                    
                    # Comment 객체 생성 (기존 테이블 구조에 맞춤)
                    from database.models import Comment
                    db_comment = Comment(
                        id=None,
                        article_id=str(db_article_id),  # articles 테이블의 id
                        content=comment['content'],
                        writer_nickname=comment['writer_nickname'],
                        writer_id=comment['writer_id'] or comment['writer_member_key'],
                        created_at=comment['created_at'],
                        parent_comment_id=None,  # 대댓글은 현재 지원하지 않음
                        collected_at=datetime.now()
                    )
                    
                    # 데이터베이스에 저장
                    comment_id = self.db.insert_comment(db_comment)
                    
                    if comment_id:
                        saved_count += 1
                        self.log_info(f"댓글 {comment['comment_id']} 저장 완료 (DB ID: {comment_id})")
                    else:
                        self.log_error(f"댓글 {comment['comment_id']} 저장 실패")
                        
                except Exception as e:
                    self.log_error(f"댓글 {comment['comment_id']} 저장 중 오류 발생: {str(e)}")
                    continue
            
            return saved_count
            
        except Exception as e:
            self.log_error(f"댓글 저장 중 오류 발생: {str(e)}")
            return 0
    
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
