import asyncio
import aiohttp
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class BabitalkUser:
    id: int
    name: str
    profile: Optional[str]

@dataclass
class BabitalkImage:
    id: int
    url: str
    small_url: str
    is_after: bool
    order: int
    is_main: bool
    is_blur: bool

@dataclass
class BabitalkEvent:
    id: int
    name: str
    image: str
    price: int
    discount_price: int
    is_live: bool
    include_vat: bool

@dataclass
class BabitalkDoctor:
    id: int
    name: str
    specialist: str
    position: str
    profile_photo: str

@dataclass
class BabitalkHospital:
    id: int
    name: str
    image: str
    region: str
    star_avg: float
    review_count: int

@dataclass
class BabitalkReview:
    id: int
    categories: List[str]
    sub_categories: List[str]
    concerns: Optional[str]
    surgery_date: str
    created_at: str
    rating: int
    text: str
    is_blind: bool
    is_image_blur: bool
    is_certificated_review: bool
    images: List[BabitalkImage]
    price: int
    service: str
    user: BabitalkUser
    event: Optional[BabitalkEvent]
    search_doctor: Optional[BabitalkDoctor]
    hospital: Optional[BabitalkHospital]

@dataclass
class BabitalkPagination:
    has_next: bool
    search_after: Optional[int]

@dataclass
class BabitalkEventAskMemo:
    id: int
    star_score: int
    category: str
    main_category_id: int
    region: str
    hospital_name: str
    user: BabitalkUser
    first_write_at: str
    real_price: int
    text: str

@dataclass
class BabitalkEventAskMemoPagination:
    has_next: bool
    search_after: Optional[int]

@dataclass
class BabitalkTalk:
    id: int
    service_id: int
    title: str
    text: str
    total_comment: int
    created_at: str
    is_vote: bool
    is_best: bool
    is_notice: bool
    user: BabitalkUser
    images: List[BabitalkImage]

@dataclass
class BabitalkTalkPagination:
    has_next: bool
    search_after: Optional[int]

class BabitalkAPI:
    def __init__(self):
        self.base_url = "https://web-api.babitalk.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
    
    async def get_surgery_reviews(self, limit: int = 24, search_after: Optional[int] = None, sort: str = "popular") -> tuple[List[BabitalkReview], BabitalkPagination]:
        """
        시술 후기 목록을 가져옵니다.
        
        Args:
            limit: 한 페이지당 후기 수 (기본값: 24)
            search_after: 페이지네이션 커서 (기본값: None)
            sort: 정렬 방식 (기본값: "popular")
        
        Returns:
            tuple[List[BabitalkReview], BabitalkPagination]: 후기 목록과 페이지네이션 정보
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # API 엔드포인트
                url = f"{self.base_url}/v1/review/"
                
                # 파라미터 구성
                params = {
                    "service": "SURGERY",
                    "limit": limit,
                    "sort": sort
                }
                
                if search_after is not None:
                    params["search_after"] = search_after
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        raise Exception(error_msg)
                    
                    json_data = await response.json()
                    
                    # 데이터 파싱
                    reviews_data = json_data.get("data", [])
                    pagination_data = json_data.get("pagination", {})
                    
                    # 후기 객체 생성
                    reviews = []
                    for review_data in reviews_data:
                        try:
                            review = self._parse_review(review_data)
                            reviews.append(review)
                        except Exception:
                            continue
                    
                    # 페이지네이션 객체 생성
                    pagination = BabitalkPagination(
                        has_next=pagination_data.get("has_next", False),
                        search_after=pagination_data.get("search_after")
                    )
                    
                    return reviews, pagination
                    
        except Exception as e:
            print(f"❌ 시술 후기 수집 실패: {e}")
            print(f"🔍 에러 타입: {type(e).__name__}")
            import traceback
            print(f"📋 상세 에러: {traceback.format_exc()}")
            return [], BabitalkPagination(has_next=False, search_after=None)
    
    async def get_reviews_by_date(self, target_date: str, limit: int = 24) -> List[BabitalkReview]:
        """
        특정 날짜의 모든 후기를 수집합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            limit: 한 페이지당 후기 수 (기본값: 24)
        
        Returns:
            List[BabitalkReview]: 해당 날짜의 모든 후기 목록
        """
        all_reviews = []
        search_after = 0  # 최신순으로 시작
        page = 1
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        
        try:
            while True:
                # API에서 후기 데이터 가져오기 (최신순)
                reviews, pagination = await self.get_surgery_reviews(
                    limit=limit,
                    search_after=search_after,
                    sort="recent"
                )
                
                if not reviews:
                    break
                
                # 날짜 필터링
                date_filtered_reviews = []
                for review in reviews:
                    try:
                        # created_at 파싱 (예: "2025-01-15 16:45:01")
                        review_date_str = review.created_at.split()[0]  # 날짜 부분만 추출
                        review_date = datetime.strptime(review_date_str, "%Y-%m-%d")
                        
                        if review_date.date() == target_date_obj.date():
                            date_filtered_reviews.append(review)
                        elif review_date.date() < target_date_obj.date():
                            # 과거 날짜를 만나면 더 이상 해당 날짜의 후기가 없으므로 중단
                            return all_reviews
                            
                    except Exception:
                        continue
                
                # 필터링된 후기 추가
                all_reviews.extend(date_filtered_reviews)
                
                # 다음 페이지 확인
                if not pagination.has_next or not pagination.search_after:
                    break
                
                search_after = pagination.search_after
                page += 1
                
                # 페이지 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(1)
            
            return all_reviews
            
        except Exception as e:
            print(f"❌ 날짜별 후기 수집 중 오류 발생: {e}")
            return all_reviews
    
    # 카테고리별 발품후기 수집을 위한 카테고리 정보
    EVENT_ASK_CATEGORIES = {
        3000: "눈",
        3100: "코", 
        3200: "지방흡입/이식",
        3300: "안면윤곽/양악",
        3400: "가슴",
        3500: "남자성형",
        3600: "기타"
    }
    
    # 자유톡 서비스별 카테고리 정보
    TALK_SERVICE_CATEGORIES = {
        79: "성형",
        71: "쁘띠/피부", 
        72: "일상"
    }
    
    async def get_event_ask_memos(self, category_id: int, limit: int = 24, search_after: Optional[int] = None, sort: str = "recent") -> tuple[List[BabitalkEventAskMemo], BabitalkEventAskMemoPagination]:
        """
        발품후기 목록을 가져옵니다.
        
        Args:
            category_id: 카테고리 ID (3000: 눈, 3100: 코, 3200: 지방흡입/이식, 3300: 안면윤곽/양악, 3400: 가슴, 3500: 남자성형, 3600: 기타)
            limit: 한 페이지당 후기 수 (기본값: 24)
            search_after: 페이지네이션 커서 (기본값: None)
            sort: 정렬 방식 (기본값: "recent")
        
        Returns:
            tuple[List[BabitalkEventAskMemo], BabitalkEventAskMemoPagination]: 발품후기 목록과 페이지네이션 정보
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # API 엔드포인트
                url = f"{self.base_url}/v1/event_ask_memos/"
                
                # 파라미터 구성
                params = {
                    "limit": limit,
                    "category_type": 305,
                    "sort": sort,
                    "category_id": category_id
                }
                
                if search_after is not None:
                    params["search_after"] = search_after
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        raise Exception(error_msg)
                    
                    json_data = await response.json()
                    
                    # 데이터 파싱
                    memos_data = json_data.get("data", [])
                    pagination_data = json_data.get("pagination", {})
                    
                    # 발품후기 객체 생성
                    memos = []
                    for memo_data in memos_data:
                        try:
                            memo = self._parse_event_ask_memo(memo_data)
                            memos.append(memo)
                        except Exception:
                            continue
                    
                    # 페이지네이션 객체 생성
                    pagination = BabitalkEventAskMemoPagination(
                        has_next=pagination_data.get("has_next", False),
                        search_after=pagination_data.get("search_after")
                    )
                    
                    return memos, pagination
                    
        except Exception as e:
            print(f"❌ 발품후기 수집 실패: {e}")
            print(f"🔍 에러 타입: {type(e).__name__}")
            import traceback
            print(f"📋 상세 에러: {traceback.format_exc()}")
            return [], BabitalkEventAskMemoPagination(has_next=False, search_after=None)
    
    async def get_event_ask_memos_by_date(self, target_date: str, category_id: int, limit: int = 24) -> List[BabitalkEventAskMemo]:
        """
        특정 날짜의 모든 발품후기를 수집합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            category_id: 카테고리 ID
            limit: 한 페이지당 후기 수 (기본값: 24)
        
        Returns:
            List[BabitalkEventAskMemo]: 해당 날짜의 모든 발품후기 목록
        """
        all_memos = []
        search_after = 0  # 최신순으로 시작
        page = 1
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        
        try:
            while True:
                # API에서 발품후기 데이터 가져오기 (최신순)
                memos, pagination = await self.get_event_ask_memos(
                    category_id=category_id,
                    limit=limit,
                    search_after=search_after,
                    sort="recent"
                )
                
                if not memos:
                    break
                
                # 날짜 필터링 (first_write_at은 "20분전", "17시간전" 등의 형식이므로 현재 시간 기준으로 계산)
                date_filtered_memos = []
                for memo in memos:
                    try:
                        # first_write_at을 실제 날짜로 변환 (현재 시간 기준)
                        memo_date = self._parse_relative_time_to_date(memo.first_write_at)
                        
                        if memo_date.date() == target_date_obj.date():
                            date_filtered_memos.append(memo)
                        elif memo_date.date() < target_date_obj.date():
                            # 과거 날짜를 만나면 더 이상 해당 날짜의 발품후기가 없으므로 중단
                            return all_memos
                            
                    except Exception:
                        continue
                
                # 필터링된 발품후기 추가
                all_memos.extend(date_filtered_memos)
                
                # 다음 페이지 확인
                if not pagination.has_next or not pagination.search_after:
                    break
                
                search_after = pagination.search_after
                page += 1
                
                # 페이지 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(1)
            
            return all_memos
            
        except Exception as e:
            print(f"❌ 날짜별 발품후기 수집 중 오류 발생: {e}")
            return all_memos
    
    def _parse_review(self, data: Dict) -> BabitalkReview:
        """
        API 응답의 후기 데이터를 BabitalkReview 객체로 파싱합니다.
        
        Args:
            data: API 응답의 후기 데이터 딕셔너리
        
        Returns:
            BabitalkReview: 파싱된 후기 객체
        """
        # 사용자 정보 파싱
        user_data = data.get("user", {})
        user = BabitalkUser(
            id=user_data.get("id", 0),
            name=user_data.get("name", ""),
            profile=user_data.get("profile")
        )
        
        # 이미지 정보 파싱
        images = []
        for image_data in data.get("images", []):
            image = BabitalkImage(
                id=image_data.get("id", 0),
                url=image_data.get("url", ""),
                small_url=image_data.get("small_url", ""),
                is_after=image_data.get("is_after", False),
                order=image_data.get("order", 0),
                is_main=image_data.get("is_main", False),
                is_blur=image_data.get("is_blur", False)
            )
            images.append(image)
        
        # 이벤트 정보 파싱 (선택적)
        event = None
        if data.get("event"):
            event_data = data["event"]
            event = BabitalkEvent(
                id=event_data.get("id", 0),
                name=event_data.get("name", ""),
                image=event_data.get("image", ""),
                price=event_data.get("price", 0),
                discount_price=event_data.get("discount_price", 0),
                is_live=event_data.get("is_live", False),
                include_vat=event_data.get("include_vat", False)
            )
        
        # 의사 정보 파싱 (선택적)
        search_doctor = None
        if data.get("search_doctor"):
            doctor_data = data["search_doctor"]
            search_doctor = BabitalkDoctor(
                id=doctor_data.get("id", 0),
                name=doctor_data.get("name", ""),
                specialist=doctor_data.get("specialist", ""),
                position=doctor_data.get("position", ""),
                profile_photo=doctor_data.get("profile_photo", "")
            )
        
        # 병원 정보 파싱 (선택적)
        hospital = None
        if data.get("hospital"):
            hospital_data = data["hospital"]
            hospital = BabitalkHospital(
                id=hospital_data.get("id", 0),
                name=hospital_data.get("name", ""),
                image=hospital_data.get("image", ""),
                region=hospital_data.get("region", ""),
                star_avg=hospital_data.get("star_avg", 0.0),
                review_count=hospital_data.get("review_count", 0)
            )
        
        # 후기 객체 생성
        review = BabitalkReview(
            id=data.get("id", 0),
            categories=data.get("categories", []),
            sub_categories=data.get("sub_categories", []),
            concerns=data.get("concerns"),
            surgery_date=data.get("surgery_date", ""),
            created_at=data.get("created_at", ""),
            rating=data.get("rating", 0),
            text=data.get("text", ""),
            is_blind=data.get("is_blind", False),
            is_image_blur=data.get("is_image_blur", False),
            is_certificated_review=data.get("is_certificated_review", False),
            images=images,
            price=data.get("price", 0),
            service=data.get("service", ""),
            user=user,
            event=event,
            search_doctor=search_doctor,
            hospital=hospital
        )
        
        return review
    
    def _parse_event_ask_memo(self, data: Dict) -> BabitalkEventAskMemo:
        """
        API 응답의 발품후기 데이터를 BabitalkEventAskMemo 객체로 파싱합니다.
        
        Args:
            data: API 응답의 발품후기 데이터 딕셔너리
        
        Returns:
            BabitalkEventAskMemo: 파싱된 발품후기 객체
        """
        # 사용자 정보 파싱
        user_data = data.get("user", {})
        user = BabitalkUser(
            id=user_data.get("id", 0),
            name=user_data.get("name", ""),
            profile=user_data.get("profile")
        )
        
        # 발품후기 객체 생성
        memo = BabitalkEventAskMemo(
            id=data.get("id", 0),
            star_score=data.get("star_score", 0),
            category=data.get("category", ""),
            main_category_id=data.get("main_category_id", 0),
            region=data.get("region", ""),
            hospital_name=data.get("hospital_name", ""),
            user=user,
            first_write_at=data.get("first_write_at", ""),
            real_price=data.get("real_price", 0),
            text=data.get("text", "")
        )
        
        return memo
    
    def _parse_relative_time_to_date(self, relative_time: str) -> datetime:
        """
        상대적 시간 표현을 실제 날짜로 변환합니다.
        
        Args:
            relative_time: "20분전", "17시간전", "3일전" 등의 상대적 시간 표현
        
        Returns:
            datetime: 실제 날짜
        """
        now = datetime.now()
        
        if "분전" in relative_time:
            minutes = int(relative_time.replace("분전", ""))
            return now - timedelta(minutes=minutes)
        elif "시간전" in relative_time:
            hours = int(relative_time.replace("시간전", ""))
            return now - timedelta(hours=hours)
        elif "일전" in relative_time:
            days = int(relative_time.replace("일전", ""))
            return now - timedelta(days=days)
        else:
            # 알 수 없는 형식이면 현재 시간 반환
            return now

    async def get_talks(self, service_id: int, limit: int = 24, search_after: Optional[int] = None, sort: str = "recent") -> tuple[List[BabitalkTalk], BabitalkTalkPagination]:
        """
        자유톡 목록을 가져옵니다.
        
        Args:
            service_id: 서비스 ID (79: 성형, 71: 쁘띠/피부, 72: 일상)
            limit: 한 페이지당 게시글 수 (기본값: 24)
            search_after: 페이지네이션 커서 (기본값: None)
            sort: 정렬 방식 (기본값: "recent")
        
        Returns:
            tuple[List[BabitalkTalk], BabitalkTalkPagination]: 자유톡 목록과 페이지네이션 정보
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # API 엔드포인트
                url = f"{self.base_url}/v1/community/talks"
                
                # 파라미터 구성
                params = {
                    "service_id": service_id,
                    "limit": limit,
                    "sort": sort
                }
                
                if search_after is not None:
                    params["search_after"] = search_after
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        raise Exception(error_msg)
                    
                    json_data = await response.json()
                    
                    # 데이터 파싱
                    talks_data = json_data.get("data", [])
                    pagination_data = json_data.get("pagination", {})
                    
                    # 자유톡 객체 생성
                    talks = []
                    for talk_data in talks_data:
                        try:
                            talk = self._parse_talk(talk_data)
                            talks.append(talk)
                        except Exception:
                            continue
                    
                    # 페이지네이션 객체 생성
                    pagination = BabitalkTalkPagination(
                        has_next=pagination_data.get("has_next", False),
                        search_after=pagination_data.get("search_after")
                    )
                    
                    return talks, pagination
                    
        except Exception as e:
            print(f"❌ 자유톡 수집 실패: {e}")
            print(f"🔍 에러 타입: {type(e).__name__}")
            import traceback
            print(f"📋 상세 에러: {traceback.format_exc()}")
            return [], BabitalkTalkPagination(has_next=False, search_after=None)

    async def get_talks_by_date(self, target_date: str, service_id: int, limit: int = 24) -> List[BabitalkTalk]:
        """
        특정 날짜의 모든 자유톡을 수집합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            service_id: 서비스 ID (79: 성형, 71: 쁘띠/피부, 72: 일상)
            limit: 한 페이지당 게시글 수 (기본값: 24)
        
        Returns:
            List[BabitalkTalk]: 해당 날짜의 모든 자유톡 목록
        """
        all_talks = []
        search_after = 0  # 최신순으로 시작
        page = 1
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        
        try:
            while True:
                # API에서 자유톡 데이터 가져오기 (최신순)
                talks, pagination = await self.get_talks(
                    service_id=service_id,
                    limit=limit,
                    search_after=search_after,
                    sort="recent"
                )
                
                if not talks:
                    break
                
                # 날짜 필터링
                date_filtered_talks = []
                for talk in talks:
                    try:
                        # created_at 파싱 (예: "2025-01-15 16:45:01")
                        talk_date_str = talk.created_at.split()[0]  # 날짜 부분만 추출
                        talk_date = datetime.strptime(talk_date_str, "%Y-%m-%d")
                        
                        if talk_date.date() == target_date_obj.date():
                            date_filtered_talks.append(talk)
                        elif talk_date.date() < target_date_obj.date():
                            # 과거 날짜를 만나면 더 이상 해당 날짜의 자유톡이 없으므로 중단
                            return all_talks
                            
                    except Exception:
                        continue
                
                # 필터링된 자유톡 추가
                all_talks.extend(date_filtered_talks)
                
                # 다음 페이지 확인
                if not pagination.has_next or not pagination.search_after:
                    break
                
                search_after = pagination.search_after
                page += 1
                
                # 페이지 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(1)
            
            return all_talks
            
        except Exception as e:
            print(f"❌ 날짜별 자유톡 수집 중 오류 발생: {e}")
            return all_talks

    def _parse_talk(self, data: Dict) -> BabitalkTalk:
        """
        자유톡 API 응답 데이터를 BabitalkTalk 객체로 파싱합니다.
        
        Args:
            data: API 응답의 자유톡 데이터
        
        Returns:
            BabitalkTalk: 파싱된 자유톡 객체
        """
        # 사용자 정보 파싱
        user_data = data.get("user", {})
        user = BabitalkUser(
            id=user_data.get("id", 0),
            name=user_data.get("name", ""),
            profile=user_data.get("profile")
        )
        
        # 이미지 정보 파싱
        images_data = data.get("images", [])
        images = []
        for img_data in images_data:
            image = BabitalkImage(
                id=img_data.get("id") or 0,
                url=img_data.get("url", ""),
                small_url=img_data.get("small_url", ""),
                is_after=img_data.get("is_after") or False,
                order=img_data.get("order", 0),
                is_main=img_data.get("is_main", False),
                is_blur=img_data.get("is_blur", False)
            )
            images.append(image)
        
        # 자유톡 객체 생성
        talk = BabitalkTalk(
            id=data.get("id", 0),
            service_id=data.get("service_id", 0),
            title=data.get("title", ""),
            text=data.get("text", ""),
            total_comment=data.get("total_comment", 0),
            created_at=data.get("created_at", ""),
            is_vote=data.get("is_vote", False),
            is_best=data.get("is_best", False),
            is_notice=data.get("is_notice", False),
            user=user,
            images=images
        )
        
        return talk

# 테스트 함수
async def test_babitalk_api():
    """바비톡 API 테스트 함수"""
    print("🧪 바비톡 API 테스트 시작")
    print("=" * 50)
    
    api = BabitalkAPI()
    
    try:
        # 자유톡 API 테스트 (성형 카테고리)
        print("💬 자유톡 API 테스트 (성형 카테고리)")
        talks, pagination = await api.get_talks(service_id=79, limit=5)
        
        print(f"\n📊 자유톡 테스트 결과:")
        print(f"   수집된 자유톡: {len(talks)}개")
        print(f"   다음 페이지 존재: {pagination.has_next}")
        print(f"   다음 페이지 커서: {pagination.search_after}")
        
        if talks:
            print(f"\n📝 첫 번째 자유톡 상세 정보:")
            first_talk = talks[0]
            print(f"   ID: {first_talk.id}")
            print(f"   제목: {first_talk.title}")
            print(f"   작성자: {first_talk.user.name}")
            print(f"   서비스 ID: {first_talk.service_id}")
            print(f"   댓글 수: {first_talk.total_comment}")
            print(f"   베스트 여부: {first_talk.is_best}")
            print(f"   작성일: {first_talk.created_at}")
            print(f"   내용 미리보기: {first_talk.text[:100]}...")
        
        # 발품후기 API 테스트 (눈 카테고리)
        print("\n👁️ 발품후기 API 테스트 (눈 카테고리)")
        memos, pagination = await api.get_event_ask_memos(category_id=3000, limit=5)
        
        print(f"\n📊 발품후기 테스트 결과:")
        print(f"   수집된 발품후기: {len(memos)}개")
        print(f"   다음 페이지 존재: {pagination.has_next}")
        print(f"   다음 페이지 커서: {pagination.search_after}")
        
        if memos:
            print(f"\n📝 첫 번째 발품후기 상세 정보:")
            first_memo = memos[0]
            print(f"   ID: {first_memo.id}")
            print(f"   작성자: {first_memo.user.name}")
            print(f"   카테고리: {first_memo.category}")
            print(f"   지역: {first_memo.region}")
            print(f"   병원명: {first_memo.hospital_name}")
            print(f"   평점: {first_memo.star_score}/5")
            print(f"   가격: {first_memo.real_price:,}원")
            print(f"   작성시간: {first_memo.first_write_at}")
            print(f"   내용 미리보기: {first_memo.text[:100]}...")
        
        # 기존 시술후기 테스트도 유지
        print(f"\n📅 시술후기 API 테스트")
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"📅 오늘 날짜({today}) 시술후기 수집 테스트")
        
        reviews = await api.get_reviews_by_date(today, limit=3)
        
        print(f"📊 시술후기 테스트 결과:")
        print(f"   수집된 시술후기: {len(reviews)}개")
        
        if reviews:
            print(f"\n📝 첫 번째 시술후기 상세 정보:")
            first_review = reviews[0]
            print(f"   ID: {first_review.id}")
            print(f"   작성자: {first_review.user.name}")
            print(f"   카테고리: {', '.join(first_review.categories)}")
            print(f"   평점: {first_review.rating}/5")
            print(f"   가격: {first_review.price:,}원")
            print(f"   작성일: {first_review.created_at}")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print("=" * 50)
    print("🧪 바비톡 API 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_babitalk_api())
