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
    
    def __init__(self, naver_cookies: str = ""):
        super().__init__()
        self.naver_cookies = naver_cookies
        self.api = NaverCafeAPI(naver_cookies)
        self.db = DatabaseManager()  # db_path 파라미터 제거
        
        # 네이버 커뮤니티 ID 설정 (존재하지 않으면 생성)
        self.naver_community_id = self._ensure_naver_community()
    
    def _ensure_naver_community(self) -> int:
        """네이버 커뮤니티가 존재하는지 확인하고, 없으면 생성"""
        try:
            # 네이버 커뮤니티 이름으로 조회
            community_name = "네이버 카페"
            existing_community = self.db.get_community_by_name(community_name)
            
            if existing_community:
                community_id = existing_community['id']
                return community_id
            else:
                # 커뮤니티 생성
                from database.models import Community
                community = Community(
                    id=None,
                    name=community_name,
                    created_at=datetime.now(),
                    description="네이버 카페 데이터 수집을 위한 커뮤니티"
                )
                community_id = self.db.insert_community(community)
                return community_id
                
        except Exception as e:
            self.log_error(f"네이버 커뮤니티 설정 중 오류: {e}")
            # 기본값 1 사용 (대부분의 DB에서 첫 번째 커뮤니티가 있을 것으로 예상)
            return 1
    
    async def collect_board_list(self, cafe_id: str) -> List[NaverCafeMenu]:
        """게시판 목록 수집"""
        try:
            
            boards = await self.api.get_board_list(cafe_id)
            
            if not boards:
                self.log_warning("수집된 게시판이 없습니다")
            
            return boards
            
        except Exception as e:
            self.log_error(f"게시판 목록 수집 실패: {str(e)}")
            return []
    
    async def collect_board_title_and_content(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> str:
        """게시판의 게시글 제목과 내용을 함께 조회"""
        try:
            
            # API를 통해 게시글 제목과 내용 조회
            result = await self.api.get_board_title_and_content(cafe_id, menu_id, per_page)
            
            if result:
                return result
            else:
                return "게시글 조회에 실패했습니다."
                
        except Exception as e:
            self.log_error(f"게시글 제목과 내용 조회 중 오류 발생: {str(e)}")
            return f"게시글 조회 오류: {str(e)}"
    
    async def collect_articles_with_detailed_content(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> Dict[str, Any]:
        """게시글을 상세 내용과 함께 수집하고 데이터베이스에 저장"""
        try:
            
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
            
            return result
            
        except Exception as e:
            self.log_error(f"상세 내용과 함께 게시글 수집 실패: {str(e)}")
            return {"total": 0, "saved": 0, "failed": 0, "details": [], "error": str(e)}
    
    async def collect_articles_with_content_and_comments(self, cafe_id: str, menu_id: str = "", per_page: int = 20, target_date: Optional[str] = None) -> Dict[str, Any]:
        """게시글을 상세 내용과 댓글과 함께 수집하고 데이터베이스에 저장 (여러 게시판 지원)"""
        try:
            self.log_info(f"상세 내용과 댓글과 함께 게시글 수집 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id}, 날짜: {target_date})")
            
            # 여러 게시판 지원: menu_id에 콤마가 있으면 여러 게시판 조회
            if ',' in menu_id:
                # 여러 게시판의 경우 각각 조회 후 합치기
                menu_list = [mid.strip() for mid in menu_id.split(',') if mid.strip()]
                all_articles_data = []
                
                for single_menu_id in menu_list:
                    self.log_info(f"게시판 {single_menu_id} 조회 중...")
                    articles_data = await self.api.get_articles_with_content_and_comments(cafe_id, single_menu_id, per_page, target_date)
                    if articles_data:
                        all_articles_data.extend(articles_data)
                        self.log_info(f"게시판 {single_menu_id}: {len(articles_data)}개 게시글 조회 완료")
                
                articles_data = all_articles_data
            else:
                # 단일 게시판 조회
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
                    
                    article = article_data['article']
                    comments = article_data['comments']
                    
                    # 중복 체크: 이미 저장된 게시글인지 먼저 확인
                    existing_article = self.db.get_article_by_platform_id_and_community_article_id("naver", article.article_id)
                    if existing_article:
                        continue
                    
                    # 게시글 저장
                    if await self._save_article(cafe_id, article):
                        saved_count += 1
                        
                        # 댓글 저장
                        if comments:
                            comment_saved = await self._save_comments(cafe_id, article.article_id, comments)
                            comments_saved_count += comment_saved
                        
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
            
            return result
            
        except Exception as e:
            self.log_error(f"상세 내용과 댓글과 함께 게시글 수집 실패: {str(e)}")
            return {"total": 0, "saved": 0, "failed": 0, "comments_saved": 0, "details": [], "error": str(e)}
    
    async def collect_articles_by_menu(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> int:
        """특정 게시판의 게시글 수집 (여러 게시판 지원)"""
        try:
            self.log_info(f"게시글 수집 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id})")
            
            # 여러 게시판 지원: menu_id에 콤마가 있으면 여러 게시판 조회
            if ',' in menu_id:
                # 여러 게시판의 경우 각각 조회 후 합치기
                menu_list = [mid.strip() for mid in menu_id.split(',') if mid.strip()]
                all_articles = []
                
                for single_menu_id in menu_list:
                    self.log_info(f"게시판 {single_menu_id} 조회 중...")
                    articles = await self.api.get_articles_with_content(cafe_id, single_menu_id, per_page)
                    if articles:
                        all_articles.extend(articles)
                        self.log_info(f"게시판 {single_menu_id}: {len(articles)}개 게시글 조회 완료")
                
                articles = all_articles
            else:
                # 단일 게시판 조회
                articles = await self.api.get_articles_with_content(cafe_id, menu_id, per_page)
            
            if not articles:
                self.log_warning("수집된 게시글이 없습니다")
                return 0
            
            # 데이터베이스에 저장
            saved_count = 0
            for article in articles:
                try:
                    # 중복 체크: 이미 저장된 게시글인지 먼저 확인
                    existing_article = self.db.get_article_by_platform_id_and_community_article_id("naver", article.article_id)
                    if existing_article:
                        continue
                    
                    if await self._save_article(cafe_id, article):
                        saved_count += 1
                except Exception as e:
                    self.log_error(f"게시글 {article.article_id} 저장 실패: {str(e)}")
                    continue
            
            return saved_count
            
        except Exception as e:
            self.log_error(f"게시글 수집 실패: {str(e)}")
            return 0
    
    async def collect_articles_by_date_with_comments(self, cafe_id: str, target_date: str, menu_id: str = "") -> Dict[str, Any]:
        """특정 날짜의 모든 게시글을 수집하고 댓글까지 포함하여 저장 (여러 게시판 지원)"""
        import time
        start_time = time.time()
        last_progress_time = start_time
        
        try:
            self.log_info(f"🚀 네이버 카페 수집 시작 - {target_date} (카페: {cafe_id})")
            
            # 날짜를 datetime 객체로 변환
            from datetime import datetime
            try:
                target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError as e:
                self.log_error(f"날짜 형식 오류: {target_date}, 예상 형식: YYYY-MM-DD")
                return {"total": 0, "saved": 0, "failed": 0, "comments_saved": 0, "details": [], "error": f"날짜 형식 오류: {str(e)}"}
            
            # 게시글 목록 조회 (페이지네이션 없이 모든 게시글)
            all_articles = []
            page = 1
            per_page = 100  # 한 번에 100개씩 조회
            
            while True:
                try:
                    # 여러 게시판 지원: menu_id에 콤마가 있으면 여러 게시판 조회
                    if ',' in menu_id:
                        articles = await self.api.get_article_list_multi_menus(cafe_id, menu_id, page, per_page)
                    else:
                        articles = await self.api.get_article_list(cafe_id, menu_id, page, per_page)
                    
                    if not articles:
                        break
                    
                    # 해당 날짜의 게시글만 필터링
                    date_filtered_articles = []
                    older_than_target = 0  # 대상 날짜보다 오래된 게시글 수
                    
                    for article in articles:
                        if article.created_at:
                            article_date = article.created_at.date()
                            if article_date == target_datetime.date():
                                date_filtered_articles.append(article)
                            elif article_date < target_datetime.date():
                                older_than_target += 1
                    
                    if date_filtered_articles:
                        all_articles.extend(date_filtered_articles)
                    
                    # 조기 종료 조건 개선
                    # 1. 전체 게시글이 대상 날짜보다 오래된 경우
                    if older_than_target > 0 and len(date_filtered_articles) == 0:
                        break
                    
                    # 2. 너무 많은 페이지를 조회한 경우 (무한 루프 방지)
                    if page >= 50:  # 최대 50페이지까지만 조회
                        break
                    
                    page += 1
                    
                    # API 호출 간격 조절
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.log_error(f"페이지 {page} 조회 실패: {str(e)}")
                    break
            
            if not all_articles:
                self.log_warning(f"📭 {target_date} 수집할 데이터 없음")
                return {"total": 0, "saved": 0, "failed": 0, "comments_saved": 0, "details": [], "message": "해당 날짜의 게시글이 없습니다"}
            
            # 각 게시글의 내용과 댓글 조회
            saved_count = 0
            failed_count = 0
            comments_saved_count = 0
            details = []
            
            for i, article in enumerate(all_articles):
                try:
                    # 중복 체크: 이미 저장된 게시글인지 먼저 확인
                    existing_article = self.db.get_article_by_platform_id_and_community_article_id("naver", article.article_id)
                    article_saved = False
                    
                    if existing_article:
                        article_saved = True
                    else:
                        # 게시글 내용 조회
                        content_html, created_at = await self.api.get_article_content(cafe_id, article.article_id)
                        if content_html:
                            article.content = self.api.parse_content_html(content_html)
                            
                            # 생성일이 없는 경우 내용 조회에서 얻은 정보로 업데이트
                            if not article.created_at and created_at:
                                article.created_at = created_at
                        else:
                            article.content = ""
                        
                        # 게시글 저장
                        if await self._save_article(cafe_id, article):
                            saved_count += 1
                            article_saved = True
                    
                    # 댓글 조회 및 저장 (게시글이 중복이어도 댓글은 수집)
                    if article_saved:
                        comments = await self.api.get_article_comments(cafe_id, article.article_id)
                        
                        if comments:
                            comment_saved = await self._save_comments(cafe_id, article.article_id, comments)
                            comments_saved_count += comment_saved
                        
                        details.append({
                            "article_id": article.article_id,
                            "title": article.subject,
                            "status": "success",
                            "content_length": len(article.content or ""),
                            "comments_saved": len(comments),
                            "created_at": article.created_at.isoformat() if article.created_at else None,
                            "is_duplicate": existing_article is not None
                        })
                    else:
                        failed_count += 1
                        details.append({
                            "article_id": article.article_id,
                            "title": article.subject,
                            "status": "failed",
                            "reason": "저장 실패"
                        })
                    
                    # 10분마다 진행상태 로그
                    current_time = time.time()
                    if current_time - last_progress_time >= 600:  # 10분 = 600초
                        self.log_info(f"📊 네이버 수집 진행중... {i+1}/{len(all_articles)} (게시글: {saved_count}개, 댓글: {comments_saved_count}개)")
                        last_progress_time = current_time
                    
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
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.log_info(f"✅ 네이버 카페 수집 완료 - {target_date}")
            self.log_info(f"📊 결과: 게시글 {saved_count}/{len(all_articles)}개, 댓글 {comments_saved_count}개 (소요시간: {elapsed_time:.2f}초)")
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
                        # self.log_info(f"댓글 {comment['comment_id']}는 이미 저장되어 있습니다")
                        continue
                    
                    # Comment 객체 생성 - 개선된 방식 사용
                    from database.models import Comment
                    db_comment = Comment(
                        id=comment['comment_id'],  # 네이버 댓글 ID
                        article_id=db_article_id,  # 데이터베이스의 article ID (숫자)
                        content=comment['content'],
                        writer_nickname=comment['writer_nickname'],
                        writer_id=comment['writer_id'] or comment['writer_member_key'],
                        created_at=comment['created_at'],
                        parent_comment_id=None,  # 대댓글은 현재 지원하지 않음
                        collected_at=datetime.now()
                    )
                    
                    # 플랫폼 정보 추가
                    db_comment.platform_id = f"naver_cafe_{cafe_id}"
                    
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
