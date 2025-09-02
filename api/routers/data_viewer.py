from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from api.models import (
    Article, Review, Comment, PaginatedResponse, PlatformType
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
            article_responses.append(Article(
                id=article['id'],
                platform_id=article['platform_id'],
                community_article_id=article['community_article_id'],
                community_id=article['community_id'],
                title=article['title'],
                content=article['content'],
                writer_nickname=article['writer_nickname'],
                writer_id=article['writer_id'],
                like_count=article['like_count'],
                comment_count=article['comment_count'],
                view_count=article['view_count'],
                images=article['images'],
                created_at=article['created_at'],
                category_name=article['category_name'],
                collected_at=article['collected_at']
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
            review_responses.append(Review(
                id=review['id'],
                platform_id=review['platform_id'],
                platform_review_id=review['platform_review_id'],
                community_id=review['community_id'],
                title=review['title'],
                content=review['content'],
                writer_nickname=review['writer_nickname'],
                writer_id=review['writer_id'],
                like_count=review['like_count'],
                rating=review['rating'],
                price=review['price'],
                images=review['images'],
                categories=review['categories'],
                sub_categories=review['sub_categories'],
                surgery_date=review['surgery_date'],
                hospital_name=review['hospital_name'],
                doctor_name=review['doctor_name'],
                is_blind=review['is_blind'],
                is_image_blur=review['is_image_blur'],
                is_certificated_review=review['is_certificated_review'],
                created_at=review['created_at'],
                collected_at=review['collected_at']
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
    platform: Optional[PlatformType] = Query(None, description="플랫폼 필터"),
    article_id: Optional[str] = Query(None, description="게시글 ID 필터"),
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
        if platform:
            filters["platform_id"] = platform.value
        if article_id:
            filters["community_article_id"] = article_id
        
        # 댓글 조회
        comments = db.get_comments_by_filters(filters, limit=limit, offset=offset)
        total = db.get_comments_count_by_filters(filters)
        
        # 응답 데이터 변환
        comment_responses = []
        for comment in comments:
            comment_responses.append(Comment(
                id=comment['id'],
                platform_id=comment['platform_id'],
                community_article_id=comment['community_article_id'],
                community_id=comment.get('community_id', 1),  # 기본값 설정
                comment_id=comment['community_comment_id'],  # 필드명 수정
                parent_comment_id=comment['parent_comment_id'],
                content=comment['content'],
                writer_nickname=comment['writer_nickname'],
                writer_id=comment['writer_id'],
                like_count=comment.get('like_count', 0),  # 기본값 설정
                created_at=comment['created_at'],
                collected_at=comment['collected_at']
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

@router.get("/articles/{article_id}", response_model=Article)
async def get_article(
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
                detail="게시글을 찾을 수 없습니다."
            )
        
        return Article(
            id=article['id'],
            platform_id=article['platform_id'],
            community_article_id=article['community_article_id'],
            community_id=article['community_id'],
            title=article['title'],
            content=article['content'],
            writer_nickname=article['writer_nickname'],
            writer_id=article['writer_id'],
            like_count=article['like_count'],
            comment_count=article['comment_count'],
            view_count=article['view_count'],
            images=article['images'],
            created_at=article['created_at'],
            category_name=article['category_name'],
            collected_at=article['collected_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"게시글 조회 실패: {str(e)}"
        )

@router.get("/reviews/{review_id}", response_model=Review)
async def get_review(
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
                detail="후기를 찾을 수 없습니다."
            )
        
        return Review(
            id=review['id'],
            platform_id=review['platform_id'],
            platform_review_id=review['platform_review_id'],
            community_id=review['community_id'],
            title=review['title'],
            content=review['content'],
            writer_nickname=review['writer_nickname'],
            writer_id=review['writer_id'],
            like_count=review['like_count'],
            rating=review['rating'],
            price=review['price'],
            images=review['images'],
            categories=review['categories'],
            sub_categories=review['sub_categories'],
            surgery_date=review['surgery_date'],
            hospital_name=review['hospital_name'],
            doctor_name=review['doctor_name'],
            is_blind=review['is_blind'],
            is_image_blur=review['is_image_blur'],
            is_certificated_review=review['is_certificated_review'],
            created_at=review['created_at'],
            collected_at=review['collected_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"후기 조회 실패: {str(e)}"
        )

@router.get("/comments/{comment_id}", response_model=Comment)
async def get_comment(
    comment_id: int,
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    특정 댓글을 조회합니다.
    """
    try:
        comment = db.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=404,
                detail="댓글을 찾을 수 없습니다."
            )
        
        return Comment(
            id=comment['id'],
            platform_id=comment['platform_id'],
            community_article_id=comment['community_article_id'],
            community_id=comment.get('community_id', 1),  # 기본값 설정
            comment_id=comment['community_comment_id'],  # 필드명 수정
            parent_comment_id=comment['parent_comment_id'],
            content=comment['content'],
            writer_nickname=comment['writer_nickname'],
            writer_id=comment['writer_id'],
            like_count=comment.get('like_count', 0),  # 기본값 설정
            created_at=comment['created_at'],
            collected_at=comment['collected_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"댓글 조회 실패: {str(e)}"
        )

@router.get("/statistics/summary")
async def get_statistics_summary(
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    데이터 수집 통계 요약을 조회합니다.
    """
    try:
        # 전체 통계
        total_articles = db.get_articles_count_by_filters({})
        total_reviews = db.get_reviews_count_by_filters({})
        total_comments = db.get_comments_count_by_filters({})
        
        # 플랫폼별 통계
        gangnamunni_articles = db.get_articles_count_by_filters({"platform_id": "gangnamunni"})
        babitalk_articles = db.get_articles_count_by_filters({"platform_id": "babitalk"})
        gangnamunni_reviews = db.get_reviews_count_by_filters({"platform_id": "gangnamunni"})
        babitalk_reviews = db.get_reviews_count_by_filters({"platform_id": "babitalk"})
        
        return {
            "total": {
                "articles": total_articles,
                "reviews": total_reviews,
                "comments": total_comments
            },
            "by_platform": {
                "gangnamunni": {
                    "articles": gangnamunni_articles,
                    "reviews": gangnamunni_reviews
                },
                "babitalk": {
                    "articles": babitalk_articles,
                    "reviews": babitalk_reviews
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 실패: {str(e)}"
        ) 