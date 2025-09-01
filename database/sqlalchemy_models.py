from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base
from datetime import datetime
from typing import Optional

class Community(Base):
    """커뮤니티 테이블"""
    __tablename__ = "communities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    description = Column(Text)
    
    # 관계 설정
    articles = relationship("Article", back_populates="community")
    reviews = relationship("Review", back_populates="community")
    
    def __repr__(self):
        return f"<Community(id={self.id}, name='{self.name}')>"

class Client(Base):
    """클라이언트(병원) 테이블"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    description = Column(Text)
    
    # 관계 설정
    excluded_articles = relationship("ExcludedArticle", back_populates="client")
    
    def __repr__(self):
        return f"<Client(id={self.id}, hospital_name='{self.hospital_name}')>"

class Article(Base):
    """게시글 테이블"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(String(50), nullable=False)
    community_article_id = Column(String(255), nullable=False)
    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)
    title = Column(Text)
    content = Column(Text, nullable=False)
    images = Column(Text)  # JSON 문자열
    writer_nickname = Column(String(255), nullable=False)
    writer_id = Column(String(255), nullable=False)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    category_name = Column(String(255))
    collected_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    community = relationship("Community", back_populates="articles")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    excluded_articles = relationship("ExcludedArticle", back_populates="article")
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_articles_platform_community', 'platform_id', 'community_article_id', unique=True),
        Index('idx_articles_community_id', 'community_id'),
        Index('idx_articles_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Article(id={self.id}, platform_id='{self.platform_id}', title='{self.title[:20]}...')>"

class Comment(Base):
    """댓글 테이블"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(String(50), nullable=False)
    community_article_id = Column(String(255), nullable=False)
    community_comment_id = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    writer_nickname = Column(String(255), nullable=False)
    writer_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    parent_comment_id = Column(String(255))  # 대댓글인 경우 부모 댓글 ID
    collected_at = Column(DateTime, default=func.now())
    
    # 외래키 설정 (복합 외래키)
    article_id = Column(Integer, ForeignKey("articles.id"))
    
    # 관계 설정
    article = relationship("Article", back_populates="comments")
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_comments_platform_article', 'platform_id', 'community_article_id'),
        Index('idx_comments_parent_id', 'parent_comment_id'),
    )
    
    def __repr__(self):
        return f"<Comment(id={self.id}, platform_id='{self.platform_id}', content='{self.content[:20]}...')>"

class ExcludedArticle(Base):
    """제외된 게시글 테이블"""
    __tablename__ = "excluded_articles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    client = relationship("Client", back_populates="excluded_articles")
    article = relationship("Article", back_populates="excluded_articles")
    
    def __repr__(self):
        return f"<ExcludedArticle(id={self.id}, client_id={self.client_id}, article_id={self.article_id})>"

class Review(Base):
    """후기 테이블 (통합)"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(String(50), nullable=False)  # "gangnamunni" 또는 "babitalk"
    platform_review_id = Column(String(255), nullable=False)  # 각 플랫폼의 고유 후기 ID
    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)
    title = Column(Text)  # 후기 제목 (바비톡의 경우 카테고리 정보)
    content = Column(Text, nullable=False)  # 후기 내용
    images = Column(Text)  # JSON 문자열
    writer_nickname = Column(String(255), nullable=False)
    writer_id = Column(String(255), nullable=False)
    like_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)  # 평점 (바비톡용)
    price = Column(Integer, default=0)  # 가격 (바비톡용)
    categories = Column(Text)  # JSON 문자열 (바비톡용)
    sub_categories = Column(Text)  # JSON 문자열 (바비톡용)
    surgery_date = Column(String(50))  # 수술 날짜 (바비톡용)
    hospital_name = Column(String(255))  # 병원명
    doctor_name = Column(String(255))  # 담당의명
    is_blind = Column(Boolean, default=False)  # 블라인드 여부 (바비톡용)
    is_image_blur = Column(Boolean, default=False)  # 이미지 블러 여부 (바비톡용)
    is_certificated_review = Column(Boolean, default=False)  # 인증 후기 여부 (바비톡용)
    created_at = Column(DateTime, default=func.now())
    collected_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    community = relationship("Community", back_populates="reviews")
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_reviews_platform_review', 'platform_id', 'platform_review_id', unique=True),
        Index('idx_reviews_platform_id', 'platform_id'),
        Index('idx_reviews_community_id', 'community_id'),
        Index('idx_reviews_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.id}, platform_id='{self.platform_id}', hospital_name='{self.hospital_name}')>"
