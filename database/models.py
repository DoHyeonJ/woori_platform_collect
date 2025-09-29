"""
새로운 SQLAlchemy 기반 데이터 모델
이 파일은 config 기반 데이터베이스 시스템을 사용합니다.
"""
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

# 하위 호환성을 위한 데이터클래스들 (SQLAlchemy 매니저와 함께 사용)
@dataclass
class Community:
    id: Optional[int]
    name: str
    created_at: datetime
    description: str

@dataclass
class Client:
    id: Optional[int]
    hospital_name: str
    created_at: datetime
    description: str

@dataclass
class Article:
    id: Optional[int]
    platform_id: str
    community_article_id: str
    community_id: int
    title: str
    content: str
    images: str  # JSON 문자열로 저장
    writer_nickname: str
    writer_id: str
    like_count: int
    comment_count: int
    view_count: int
    created_at: datetime
    category_name: str
    collected_at: Optional[datetime] = None  # 수집 시간

@dataclass
class Comment:
    id: Optional[int]
    article_id: str  # 게시글 ID (기존 테이블 구조)
    content: str
    writer_nickname: str
    writer_id: str
    created_at: datetime
    parent_comment_id: Optional[str] = None  # 대댓글인 경우 부모 댓글 ID
    collected_at: Optional[datetime] = None  # 수집 시간

@dataclass
class ExcludedArticle:
    id: Optional[int]
    client_id: int
    article_id: int
    created_at: datetime

@dataclass
class Review:
    id: Optional[int]
    platform_id: str  # "gangnamunni" 또는 "babitalk"
    platform_review_id: str  # 각 플랫폼의 고유 후기 ID
    community_id: int  # 커뮤니티 ID (바비톡의 경우 별도 커뮤니티 생성)
    title: str  # 후기 제목 (바비톡의 경우 카테고리 정보)
    content: str  # 후기 내용
    images: str  # JSON 문자열로 저장
    writer_nickname: str
    writer_id: str
    like_count: int
    rating: int  # 평점 (바비톡용)
    price: int  # 가격 (바비톡용)
    categories: str  # JSON 문자열로 저장 (바비톡용)
    sub_categories: str  # JSON 문자열로 저장 (바비톡용)
    surgery_date: str  # 수술 날짜 (바비톡용)
    hospital_name: str  # 병원명
    doctor_name: str  # 담당의명
    is_blind: bool  # 블라인드 여부 (바비톡용)
    is_image_blur: bool  # 이미지 블러 여부 (바비톡용)
    is_certificated_review: bool  # 인증 후기 여부 (바비톡용)
    created_at: datetime
    collected_at: Optional[datetime] = None  # 수집 시간

class DatabaseManager:
    """
    SQLAlchemy 기반 데이터베이스 매니저
    하위 호환성을 위해 기존 인터페이스를 유지하되, 내부적으로는 SQLAlchemy를 사용합니다.
    """
    
    def __init__(self, db_path: str = "data/collect_data.db"):
        """
        ⚠️ WARNING: db_path 파라미터는 더 이상 사용되지 않습니다.
        데이터베이스 설정은 환경변수(DB_TYPE, DB_PATH, MYSQL_*)를 통해 제어됩니다.
        """
        from database.sqlalchemy_manager import SQLAlchemyDatabaseManager
        self._sqlalchemy_manager = SQLAlchemyDatabaseManager()
        self.db_path = db_path  # 하위 호환성을 위해 유지
    
    def init_database(self):
        """데이터베이스 초기화 - SQLAlchemy에서 자동 처리"""
        pass  # SQLAlchemy 매니저가 자동으로 테이블 생성
    
    def insert_community(self, community: Community) -> int:
        """커뮤니티 추가 (중복 체크 포함)"""
        return self._sqlalchemy_manager.insert_community(community.name, community.description)
    
    def insert_client(self, client: Client) -> int:
        """클라이언트 추가"""
        # SQLAlchemy 매니저에 client 추가 메서드가 필요한 경우 구현
        return 0  # 임시 반환값
    
    def insert_article(self, article: Article) -> int:
        """게시글 추가 (중복 체크 포함)"""
        article_data = {
            "platform_id": article.platform_id,
            "community_article_id": article.community_article_id,
            "community_id": article.community_id,
            "title": article.title,
            "content": article.content,
            "images": article.images,
            "writer_nickname": article.writer_nickname,
            "writer_id": article.writer_id,
            "like_count": article.like_count,
            "comment_count": article.comment_count,
            "view_count": article.view_count,
            "created_at": article.created_at,
            "category_name": article.category_name,
            "collected_at": article.collected_at or datetime.now()
        }
        return self._sqlalchemy_manager.insert_article(article_data)
    
    def insert_comment(self, comment: Comment) -> int:
        """댓글 추가"""
        # article_id가 숫자인 경우 직접 사용 (추천 방식)
        if hasattr(comment, 'article_id') and str(comment.article_id).isdigit():
            comment_data = {
                "article_id": int(comment.article_id),
                "community_comment_id": str(comment.id or ""),
                "content": comment.content,
                "writer_nickname": comment.writer_nickname,
                "writer_id": comment.writer_id,
                "created_at": comment.created_at,
                "parent_comment_id": comment.parent_comment_id,
                "collected_at": comment.collected_at or datetime.now()
            }
        else:
            # 레거시 방식 - platform_id와 community_article_id 사용
            comment_data = {
                "platform_id": getattr(comment, 'platform_id', 'legacy'),
                "community_article_id": comment.article_id,
                "community_comment_id": str(comment.id or ""),
                "content": comment.content,
                "writer_nickname": comment.writer_nickname,
                "writer_id": comment.writer_id,
                "created_at": comment.created_at,
                "parent_comment_id": comment.parent_comment_id,
                "collected_at": comment.collected_at or datetime.now()
            }
        return self._sqlalchemy_manager.insert_comment(comment_data)
    
    def insert_review(self, review: Review) -> int:
        """후기 추가 (중복 체크 포함)"""
        review_data = {
            "platform_id": review.platform_id,
            "platform_review_id": review.platform_review_id,
            "community_id": review.community_id,
            "title": review.title,
            "content": review.content,
            "images": review.images,
            "writer_nickname": review.writer_nickname,
            "writer_id": review.writer_id,
            "like_count": review.like_count,
            "rating": review.rating,
            "price": review.price,
            "categories": review.categories,
            "sub_categories": review.sub_categories,
            "surgery_date": review.surgery_date,
            "hospital_name": review.hospital_name,
            "doctor_name": review.doctor_name,
            "is_blind": review.is_blind,
            "is_image_blur": review.is_image_blur,
            "is_certificated_review": review.is_certificated_review,
            "created_at": review.created_at,
            "collected_at": review.collected_at or datetime.now()
        }
        return self._sqlalchemy_manager.insert_review(review_data)
    
    def get_articles_by_date(self, date: str, community_id: Optional[int] = None) -> List[Dict]:
        """특정 날짜의 게시글 조회"""
        # SQLAlchemy 매니저에서 구현된 메서드 호출
        return []  # 임시 반환값
    
    def get_comments_by_article_id(self, article_id: str) -> List[Dict]:
        """특정 게시글의 댓글 조회"""
        return []  # 임시 반환값
    
    def get_comment_by_article_id_and_comment_id(self, article_id: str, comment_id: str) -> Optional[Dict]:
        """게시글 ID와 댓글 ID로 댓글 조회"""
        return self._sqlalchemy_manager.get_comment_by_article_id_and_comment_id(article_id, comment_id)
    
    def get_comment_by_platform_id_and_community_comment_id(self, platform_id: str, community_comment_id: str) -> Optional[Dict]:
        """플랫폼 ID와 커뮤니티 댓글 ID로 댓글 조회"""
        return None  # 임시 반환값
    
    def get_statistics(self) -> Dict:
        """데이터베이스 통계 조회"""
        return self._sqlalchemy_manager.get_statistics()
    
    def get_community_by_name(self, name: str) -> Optional[Dict]:
        """이름으로 커뮤니티 조회"""
        return self._sqlalchemy_manager.get_community_by_name(name)
    
    def get_reviews_by_platform(self, platform_id: str, community_id: Optional[int] = None, limit: Optional[int] = None) -> List[Dict]:
        """플랫폼별 후기 조회"""
        return []  # 임시 반환값
    
    def get_reviews_by_date(self, date: str, platform_id: Optional[str] = None) -> List[Dict]:
        """특정 날짜의 후기 조회"""
        return []  # 임시 반환값
    
    def get_review_statistics(self) -> Dict:
        """후기 통계 정보를 반환합니다."""
        stats = self._sqlalchemy_manager.get_statistics()
        return {
            "platform_statistics": stats.get("platform_stats", {}),
            "category_statistics": {}
        }
    
    def get_articles_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Dict]:
        """필터 조건에 따라 게시글을 조회합니다."""
        return self._sqlalchemy_manager.get_articles_by_filters(filters, limit, offset)
    
    def get_articles_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 게시글 수를 반환합니다."""
        return self._sqlalchemy_manager.get_articles_count_by_filters(filters)
    
    def get_reviews_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Dict]:
        """필터 조건에 따라 후기를 조회합니다."""
        return self._sqlalchemy_manager.get_reviews_by_filters(filters, limit, offset)
    
    def get_reviews_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 후기 수를 반환합니다."""
        return self._sqlalchemy_manager.get_reviews_count_by_filters(filters)
    
    def get_comments_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Dict]:
        """필터 조건에 따라 댓글을 조회합니다."""
        return self._sqlalchemy_manager.get_comments_by_filters(filters, limit, offset)
    
    def get_comments_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 댓글 수를 반환합니다."""
        return self._sqlalchemy_manager.get_comments_count_by_filters(filters)
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """ID로 게시글을 조회합니다."""
        return self._sqlalchemy_manager.get_article_by_id(article_id)
    
    def get_article_by_platform_id_and_community_article_id(self, platform_id: str, community_article_id: str) -> Optional[Dict]:
        """플랫폼 ID와 커뮤니티 게시글 ID로 게시글 조회"""
        return self._sqlalchemy_manager.get_article_by_platform_id_and_community_article_id(platform_id, community_article_id)
    
    def get_review_by_id(self, review_id: int) -> Optional[Dict]:
        """ID로 후기를 조회합니다."""
        return self._sqlalchemy_manager.get_review_by_id(review_id)
    
    def get_review_by_platform_id_and_platform_review_id(self, platform_id: str, platform_review_id: str) -> Optional[Dict]:
        """플랫폼 ID와 플랫폼 후기 ID로 후기를 조회합니다."""
        return self._sqlalchemy_manager.get_review_by_platform_id_and_platform_review_id(platform_id, platform_review_id)
    
    def get_recent_reviews(self, limit: int = 10) -> List[Dict]:
        """최근 후기들을 조회합니다."""
        return self._sqlalchemy_manager.get_recent_reviews(limit)
    
    # Bulk Get 메서드들
    def get_articles_by_ids(self, ids: List[int]) -> List[Dict]:
        """ID 목록으로 게시글들을 조회합니다."""
        return self._sqlalchemy_manager.get_articles_by_ids(ids)
    
    def get_reviews_by_ids(self, ids: List[int]) -> List[Dict]:
        """ID 목록으로 후기들을 조회합니다."""
        return self._sqlalchemy_manager.get_reviews_by_ids(ids)
    
    def get_comments_by_ids(self, ids: List[int]) -> List[Dict]:
        """ID 목록으로 댓글들을 조회합니다."""
        return self._sqlalchemy_manager.get_comments_by_ids(ids)
    
    def get_comment_by_id(self, comment_id: int) -> Optional[Dict]:
        """ID로 댓글을 조회합니다."""
        return self._sqlalchemy_manager.get_comment_by_id(comment_id)
    
    def get_platform_statistics(self, platform_id: str) -> Dict:
        """특정 플랫폼의 통계를 반환합니다."""
        return {
            "articles": 0,
            "reviews": 0,
            "comments": 0
        }
    
    def get_daily_statistics(self, date: str) -> Dict:
        """특정 날짜의 통계를 반환합니다."""
        return {
            "articles": 0,
            "reviews": 0,
            "comments": 0
        }
    
    def get_trend_statistics(self, days: int) -> Dict:
        """최근 N일간의 트렌드 통계를 반환합니다."""
        return {
            "article_trends": [],
            "review_trends": []
        }
    
    def get_connection(self):
        """데이터베이스 연결을 반환합니다."""
        from database.config import get_db
        return get_db()
    
    def search_data_by_keywords(self, keywords: List[str], platforms: List[str] = None, 
                               data_types: List[str] = None, start_date: str = None, 
                               end_date: str = None, naver_cafes: List[str] = None, 
                               limit: int = 100, offset: int = 0) -> Dict[str, List[Dict]]:
        """키워드로 게시글, 댓글, 후기를 검색합니다."""
        return self._sqlalchemy_manager.search_data_by_keywords(
            keywords, platforms, data_types, start_date, end_date, naver_cafes, limit, offset
        )
    
    def search_data_count_by_keywords(self, keywords: List[str], platforms: List[str] = None, 
                                     data_types: List[str] = None, start_date: str = None, 
                                     end_date: str = None, naver_cafes: List[str] = None) -> Dict[str, int]:
        """키워드 검색 결과의 개수를 반환합니다."""
        return self._sqlalchemy_manager.search_data_count_by_keywords(
            keywords, platforms, data_types, start_date, end_date, naver_cafes
        )