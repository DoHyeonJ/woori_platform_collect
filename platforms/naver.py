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
        
        # 기본 헤더 설정
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://cafe.naver.com/"
        }
        
        # 쿠키가 있는 경우 헤더에 추가
        if naver_cookies and naver_cookies.strip():
            self.headers["Cookie"] = naver_cookies.strip()
            self.log_info(f"네이버 쿠키 설정됨: {naver_cookies[:50]}...")
        else:
            self.log_warning("네이버 쿠키가 설정되지 않았습니다. 일부 API 호출이 실패할 수 있습니다.")
        
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
            
            # 새로운 네이버 API 엔드포인트 사용
            url = f"https://article.cafe.naver.com/gw/v3/cafes/{cafe_id}/menus"
            params = {
                "useCafeId": "true",
                "requestFrom": "A"
            }
            
            self.log_info(f"요청 URL: {url}")
            self.log_info(f"요청 파라미터: {params}")
            self.log_info(f"요청 헤더: {self.headers}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    self.log_info(f"응답 상태 코드: {response.status}")
                    self.log_info(f"응답 헤더: {dict(response.headers)}")
                    
                    if response.status == 200:
                        data = await response.json()
                        self.log_info(f"응답 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        # 새로운 API 응답 구조에 맞춰 수정
                        if 'result' in data and 'menus' in data['result']:
                            menus = data['result']['menus']
                            self.log_info(f"메뉴 개수: {len(menus)}개")
                            
                            menu_list = []
                            for menu in menus:
                                # P(프로필), L(링크), F(폴더) 제외
                                if menu.get('menuType') not in ['P', 'L', 'F']:
                                    menu_list.append(NaverCafeMenu(
                                        menu_id=int(menu.get('id', 0)),
                                        menu_name=html.unescape(menu.get('name', '')),
                                        menu_type=menu.get('menuType', ''),
                                        board_type=menu.get('boardType', ''),
                                        sort=menu.get('sort', 0)
                                    ))
                            
                            # 정렬 순서대로 정렬
                            menu_list.sort(key=lambda x: x.sort)
                            self.log_info(f"게시판 {len(menu_list)}개 조회 완료")
                            return menu_list
                        else:
                            self.log_error("게시판 목록 데이터 구조가 올바르지 않습니다")
                            self.log_error(f"응답 구조: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                            if 'result' in data:
                                self.log_error(f"result 구조: {list(data['result'].keys()) if isinstance(data['result'], dict) else 'Not a dict'}")
                            return []
                    else:
                        response_text = await response.text()
                        self.log_error(f"게시판 목록 조회 실패: HTTP {response.status}")
                        self.log_error(f"응답 내용: {response_text}")
                        return []
                        
        except Exception as e:
            self.log_error(f"게시판 목록 조회 중 오류 발생: {str(e)}")
            import traceback
            self.log_error(f"상세 오류: {traceback.format_exc()}")
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
                    self.log_info(f"응답 상태 코드: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        self.log_info(f"응답 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        article_list = []
                        if 'message' in data and 'result' in data['message'] and 'articleList' in data['message']['result']:
                            articles = data['message']['result']['articleList']
                            # 게시글 ID 순으로 정렬
                            articles.sort(key=lambda x: x['articleId'])
                            
                            for article in articles:
                                # writeDate를 Unix timestamp (밀리초)에서 datetime으로 변환
                                created_at = self._convert_write_date(article.get('writeDateTimestamp'))
                                
                                article_list.append(NaverCafeArticle(
                                    article_id=article['articleId'],
                                    subject=article['subject'],
                                    writer_nickname=article['writerNickname'],
                                    writer_id=article.get('writerId', ''),
                                    created_at=created_at,
                                    view_count=article.get('readCount', 0),
                                    comment_count=article.get('commentCount', 0),
                                    like_count=article.get('likeCount', 0)
                                ))
                            
                            self.log_info(f"게시글 {len(article_list)}개 조회 완료")
                            return article_list
                        else:
                            self.log_error("게시글 목록 데이터 구조가 올바르지 않습니다")
                            self.log_error(f"응답 구조: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                            if 'result' in data:
                                self.log_error(f"result 구조: {list(data['result'].keys()) if isinstance(data['result'], dict) else 'Not a dict'}")
                            return []
                    else:
                        response_text = await response.text()
                        self.log_error(f"게시글 목록 조회 실패: HTTP {response.status}")
                        self.log_error(f"응답 내용: {response_text}")
                        return []
                        
        except Exception as e:
            self.log_error(f"게시글 목록 조회 중 오류 발생: {str(e)}")
            import traceback
            self.log_error(f"상세 오류: {traceback.format_exc()}")
            return []
    
    async def get_article_content(self, cafe_id: str, article_id: str, retry_count: int = 0) -> Optional[tuple[str, datetime]]:
        """게시글 내용 조회 (재시도 로직 포함)"""
        try:
            self.log_info(f"게시글 내용 조회 시작 (카페 ID: {cafe_id}, 게시글 ID: {article_id}, 재시도: {retry_count})")
            
            # 올바른 네이버 API 엔드포인트 사용
            url = f"https://article.cafe.naver.com/gw/v3/cafes/{cafe_id}/articles/{article_id}"
            params = {
                "query": "",
                "boardType": "L",  # 기본값, 필요시 동적으로 설정
                "useCafeId": "true",
                "requestFrom": "A"
            }
            
            self.log_info(f"요청 URL: {url}")
            self.log_info(f"요청 파라미터: {params}")
            self.log_info(f"요청 헤더: {self.headers}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    self.log_info(f"응답 상태 코드: {response.status}")
                    self.log_info(f"응답 헤더: {dict(response.headers)}")
                    
                    if response.status == 200:
                        data = await response.json()
                        self.log_info(f"응답 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        # 시스템 에러 체크
                        if 'error_code' in data and data['error_code'] == '000':
                            error_msg = data.get('message', 'Unknown system error')
                            self.log_error(f"네이버 시스템 에러 발생: {error_msg}")
                            
                            # 재시도 로직 (최대 3회)
                            if retry_count < 3:
                                self.log_info(f"시스템 에러로 인한 재시도 {retry_count + 1}/3")
                                await asyncio.sleep(2 ** retry_count)  # 지수 백오프
                                return await self.get_article_content(cafe_id, article_id, retry_count + 1)
                            else:
                                self.log_error(f"최대 재시도 횟수 초과: {article_id}")
                                return None, None
                        
                        # 새로운 API 응답 구조에 맞춰 수정
                        if 'result' in data and 'article' in data['result'] and 'contentHtml' in data['result']['article']:
                            content = data['result']['article']['contentHtml']
                            self.log_info(f"게시글 내용 조회 성공 (길이: {len(content)}자)")
                            
                            # 추가 정보 로깅
                            article_info = data['result']['article']
                            self.log_info(f"게시글 제목: {article_info.get('subject', 'N/A')}")
                            self.log_info(f"작성자: {article_info.get('writer', {}).get('nick', 'N/A')}")
                            
                            # 생성일 정보 로깅 및 변환
                            write_date = article_info.get('writeDate')
                            created_at = self._convert_write_date(write_date)
                            
                            if created_at:
                                self.log_info(f"게시글 생성일: {created_at}")
                            else:
                                self.log_info("게시글 생성일 정보 없음")
                            
                            # content와 created_at을 함께 반환 (튜플 형태)
                            return content, created_at
                        else:
                            self.log_error(f"게시글 내용 데이터 구조가 올바르지 않습니다")
                            self.log_error(f"응답 구조: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                            if 'result' in data:
                                self.log_error(f"result 구조: {list(data['result'].keys()) if isinstance(data['result'], dict) else 'Not a dict'}")
                            if 'result' in data and 'article' in data['result']:
                                self.log_error(f"article 구조: {list(data['result']['article'].keys()) if isinstance(data['result']['article'], dict) else 'Not a dict'}")
                            return None, None
                    else:
                        response_text = await response.text()
                        self.log_error(f"게시글 내용 조회 실패: HTTP {response.status}")
                        self.log_error(f"응답 내용: {response_text}")
                        return None, None
                        
        except Exception as e:
            self.log_error(f"게시글 내용 조회 중 오류 발생: {str(e)}")
            import traceback
            self.log_error(f"상세 오류: {traceback.format_exc()}")
            return None, None
    
    async def get_article_comments(self, cafe_id: str, article_id: str) -> List[Dict[str, Any]]:
        """게시글의 댓글 목록 조회"""
        try:
            self.log_info(f"댓글 목록 조회 시작 (카페 ID: {cafe_id}, 게시글 ID: {article_id})")
            
            # 댓글 조회 API 엔드포인트 (게시글 내용 조회 시 함께 받아옴)
            # 실제로는 게시글 내용 조회 시 comments 정보가 함께 포함됨
            url = f"https://article.cafe.naver.com/gw/v3/cafes/{cafe_id}/articles/{article_id}"
            params = {
                "query": "",
                "boardType": "L",
                "useCafeId": "true",
                "requestFrom": "A"
            }
            
            self.log_info(f"요청 URL: {url}")
            self.log_info(f"요청 파라미터: {params}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    self.log_info(f"응답 상태 코드: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # 댓글 정보 추출
                        if 'result' in data and 'comments' in data['result']:
                            comments_data = data['result']['comments']
                            
                            if 'items' in comments_data:
                                comments = comments_data['items']
                                self.log_info(f"댓글 {len(comments)}개 조회 완료")
                                
                                # 댓글 데이터 정리
                                processed_comments = []
                                for comment in comments:
                                    # updateDate를 datetime으로 변환
                                    created_at = self._convert_write_date(comment.get('updateDate'))
                                    
                                    processed_comment = {
                                        'comment_id': str(comment.get('id', '')),
                                        'ref_id': str(comment.get('refId', '')),
                                        'writer_nickname': comment.get('writer', {}).get('nick', ''),
                                        'writer_id': comment.get('writer', {}).get('id', ''),
                                        'writer_member_key': comment.get('writer', {}).get('memberKey', ''),
                                        'content': comment.get('content', ''),
                                        'created_at': created_at,
                                        'member_level': comment.get('memberLevel', 0),
                                        'is_deleted': comment.get('isDeleted', False),
                                        'is_article_writer': comment.get('isArticleWriter', False),
                                        'is_new': comment.get('isNew', False)
                                    }
                                    processed_comments.append(processed_comment)
                                    
                                    self.log_info(f"댓글 {processed_comment['comment_id']} 처리 완료: {processed_comment['writer_nickname']}")
                                
                                return processed_comments
                            else:
                                self.log_info("댓글이 없습니다")
                                return []
                        else:
                            self.log_info("댓글 데이터 구조가 올바르지 않습니다")
                            return []
                    else:
                        response_text = await response.text()
                        self.log_error(f"댓글 조회 실패: HTTP {response.status}")
                        self.log_error(f"응답 내용: {response_text}")
                        return []
                        
        except Exception as e:
            self.log_error(f"댓글 목록 조회 중 오류 발생: {str(e)}")
            import traceback
            self.log_error(f"상세 오류: {traceback.format_exc()}")
            return []
    
    async def get_articles_with_content(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> List[NaverCafeArticle]:
        """게시글 목록과 내용을 함께 조회 (개선된 버전)"""
        try:
            self.log_info(f"게시글과 내용 조회 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id})")
            
            # 게시글 목록 조회
            articles = await self.get_article_list(cafe_id, menu_id, 1, per_page)
            
            if not articles:
                self.log_warning("수집할 게시글이 없습니다")
                return []
            
            # 각 게시글의 내용 조회
            articles_with_content = []
            for i, article in enumerate(articles):
                try:
                    self.log_info(f"게시글 {i+1}/{len(articles)} 내용 조회 중...")
                    
                    content_html, created_at = await self.get_article_content(cafe_id, article.article_id)
                    if content_html:
                        article.content = self.parse_content_html(content_html)
                        self.log_info(f"게시글 {article.article_id} 내용 파싱 완료")
                        
                        # 생성일이 없는 경우 내용 조회에서 얻은 정보로 업데이트
                        if not article.created_at and created_at:
                            article.created_at = created_at
                            self.log_info(f"게시글 {article.article_id} 생성일 업데이트: {created_at}")
                        elif article.created_at:
                            self.log_info(f"게시글 {article.article_id} 기존 생성일 유지: {article.created_at}")
                    else:
                        self.log_warning(f"게시글 {article.article_id} 내용 조회 실패")
                        article.content = ""
                    
                    # 생성일 정보 로깅
                    if article.created_at:
                        self.log_info(f"게시글 {article.article_id} 최종 생성일: {article.created_at}")
                    else:
                        self.log_warning(f"게시글 {article.article_id} 생성일 정보 없음")
                    
                    articles_with_content.append(article)
                    
                    # API 호출 간격 조절 (네이버 API 제한 고려)
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    self.log_error(f"게시글 {article.article_id} 내용 조회 실패: {str(e)}")
                    article.content = ""
                    articles_with_content.append(article)
                    continue
            
            self.log_info(f"게시글과 내용 조회 완료: {len(articles_with_content)}개")
            return articles_with_content
            
        except Exception as e:
            self.log_error(f"게시글과 내용 조회 중 오류 발생: {str(e)}")
            return []
    
    async def get_board_title_and_content(self, cafe_id: str, menu_id: str = "", per_page: int = 20) -> str:
        """게시판의 게시글 제목과 내용을 가져옵니다 (참고 코드 기반)"""
        try:
            self.log_info(f"게시글 제목과 내용 조회 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id})")
            
            # 게시글 목록 조회
            articles = await self.get_article_list(cafe_id, menu_id, 1, per_page)
            
            if not articles:
                return "수집할 게시글이 없습니다."
            
            result = ""
            content_cnt = 1
            
            for article in articles:
                try:
                    self.log_info(f"게시글 {content_cnt}/{len(articles)} 처리 중...")
                    
                    # 게시글 내용 조회
                    board_content, created_at = await self.get_article_content(cafe_id, article.article_id)
                    if board_content:
                        content = self.parse_content_html(board_content)
                        
                        # 내용이 너무 길면 요약
                        if content and len(content) > 200:
                            content = content[:200] + "..."
                        
                        result += f"게시글 {content_cnt}:\n제목: {article.subject}\n작성자: {article.writer_nickname}\n내용: {content}\n\n"
                    else:
                        result += f"게시글 {content_cnt}:\n제목: {article.subject}\n작성자: {article.writer_nickname}\n내용: 조회 실패\n\n"
                    
                    content_cnt += 1
                    
                    # API 호출 간격 조절
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    self.log_error(f"게시글 {content_cnt} 내용 수집 실패: {str(e)}")
                    result += f"게시글 {content_cnt}:\n제목: {article.subject}\n내용: 오류 발생\n\n"
                    content_cnt += 1
                    continue
            
            self.log_info(f"게시글 제목과 내용 조회 완료: {content_cnt-1}개")
            return result
            
        except Exception as e:
            self.log_error(f"게시글 제목과 내용 조회 중 오류 발생: {str(e)}")
            return f"게시글 조회 실패: {str(e)}"
    
    async def get_articles_with_content_and_comments(self, cafe_id: str, menu_id: str = "", per_page: int = 20, target_date: Optional[str] = None, limit: int = 0) -> List[Dict[str, Any]]:
        """
        게시글 목록, 내용, 댓글을 함께 조회
        
        Args:
            cafe_id: 카페 ID
            menu_id: 메뉴 ID (기본값: "")
            per_page: 페이지당 게시글 수 (기본값: 20)
            target_date: 대상 날짜 (기본값: None)
            limit: 수집할 최대 개수 (0이면 무제한)
        """
        try:
            self.log_info(f"게시글과 내용, 댓글 조회 시작 (카페 ID: {cafe_id}, 메뉴 ID: {menu_id}, 날짜: {target_date})")
            
            # limit이 설정된 경우 페이지당 개수를 limit에 맞춰 조정
            if limit > 0:
                initial_per_page = min(per_page * 4, limit) if target_date else min(per_page, limit)
            else:
                initial_per_page = per_page * 4 if target_date else per_page
            
            articles = await self.get_article_list(cafe_id, menu_id, 1, initial_per_page)
            
            if not articles:
                self.log_warning("수집할 게시글이 없습니다")
                return []
            
            self.log_info(f"초기 게시글 {len(articles)}개 조회 완료")
            
            # 각 게시글의 내용과 댓글 조회 (생성일 정보 포함)
            articles_with_content_and_comments = []
            consecutive_404_errors = 0
            max_404_errors = 5
            
            for i, article in enumerate(articles):
                try:
                    # limit 체크 (0이면 무제한)
                    if limit > 0 and len(articles_with_content_and_comments) >= limit:
                        self.log_info(f"📊 수집 개수 제한 도달: {limit}개")
                        break
                    
                    self.log_info(f"게시글 {i+1}/{len(articles)} 처리 중... (ID: {article.article_id})")
                    
                    # 게시글별 5초 딜레이 (과부하 방지)
                    await asyncio.sleep(5)
                    
                    # 게시글 내용 조회
                    content_html, created_at = await self.get_article_content(cafe_id, article.article_id)
                    if content_html:
                        article.content = self.parse_content_html(content_html)
                        self.log_info(f"게시글 {article.article_id} 내용 파싱 완료")
                        
                        # 생성일이 없는 경우 내용 조회에서 얻은 정보로 업데이트
                        if not article.created_at and created_at:
                            article.created_at = created_at
                            self.log_info(f"게시글 {article.article_id} 생성일 업데이트: {created_at}")
                    else:
                        self.log_warning(f"게시글 {article.article_id} 내용 조회 실패")
                        article.content = ""
                    
                    # 댓글 조회
                    comments = await self.get_article_comments(cafe_id, article.article_id)
                    self.log_info(f"게시글 {article.article_id} 댓글 {len(comments)}개 조회 완료")
                    
                    # 결과 데이터 구성
                    article_data = {
                        'article': article,
                        'comments': comments,
                        'comment_count': len(comments)
                    }
                    
                    articles_with_content_and_comments.append(article_data)
                    
                    # API 호출 간격 조절
                    await asyncio.sleep(0.3)
                    
                    # limit 체크 (0이면 무제한) - 게시글 처리 후 체크
                    if limit > 0 and len(articles_with_content_and_comments) >= limit:
                        self.log_info(f"📊 수집 개수 제한 도달: {limit}개")
                        break
                    
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg or "Not Found" in error_msg:
                        consecutive_404_errors += 1
                        self.log_error(f"❌ 404 에러 발생 (연속 {consecutive_404_errors}회): {e}")
                        
                        if consecutive_404_errors >= max_404_errors:
                            self.log_error(f"🚫 연속 404 에러 {max_404_errors}회 발생. 20분 대기 후 재시도합니다.")
                            await asyncio.sleep(20 * 60)  # 20분 대기
                            consecutive_404_errors = 0  # 카운터 리셋
                        else:
                            await asyncio.sleep(5)  # 5초 대기
                    else:
                        self.log_error(f"게시글 {article.article_id} 처리 실패: {str(e)}")
                    
                    article_data = {
                        'article': article,
                        'comments': [],
                        'comment_count': 0
                    }
                    articles_with_content_and_comments.append(article_data)
                    continue
            
            # 날짜 필터링 (target_date가 지정된 경우, 내용 조회 후 수행)
            if target_date:
                try:
                    from datetime import datetime
                    target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
                    self.log_info(f"날짜 필터링 적용: {target_date}")
                    
                    # 해당 날짜의 게시글만 필터링
                    filtered_articles = []
                    for article_data in articles_with_content_and_comments:
                        article = article_data['article']
                        if article.created_at and article.created_at.date() == target_datetime.date():
                            filtered_articles.append(article_data)
                    
                    articles_with_content_and_comments = filtered_articles
                    self.log_info(f"날짜 필터링 후 게시글 수: {len(articles_with_content_and_comments)}개")
                    
                    # 필터링된 게시글이 per_page보다 적으면 더 많은 게시글을 조회
                    if len(articles_with_content_and_comments) < per_page:
                        self.log_info(f"필터링된 게시글이 {per_page}개보다 적어서 추가 조회를 시도합니다")
                        # 이미 충분한 게시글을 조회했으므로 현재 결과를 반환
                        self.log_warning(f"요청된 날짜({target_date})에 해당하는 게시글이 {len(articles_with_content_and_comments)}개만 있습니다")
                        
                except ValueError as e:
                    self.log_error(f"날짜 형식 오류: {target_date}, 예상 형식: YYYY-MM-DD")
                    return []
            
            # per_page만큼만 처리
            articles_with_content_and_comments = articles_with_content_and_comments[:per_page]
            self.log_info(f"최종 처리할 게시글 수: {len(articles_with_content_and_comments)}개")
            
            self.log_info(f"게시글과 내용, 댓글 조회 완료: {len(articles_with_content_and_comments)}개")
            return articles_with_content_and_comments
            
        except Exception as e:
            self.log_error(f"게시글과 내용, 댓글 조회 중 오류 발생: {str(e)}")
            return []
    
    def parse_content_html(self, html_content: str) -> str:
        """HTML 내용을 텍스트로 파싱 (새로운 네이버 에디터 구조에 맞춰 수정)"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 새로운 네이버 에디터 구조에 맞춰 수정
            content_parts = []
            
            # 1. 기본 텍스트 모듈 (.se-module-text)
            text_elements = soup.select('.se-module-text .se-text-paragraph span')
            if text_elements:
                for element in text_elements:
                    text = element.get_text(strip=True)
                    if text:
                        content_parts.append(text)
            
            # 2. 제목 모듈 (.se-module-title)
            title_elements = soup.select('.se-module-title .se-text-paragraph span')
            if title_elements:
                for element in title_elements:
                    text = element.get_text(strip=True)
                    if text:
                        content_parts.append(f"제목: {text}")
            
            # 3. 이미지 설명 (.se-module-image .se-caption)
            image_captions = soup.select('.se-module-image .se-caption')
            if image_captions:
                for caption in image_captions:
                    text = caption.get_text(strip=True)
                    if text:
                        content_parts.append(f"이미지: {text}")
            
            # 4. 새로운 네이버 에디터 구조 지원
            # .se-component-content 내의 모든 텍스트 요소
            component_texts = soup.select('.se-component-content .se-text-paragraph span')
            for element in component_texts:
                text = element.get_text(strip=True)
                if text and text not in content_parts:  # 중복 제거
                    content_parts.append(text)
            
            # 5. 기타 텍스트 요소들 (fallback)
            other_texts = soup.select('p, div, span')
            for element in other_texts:
                text = element.get_text(strip=True)
                if text and len(text) > 5 and text not in content_parts:  # 중복 제거 및 최소 길이 체크
                    content_parts.append(text)
            
            # 6. 전체 텍스트가 없는 경우 fallback
            if not content_parts:
                content = soup.get_text(strip=True)
                # HTML 태그 제거 및 정리
                import re
                content = re.sub(r'<[^>]+>', '', content)
                content = re.sub(r'\s+', ' ', content)
                content_parts.append(content)
            
            # 내용 결합
            final_content = ' '.join(content_parts)
            
            # 내용 길이 제한 (너무 긴 경우)
            if len(final_content) > 2000:
                final_content = final_content[:2000] + "..."
            
            return final_content
            
        except ImportError:
            self.log_error("BeautifulSoup이 설치되지 않았습니다. pip install beautifulsoup4")
            return html_content
        except Exception as e:
            self.log_error(f"HTML 파싱 중 오류 발생: {str(e)}")
            return html_content
    

    
    def _convert_write_date(self, write_date) -> Optional[datetime]:
        """writeDate를 datetime으로 변환하는 헬퍼 함수"""
        if not write_date:
            return None
        
        try:
            # Unix timestamp (밀리초)를 초 단위로 변환 후 datetime으로 변환
            timestamp_seconds = int(write_date) / 1000
            created_at = datetime.fromtimestamp(timestamp_seconds)
            # 로그를 줄이기 위해 debug 레벨로 변경 (너무 많은 로그 방지)
            # self.log_info(f"생성일 변환 성공: {write_date} -> {created_at}")
            return created_at
        except (ValueError, TypeError) as e:
            self.log_error(f"생성일 변환 실패: {write_date}, 오류: {str(e)}")
            return None
    
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
