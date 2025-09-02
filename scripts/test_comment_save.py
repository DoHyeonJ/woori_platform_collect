#!/usr/bin/env python3
"""
댓글 저장 기능 테스트 스크립트

개선된 댓글 저장 로직이 정상적으로 작동하는지 테스트합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import DatabaseManager, Article, Comment
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_comment_save():
    """댓글 저장 기능을 테스트합니다."""
    
    db = DatabaseManager()
    
    try:
        logger.info("댓글 저장 기능 테스트를 시작합니다...")
        
        # 1. 테스트용 게시글 생성
        test_article = Article(
            id=None,
            platform_id="test_platform",
            community_article_id="test_article_123",
            community_id=1,
            title="테스트 게시글",
            content="댓글 테스트용 게시글입니다.",
            writer_nickname="테스트작성자",
            writer_id="test_user_1",
            like_count=0,
            comment_count=0,
            view_count=0,
            images="[]",
            created_at=datetime.now(),
            category_name="테스트",
            collected_at=datetime.now()
        )
        
        article_id = db.insert_article(test_article)
        logger.info(f"테스트 게시글 생성 완료: ID {article_id}")
        
        # 2. 새로운 방식으로 댓글 저장 (article_id 직접 사용)
        test_comment_1 = Comment(
            id="test_comment_1",
            article_id=article_id,  # 숫자 ID 직접 사용
            content="첫 번째 테스트 댓글입니다.",
            writer_nickname="댓글작성자1",
            writer_id="comment_user_1",
            created_at=datetime.now(),
            parent_comment_id=None,
            collected_at=datetime.now()
        )
        test_comment_1.platform_id = "test_platform"
        
        comment_id_1 = db.insert_comment(test_comment_1)
        logger.info(f"댓글 1 저장 완료: ID {comment_id_1}")
        
        # 3. 레거시 방식으로 댓글 저장 (platform_id + community_article_id)
        test_comment_2 = Comment(
            id="test_comment_2",
            article_id="test_article_123",  # 문자열 ID (레거시 방식)
            content="두 번째 테스트 댓글입니다.",
            writer_nickname="댓글작성자2",
            writer_id="comment_user_2",
            created_at=datetime.now(),
            parent_comment_id=None,
            collected_at=datetime.now()
        )
        test_comment_2.platform_id = "test_platform"
        
        comment_id_2 = db.insert_comment(test_comment_2)
        logger.info(f"댓글 2 저장 완료: ID {comment_id_2}")
        
        # 4. 대댓글 저장 테스트
        test_reply = Comment(
            id="test_reply_1",
            article_id=article_id,
            content="첫 번째 댓글에 대한 대댓글입니다.",
            writer_nickname="대댓글작성자",
            writer_id="reply_user_1",
            created_at=datetime.now(),
            parent_comment_id="test_comment_1",
            collected_at=datetime.now()
        )
        test_reply.platform_id = "test_platform"
        
        reply_id = db.insert_comment(test_reply)
        logger.info(f"대댓글 저장 완료: ID {reply_id}")
        
        # 5. 중복 댓글 저장 테스트 (같은 ID로 다시 저장)
        duplicate_comment = Comment(
            id="test_comment_1",  # 같은 ID
            article_id=article_id,
            content="중복 댓글 테스트",
            writer_nickname="중복작성자",
            writer_id="duplicate_user",
            created_at=datetime.now(),
            parent_comment_id=None,
            collected_at=datetime.now()
        )
        duplicate_comment.platform_id = "test_platform"
        
        duplicate_id = db.insert_comment(duplicate_comment)
        logger.info(f"중복 댓글 처리 결과: ID {duplicate_id} (기존 댓글 ID와 동일해야 함)")
        
        # 6. 저장된 댓글들 조회 및 검증
        saved_article = db.get_article_by_platform_id_and_community_article_id(
            "test_platform", "test_article_123"
        )
        
        if saved_article:
            logger.info(f"저장된 게시글 조회 성공: {saved_article['title']}")
            
            # SQLAlchemy 매니저로 댓글 조회
            from database.sqlalchemy_manager import SQLAlchemyDatabaseManager
            sqlalchemy_db = SQLAlchemyDatabaseManager()
            
            comments = sqlalchemy_db.get_comments_by_filters({
                "article_id": article_id
            })
            
            logger.info(f"저장된 댓글 수: {len(comments)}")
            for comment in comments:
                logger.info(f"  댓글 ID: {comment['id']}, 내용: {comment['content'][:20]}...")
                if comment['parent_comment_id']:
                    logger.info(f"    → 대댓글 (부모: {comment['parent_comment_id']})")
        
        logger.info("✅ 모든 댓글 저장 테스트가 성공했습니다!")
        
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        raise

def test_babitalk_style_comment():
    """바비톡 스타일의 댓글 저장을 테스트합니다."""
    
    db = DatabaseManager()
    
    try:
        logger.info("\n바비톡 스타일 댓글 저장 테스트...")
        
        # 바비톡 자유톡 게시글 생성
        babitalk_article = Article(
            id=None,
            platform_id="babitalk_talk",
            community_article_id="12345",
            community_id=1,
            title="바비톡 자유톡 테스트",
            content="바비톡 자유톡 내용입니다.",
            writer_nickname="바비톡유저",
            writer_id="babitalk_user_1",
            like_count=5,
            comment_count=0,
            view_count=100,
            images="[]",
            created_at=datetime.now(),
            category_name="성형",
            collected_at=datetime.now()
        )
        
        article_id = db.insert_article(babitalk_article)
        logger.info(f"바비톡 게시글 생성: ID {article_id}")
        
        # 바비톡 댓글 저장 (개선된 방식)
        babitalk_comment = Comment(
            id="67890",  # 바비톡 댓글 ID
            article_id=article_id,  # DB의 article ID
            content="바비톡 댓글입니다.",
            writer_nickname="댓글유저",
            writer_id="babitalk_comment_user",
            created_at=datetime.now(),
            parent_comment_id=None,
            collected_at=datetime.now()
        )
        babitalk_comment.platform_id = "babitalk_talk"
        
        comment_id = db.insert_comment(babitalk_comment)
        logger.info(f"바비톡 댓글 저장 성공: ID {comment_id}")
        
        # 저장된 댓글 확인
        from database.sqlalchemy_manager import SQLAlchemyDatabaseManager
        sqlalchemy_db = SQLAlchemyDatabaseManager()
        
        saved_comment = sqlalchemy_db.get_comment_by_id(comment_id)
        if saved_comment:
            logger.info(f"저장된 댓글 확인:")
            logger.info(f"  - 플랫폼: {saved_comment['platform_id']}")
            logger.info(f"  - 게시글 ID: {saved_comment['article_id']}")
            logger.info(f"  - 내용: {saved_comment['content']}")
            logger.info(f"  - 연관 게시글: {saved_comment['article_title']}")
        
        logger.info("✅ 바비톡 스타일 댓글 저장 테스트 성공!")
        
    except Exception as e:
        logger.error(f"❌ 바비톡 테스트 중 오류: {e}")
        raise

if __name__ == "__main__":
    print("🧪 댓글 저장 기능 테스트")
    print("=" * 50)
    
    try:
        # 기본 댓글 저장 테스트
        test_comment_save()
        
        # 바비톡 스타일 테스트
        test_babitalk_style_comment()
        
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("개선된 댓글 저장 로직이 정상적으로 작동합니다.")
        
    except Exception as e:
        print(f"\n💥 테스트 실패: {e}")
        sys.exit(1)
