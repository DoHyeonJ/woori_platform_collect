#!/usr/bin/env python3
"""
댓글 연관관계 수정 스크립트

이 스크립트는 기존 댓글 데이터의 연관관계를 수정하여 
새로운 DB 구조와 호환되도록 합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.sqlalchemy_manager import SQLAlchemyDatabaseManager
from database.sqlalchemy_models import Comment, Article
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_comment_relations():
    """댓글의 연관관계를 수정합니다."""
    
    db_manager = SQLAlchemyDatabaseManager()
    session = db_manager.get_session()
    
    try:
        logger.info("댓글 연관관계 수정 작업을 시작합니다...")
        
        # article_id가 NULL이거나 잘못된 댓글들 찾기
        problematic_comments = session.query(Comment).filter(
            Comment.article_id.is_(None)
        ).all()
        
        logger.info(f"수정이 필요한 댓글 수: {len(problematic_comments)}")
        
        fixed_count = 0
        failed_count = 0
        
        for comment in problematic_comments:
            try:
                # platform_id와 community_article_id로 해당 게시글 찾기
                article = session.query(Article).filter(
                    and_(
                        Article.platform_id == comment.platform_id,
                        Article.community_article_id == comment.community_article_id
                    )
                ).first()
                
                if article:
                    # article_id 업데이트
                    comment.article_id = article.id
                    fixed_count += 1
                    logger.info(f"댓글 {comment.id} 연관관계 수정: article_id = {article.id}")
                else:
                    logger.warning(f"댓글 {comment.id}에 해당하는 게시글을 찾을 수 없습니다: "
                                 f"platform_id={comment.platform_id}, "
                                 f"community_article_id={comment.community_article_id}")
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"댓글 {comment.id} 수정 중 오류: {e}")
                failed_count += 1
        
        # 변경사항 커밋
        session.commit()
        
        logger.info(f"댓글 연관관계 수정 완료!")
        logger.info(f"  - 수정 성공: {fixed_count}개")
        logger.info(f"  - 수정 실패: {failed_count}개")
        
        # 통계 출력
        print_comment_statistics(session)
        
    except Exception as e:
        session.rollback()
        logger.error(f"댓글 연관관계 수정 중 오류 발생: {e}")
        raise
    finally:
        session.close()

def print_comment_statistics(session: Session):
    """댓글 통계를 출력합니다."""
    
    logger.info("\n=== 댓글 통계 ===")
    
    # 전체 댓글 수
    total_comments = session.query(Comment).count()
    logger.info(f"전체 댓글 수: {total_comments}")
    
    # 연관관계가 설정된 댓글 수
    linked_comments = session.query(Comment).filter(Comment.article_id.isnot(None)).count()
    logger.info(f"연관관계 설정된 댓글: {linked_comments}")
    
    # 연관관계가 없는 댓글 수
    orphaned_comments = session.query(Comment).filter(Comment.article_id.is_(None)).count()
    logger.info(f"연관관계 없는 댓글: {orphaned_comments}")
    
    # 플랫폼별 댓글 수
    platform_stats = session.query(Comment.platform_id, 
                                   session.func.count(Comment.id)).group_by(Comment.platform_id).all()
    
    logger.info("\n플랫폼별 댓글 수:")
    for platform_id, count in platform_stats:
        logger.info(f"  {platform_id}: {count}개")

def validate_comment_integrity():
    """댓글 데이터 무결성을 검증합니다."""
    
    db_manager = SQLAlchemyDatabaseManager()
    session = db_manager.get_session()
    
    try:
        logger.info("\n=== 댓글 데이터 무결성 검증 ===")
        
        # 존재하지 않는 article_id를 참조하는 댓글 찾기
        invalid_comments = session.query(Comment).filter(
            ~Comment.article_id.in_(session.query(Article.id))
        ).all()
        
        if invalid_comments:
            logger.warning(f"유효하지 않은 article_id를 참조하는 댓글: {len(invalid_comments)}개")
            for comment in invalid_comments[:5]:  # 처음 5개만 출력
                logger.warning(f"  댓글 ID {comment.id}: article_id={comment.article_id}")
        else:
            logger.info("모든 댓글의 연관관계가 유효합니다.")
        
        # 중복 댓글 체크
        duplicates = session.query(Comment.platform_id, Comment.community_comment_id,
                                 session.func.count(Comment.id).label('count')).group_by(
                                     Comment.platform_id, Comment.community_comment_id
                                 ).having(session.func.count(Comment.id) > 1).all()
        
        if duplicates:
            logger.warning(f"중복된 댓글: {len(duplicates)}개")
            for platform_id, comment_id, count in duplicates[:5]:
                logger.warning(f"  {platform_id}/{comment_id}: {count}개")
        else:
            logger.info("중복된 댓글이 없습니다.")
            
    finally:
        session.close()

if __name__ == "__main__":
    print("🔧 댓글 연관관계 수정 스크립트")
    print("=" * 50)
    
    try:
        # 1. 댓글 연관관계 수정
        fix_comment_relations()
        
        # 2. 데이터 무결성 검증
        validate_comment_integrity()
        
        print("\n✅ 댓글 연관관계 수정이 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 작업 중 오류 발생: {e}")
        sys.exit(1)
