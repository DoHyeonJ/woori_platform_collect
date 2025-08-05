import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class Writer:
    id: int
    doctor_id: Optional[int]
    profile: str
    nickname: str
    level: int
    engagement_type: Optional[str]

@dataclass
class Photo:
    url: str

@dataclass
class Comment:
    id: int
    status: int
    writer: Writer
    create_time: str
    reply_comment_id: Optional[int]
    is_admin: bool
    edited: bool
    contents: str
    has_thumb_up: bool
    thumb_up_count: int
    comment_count: int
    callee_nickname: Optional[str]
    lang: str
    translate_result: Optional[str]
    show_original_content: bool
    replies: List['Comment']

@dataclass
class Article:
    id: int
    category_id: int
    category_name: str
    writer: Writer
    writer_doctor_id: Optional[int]
    has_thumb_up: bool
    comment_count: int
    thumb_up_count: int
    view_count: int
    create_time: str
    edited: bool
    title: str
    contents: str
    photos: List[Photo]
    lang: str
    has_doctor_comment: bool
    translate_result: Optional[str]
    is_admin: bool = False
    has_subscribed: bool = False
    comments: List[Comment] = None

class GangnamUnniAPI:
    def __init__(self):
        self.base_url = "https://www.gangnamunni.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Authorization": "a70ba5dec9424aeb99e956a19cba87a3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    
    async def get_article_list(self, category: str = "hospital_question", page: int = 1, limit: int = 20) -> List[Article]:
        """
        강남언니 커뮤니티 게시글 목록을 가져옵니다.
        
        Args:
            category: 카테고리 (기본값: "hospital_question" - 병원질문)
            page: 페이지 번호 (기본값: 1)
            limit: 한 페이지당 게시글 수 (기본값: 20)
        
        Returns:
            List[Article]: 게시글 목록
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # API 엔드포인트 사용
                url = f"{self.base_url}/api/v2/community"
                
                # 페이지 계산 (API는 start 파라미터 사용)
                start = (page - 1) * limit
                
                # 카테고리 ID 매핑
                category_ids = {
                    "hospital_question": 11,  # 병원질문
                    "surgery_question": 2,    # 시술/수술질문
                    "free_chat": 1,           # 자유수다
                    "review": 5,              # 발품후기
                    "ask_doctor": 13,         # 의사에게 물어보세요
                }
                
                category_id = category_ids.get(category, 11)
                
                params = {
                    "start": start,
                    "length": limit,
                    "sort": "createTime",
                    "categoryIds": category_id,
                    "draw": 0
                }
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                    
                    json_data = await response.json()
                    
                    # FAIL 응답이 나와도 data가 있으면 처리
                    if json_data.get("reason") == "FAIL" and json_data.get("data") is None:
                        return []
                    
                    # data 배열에서 게시글 목록 추출
                    articles_data = json_data.get("data", [])
                    
                    articles = []
                    for item in articles_data:
                        article = self._parse_article_from_api(item)
                        articles.append(article)
                    
                    return articles
                    
        except Exception as e:
            print(f"게시글 목록 가져오기 실패: {e}")
            # API 실패 시 빈 리스트 반환
            return []
    
    async def get_articles_by_date(self, target_date: str, category: str = "hospital_question") -> List[Article]:
        """
        특정 날짜의 게시글을 모두 수집합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식, 예: "2024-01-15")
            category: 카테고리 (기본값: "hospital_question" - 병원질문)
        
        Returns:
            List[Article]: 해당 날짜의 게시글 목록
        """
        try:
            # 날짜 형식 검증
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            print(f"잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요. (예: 2024-01-15)")
            return []
        
        all_articles = []
        page = 1
        max_pages = 100  # 최대 페이지 수 제한
        consecutive_empty_pages = 0  # 연속으로 빈 페이지가 나온 횟수
        max_consecutive_empty = 3  # 최대 연속 빈 페이지 수
        found_target_date = False  # 목표 날짜 게시글을 찾았는지 확인
        
        while page <= max_pages and consecutive_empty_pages < max_consecutive_empty:
            try:
                # 현재 페이지의 게시글 가져오기
                page_articles = await self.get_article_list(category=category, page=page, limit=20)
                
                if not page_articles:
                    consecutive_empty_pages += 1
                    page += 1
                    await asyncio.sleep(1)
                    continue
                
                # 날짜별 필터링
                target_date_articles = []
                older_articles_found = False
                
                for article in page_articles:
                    try:
                        article_date = self._parse_article_date(article.create_time)
                        
                        if article_date == target_date_obj:
                            target_date_articles.append(article)
                            found_target_date = True
                        elif article_date < target_date_obj:
                            # 더 오래된 게시글이 나오면 수집 중단
                            older_articles_found = True
                            break
                        elif article_date > target_date_obj:
                            # 더 최신 게시글이 나오면 계속 진행
                            continue
                            
                    except (ValueError, IndexError) as e:
                        continue
                
                # 해당 날짜의 게시글 추가
                if target_date_articles:
                    all_articles.extend(target_date_articles)
                
                # 더 오래된 게시글이 발견되면 수집 중단
                if older_articles_found:
                    break
                
                # 페이지 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(1)
                
                page += 1
                
            except Exception as e:
                break
        
        return all_articles
    
    def _parse_article_date(self, time_str: str) -> date:
        """
        게시글의 시간 문자열을 날짜로 파싱합니다.
        
        Args:
            time_str: 시간 문자열 (YYYY-MM-DD HH:MM:SS 형식)
        
        Returns:
            date: 파싱된 날짜
        """
        try:
            # "YYYY-MM-DD HH:MM:SS" 형식에서 날짜 부분만 추출
            date_str = time_str.split(' ')[0]
            result = datetime.strptime(date_str, "%Y-%m-%d").date()
            return result
        except (ValueError, IndexError) as e:
            # 오류 발생 시 오늘 날짜 반환
            return datetime.now().date()
    

    
    async def get_comments(self, article_id: int) -> List[Comment]:
        """
        특정 게시글의 댓글 목록을 가져옵니다.
        
        Args:
            article_id: 게시글 ID
        
        Returns:
            List[Comment]: 댓글 목록
        """
        print(f"        🔍 댓글 수집 시작: 게시글 ID {article_id}")
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # 게시글 상세 페이지 URL
                url = f"{self.base_url}/community/{article_id}"
                print(f"        📡 페이지 URL: {url}")
                
                async with session.get(url) as response:
                    print(f"        📊 HTTP 상태: {response.status}")
                    
                    if response.status != 200:
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        print(f"        ❌ HTTP 오류: {error_msg}")
                        raise Exception(error_msg)
                    
                    html_content = await response.text()
                    print(f"        📄 HTML 크기: {len(html_content)} bytes")
                    
                    # __NEXT_DATA__ 스크립트에서 댓글 데이터 추출
                    import re
                    import json
                    
                    # __NEXT_DATA__ 스크립트 태그 찾기
                    next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
                    match = re.search(next_data_pattern, html_content, re.DOTALL)
                    
                    if not match:
                        print(f"        ❌ __NEXT_DATA__ 스크립트를 찾을 수 없습니다.")
                        return []
                    
                    try:
                        next_data = json.loads(match.group(1))
                        print(f"        ✅ __NEXT_DATA__ 파싱 성공")
                        
                        # 댓글 데이터 추출
                        comments_data = next_data.get("props", {}).get("pageProps", {}).get("communityDocumentComments", [])
                        print(f"        📋 원본 댓글 데이터: {len(comments_data)}개")
                        
                        comments = []
                        for i, comment_data in enumerate(comments_data):
                            try:
                                comment = self._parse_comment_from_ssr(comment_data)
                                comments.append(comment)
                                print(f"        ✅ 댓글 {i+1} 파싱 성공: ID {comment.id}, 작성자 {comment.writer.nickname}")
                            except Exception as parse_error:
                                print(f"        ⚠️  댓글 {i+1} 파싱 실패: {parse_error}")
                        
                        print(f"        🎉 총 {len(comments)}개 댓글 파싱 완료")
                        return comments
                        
                    except json.JSONDecodeError as e:
                        print(f"        ❌ JSON 파싱 실패: {e}")
                        return []
                    
        except Exception as e:
            print(f"        ❌ 댓글 수집 실패: {e}")
            print(f"        🔍 에러 타입: {type(e).__name__}")
            # 오류가 발생해도 빈 리스트 반환 (pass 처리)
            return []
    

    
    def _parse_article_from_api(self, data: Dict) -> Article:
        """
        API 응답의 게시글 데이터를 Article 객체로 파싱합니다.
        
        Args:
            data: API 응답의 게시글 데이터 딕셔너리
        
        Returns:
            Article: 파싱된 게시글 객체
        """
        # 작성자 정보 파싱 (API 형식)
        writer = Writer(
            id=data.get("writerId", 0),
            doctor_id=data.get("writerDoctorId"),
            profile=data.get("writerProfile", ""),
            nickname=data.get("writerNickName", ""),
            level=data.get("writerLevel", 1),
            engagement_type=data.get("writerEngagementType")
        )
        
        # 사진 정보 파싱 (API에서는 문자열 배열)
        photos = []
        for photo_url in data.get("photos", []):
            photo = Photo(url=photo_url)
            photos.append(photo)
        
        # createTime을 타임스탬프에서 문자열로 변환
        create_time_timestamp = data.get("createTime", 0)
        if create_time_timestamp:
            create_time_str = self._timestamp_to_readable_time(create_time_timestamp)
        else:
            create_time_str = ""
        
        # 게시글 객체 생성
        article = Article(
            id=data.get("id", 0),
            category_id=data.get("categoryId", 0),
            category_name=data.get("categoryName", ""),
            writer=writer,
            writer_doctor_id=data.get("writerDoctorId"),
            has_thumb_up=data.get("hasThumbUp", False),
            comment_count=data.get("commentCount", 0),
            thumb_up_count=data.get("thumbUpCount", 0),
            view_count=data.get("viewCount", 0),
            create_time=create_time_str,
            edited=data.get("edited", False),
            title="",  # API에는 title 필드가 없음
            contents=data.get("contents", ""),
            photos=photos,
            lang=data.get("lang", "ko"),
            has_doctor_comment=data.get("hasDoctorComment", False),
            translate_result=data.get("translateResult")
        )
        
        return article
    
    def _timestamp_to_readable_time(self, timestamp: int) -> str:
        """
        타임스탬프(밀리초)를 정확한 시간 형식으로 변환합니다.
        
        Args:
            timestamp: 밀리초 타임스탬프
        
        Returns:
            str: 정확한 시간 형식 (YYYY-MM-DD HH:MM:SS)
        """
        from datetime import datetime
        
        # 타임스탬프를 datetime 객체로 변환
        dt = datetime.fromtimestamp(timestamp / 1000)
        
        # 정확한 시간 형식으로 반환
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def _parse_article(self, data: Dict) -> Article:
        """
        게시글 데이터를 Article 객체로 파싱합니다.
        
        Args:
            data: 게시글 데이터 딕셔너리
        
        Returns:
            Article: 파싱된 게시글 객체
        """
        # 작성자 정보 파싱
        writer_data = data.get("writer", {})
        writer = Writer(
            id=writer_data.get("id", 0),
            doctor_id=writer_data.get("doctorId"),
            profile=writer_data.get("profile", ""),
            nickname=writer_data.get("nickname", ""),
            level=writer_data.get("level", 1),
            engagement_type=writer_data.get("engagementType")
        )
        
        # 사진 정보 파싱
        photos = []
        for photo_data in data.get("photos", []):
            photo = Photo(url=photo_data.get("url", ""))
            photos.append(photo)
        
        # 게시글 객체 생성
        article = Article(
            id=data.get("id", 0),
            category_id=data.get("categoryId", 0),
            category_name=data.get("categoryName", ""),
            writer=writer,
            writer_doctor_id=data.get("writerDoctorId"),
            has_thumb_up=data.get("hasThumbUp", False),
            comment_count=data.get("commentCount", 0),
            thumb_up_count=data.get("thumbUpCount", 0),
            view_count=data.get("viewCount", 0),
            create_time=data.get("createTime", ""),
            edited=data.get("edited", False),
            title=data.get("title", ""),
            contents=data.get("contents", ""),
            photos=photos,
            lang=data.get("lang", "ko"),
            has_doctor_comment=data.get("hasDoctorComment", False),
            translate_result=data.get("translateResult")
        )
        
        return article
    

    
    def _parse_comment_from_ssr(self, data: Dict) -> Comment:
        """
        SSR 데이터의 댓글 데이터를 Comment 객체로 파싱합니다.
        
        Args:
            data: SSR 댓글 데이터 딕셔너리
        
        Returns:
            Comment: 파싱된 댓글 객체
        """
        try:
            # 댓글 작성자 정보 파싱 (SSR 형식)
            writer_data = data.get("writer", {})
            writer = Writer(
                id=writer_data.get("id", 0),
                doctor_id=writer_data.get("doctorId"),
                profile=writer_data.get("profile", ""),
                nickname=writer_data.get("nickname", ""),
                level=writer_data.get("level", 1),
                engagement_type=writer_data.get("engagementType")
            )
            
            # createTime은 이미 문자열 형태
            create_time_str = data.get("createTime", "")
            
            # 대댓글 파싱
            replies = []
            replies_data = data.get("replies", [])
            if replies_data:
                print(f"          🔄 대댓글 {len(replies_data)}개 파싱 중...")
                for reply_data in replies_data:
                    reply = self._parse_comment_from_ssr(reply_data)
                    replies.append(reply)
            
            # 댓글 객체 생성
            comment = Comment(
                id=data.get("id", 0),
                status=data.get("status", 1),
                writer=writer,
                create_time=create_time_str,
                reply_comment_id=data.get("replyCommentId"),
                is_admin=data.get("isAdmin", False),
                edited=data.get("edited", False),
                contents=data.get("contents", ""),
                has_thumb_up=data.get("hasThumbUp", False),
                thumb_up_count=data.get("thumbUpCount", 0),
                comment_count=data.get("commentCount", 0),
                callee_nickname=data.get("calleeNickName"),
                lang=data.get("lang", "ko"),
                translate_result=data.get("translateResult"),
                show_original_content=data.get("showOriginalContent", True),
                replies=replies
            )
            
            return comment
            
        except Exception as e:
            print(f"          ❌ 댓글 파싱 실패: {e}")
            print(f"          📋 원본 데이터: {data}")
            raise e
    
    def _parse_comment_from_api(self, data: Dict) -> Comment:
        """
        API 응답의 댓글 데이터를 Comment 객체로 파싱합니다.
        
        Args:
            data: API 응답의 댓글 데이터 딕셔너리
        
        Returns:
            Comment: 파싱된 댓글 객체
        """
        try:
            # 댓글 작성자 정보 파싱 (API 형식)
            writer = Writer(
                id=data.get("writerId", 0),
                doctor_id=data.get("writerDoctorId"),
                profile=data.get("writerProfile", ""),
                nickname=data.get("writerNickName", ""),
                level=data.get("writerLevel", 1),
                engagement_type=data.get("writerEngagementType")
            )
            
            # createTime을 타임스탬프에서 문자열로 변환
            create_time_timestamp = data.get("createTime", 0)
            if create_time_timestamp:
                create_time_str = self._timestamp_to_readable_time(create_time_timestamp)
            else:
                create_time_str = ""
            
            # 대댓글 파싱
            replies = []
            replies_data = data.get("replies", [])
            if replies_data:
                print(f"          🔄 대댓글 {len(replies_data)}개 파싱 중...")
                for reply_data in replies_data:
                    reply = self._parse_comment_from_api(reply_data)
                    replies.append(reply)
            
            # 댓글 객체 생성
            comment = Comment(
                id=data.get("id", 0),
                status=data.get("status", 1),
                writer=writer,
                create_time=create_time_str,
                reply_comment_id=data.get("replyCommentId"),
                is_admin=data.get("isAdmin", False),
                edited=data.get("edited", False),
                contents=data.get("contents", ""),
                has_thumb_up=data.get("hasThumbUp", False),
                thumb_up_count=data.get("thumbUpCount", 0),
                comment_count=data.get("commentCount", 0),
                callee_nickname=data.get("calleeNickName"),
                lang=data.get("lang", "ko"),
                translate_result=data.get("translateResult"),
                show_original_content=data.get("showOriginalContent", True),
                replies=replies
            )
            
            return comment
            
        except Exception as e:
            print(f"          ❌ 댓글 파싱 실패: {e}")
            print(f"          📋 원본 데이터: {data}")
            raise e
    

    
    async def search_articles(self, keyword: str, category: str = "hospital_question") -> List[Article]:
        """
        키워드로 게시글을 검색합니다.
        
        Args:
            keyword: 검색 키워드
            category: 카테고리 (기본값: "hospital_question")
        
        Returns:
            List[Article]: 검색 결과 게시글 목록
        """
        try:
            # 전체 게시글 목록을 가져와서 키워드 필터링
            articles = await self.get_article_list(category=category, page=1, limit=100)
            
            filtered_articles = []
            for article in articles:
                if (keyword.lower() in article.title.lower() or 
                    keyword.lower() in article.contents.lower() or
                    keyword.lower() in article.writer.nickname.lower()):
                    filtered_articles.append(article)
            
            return filtered_articles
            
        except Exception as e:
            print(f"게시글 검색 실패: {e}")
            return []

# 사용 예시
async def main():
    api = GangnamUnniAPI()
    
    # 모든 카테고리의 게시글 수집
    target_date = "2025-08-03"
    categories = {
        "hospital_question": "병원질문",
        "surgery_question": "시술/수술질문", 
        "free_chat": "자유수다",
        "review": "발품후기",
        "ask_doctor": "의사에게 물어보세요"
    }
    
    all_articles = []
    
    for category_key, category_name in categories.items():
        print(f"\n=== {category_name} 카테고리 수집 중 ===")
        articles = await api.get_articles_by_date(target_date, category=category_key)
        print(f"{category_name}: {len(articles)}개 게시글 수집됨")
        
        # 카테고리 정보 추가
        for article in articles:
            article.category_name = category_name
        
        all_articles.extend(articles)
    
    print(f"\n=== {target_date} 전체 게시글 목록 (총 {len(all_articles)}개) ===")
    for i, article in enumerate(all_articles, 1):
        print(f"\n{i}. 게시글 ID: {article.id}")
        print(f"   카테고리: {article.category_name}")
        print(f"   내용: {article.contents}")
        print(f"   작성자: {article.writer.nickname} (레벨 {article.writer.level})")
        print(f"   조회수: {article.view_count}, 댓글: {article.comment_count}")
        print(f"   작성시간: {article.create_time}")
        print(f"   사진 수: {len(article.photos)}")
        
        # 댓글이 있는 경우에만 댓글 가져오기 시도
        if article.comment_count > 0:
            try:
                comments = await api.get_comments(article.id)
                if comments:
                    print(f"   === 댓글 목록 (총 {len(comments)}개) ===")
                    for j, comment in enumerate(comments, 1):
                        print(f"     {j}. 댓글 ID: {comment.id}")
                        print(f"        작성자: {comment.writer.nickname} (레벨 {comment.writer.level})")
                        print(f"        내용: {comment.contents}")
                        print(f"        작성시간: {comment.create_time}")
                        print(f"        좋아요: {comment.thumb_up_count}")
                        
                        if comment.replies:
                            print(f"        대댓글 수: {len(comment.replies)}")
                else:
                    print("   댓글이 없습니다.")
            except Exception as e:
                print(f"   댓글 가져오기 실패: {e}")
        else:
            print("   댓글이 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())

