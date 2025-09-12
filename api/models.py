from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class PlatformType(str, Enum):
    """플랫폼 타입"""
    GANGNAMUNNI = "gangnamunni"
    BABITALK = "babitalk"
    BABITALK_TALK = "babitalk_talk"
    BABITALK_EVENT_ASK = "babitalk_event_ask"
    NAVER = "naver"

class GangnamUnniCategory(str, Enum):
    """강남언니 카테고리 상세"""
    HOSPITAL_QUESTION = "hospital_question"  # 병원질문
    SURGERY_QUESTION = "surgery_question"    # 시술/수술질문
    FREE_CHAT = "free_chat"                  # 자유수다
    REVIEW = "review"                         # 발품후기
    ASK_DOCTOR = "ask_doctor"                # 의사에게 물어보세요

class BabitalkCategory(str, Enum):
    """바비톡 카테고리 상세"""
    SURGERY_REVIEW = "surgery_review"        # 시술 후기
    EVENT_ASK_MEMO = "event_ask_memo"        # 발품후기
    TALK = "talk"                             # 자유톡

class BabitalkEventAskCategory(int, Enum):
    """바비톡 발품후기 카테고리 ID"""
    EYES = 3000           # 눈
    NOSE = 3100           # 코
    LIPOSUCTION = 3200    # 지방흡입/이식
    FACE_CONTOUR = 3300   # 안면윤곽/양악
    BREAST = 3400         # 가슴
    MALE_PLASTIC = 3500   # 남자성형
    ETC = 3600            # 기타

class BabitalkTalkService(int, Enum):
    """바비톡 자유톡 서비스 ID"""
    PLASTIC_SURGERY = 79  # 성형
    BEAUTY_SKIN = 71      # 쁘띠/피부
    DAILY_LIFE = 72       # 일상

class SortType(str, Enum):
    """정렬 타입"""
    RECENT = "recent"      # 최신순
    POPULAR = "popular"    # 인기순
    CREATE_TIME = "createTime"  # 작성시간순

class DataType(str, Enum):
    """데이터 타입"""
    ARTICLE = "article"
    REVIEW = "review"
    COMMENT = "comment"

# 요청 모델들
class GangnamUnniCollectionRequest(BaseModel):
    """강남언니 데이터 수집 요청 모델"""
    category: GangnamUnniCategory = Field(..., description="강남언니 카테고리")
    target_date: str = Field(..., description="수집할 날짜 (YYYY-MM-DD)")
    save_as_reviews: bool = Field(False, description="후기 테이블에 저장할지 여부")
    limit: int = Field(24, ge=1, le=100, description="페이지당 수집할 데이터 수 (1-100)")
    token: Optional[str] = Field(None, description="강남언니 API 토큰 (None이면 기본값 사용)")

class BabitalkCollectionRequest(BaseModel):
    """바비톡 데이터 수집 요청 모델"""
    category: BabitalkCategory = Field(..., description="바비톡 카테고리")
    target_date: str = Field(..., description="수집할 날짜 (YYYY-MM-DD)")
    limit: int = Field(24, ge=1, le=100, description="페이지당 수집할 데이터 수 (1-100)")
    # 발품후기 카테고리별 수집 시 사용
    category_id: Optional[BabitalkEventAskCategory] = Field(None, description="발품후기 카테고리 ID (category가 event_ask_memo일 때 필요)")
    # 자유톡 서비스별 수집 시 사용
    service_id: Optional[BabitalkTalkService] = Field(None, description="자유톡 서비스 ID (category가 talk일 때 필요)")

class NaverCollectionRequest(BaseModel):
    """네이버 카페 데이터 수집 요청 모델"""
    cafe_id: str = Field("12285441", description="카페 ID (예: 10912875)")
    target_date: Optional[str] = Field(None, description="수집할 날짜 (YYYY-MM-DD, 비워두면 오늘 날짜)")
    menu_id: Optional[str] = Field("38", description="특정 게시판 ID (비워두면 전체 게시판)")
    limit: int = Field(20, ge=0, le=100, description="수집할 데이터 수 (0: 제한없음, 1-100: 지정된 수만큼)")
    cookies: str = Field("", description="네이버 로그인 쿠키 (예: NID_AUT=...; NID_SES=...)")

# 응답 모델들
class CollectionResult(BaseModel):
    """데이터 수집 결과 모델"""
    platform: PlatformType = Field(..., description="수집한 플랫폼")
    category: str = Field(..., description="수집한 카테고리")
    target_date: str = Field(..., description="수집한 날짜")
    total_articles: int = Field(0, description="수집된 게시글 수")
    total_comments: int = Field(0, description="수집된 댓글 수")
    total_reviews: int = Field(0, description="수집된 후기 수")
    execution_time: float = Field(..., description="실행 시간 (초)")
    status: str = Field(..., description="수집 상태")
    message: str = Field(..., description="수집 결과 메시지")
    timestamp: datetime = Field(..., description="수집 완료 시간")

class NaverBoardInfo(BaseModel):
    """네이버 카페 게시판 정보"""
    menu_id: int = Field(..., description="게시판 ID")
    menu_name: str = Field(..., description="게시판 이름")
    menu_type: str = Field(..., description="게시판 타입")
    board_type: str = Field(..., description="보드 타입")
    sort: int = Field(..., description="정렬 순서")

class NaverBoardListResponse(BaseModel):
    """네이버 카페 게시판 목록 응답"""
    cafe_id: str = Field(..., description="카페 ID")
    cafe_name: Optional[str] = Field(None, description="카페 이름")
    boards: List[NaverBoardInfo] = Field(..., description="게시판 목록")
    total_boards: int = Field(..., description="총 게시판 수")
    timestamp: datetime = Field(..., description="조회 시간")

class PaginatedResponse(BaseModel):
    """페이지네이션 응답 모델"""
    data: List[Any] = Field(..., description="데이터 목록")
    total: int = Field(..., description="전체 데이터 수")
    page: int = Field(..., description="현재 페이지")
    limit: int = Field(..., description="페이지당 데이터 수")
    total_pages: int = Field(..., description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")

# 데이터 모델들
class Article(BaseModel):
    """게시글 모델"""
    id: Optional[int] = None
    platform_id: str = Field(..., description="플랫폼 ID")
    community_article_id: str = Field(..., description="커뮤니티 게시글 ID")
    community_id: int = Field(..., description="커뮤니티 ID")
    title: Optional[str] = Field(None, description="게시글 제목")
    content: str = Field(..., description="게시글 내용")
    images: Optional[str] = Field(None, description="이미지 JSON 문자열")
    writer_nickname: str = Field(..., description="작성자 닉네임")
    writer_id: str = Field(..., description="작성자 ID")
    like_count: int = Field(0, description="좋아요 수")
    comment_count: int = Field(0, description="댓글 수")
    view_count: int = Field(0, description="조회수")
    created_at: Optional[datetime] = Field(None, description="작성 시간")
    category_name: Optional[str] = Field(None, description="카테고리명")
    collected_at: Optional[datetime] = Field(None, description="수집 시간")
    article_url: Optional[str] = Field(None, description="원문 링크")

class Comment(BaseModel):
    """댓글 모델"""
    id: Optional[int] = None
    platform_id: str = Field(..., description="플랫폼 ID")
    community_article_id: str = Field(..., description="커뮤니티 게시글 ID")
    community_id: int = Field(..., description="커뮤니티 ID")
    comment_id: str = Field(..., description="댓글 ID")
    parent_comment_id: Optional[str] = Field(None, description="부모 댓글 ID")
    content: str = Field(..., description="댓글 내용")
    writer_nickname: str = Field(..., description="작성자 닉네임")
    writer_id: str = Field(..., description="작성자 ID")
    like_count: int = Field(0, description="좋아요 수")
    created_at: Optional[datetime] = Field(None, description="작성 시간")
    collected_at: Optional[datetime] = Field(None, description="수집 시간")

class Review(BaseModel):
    """후기 모델"""
    id: Optional[int] = None
    platform_id: str = Field(..., description="플랫폼 ID")
    platform_review_id: str = Field(..., description="플랫폼 후기 ID")
    community_id: int = Field(..., description="커뮤니티 ID")
    title: Optional[str] = Field(None, description="후기 제목")
    content: str = Field(..., description="후기 내용")
    images: Optional[str] = Field(None, description="이미지 JSON 문자열")
    writer_nickname: str = Field(..., description="작성자 닉네임")
    writer_id: str = Field(..., description="작성자 ID")
    like_count: int = Field(0, description="좋아요 수")
    rating: int = Field(0, description="평점")
    price: int = Field(0, description="가격")
    categories: Optional[str] = Field(None, description="카테고리 JSON 문자열")
    sub_categories: Optional[str] = Field(None, description="하위 카테고리 JSON 문자열")
    surgery_date: Optional[str] = Field(None, description="수술 날짜")
    hospital_name: Optional[str] = Field(None, description="병원명")
    doctor_name: Optional[str] = Field(None, description="담당의명")
    is_blind: bool = Field(False, description="블라인드 여부")
    is_image_blur: bool = Field(False, description="이미지 블러 여부")
    is_certificated_review: bool = Field(False, description="인증 후기 여부")
    created_at: Optional[datetime] = Field(None, description="작성 시간")
    collected_at: Optional[datetime] = Field(None, description="수집 시간")
    article_url: Optional[str] = Field(None, description="원문 링크")

# 검색 관련 모델들
class SearchRequest(BaseModel):
    """키워드 검색 요청 모델"""
    keywords: str = Field(..., description="검색 키워드 (콤마로 구분)")
    platforms: Optional[List[PlatformType]] = Field(None, description="플랫폼 필터 (다중선택)")
    data_types: Optional[List[DataType]] = Field(None, description="데이터 타입 필터 (다중선택)")
    start_date: Optional[str] = Field(None, description="시작 날짜 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="종료 날짜 (YYYY-MM-DD)")
    page: int = Field(1, ge=1, description="페이지 번호")
    limit: int = Field(20, ge=1, le=1000, description="페이지당 데이터 수")

class SearchResponse(BaseModel):
    """키워드 검색 응답 모델"""
    articles: List[Article] = Field(..., description="검색된 게시글 목록")
    comments: List[Comment] = Field(..., description="검색된 댓글 목록")
    reviews: List[Review] = Field(..., description="검색된 후기 목록")
    total_counts: Dict[str, int] = Field(..., description="타입별 총 개수")
    page: int = Field(..., description="현재 페이지")
    limit: int = Field(..., description="페이지당 데이터 수")
    total_pages: int = Field(..., description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")
    search_info: Dict[str, Any] = Field(..., description="검색 조건 정보") 