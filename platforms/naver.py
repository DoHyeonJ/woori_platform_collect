#!/usr/bin/env python3
"""
네이버 카페 API 클라이언트
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import html
import logging

from utils.logger import LoggedClass

@dataclass
class NaverCafeMenu:
    """네이버 카페 메뉴 정보"""
    menu_id: int
    menu_name: str
    menu_type: str
    board_type: str
    sort: int

@dataclass
class NaverCafeArticle:
    """네이버 카페 게시글 정보"""
    article_id: str
    subject: str
    writer_nickname: str
    writer_id: str
    content: Optional[str] = None
    created_at: Optional[datetime] = None
    view_count: Optional[int] = None
    comment_count: Optional[int] = None
    like_count: Optional[int] = None

class NaverCafeAPI(LoggedClass):
    """네이버 카페 API 클라이언트"""
    
    def __init__(self, naver_cookies: str = ""):
        super().__init__()
        self.naver_cookies = naver_cookies
        self.base_url = "https://apis.naver.com"
        
        # 쿠키가 있는 경우와 없는 경우를 구분하여 헤더 설정
        if naver_cookies and naver_cookies.strip() and not naver_cookies.strip().endswith("="):
            # 실제 쿠키가 있는 경우
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json",
                "Referer": "https://cafe.naver.com/",
                "Cookie": naver_cookies
            }
        else:
            # 쿠키가 없는 경우 (게시판 목록 조회용)
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json",
                "Referer": "https://cafe.naver.com/"
            }
        
        # 주요 카페 ID 목록
        self.cafe_ids = {
            "여우야": "10912875",
            "A+여우야": "12285441", 
            "성형위키백과": "11498714",
            "여생남정": "13067396",
            "시크먼트": "23451561",
            "가아사": "15880379",
            "파우더룸": "10050813"
        }
    
    async def get_board_list(self, cafe_id: str) -> List[NaverCafeMenu]:
        """게시판 목록 조회"""
        try:
            self.log_info(f"게시판 목록 조회 시작 (카페 ID: {cafe_id})")
            
            url = f"{self.base_url}/cafe-web/cafe2/SideMenuList"
            params = {"cafeId": cafe_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        menu_list = []
                        if 'message' in data and 'result' in data['message'] and 'menus' in data['message']['result']:
                            for menu in data['message']['result']['menus']:
                                # P(프로필), L(링크), F(폴더) 제외
                                if menu['menuType'] not in ['P', 'L', 'F']:
                                    menu_list.append(NaverCafeMenu(
                                        menu_id=int(menu['menuId']), # 문자열에서 int로 변환
                                        menu_name=html.unescape(menu['menuName']),
                                        menu_type=menu['menuType'],
                                        board_type=menu['boardType'],
                                        sort=menu['listOrder']
                                    ))
                            
                            # 정렬 순서대로 정렬
                            menu_list.sort(key=lambda x: x.sort)
                            self.log_info(f"게시판 {len(menu_list)}개 조회 완료")
                            return menu_list
                        else:
                            self.log_error("게시판 목록 데이터 구조가 올바르지 않습니다")
                            return []
                    else:
                        self.log_error(f"게시판 목록 조회 실패: HTTP {response.status}")
                        return []
                        
        except Exception as e:
            self.log_error(f"게시판 목록 조회 중 오류 발생: {str(e)}")
            return []
    
    async def get_article_list(self, cafe_id: str, menu_id: str = "", page: int = 1, per_page: int = 20) -> List[NaverCafeArticle]:
        """게시글 목록 조회"""
        try:
            self.log_info(f"게시글 목록 조회 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id}, 페이지: {page})")
            
            url = f"{self.base_url}/cafe-web/cafe2/ArticleListV2dot1.json"
            params = {
                "search.clubid": cafe_id,
                "search.queryType": "lastArticle",
                "search.menuid": menu_id,
                "search.page": page,
                "search.perPage": per_page,
                "adUnit": "MW_CAFE_ARTICLE_LIST_RS"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        article_list = []
                        if 'message' in data and 'result' in data['message'] and 'articleList' in data['message']['result']:
                            articles = data['message']['result']['articleList']
                            # 게시글 ID 순으로 정렬
                            articles.sort(key=lambda x: x['articleId'])
                            
                            for article in articles:
                                article_list.append(NaverCafeArticle(
                                    article_id=article['articleId'],
                                    subject=article['subject'],
                                    writer_nickname=article['writerNickname'],
                                    writer_id=article.get('writerId', ''),
                                    created_at=datetime.fromisoformat(article.get('writeDate', '').replace('Z', '+00:00')) if article.get('writeDate') else None,
                                    view_count=article.get('readCount', 0),
                                    comment_count=article.get('commentCount', 0),
                                    like_count=article.get('likeCount', 0)
                                ))
                            
                            self.log_info(f"게시글 {len(article_list)}개 조회 완료")
                            return article_list
                        else:
                            self.log_error("게시글 목록 데이터 구조가 올바르지 않습니다")
                            return []
                    else:
                        self.log_error(f"게시글 목록 조회 실패: HTTP {response.status}")
                        return []
                        
        except Exception as e:
            self.log_error(f"게시글 목록 조회 중 오류 발생: {str(e)}")
            return []
    
    async def get_article_content(self, cafe_id: str, article_id: str) -> Optional[str]:
        """게시글 내용 조회"""
        try:
            self.log_info(f"게시글 내용 조회 시작 (카페 ID: {cafe_id}, 게시글 ID: {article_id})")
            
            url = f"https://apis.naver.com/cafe-articleapi/v2.1/cafes/{cafe_id}/articles/{article_id}"
            params = {
                "useCafeId": "true",
                "requestFrom": "A"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'result' in data and 'article' in data['result'] and 'contentHtml' in data['result']['article']:
                            content = data['result']['article']['contentHtml']
                            self.log_info("게시글 내용 조회 완료")
                            return content
                        else:
                            self.log_error("게시글 내용 데이터 구조가 올바르지 않습니다")
                            return None
                    else:
                        self.log_error(f"게시글 내용 조회 실패: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            self.log_error(f"게시글 내용 조회 중 오류 발생: {str(e)}")
            return None
    
    def parse_content_html(self, html_content: str) -> str:
        """HTML 내용을 텍스트로 파싱"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 내용 추출 (네이버 에디터 텍스트)
            elements = soup.select('.se-module-text .se-text-paragraph span')
            if elements:
                content = ' '.join([element.get_text(strip=True) for element in elements])
            else:
                # 다른 형태의 내용도 시도
                content = soup.get_text(strip=True)
            
            return content
            
        except ImportError:
            self.log_error("BeautifulSoup이 설치되지 않았습니다. pip install beautifulsoup4")
            return html_content
        except Exception as e:
            self.log_error(f"HTML 파싱 중 오류 발생: {str(e)}")
            return html_content
    
    async def get_articles_with_content(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> List[NaverCafeArticle]:
        """게시글 목록과 내용을 함께 조회"""
        try:
            self.log_info(f"게시글과 내용 조회 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id})")
            
            # 게시글 목록 조회
            articles = await self.get_article_list(cafe_id, menu_id, 1, per_page)
            
            # 각 게시글의 내용 조회
            for article in articles:
                try:
                    content_html = await self.get_article_content(cafe_id, article.article_id)
                    if content_html:
                        article.content = self.parse_content_html(content_html)
                    
                    # API 호출 간격 조절
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.log_error(f"게시글 {article.article_id} 내용 조회 실패: {str(e)}")
                    continue
            
            self.log_info(f"게시글과 내용 조회 완료: {len(articles)}개")
            return articles
            
        except Exception as e:
            self.log_error(f"게시글과 내용 조회 중 오류 발생: {str(e)}")
            return []
    
    def get_cafe_name_by_id(self, cafe_id: str) -> Optional[str]:
        """카페 ID로 카페 이름 조회"""
        for name, id_val in self.cafe_ids.items():
            if id_val == cafe_id:
                return name
        return None
    
    def get_cafe_id_by_name(self, cafe_name: str) -> Optional[str]:
        """카페 이름으로 카페 ID 조회"""
        return self.cafe_ids.get(cafe_name)
    
    def list_cafes(self) -> Dict[str, str]:
        """지원하는 카페 목록 반환"""
        return self.cafe_ids.copy()
