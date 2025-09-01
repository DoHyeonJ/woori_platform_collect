#!/usr/bin/env python3
"""
SQLite에서 MySQL로 데이터 마이그레이션 스크립트

사용법:
1. .env 파일에서 DB_TYPE=sqlite로 설정하여 기존 SQLite 데이터 읽기
2. MySQL 데이터베이스와 사용자를 미리 생성
3. 이 스크립트 실행하여 데이터 마이그레이션
4. .env 파일에서 DB_TYPE=mysql로 변경
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

from database.models import DatabaseManager  # 기존 SQLite 매니저
from database.sqlalchemy_manager import SQLAlchemyDatabaseManager  # 새 SQLAlchemy 매니저
from utils.logger import get_logger

logger = get_logger("MIGRATION")

class DataMigrator:
    """SQLite에서 MySQL로 데이터 마이그레이션을 수행하는 클래스"""
    
    def __init__(self):
        # SQLite 매니저 (소스)
        self.sqlite_manager = DatabaseManager()
        
        # MySQL 매니저 (대상) - 환경 변수를 MySQL로 설정 후 사용
        # 임시로 환경 변수 변경
        original_db_type = os.getenv("DB_TYPE", "sqlite")
        os.environ["DB_TYPE"] = "mysql"
        self.mysql_manager = SQLAlchemyDatabaseManager()
        
        # 다시 원래대로 복원 (마이그레이션 중에는 SQLite를 주로 사용)
        os.environ["DB_TYPE"] = original_db_type
    
    def check_mysql_connection(self):
        """MySQL 연결 확인"""
        try:
            self.mysql_manager.init_database()
            logger.info("✅ MySQL 연결 및 테이블 생성 성공")
            return True
        except Exception as e:
            logger.error(f"❌ MySQL 연결 실패: {e}")
            return False
    
    def migrate_communities(self):
        """커뮤니티 데이터 마이그레이션"""
        logger.info("🔄 커뮤니티 데이터 마이그레이션 시작...")
        
        try:
            # SQLite에서 커뮤니티 데이터 조회
            with self.sqlite_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM communities")
                communities = cursor.fetchall()
            
            migrated_count = 0
            for community in communities:
                try:
                    community_id = self.mysql_manager.insert_community(
                        name=community[1],  # name
                        description=community[3] or ""  # description
                    )
                    migrated_count += 1
                    logger.debug(f"커뮤니티 마이그레이션: {community[1]} -> ID: {community_id}")
                except Exception as e:
                    logger.warning(f"커뮤니티 마이그레이션 실패: {community[1]} - {e}")
            
            logger.info(f"✅ 커뮤니티 마이그레이션 완료: {migrated_count}/{len(communities)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 커뮤니티 마이그레이션 중 오류: {e}")
            return False
    
    def migrate_clients(self):
        """클라이언트 데이터 마이그레이션"""
        logger.info("🔄 클라이언트 데이터 마이그레이션 시작...")
        
        try:
            # SQLite에서 클라이언트 데이터 조회
            with self.sqlite_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clients")
                clients = cursor.fetchall()
            
            migrated_count = 0
            for client in clients:
                try:
                    client_id = self.mysql_manager.insert_client(
                        hospital_name=client[1],  # hospital_name
                        description=client[3] or ""  # description
                    )
                    migrated_count += 1
                    logger.debug(f"클라이언트 마이그레이션: {client[1]} -> ID: {client_id}")
                except Exception as e:
                    logger.warning(f"클라이언트 마이그레이션 실패: {client[1]} - {e}")
            
            logger.info(f"✅ 클라이언트 마이그레이션 완료: {migrated_count}/{len(clients)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 클라이언트 마이그레이션 중 오류: {e}")
            return False
    
    def migrate_articles(self):
        """게시글 데이터 마이그레이션"""
        logger.info("🔄 게시글 데이터 마이그레이션 시작...")
        
        try:
            # SQLite에서 게시글 데이터 조회
            with self.sqlite_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM articles")
                articles = cursor.fetchall()
            
            migrated_count = 0
            for article in articles:
                try:
                    article_data = {
                        'platform_id': article[1],
                        'community_article_id': article[2],
                        'community_id': article[3],
                        'title': article[4],
                        'content': article[5],
                        'images': article[6],
                        'writer_nickname': article[7],
                        'writer_id': article[8],
                        'like_count': article[9] or 0,
                        'comment_count': article[10] or 0,
                        'view_count': article[11] or 0,
                        'created_at': datetime.fromisoformat(article[12]) if article[12] else datetime.now(),
                        'category_name': article[13],
                        'collected_at': datetime.fromisoformat(article[14]) if article[14] else datetime.now()
                    }
                    
                    article_id = self.mysql_manager.insert_article(article_data)
                    migrated_count += 1
                    
                    if migrated_count % 100 == 0:
                        logger.info(f"진행 상황: {migrated_count}/{len(articles)} 게시글 마이그레이션 완료")
                    
                except Exception as e:
                    logger.warning(f"게시글 마이그레이션 실패: {article[1]}/{article[2]} - {e}")
            
            logger.info(f"✅ 게시글 마이그레이션 완료: {migrated_count}/{len(articles)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 게시글 마이그레이션 중 오류: {e}")
            return False
    
    def migrate_comments(self):
        """댓글 데이터 마이그레이션"""
        logger.info("🔄 댓글 데이터 마이그레이션 시작...")
        
        try:
            # SQLite에서 댓글 데이터 조회
            with self.sqlite_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM comments")
                comments = cursor.fetchall()
            
            migrated_count = 0
            for comment in comments:
                try:
                    comment_data = {
                        'platform_id': comment[1],
                        'community_article_id': comment[2],
                        'community_comment_id': comment[3],
                        'content': comment[4],
                        'writer_nickname': comment[5],
                        'writer_id': comment[6],
                        'created_at': datetime.fromisoformat(comment[7]) if comment[7] else datetime.now(),
                        'parent_comment_id': comment[8],
                        'collected_at': datetime.fromisoformat(comment[9]) if comment[9] else datetime.now()
                    }
                    
                    comment_id = self.mysql_manager.insert_comment(comment_data)
                    migrated_count += 1
                    
                    if migrated_count % 100 == 0:
                        logger.info(f"진행 상황: {migrated_count}/{len(comments)} 댓글 마이그레이션 완료")
                    
                except Exception as e:
                    logger.warning(f"댓글 마이그레이션 실패: {comment[3]} - {e}")
            
            logger.info(f"✅ 댓글 마이그레이션 완료: {migrated_count}/{len(comments)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 댓글 마이그레이션 중 오류: {e}")
            return False
    
    def migrate_reviews(self):
        """후기 데이터 마이그레이션"""
        logger.info("🔄 후기 데이터 마이그레이션 시작...")
        
        try:
            # SQLite에서 후기 데이터 조회
            with self.sqlite_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reviews")
                reviews = cursor.fetchall()
            
            migrated_count = 0
            for review in reviews:
                try:
                    review_data = {
                        'platform_id': review[1],
                        'platform_review_id': review[2],
                        'community_id': review[3],
                        'title': review[4],
                        'content': review[5],
                        'images': review[6],
                        'writer_nickname': review[7],
                        'writer_id': review[8],
                        'like_count': review[9] or 0,
                        'rating': review[10] or 0,
                        'price': review[11] or 0,
                        'categories': review[12],
                        'sub_categories': review[13],
                        'surgery_date': review[14],
                        'hospital_name': review[15],
                        'doctor_name': review[16],
                        'is_blind': bool(review[17]) if review[17] is not None else False,
                        'is_image_blur': bool(review[18]) if review[18] is not None else False,
                        'is_certificated_review': bool(review[19]) if review[19] is not None else False,
                        'created_at': datetime.fromisoformat(review[20]) if review[20] else datetime.now(),
                        'collected_at': datetime.fromisoformat(review[21]) if review[21] else datetime.now()
                    }
                    
                    review_id = self.mysql_manager.insert_review(review_data)
                    migrated_count += 1
                    
                    if migrated_count % 100 == 0:
                        logger.info(f"진행 상황: {migrated_count}/{len(reviews)} 후기 마이그레이션 완료")
                    
                except Exception as e:
                    logger.warning(f"후기 마이그레이션 실패: {review[1]}/{review[2]} - {e}")
            
            logger.info(f"✅ 후기 마이그레이션 완료: {migrated_count}/{len(reviews)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 후기 마이그레이션 중 오류: {e}")
            return False
    
    def run_migration(self):
        """전체 마이그레이션 실행"""
        logger.info("🚀 SQLite → MySQL 데이터 마이그레이션 시작")
        logger.info("=" * 60)
        
        # MySQL 연결 확인
        if not self.check_mysql_connection():
            logger.error("❌ MySQL 연결에 실패했습니다. 설정을 확인해주세요.")
            return False
        
        # 순서대로 마이그레이션 실행
        migration_steps = [
            ("커뮤니티", self.migrate_communities),
            ("클라이언트", self.migrate_clients),
            ("게시글", self.migrate_articles),
            ("댓글", self.migrate_comments),
            ("후기", self.migrate_reviews)
        ]
        
        for step_name, step_function in migration_steps:
            logger.info(f"\n📋 {step_name} 마이그레이션 시작...")
            if not step_function():
                logger.error(f"❌ {step_name} 마이그레이션에 실패했습니다.")
                return False
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 모든 데이터 마이그레이션이 성공적으로 완료되었습니다!")
        logger.info("💡 이제 .env 파일에서 DB_TYPE=mysql로 변경하여 MySQL을 사용하세요.")
        
        return True

def main():
    """메인 함수"""
    logger.info("SQLite → MySQL 데이터 마이그레이션 도구")
    logger.info("=" * 60)
    
    # 환경 변수 확인
    if not os.getenv("MYSQL_HOST"):
        logger.error("❌ MySQL 환경 변수가 설정되지 않았습니다.")
        logger.info("💡 .env 파일에 MySQL 연결 정보를 설정해주세요:")
        logger.info("   MYSQL_HOST=localhost")
        logger.info("   MYSQL_PORT=3306")
        logger.info("   MYSQL_USER=your_username")
        logger.info("   MYSQL_PASSWORD=your_password")
        logger.info("   MYSQL_DATABASE=woori_platform_collect")
        return
    
    # 사용자 확인
    response = input("\n⚠️  기존 MySQL 데이터가 있다면 덮어씌워질 수 있습니다. 계속하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        logger.info("❌ 마이그레이션이 취소되었습니다.")
        return
    
    # 마이그레이션 실행
    migrator = DataMigrator()
    success = migrator.run_migration()
    
    if success:
        logger.info("\n🎯 다음 단계:")
        logger.info("1. .env 파일에서 DB_TYPE=mysql로 변경")
        logger.info("2. API 서버 재시작")
        logger.info("3. 애플리케이션이 MySQL을 사용하는지 확인")
    else:
        logger.error("\n❌ 마이그레이션 중 오류가 발생했습니다. 로그를 확인해주세요.")

if __name__ == "__main__":
    main()
