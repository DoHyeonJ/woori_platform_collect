import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, date
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가 (직접 실행 시)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import LoggedClass

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
class ReviewAuthor:
    id: int
    level: int
    nickName: str
    profileImage: str

@dataclass
class ReviewTreatment:
    id: int
    name: str

@dataclass
class ReviewHospital:
    id: int
    name: str
    districtName: str
    country: str

@dataclass
class ReviewServiceOffer:
    id: int
    operationType: str

@dataclass
class ReviewCost:
    currency: str
    amount: int

@dataclass
class ReviewProgressPhoto:
    url: str
    progressDate: str

@dataclass
class ReviewAmplitudeTreatmentInfo:
    treatmentIdList: List[int]
    treatmentLabelList: List[str]
    treatmentCategoryTagIdList: List[int]
    treatmentCategoryTagLabelList: List[str]
    treatmentGroupTagIdList: List[int]
    treatmentGroupTagLabelList: List[str]
    concernTagIdList: List[int]
    concernTagLabelList: List[str]
    concernBodyPartTagIdList: List[int]
    concernBodyPartTagLabelList: List[str]

@dataclass
class Review:
    id: int
    author: ReviewAuthor
    treatments: List[ReviewTreatment]
    hospital: ReviewHospital
    serviceOffer: Optional[ReviewServiceOffer]
    totalRating: int
    totalCost: Optional[ReviewCost]
    description: str
    descriptionLanguage: str
    beforePhotos: List[str]
    afterPhotos: List[str]
    postedAtUtc: str
    editedLastAtUtc: str
    procedureProofApproved: bool
    amplitudeTreatmentInfo: ReviewAmplitudeTreatmentInfo
    highlights: List[str]
    progressReviewPhotos: List[ReviewProgressPhoto]
    treatmentReceivedAtUtc: str
    lastProgressDate: Optional[str]
    translation: Optional[str]
    costChangedReasons: Optional[Dict]
    isProgressOnGoing: Optional[bool]

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

class GangnamUnniAPI(LoggedClass):
    def __init__(self, token: str = "456c327614a94565b61f40f6683cda6c"):
        super().__init__("GangnamUnniAPI")
        self.base_url = "https://www.gangnamunni.com"
        self.token = token
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    
    async def get_article_list(self, category: str = "hospital_question", page: int = 1) -> List[Article]:
        """
        강남언니 커뮤니티 게시글 목록을 가져옵니다.
        
        Args:
            category: 카테고리 (기본값: "hospital_question" - 병원질문)
            page: 페이지 번호 (기본값: 1)
        
        Returns:
            List[Article]: 게시글 목록
        """
        try:
            # 토큰을 포함한 헤더 생성
            api_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Referer": "https://www.gangnamunni.com/",
                "Origin": "https://www.gangnamunni.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Cookie": f"token={self.token}"
            }
            
            # 새로운 solar API 엔드포인트 사용
            url = f"{self.base_url}/api/solar/search/document"
            
            # 페이지 계산 (API는 start 파라미터 사용, 고정 20개)
            start = (page - 1) * 20
            
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
                "length": 20,  # 고정 20개
                "sort": "createTime",
                "categoryIds": category_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=api_headers) as response:
                    if response.status == 404:
                        raise Exception(f"404 Not Found: 게시글을 찾을 수 없습니다")
                    elif response.status != 200:
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                    
                    json_data = await response.json()
                    
                    # SUCCESS 응답 확인
                    if json_data.get("reason") != "SUCCESS":
                        self.log_error(f"API 응답 오류: {json_data.get('reason')}")
                        return []
                    
                    # data 배열에서 게시글 목록 추출
                    articles_data = json_data.get("data", [])
                    
                    articles = []
                    for item in articles_data:
                        article = self._parse_article_from_solar_api(item)
                        articles.append(article)
                    
                    return articles
                    
        except Exception as e:
            self.log_error(f"게시글 목록 가져오기 실패: {e}")
            # API 실패 시 빈 리스트 반환
            return []
    
    async def get_articles_by_date(self, target_date: str, category: str = "hospital_question") -> List[Article]:
        """
        특정 날짜의 게시글을 수집합니다.
        
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
            self.log_error(f"잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요. (예: 2024-01-15)")
            return []
        
        all_articles = []
        page = 1
        max_pages = 100  # 최대 페이지 수 제한
        consecutive_empty_pages = 0  # 연속으로 빈 페이지가 나온 횟수
        max_consecutive_empty = 3  # 최대 연속 빈 페이지 수
        found_target_date = False  # 목표 날짜 게시글을 찾았는지 확인
        consecutive_404_errors = 0  # 연속 404 에러 횟수
        max_404_errors = 5  # 최대 연속 404 에러 허용 횟수
        
        while page <= max_pages and consecutive_empty_pages < max_consecutive_empty:
            try:
                # 현재 페이지의 게시글 가져오기
                page_articles = await self.get_article_list(category=category, page=page)
                
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
                    self.log_error(f"페이지 {page} 수집 실패: {e}")
                    consecutive_empty_pages += 1
                
                page += 1
                await asyncio.sleep(2)
        
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
        self.log_info(f"        🔍 댓글 수집 시작: 게시글 ID {article_id}")
        
        # 게시글별 5초 딜레이 (과부하 방지)
        await asyncio.sleep(5)
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # 게시글 상세 페이지 URL
                url = f"{self.base_url}/community/{article_id}"
                self.log_info(f"        📡 페이지 URL: {url}")
                
                async with session.get(url) as response:
                    self.log_info(f"        📊 HTTP 상태: {response.status}")
                    
                    if response.status == 404:
                        error_msg = f"404 Not Found: 게시글 ID {article_id}를 찾을 수 없습니다"
                        self.log_error(f"        ❌ HTTP 오류: {error_msg}")
                        raise Exception(error_msg)
                    elif response.status != 200:
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        self.log_error(f"        ❌ HTTP 오류: {error_msg}")
                        raise Exception(error_msg)
                    
                    html_content = await response.text()
                    self.log_info(f"        📄 HTML 크기: {len(html_content)} bytes")
                    
                    # __NEXT_DATA__ 스크립트에서 댓글 데이터 추출
                    import re
                    import json
                    
                    # __NEXT_DATA__ 스크립트 태그 찾기
                    next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
                    match = re.search(next_data_pattern, html_content, re.DOTALL)
                    
                    if not match:
                        self.log_error(f"        ❌ __NEXT_DATA__ 스크립트를 찾을 수 없습니다.")
                        return []
                    
                    try:
                        next_data = json.loads(match.group(1))
                        self.log_info(f"        ✅ __NEXT_DATA__ 파싱 성공")
                        
                        # 댓글 데이터 추출
                        comments_data = next_data.get("props", {}).get("pageProps", {}).get("communityDocumentComments", [])
                        self.log_info(f"        📋 원본 댓글 데이터: {len(comments_data)}개")
                        
                        comments = []
                        for i, comment_data in enumerate(comments_data):
                            try:
                                comment = self._parse_comment_from_ssr(comment_data)
                                comments.append(comment)
                                self.log_info(f"        ✅ 댓글 {i+1} 파싱 성공: ID {comment.id}, 작성자 {comment.writer.nickname}")
                            except Exception as parse_error:
                                self.log_warning(f"        ⚠️  댓글 {i+1} 파싱 실패: {parse_error}")
                        
                        self.log_info(f"        🎉 총 {len(comments)}개 댓글 파싱 완료")
                        return comments
                        
                    except json.JSONDecodeError as e:
                        self.log_error(f"        ❌ JSON 파싱 실패: {e}")
                        return []
                    
        except Exception as e:
            self.log_error(f"        ❌ 댓글 수집 실패: {e}")
            self.log_error(f"        🔍 에러 타입: {type(e).__name__}")
            # 오류가 발생해도 빈 리스트 반환 (pass 처리)
            return []
    
    def _parse_article_from_solar_api(self, data: Dict) -> Article:
        """
        새로운 solar API 응답의 게시글 데이터를 Article 객체로 파싱합니다.
        
        Args:
            data: solar API 응답의 게시글 데이터 딕셔너리
        
        Returns:
            Article: 파싱된 게시글 객체
        """
        # 작성자 정보 파싱 (solar API 형식)
        writer = Writer(
            id=data.get("writerId", 0),
            doctor_id=data.get("writerDoctorId"),
            profile=data.get("writerProfile", ""),
            nickname=data.get("writerNickName", ""),
            level=data.get("writerLevel", 1),
            engagement_type=data.get("writerEngagementType")
        )
        
        # 사진 정보 파싱 (solar API에서는 문자열 배열)
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
            title="",  # solar API에는 title 필드가 없음
            contents=data.get("contents", ""),
            photos=photos,
            lang=data.get("lang", "ko"),
            has_doctor_comment=data.get("hasDoctorComment", False),
            translate_result=data.get("translateResult")
        )
        
        return article

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
                self.log_info(f"          🔄 대댓글 {len(replies_data)}개 파싱 중...")
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
            self.log_error(f"          ❌ 댓글 파싱 실패: {e}")
            self.log_error(f"          📋 원본 데이터: {data}")
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
                self.log_info(f"          🔄 대댓글 {len(replies_data)}개 파싱 중...")
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
            self.log_error(f"          ❌ 댓글 파싱 실패: {e}")
            self.log_error(f"          📋 원본 데이터: {data}")
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
            articles = await self.get_article_list(category=category, page=1)
            
            filtered_articles = []
            for article in articles:
                if (keyword.lower() in article.title.lower() or 
                    keyword.lower() in article.contents.lower() or
                    keyword.lower() in article.writer.nickname.lower()):
                    filtered_articles.append(article)
            
            return filtered_articles
            
        except Exception as e:
            self.log_error(f"게시글 검색 실패: {e}")
            return []

    async def get_reviews(self, page_index: int = 0, page_size: int = 20, sort: str = "RECENT_POSTED_AT", keyword: str = "성형") -> List[Review]:
        """
        강남언니 리뷰 목록을 가져옵니다.
        
        Args:
            page_index: 페이지 인덱스 (기본값: 0)
            page_size: 페이지당 리뷰 수 (기본값: 20)
            sort: 정렬 방식 (기본값: "RECENT_POSTED_AT")
            keyword: 검색 키워드 (기본값: "성형" - 모든 리뷰 조회용)
        
        Returns:
            List[Review]: 리뷰 목록
        """
        try:
            # 리뷰 API 엔드포인트
            url = "https://env.gnsister.com/display/search-view/reviews"
            
            # 요청 헤더
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Authorization": self.token
            }
            
            # 요청 바디
            payload = {
                "filters": {
                    "gender": "",
                    "hasPhotos": False,
                    "procedureProofApproved": False
                },
                "keyword": "고민",
                "pagination": {
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "sort": sort
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                    
                    json_data = await response.json()
                    
                    # contents 배열에서 리뷰 목록 추출
                    reviews_data = json_data.get("contents", [])
                    
                    reviews = []
                    for item in reviews_data:
                        review = self._parse_review_from_api(item)
                        reviews.append(review)
                    
                    return reviews
                    
        except Exception as e:
            self.log_error(f"리뷰 목록 가져오기 실패: {e}")
            return []

    async def get_reviews_by_date(self, target_date: str, max_pages: int = 50) -> List[Review]:
        """
        특정 날짜의 리뷰를 수집합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식, 예: "2024-01-15")
            max_pages: 최대 수집할 페이지 수 (기본값: 50)
        
        Returns:
            List[Review]: 해당 날짜의 리뷰 목록
        """
        try:
            # 날짜 형식 검증
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            self.log_error(f"잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요. (예: 2024-01-15)")
            return []
        
        all_reviews = []
        page_index = 0
        consecutive_empty_pages = 0
        max_consecutive_empty = 3
        found_target_date = False
        consecutive_404_errors = 0
        max_404_errors = 5
        
        while page_index < max_pages and consecutive_empty_pages < max_consecutive_empty:
            try:
                # 현재 페이지의 리뷰 가져오기
                page_reviews = await self.get_reviews(page_index=page_index, page_size=20)
                
                self.log_info(f"📄 페이지 {page_index + 1}: {len(page_reviews)}개 리뷰 조회")
                
                if not page_reviews:
                    consecutive_empty_pages += 1
                    self.log_info(f"📭 빈 페이지 {consecutive_empty_pages}회 연속")
                    page_index += 1
                    await asyncio.sleep(1)
                    continue
                else:
                    consecutive_empty_pages = 0  # 리뷰가 있으면 카운터 리셋
                
                # 날짜별 필터링
                target_date_reviews = []
                older_reviews_found = False
                
                for review in page_reviews:
                    try:
                        # postedAtUtc를 날짜로 변환
                        review_date = self._parse_review_date(review.postedAtUtc)
                        
                        if review_date == target_date_obj:
                            target_date_reviews.append(review)
                            found_target_date = True
                        elif review_date < target_date_obj:
                            # 더 오래된 리뷰가 나오면 수집 중단
                            older_reviews_found = True
                            break
                        elif review_date > target_date_obj:
                            # 더 최신 리뷰가 나오면 계속 진행
                            continue
                            
                    except (ValueError, IndexError) as e:
                        continue
                
                # 해당 날짜의 리뷰 추가
                if target_date_reviews:
                    all_reviews.extend(target_date_reviews)
                    self.log_info(f"✅ 페이지 {page_index + 1}: {len(target_date_reviews)}개 리뷰 추가 (총 {len(all_reviews)}개)")
                else:
                    self.log_info(f"📅 페이지 {page_index + 1}: 해당 날짜 리뷰 없음")
                
                # 더 오래된 리뷰가 발견되면 수집 중단
                if older_reviews_found:
                    self.log_info(f"🛑 더 오래된 리뷰 발견으로 수집 중단 (페이지 {page_index + 1})")
                    break
                
                # 페이지 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(1)
                
                page_index += 1
                
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
                    self.log_error(f"페이지 {page_index} 수집 실패: {e}")
                    consecutive_empty_pages += 1
                
                page_index += 1
                await asyncio.sleep(2)
        
        self.log_info(f"🏁 리뷰 수집 완료: 총 {len(all_reviews)}개 (페이지 {page_index}개 처리)")
        return all_reviews

    async def get_review_detail(self, review_id: int) -> Optional[dict]:
        """리뷰 상세 정보를 가져옵니다."""
        url = "https://env.gnsister.com/review/query/page/user/procedure-journey/v1/review-detail/main"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.token
        }
        payload = {"id": review_id}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        self.log_error(f"❌ 리뷰 상세 조회 실패 (ID: {review_id}): HTTP {response.status}")
                        return None
                    
                    json_data = await response.json()
                    return json_data
                    
        except Exception as e:
            self.log_error(f"❌ 리뷰 상세 조회 중 오류 (ID: {review_id}): {e}")
            return None

    def _parse_review_date(self, utc_time_str: str) -> date:
        """
        리뷰의 UTC 시간 문자열을 날짜로 파싱합니다.
        
        Args:
            utc_time_str: UTC 시간 문자열 (YYYY-MM-DDTHH:MM:SSZ 형식)
        
        Returns:
            date: 파싱된 날짜
        """
        try:
            # "YYYY-MM-DDTHH:MM:SSZ" 형식에서 날짜 부분만 추출
            date_str = utc_time_str.split('T')[0]
            result = datetime.strptime(date_str, "%Y-%m-%d").date()
            return result
        except (ValueError, IndexError) as e:
            # 오류 발생 시 오늘 날짜 반환
            return datetime.now().date()

    def _parse_review_from_api(self, data: Dict) -> Review:
        """
        리뷰 API 응답의 데이터를 Review 객체로 파싱합니다.
        
        Args:
            data: 리뷰 API 응답의 데이터 딕셔너리
        
        Returns:
            Review: 파싱된 리뷰 객체
        """
        # 작성자 정보 파싱
        author_data = data.get("author", {})
        author = ReviewAuthor(
            id=author_data.get("id", 0),
            level=author_data.get("level", 1),
            nickName=author_data.get("nickName", ""),
            profileImage=author_data.get("profileImage", "")
        )
        
        # 시술 정보 파싱
        treatments = []
        for treatment_data in data.get("treatments", []):
            treatment = ReviewTreatment(
                id=treatment_data.get("id", 0),
                name=treatment_data.get("name", "")
            )
            treatments.append(treatment)
        
        # 병원 정보 파싱
        hospital_data = data.get("hospital", {})
        hospital = ReviewHospital(
            id=hospital_data.get("id", 0),
            name=hospital_data.get("name", ""),
            districtName=hospital_data.get("districtName", ""),
            country=hospital_data.get("country", "")
        )
        
        # 서비스 오퍼 정보 파싱
        service_offer = None
        service_offer_data = data.get("serviceOffer")
        if service_offer_data:
            service_offer = ReviewServiceOffer(
                id=service_offer_data.get("id", 0),
                operationType=service_offer_data.get("operationType", "")
            )
        
        # 비용 정보 파싱
        total_cost = None
        cost_data = data.get("totalCost")
        if cost_data:
            total_cost = ReviewCost(
                currency=cost_data.get("currency", ""),
                amount=cost_data.get("amount", 0)
            )
        
        # 진행 사진 파싱
        progress_photos = []
        for photo_data in data.get("progressReviewPhotos", []):
            progress_photo = ReviewProgressPhoto(
                url=photo_data.get("url", ""),
                progressDate=photo_data.get("progressDate", "")
            )
            progress_photos.append(progress_photo)
        
        # 시술 정보 파싱
        amplitude_data = data.get("amplitudeTreatmentInfo", {})
        amplitude_treatment_info = ReviewAmplitudeTreatmentInfo(
            treatmentIdList=amplitude_data.get("treatmentIdList", []),
            treatmentLabelList=amplitude_data.get("treatmentLabelList", []),
            treatmentCategoryTagIdList=amplitude_data.get("treatmentCategoryTagIdList", []),
            treatmentCategoryTagLabelList=amplitude_data.get("treatmentCategoryTagLabelList", []),
            treatmentGroupTagIdList=amplitude_data.get("treatmentGroupTagIdList", []),
            treatmentGroupTagLabelList=amplitude_data.get("treatmentGroupTagLabelList", []),
            concernTagIdList=amplitude_data.get("concernTagIdList", []),
            concernTagLabelList=amplitude_data.get("concernTagLabelList", []),
            concernBodyPartTagIdList=amplitude_data.get("concernBodyPartTagIdList", []),
            concernBodyPartTagLabelList=amplitude_data.get("concernBodyPartTagLabelList", [])
        )
        
        # 리뷰 객체 생성
        review = Review(
            id=data.get("id", 0),
            author=author,
            treatments=treatments,
            hospital=hospital,
            serviceOffer=service_offer,
            totalRating=data.get("totalRating", 0),
            totalCost=total_cost,
            description=data.get("description", ""),
            descriptionLanguage=data.get("descriptionLanguage", "ko"),
            beforePhotos=data.get("beforePhotos", []),
            afterPhotos=data.get("afterPhotos", []),
            postedAtUtc=data.get("postedAtUtc", ""),
            editedLastAtUtc=data.get("editedLastAtUtc", ""),
            procedureProofApproved=data.get("procedureProofApproved", False),
            amplitudeTreatmentInfo=amplitude_treatment_info,
            highlights=data.get("highlights", []),
            progressReviewPhotos=progress_photos,
            treatmentReceivedAtUtc=data.get("treatmentReceivedAtUtc", ""),
            lastProgressDate=data.get("lastProgressDate"),
            translation=data.get("translation"),
            costChangedReasons=data.get("costChangedReasons"),
            isProgressOnGoing=data.get("isProgressOnGoing")
        )
        
        return review

# 테스트 함수
async def test_gannamunni_api():
    """강남언니 API 테스트 함수"""
    from utils.logger import get_logger
    logger = get_logger("GANNAMUNNI_TEST")
    
    logger.info("🧪 강남언니 API 테스트 시작")
    logger.info("=" * 50)
    
    api = GangnamUnniAPI()
    
    try:
        # 게시글 목록 테스트
        logger.info("📝 게시글 목록 테스트")
        articles = await api.get_article_list(category="hospital_question", page=1)
        
        logger.info(f"\n📊 게시글 목록 테스트 결과:")
        logger.info(f"   수집된 게시글: {len(articles)}개")
        
        if articles:
            logger.info(f"\n📝 첫 번째 게시글 상세 정보:")
            first_article = articles[0]
            logger.info(f"   ID: {first_article.id}")
            logger.info(f"   작성자: {first_article.writer.nickname}")
            logger.info(f"   카테고리: {first_article.category_name}")
            logger.info(f"   조회수: {first_article.view_count}")
            logger.info(f"   댓글 수: {first_article.comment_count}")
            logger.info(f"   작성시간: {first_article.create_time}")
            logger.info(f"   내용 미리보기: {first_article.contents[:100]}...")
        
        # 날짜별 게시글 테스트
        logger.info(f"\n📅 날짜별 게시글 테스트")
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"📅 오늘 날짜({today}) 게시글 수집 테스트")
        
        date_articles = await api.get_articles_by_date(today, category="hospital_question")
        
        logger.info(f"📊 날짜별 게시글 테스트 결과:")
        logger.info(f"   수집된 게시글: {len(date_articles)}개")
        
        if date_articles:
            logger.info(f"\n📝 첫 번째 날짜별 게시글 상세 정보:")
            first_date_article = date_articles[0]
            logger.info(f"   ID: {first_date_article.id}")
            logger.info(f"   작성자: {first_date_article.writer.nickname}")
            logger.info(f"   내용 미리보기: {first_date_article.contents[:100]}...")
        
        # 댓글 테스트 (게시글이 있는 경우에만)
        if articles and articles[0].comment_count > 0:
            logger.info(f"\n💬 댓글 테스트")
            comments = await api.get_comments(articles[0].id)
            
            logger.info(f"📊 댓글 테스트 결과:")
            logger.info(f"   수집된 댓글: {len(comments)}개")
            
            if comments:
                logger.info(f"\n📝 첫 번째 댓글 상세 정보:")
                first_comment = comments[0]
                logger.info(f"   ID: {first_comment.id}")
                logger.info(f"   작성자: {first_comment.writer.nickname}")
                logger.info(f"   내용: {first_comment.contents}")
                logger.info(f"   작성시간: {first_comment.create_time}")
        
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        logger.error(f"📋 상세 오류: {traceback.format_exc()}")
    
    logger.info("=" * 50)
    logger.info("🧪 강남언니 API 테스트 완료")

async def test_get_reviews():
    from utils.logger import get_logger
    logger = get_logger("GANNAMUNNI_TEST")
    
    logger.info("🧪 강남언니 API 테스트 시작")
    logger.info("=" * 50)
    
    api = GangnamUnniAPI("ca06262d608b4ea3be4cc026454081cd")
    
    # get_reviews 함수 호출 테스트
    logger.info(f"\n🧪 get_reviews 함수 호출 테스트")
    try:
        reviews = await api.get_reviews(page_index=100, page_size=20)
        logger.info(f"📊 get_reviews 결과: {len(reviews)}개 리뷰 수집됨")
        if reviews:
            # print(reviews)
            # logger.info(f"📝 첫 번째 리뷰 정보:")
            # first_review = reviews[0]
            pass
            
    except Exception as e:
        logger.error(f"❌ get_reviews 테스트 중 오류 발생: {e}")


if __name__ == "__main__":
    asyncio.run(test_get_reviews())

