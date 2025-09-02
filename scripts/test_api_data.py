#!/usr/bin/env python3
"""
API 데이터 조회 테스트 스크립트

데이터베이스에 실제 데이터가 있는지 확인하고 API가 정상적으로 작동하는지 테스트합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import DatabaseManager
from database.sqlalchemy_manager import SQLAlchemyDatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """데이터베이스 연결 및 기본 데이터 확인"""
    
    print("🔍 데이터베이스 연결 테스트")
    print("=" * 50)
    
    try:
        # SQLAlchemy 매니저 직접 테스트
        sqlalchemy_db = SQLAlchemyDatabaseManager()
        
        # 전체 게시글 수 확인
        total_articles = sqlalchemy_db.get_articles_count_by_filters({})
        print(f"📊 전체 게시글 수: {total_articles}")
        
        if total_articles > 0:
            # 최근 게시글 5개 조회
            recent_articles = sqlalchemy_db.get_articles_by_filters({}, limit=5)
            print(f"\n📝 최근 게시글 {len(recent_articles)}개:")
            for article in recent_articles:
                print(f"  - ID: {article['id']}, 플랫폼: {article['platform_id']}, 제목: {article['title'][:30]}...")
            
            # 바비톡 게시글 확인
            babitalk_articles = sqlalchemy_db.get_articles_by_filters({"platform_id": "babitalk_talk"}, limit=3)
            print(f"\n🎯 바비톡 게시글 {len(babitalk_articles)}개:")
            for article in babitalk_articles:
                print(f"  - ID: {article['id']}, 제목: {article['title'][:30]}...")
        else:
            print("❌ 게시글 데이터가 없습니다.")
        
        # 전체 후기 수 확인
        total_reviews = sqlalchemy_db.get_reviews_count_by_filters({})
        print(f"\n📊 전체 후기 수: {total_reviews}")
        
        # 전체 댓글 수 확인
        total_comments = sqlalchemy_db.get_comments_count_by_filters({})
        print(f"📊 전체 댓글 수: {total_comments}")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")

def test_legacy_database_manager():
    """레거시 데이터베이스 매니저 테스트"""
    
    print("\n🔍 레거시 데이터베이스 매니저 테스트")
    print("=" * 50)
    
    try:
        db = DatabaseManager()
        
        # 게시글 조회 테스트
        articles = db.get_articles_by_filters({}, limit=3)
        print(f"📝 레거시 매니저로 조회한 게시글 수: {len(articles)}")
        
        if articles:
            for article in articles:
                print(f"  - ID: {article['id']}, 플랫폼: {article['platform_id']}, 제목: {article['title'][:30]}...")
        
        # 게시글 수 확인
        total = db.get_articles_count_by_filters({})
        print(f"📊 레거시 매니저로 조회한 전체 게시글 수: {total}")
        
        # 바비톡 필터 테스트
        babitalk_articles = db.get_articles_by_filters({"platform_id": "babitalk_talk"}, limit=3)
        print(f"🎯 바비톡 필터로 조회한 게시글 수: {len(babitalk_articles)}")
        
        # 실제 플랫폼 ID 확인
        if articles:
            print(f"\n🔍 실제 플랫폼 ID들:")
            platform_ids = set()
            for article in articles:
                platform_ids.add(article['platform_id'])
            for platform_id in platform_ids:
                print(f"  - {platform_id}")
        
    except Exception as e:
        print(f"❌ 레거시 매니저 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")

def test_platform_filtering():
    """플랫폼별 필터링 테스트"""
    
    print("\n🔍 플랫폼별 필터링 테스트")
    print("=" * 50)
    
    try:
        db = DatabaseManager()
        
        # 각 플랫폼별 데이터 확인
        platforms = ["babitalk_talk", "babitalk", "babitalk_event_ask", "gangnamunni"]
        
        for platform in platforms:
            count = db.get_articles_count_by_filters({"platform_id": platform})
            print(f"📊 {platform}: {count}개")
            
            if count > 0:
                articles = db.get_articles_by_filters({"platform_id": platform}, limit=2)
                for article in articles:
                    print(f"    - ID: {article['id']}, 제목: {article['title'][:20]}...")
        
    except Exception as e:
        print(f"❌ 플랫폼 필터링 테스트 실패: {e}")

if __name__ == "__main__":
    print("🧪 API 데이터 조회 테스트")
    print("=" * 50)
    
    try:
        # 1. 데이터베이스 연결 테스트
        test_database_connection()
        
        # 2. 레거시 매니저 테스트
        test_legacy_database_manager()
        
        # 3. 플랫폼별 필터링 테스트
        test_platform_filtering()
        
        print("\n✅ 모든 테스트가 완료되었습니다!")
        
    except Exception as e:
        print(f"\n💥 테스트 중 오류 발생: {e}")
        sys.exit(1)
