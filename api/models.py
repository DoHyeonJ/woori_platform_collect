from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class PlatformType(str, Enum):
    """플랫폼 타입"""
    GANGNAMUNNI = "gangnamunni"
    BABITALK = "babitalk"

class CategoryType(str, Enum):
    """카테고리 타입"""
    # 강남언니 카테고리
    HOSPITAL_QUESTION = "hospital_question"
    SURGERY_QUESTION = "surgery_question"
    FREE_CHAT = "free_chat"
    REVIEW = "review"
    ASK_DOCTOR = "ask_doctor"
    
    # 바비톡 카테고리
    SURGERY_REVIEW = "surgery_review"
    EVENT_ASK_MEMO = "event_ask_memo"
    TALK = "talk"

class DataType(str, Enum):
    """데이터 타입"""
    ARTICLE = "article"
    REVIEW = "review"
    COMMENT = "comment"

# 요청 모델들
class CollectionRequest(BaseModel):
    """데이터 수집 요청 모델"""
    platform: PlatformType
    category: CategoryType
    target_date: str = Field(..., description="수집할 날짜 (YYYY-MM-DD)")
    save_as_reviews: bool = Field(False, description="후기 테이블에 저장할지 여부")
    limit: int = Field(24, description="페이지당 수집할 데이터 수")

class BatchCollectionRequest(BaseModel):
    """배치 데이터 수집 요청 모델"""
    platform: PlatformType
    target_date: str = Field(..., description="수집할 날짜 (YYYY-MM-DD)")
    save_as_reviews: bool = Field(False, description="후기 테이블에 저장할지 여부")
    limit: int = Field(24, description="페이지당 수집할 데이터 수")

class DateRangeRequest(BaseModel):
    """날짜 범위 요청 모델"""
    start_date: str = Field(..., description="시작 날짜 (YYYY-MM-DD)")
    end_date: str = Field(..., description="종료 날짜 (YYYY-MM-DD)")
    platform: Optional[PlatformType] = None
    category: Optional[CategoryType] = None

class PaginationRequest(BaseModel):
    """페이지네이션 요청 모델"""
    page: int = Field(1, ge=1, description="페이지 번호")
    limit: int = Field(20, ge=1, le=100, description="페이지당 데이터 수")

# 응답 모델들
class CollectionResult(BaseModel):
    """데이터 수집 결과 모델"""
    platform: PlatformType
    category: CategoryType
    target_date: str
    total_articles: int
    total_comments: int
    total_reviews: int
    execution_time: float
    status: str
    message: str
    timestamp: datetime

class BatchCollectionResult(BaseModel):
    """배치 데이터 수집 결과 모델"""
    platform: PlatformType
    target_date: str
    categories: Dict[str, CollectionResult]
    total_articles: int
    total_comments: int
    total_reviews: int
    execution_time: float
    status: str
    message: str
    timestamp: datetime

class ArticleResponse(BaseModel):
    """게시글 응답 모델"""
    id: int
    platform_id: str
    community_article_id: int
    community_id: int
    title: str
    content: str
    writer_nickname: str
    writer_id: str
    like_count: int
    comment_count: int
    view_count: int
    images: str
    created_at: datetime
    category_name: str

class ReviewResponse(BaseModel):
    """후기 응답 모델"""
    id: int
    platform_id: str
    platform_review_id: int
    community_id: int
    title: str
    content: str
    writer_nickname: str
    writer_id: str
    rating: int
    price: int
    images: str
    hospital_name: str
    doctor_name: str
    created_at: datetime
    category_name: str

class CommentResponse(BaseModel):
    """댓글 응답 모델"""
    id: int
    article_id: int
    parent_comment_id: Optional[int]
    writer_nickname: str
    writer_id: str
    content: str
    like_count: int
    created_at: datetime

class StatisticsResponse(BaseModel):
    """통계 응답 모델"""
    total_communities: int
    total_articles: int
    total_reviews: int
    total_comments: int
    platform_statistics: Dict[str, Dict[str, int]]
    review_statistics: Dict[str, int]
    timestamp: datetime

class PaginatedResponse(BaseModel):
    """페이지네이션 응답 모델"""
    data: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool

class HealthResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str
    database: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str
    message: str
    timestamp: datetime 