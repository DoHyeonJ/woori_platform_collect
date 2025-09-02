"""
Legacy SQLite DatabaseManager - 호환성을 위해 보관
이 파일은 기존 스크립트들과의 호환성을 위해 유지됩니다.
새로운 개발에서는 database/sqlalchemy_manager.py를 사용하세요.
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

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

class LegacyDatabaseManager:
    """Legacy SQLite DatabaseManager - 호환성을 위해 유지"""
    
    def __init__(self, db_path: str = "data/collect_data.db"):
        print("⚠️ WARNING: LegacyDatabaseManager는 더 이상 사용되지 않습니다.")
        print("   새로운 개발에서는 database.sqlalchemy_manager.SQLAlchemyDatabaseManager를 사용하세요.")
        
        from database.sqlalchemy_manager import SQLAlchemyDatabaseManager
        self._sqlalchemy_manager = SQLAlchemyDatabaseManager()
        self.db_path = db_path
    
    def init_database(self):
        """데이터베이스 초기화 - SQLAlchemy 매니저에 위임"""
        pass  # SQLAlchemy 매니저가 자동으로 처리
    
    def insert_community(self, community: Community) -> int:
        """커뮤니티 추가 - SQLAlchemy 매니저에 위임"""
        return self._sqlalchemy_manager.insert_community(community.name, community.description)
    
    def insert_article(self, article: Article) -> int:
        """게시글 추가 - SQLAlchemy 매니저에 위임"""
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
        """댓글 추가 - SQLAlchemy 매니저에 위임"""
        comment_data = {
            "platform_id": "legacy",  # 기본값 설정
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
        """후기 추가 - SQLAlchemy 매니저에 위임"""
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
    
    def get_community_by_name(self, name: str) -> Optional[Dict]:
        """이름으로 커뮤니티 조회 - SQLAlchemy 매니저에 위임"""
        return self._sqlalchemy_manager.get_community_by_name(name)
    
    def get_article_by_platform_id_and_community_article_id(self, platform_id: str, community_article_id: str) -> Optional[Dict]:
        """플랫폼 ID와 커뮤니티 게시글 ID로 게시글 조회 - SQLAlchemy 매니저에 위임"""
        return self._sqlalchemy_manager.get_article_by_platform_id_and_community_article_id(platform_id, community_article_id)
    
    def get_comment_by_article_id_and_comment_id(self, article_id: str, comment_id: str) -> Optional[Dict]:
        """게시글 ID와 댓글 ID로 댓글 조회"""
        # SQLAlchemy 매니저의 메서드를 호출하되, 레거시 방식에 맞게 조정
        return self._sqlalchemy_manager.get_comment_by_article_id_and_comment_id(article_id, comment_id)
    
    def get_statistics(self) -> Dict:
        """데이터베이스 통계 조회 - SQLAlchemy 매니저에 위임"""
        return self._sqlalchemy_manager.get_statistics()
    
    def get_review_statistics(self) -> Dict:
        """후기 통계 조회 - SQLAlchemy 매니저에 위임"""
        stats = self._sqlalchemy_manager.get_statistics()
        return {
            "platform_statistics": stats.get("platform_stats", {}),
            "category_statistics": {}  # 필요시 구현
        }
    
    def get_articles_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 게시글 수 조회 - SQLAlchemy 매니저에 위임"""
        # SQLAlchemy 매니저에서 해당 메서드 구현 필요
        return 0  # 임시 반환값
    
    def get_connection(self):
        """데이터베이스 연결 반환 - SQLAlchemy 세션 반환"""
        from database.config import get_db
        return get_db()

# 하위 호환성을 위한 별칭
DatabaseManager = LegacyDatabaseManager
