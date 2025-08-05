from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from api.models import (
    ArticleResponse, ReviewResponse, CommentResponse, PaginatedResponse,
    PlatformType, CategoryType, DateRangeRequest, PaginationRequest
)
from api.dependencies import get_database_manager
from database.models import DatabaseManager

router = APIRouter()

@router.get("/articles", response_model=PaginatedResponse)
async def get_articles(
    platform: Optional[PlatformType] = Query(None, description="플랫폼 필터"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 데이터 수"),
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    게시글 목록을 조회합니다.
    """
    try:
        offset = (page - 1) * limit
        
        # 필터 조건 구성
        filters = {}
        if platform:
            filters["platform_id"] = platform.value
        if category:
            filters["category_name"] = category
        
        # 게시글 조회
        articles = db.get_articles_by_filters(filters, limit=limit, offset=offset)
        total = db.get_articles_count_by_filters(filters)
        
        # 응답 데이터 변환
        article_responses = []
        for article in articles:
            article_responses.append(ArticleResponse(
                id=article.id,
                platform_id=article.platform_id,
                community_article_id=article.community_article_id,
                community_id=article.community_id,
                title=article.title,
                content=article.content,
                writer_nickname=article.writer_nickname,
                writer_id=article.writer_id,
                like_count=article.like_count,
                comment_count=article.comment_count,
                view_count=article.view_count,
                images=article.images,
                created_at=article.created_at,
                category_name=article.category_name
            ))
        
        total_pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=article_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"게시글 조회 실패: {str(e)}"
        )

@router.get("/reviews", response_model=PaginatedResponse)
async def get_reviews(
    platform: Optional[PlatformType] = Query(None, description="플랫폼 필터"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 데이터 수"),
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    후기 목록을 조회합니다.
    """
    try:
        offset = (page - 1) * limit
        
        # 필터 조건 구성
        filters = {}
        if platform:
            filters["platform_id"] = platform.value
        if category:
            filters["category_name"] = category
        
        # 후기 조회
        reviews = db.get_reviews_by_filters(filters, limit=limit, offset=offset)
        total = db.get_reviews_count_by_filters(filters)
        
        # 응답 데이터 변환
        review_responses = []
        for review in reviews:
            review_responses.append(ReviewResponse(
                id=review.id,
                platform_id=review.platform_id,
                platform_review_id=review.platform_review_id,
                community_id=review.community_id,
                title=review.title,
                content=review.content,
                writer_nickname=review.writer_nickname,
                writer_id=review.writer_id,
                rating=review.rating,
                price=review.price,
                images=review.images,
                hospital_name=review.hospital_name,
                doctor_name=review.doctor_name,
                created_at=review.created_at,
                category_name=review.category_name
            ))
        
        total_pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=review_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"후기 조회 실패: {str(e)}"
        )

@router.get("/comments", response_model=PaginatedResponse)
async def get_comments(
    article_id: Optional[int] = Query(None, description="게시글 ID 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 데이터 수"),
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    댓글 목록을 조회합니다.
    """
    try:
        offset = (page - 1) * limit
        
        # 필터 조건 구성
        filters = {}
        if article_id:
            filters["article_id"] = article_id
        
        # 댓글 조회
        comments = db.get_comments_by_filters(filters, limit=limit, offset=offset)
        total = db.get_comments_count_by_filters(filters)
        
        # 응답 데이터 변환
        comment_responses = []
        for comment in comments:
            comment_responses.append(CommentResponse(
                id=comment.id,
                article_id=comment.article_id,
                parent_comment_id=comment.parent_comment_id,
                writer_nickname=comment.writer_nickname,
                writer_id=comment.writer_id,
                content=comment.content,
                like_count=comment.like_count,
                created_at=comment.created_at
            ))
        
        total_pages = (total + limit - 1) // limit
        
        return PaginatedResponse(
            data=comment_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"댓글 조회 실패: {str(e)}"
        )

@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article_by_id(
    article_id: int,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    특정 게시글을 조회합니다.
    """
    try:
        article = db.get_article_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=404,
                detail=f"게시글을 찾을 수 없습니다: {article_id}"
            )
        
        return ArticleResponse(
            id=article.id,
            platform_id=article.platform_id,
            community_article_id=article.community_article_id,
            community_id=article.community_id,
            title=article.title,
            content=article.content,
            writer_nickname=article.writer_nickname,
            writer_id=article.writer_id,
            like_count=article.like_count,
            comment_count=article.comment_count,
            view_count=article.view_count,
            images=article.images,
            created_at=article.created_at,
            category_name=article.category_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"게시글 조회 실패: {str(e)}"
        )

@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review_by_id(
    review_id: int,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    특정 후기를 조회합니다.
    """
    try:
        review = db.get_review_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=404,
                detail=f"후기를 찾을 수 없습니다: {review_id}"
            )
        
        return ReviewResponse(
            id=review.id,
            platform_id=review.platform_id,
            platform_review_id=review.platform_review_id,
            community_id=review.community_id,
            title=review.title,
            content=review.content,
            writer_nickname=review.writer_nickname,
            writer_id=review.writer_id,
            rating=review.rating,
            price=review.price,
            images=review.images,
            hospital_name=review.hospital_name,
            doctor_name=review.doctor_name,
            created_at=review.created_at,
            category_name=review.category_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"후기 조회 실패: {str(e)}"
        )

@router.get("/articles/{article_id}/comments", response_model=List[CommentResponse])
async def get_comments_by_article_id(
    article_id: int,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    특정 게시글의 댓글 목록을 조회합니다.
    """
    try:
        comments = db.get_comments_by_article_id(article_id)
        
        comment_responses = []
        for comment in comments:
            comment_responses.append(CommentResponse(
                id=comment.id,
                article_id=comment.article_id,
                parent_comment_id=comment.parent_comment_id,
                writer_nickname=comment.writer_nickname,
                writer_id=comment.writer_id,
                content=comment.content,
                like_count=comment.like_count,
                created_at=comment.created_at
            ))
        
        return comment_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"댓글 조회 실패: {str(e)}"
        ) 