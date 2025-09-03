#!/usr/bin/env python3
"""
localhost에서 db.hellobdd2.gabia.io로 데이터 마이그레이션 스크립트

사용법:
1. 코드에서 소스 DB 설정 (localhost) 하드코딩
2. 코드에서 대상 DB 설정 (db.hellobdd2.gabia.io) 하드코딩
3. 이 스크립트 실행하여 데이터 마이그레이션
4. articles, comments, reviews 테이블의 데이터를 그대로 마이그레이션
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger("MIGRATION")

class DatabaseMigrator:
    """데이터베이스 간 데이터 마이그레이션을 수행하는 클래스"""
    
    def __init__(self):
        # 소스 DB 설정 (localhost)
        self.source_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '1234',  # 실제 비밀번호로 변경
            'database': 'woori_collect',
            'charset': 'utf8mb4'
        }
        
        # 대상 DB 설정 (db.hellobdd2.gabia.io)
        self.target_config = {
            'host': 'db.hellobdd2.gabia.io',
            'port': 3306,
            'user': 'hellobdd2',
            'password': 'ahdtlfcjstk0805!',  # 실제 비밀번호로 변경
            'database': 'dbhellobdd2',
            'charset': 'utf8mb4'
        }
        
        # SQLAlchemy 엔진 생성
        self.source_engine = self._create_engine(self.source_config)
        self.target_engine = self._create_engine(self.target_config)
        
        # 세션 팩토리 생성
        self.SourceSession = sessionmaker(bind=self.source_engine)
        self.TargetSession = sessionmaker(bind=self.target_engine)
    
    def _create_engine(self, config: Dict) -> create_engine:
        """SQLAlchemy 엔진 생성"""
        connection_string = (
            f"mysql+pymysql://{config['user']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
            f"?charset={config['charset']}"
        )
        
        return create_engine(
            connection_string,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    def check_connections(self) -> bool:
        """소스 및 대상 데이터베이스 연결 확인"""
        logger.info("🔍 데이터베이스 연결 확인 중...")
        
        try:
            # 소스 DB 연결 확인
            with self.source_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.fetchone()[0] == 1:
                    logger.info("✅ 소스 DB (localhost) 연결 성공")
                else:
                    logger.error("❌ 소스 DB 연결 테스트 실패")
                    return False
            
            # 대상 DB 연결 확인
            with self.target_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.fetchone()[0] == 1:
                    logger.info("✅ 대상 DB (db.hellobdd2.gabia.io) 연결 성공")
                else:
                    logger.error("❌ 대상 DB 연결 테스트 실패")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            return False
    
    def get_table_count(self, engine: create_engine, table_name: str) -> int:
        """테이블의 레코드 수 조회"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.fetchone()[0]
        except Exception as e:
            logger.error(f"테이블 {table_name} 카운트 조회 실패: {e}")
            return 0
    
    def migrate_communities(self) -> bool:
        """커뮤니티 데이터 마이그레이션"""
        logger.info("🔄 커뮤니티 데이터 마이그레이션 시작...")
        
        try:
            # 소스에서 커뮤니티 조회
            with self.source_engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM communities"))
                source_communities = result.fetchall()
            
            migrated_count = 0
            for community in source_communities:
                try:
                    # 대상 DB에 커뮤니티 추가 (중복 체크 포함)
                    with self.target_engine.connect() as conn:
                        # 기존 커뮤니티 확인
                        check_result = conn.execute(
                            text("SELECT id FROM communities WHERE name = :name"),
                            {"name": community[1]}
                        )
                        existing = check_result.fetchone()
                        
                        if existing:
                            logger.debug(f"커뮤니티 이미 존재: {community[1]}")
                            continue
                        
                        # 새 커뮤니티 삽입
                        conn.execute(
                            text("""
                                INSERT INTO communities (name, created_at, description)
                                VALUES (:name, :created_at, :description)
                            """),
                            {
                                "name": community[1],
                                "created_at": community[2] or datetime.now(),
                                "description": community[3] or ""
                            }
                        )
                        conn.commit()
                        migrated_count += 1
                        logger.debug(f"커뮤니티 마이그레이션: {community[1]}")
                        
                except Exception as e:
                    logger.warning(f"커뮤니티 마이그레이션 실패: {community[1]} - {e}")
            
            logger.info(f"✅ 커뮤니티 마이그레이션 완료: {migrated_count}/{len(source_communities)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 커뮤니티 마이그레이션 중 오류: {e}")
            return False
    
    def migrate_articles(self) -> bool:
        """게시글 데이터 마이그레이션"""
        logger.info("🔄 게시글 데이터 마이그레이션 시작...")
        
        try:
            # 소스에서 게시글 조회
            with self.source_engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM articles"))
                source_articles = result.fetchall()
            
            migrated_count = 0
            for article in source_articles:
                try:
                    # 대상 DB에 게시글 추가 (중복 체크 포함)
                    with self.target_engine.connect() as conn:
                        # 기존 게시글 확인
                        check_result = conn.execute(
                            text("""
                                SELECT id FROM articles 
                                WHERE platform_id = :platform_id 
                                AND community_article_id = :community_article_id
                            """),
                            {
                                "platform_id": article[1],
                                "community_article_id": article[2]
                            }
                        )
                        existing = check_result.fetchone()
                        
                        if existing:
                            logger.debug(f"게시글 이미 존재: {article[1]}/{article[2]}")
                            continue
                        
                        # 새 게시글 삽입
                        conn.execute(
                            text("""
                                INSERT INTO articles (
                                    platform_id, community_article_id, community_id, title, content,
                                    images, writer_nickname, writer_id, like_count, comment_count,
                                    view_count, created_at, category_name, collected_at
                                ) VALUES (
                                    :platform_id, :community_article_id, :community_id, :title, :content,
                                    :images, :writer_nickname, :writer_id, :like_count, :comment_count,
                                    :view_count, :created_at, :category_name, :collected_at
                                )
                            """),
                            {
                                "platform_id": article[1],
                                "community_article_id": article[2],
                                "community_id": article[3],
                                "title": article[4],
                                "content": article[5],
                                "images": article[6],
                                "writer_nickname": article[7],
                                "writer_id": article[8],
                                "like_count": article[9] or 0,
                                "comment_count": article[10] or 0,
                                "view_count": article[11] or 0,
                                "created_at": article[12] or datetime.now(),
                                "category_name": article[13],
                                "collected_at": article[14] or datetime.now()
                            }
                        )
                        conn.commit()
                        migrated_count += 1
                        
                        if migrated_count % 100 == 0:
                            logger.info(f"진행 상황: {migrated_count}/{len(source_articles)} 게시글 마이그레이션 완료")
                        
                except Exception as e:
                    logger.warning(f"게시글 마이그레이션 실패: {article[1]}/{article[2]} - {e}")
            
            logger.info(f"✅ 게시글 마이그레이션 완료: {migrated_count}/{len(source_articles)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 게시글 마이그레이션 중 오류: {e}")
            return False
    
    def migrate_comments(self) -> bool:
        """댓글 데이터 마이그레이션"""
        logger.info("🔄 댓글 데이터 마이그레이션 시작...")
        
        try:
            # 소스에서 댓글 조회
            with self.source_engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM comments"))
                source_comments = result.fetchall()
            
            migrated_count = 0
            for comment in source_comments:
                try:
                    # 대상 DB에서 해당 게시글 찾기
                    with self.target_engine.connect() as conn:
                        article_result = conn.execute(
                            text("""
                                SELECT id FROM articles 
                                WHERE platform_id = :platform_id 
                                AND community_article_id = :community_article_id
                            """),
                            {
                                "platform_id": comment[1],
                                "community_article_id": comment[2]
                            }
                        )
                        target_article = article_result.fetchone()
                        
                        if not target_article:
                            logger.warning(f"댓글의 게시글을 찾을 수 없음: {comment[1]}/{comment[2]}")
                            continue
                        
                        # 기존 댓글 확인
                        check_result = conn.execute(
                            text("""
                                SELECT id FROM comments 
                                WHERE platform_id = :platform_id 
                                AND community_comment_id = :community_comment_id
                            """),
                            {
                                "platform_id": comment[1],
                                "community_comment_id": comment[3]
                            }
                        )
                        existing = check_result.fetchone()
                        
                        if existing:
                            logger.debug(f"댓글 이미 존재: {comment[3]}")
                            continue
                        
                        # 새 댓글 삽입
                        conn.execute(
                            text("""
                                INSERT INTO comments (
                                    platform_id, community_article_id, community_comment_id, content,
                                    writer_nickname, writer_id, created_at, parent_comment_id,
                                    collected_at, article_id
                                ) VALUES (
                                    :platform_id, :community_article_id, :community_comment_id, :content,
                                    :writer_nickname, :writer_id, :created_at, :parent_comment_id,
                                    :collected_at, :article_id
                                )
                            """),
                            {
                                "platform_id": comment[1],
                                "community_article_id": comment[2],
                                "community_comment_id": comment[3],
                                "content": comment[4],
                                "writer_nickname": comment[5],
                                "writer_id": comment[6],
                                "created_at": comment[7] or datetime.now(),
                                "parent_comment_id": comment[8],
                                "collected_at": comment[9] or datetime.now(),
                                "article_id": target_article[0]
                            }
                        )
                        conn.commit()
                        migrated_count += 1
                        
                        if migrated_count % 100 == 0:
                            logger.info(f"진행 상황: {migrated_count}/{len(source_comments)} 댓글 마이그레이션 완료")
                        
                except Exception as e:
                    logger.warning(f"댓글 마이그레이션 실패: {comment[3]} - {e}")
            
            logger.info(f"✅ 댓글 마이그레이션 완료: {migrated_count}/{len(source_comments)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 댓글 마이그레이션 중 오류: {e}")
            return False
    
    def migrate_reviews(self) -> bool:
        """후기 데이터 마이그레이션"""
        logger.info("🔄 후기 데이터 마이그레이션 시작...")
        
        try:
            # 소스에서 후기 조회
            with self.source_engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM reviews"))
                source_reviews = result.fetchall()
            
            migrated_count = 0
            for review in source_reviews:
                try:
                    # 대상 DB에 후기 추가 (중복 체크 포함)
                    with self.target_engine.connect() as conn:
                        # 기존 후기 확인
                        check_result = conn.execute(
                            text("""
                                SELECT id FROM reviews 
                                WHERE platform_id = :platform_id 
                                AND platform_review_id = :platform_review_id
                            """),
                            {
                                "platform_id": review[1],
                                "platform_review_id": review[2]
                            }
                        )
                        existing = check_result.fetchone()
                        
                        if existing:
                            logger.debug(f"후기 이미 존재: {review[1]}/{review[2]}")
                            continue
                        
                        # 새 후기 삽입
                        conn.execute(
                            text("""
                                INSERT INTO reviews (
                                    platform_id, platform_review_id, community_id, title, content,
                                    images, writer_nickname, writer_id, like_count, rating, price,
                                    categories, sub_categories, surgery_date, hospital_name, doctor_name,
                                    is_blind, is_image_blur, is_certificated_review, created_at, collected_at
                                ) VALUES (
                                    :platform_id, :platform_review_id, :community_id, :title, :content,
                                    :images, :writer_nickname, :writer_id, :like_count, :rating, :price,
                                    :categories, :sub_categories, :surgery_date, :hospital_name, :doctor_name,
                                    :is_blind, :is_image_blur, :is_certificated_review, :created_at, :collected_at
                                )
                            """),
                            {
                                "platform_id": review[1],
                                "platform_review_id": review[2],
                                "community_id": review[3],
                                "title": review[4],
                                "content": review[5],
                                "images": review[6],
                                "writer_nickname": review[7],
                                "writer_id": review[8],
                                "like_count": review[9] or 0,
                                "rating": review[10] or 0,
                                "price": review[11] or 0,
                                "categories": review[12],
                                "sub_categories": review[13],
                                "surgery_date": review[14],
                                "hospital_name": review[15],
                                "doctor_name": review[16],
                                "is_blind": bool(review[17]) if review[17] is not None else False,
                                "is_image_blur": bool(review[18]) if review[18] is not None else False,
                                "is_certificated_review": bool(review[19]) if review[19] is not None else False,
                                "created_at": review[20] or datetime.now(),
                                "collected_at": review[21] or datetime.now()
                            }
                        )
                        conn.commit()
                        migrated_count += 1
                        
                        if migrated_count % 100 == 0:
                            logger.info(f"진행 상황: {migrated_count}/{len(source_reviews)} 후기 마이그레이션 완료")
                        
                except Exception as e:
                    logger.warning(f"후기 마이그레이션 실패: {review[1]}/{review[2]} - {e}")
            
            logger.info(f"✅ 후기 마이그레이션 완료: {migrated_count}/{len(source_reviews)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 후기 마이그레이션 중 오류: {e}")
            return False
    
    def get_migration_statistics(self) -> Dict:
        """마이그레이션 통계 조회"""
        logger.info("📊 마이그레이션 통계 조회 중...")
        
        try:
            # 소스 DB 통계
            source_stats = {
                'communities': self.get_table_count(self.source_engine, 'communities'),
                'articles': self.get_table_count(self.source_engine, 'articles'),
                'comments': self.get_table_count(self.source_engine, 'comments'),
                'reviews': self.get_table_count(self.source_engine, 'reviews')
            }
            
            # 대상 DB 통계
            target_stats = {
                'communities': self.get_table_count(self.target_engine, 'communities'),
                'articles': self.get_table_count(self.target_engine, 'articles'),
                'comments': self.get_table_count(self.target_engine, 'comments'),
                'reviews': self.get_table_count(self.target_engine, 'reviews')
            }
            
            return {
                'source': source_stats,
                'target': target_stats
            }
            
        except Exception as e:
            logger.error(f"❌ 통계 조회 중 오류: {e}")
            return {}
    
    def run_migration(self) -> bool:
        """전체 마이그레이션 실행"""
        logger.info("🚀 localhost → db.hellobdd2.gabia.io 데이터 마이그레이션 시작")
        logger.info("=" * 80)
        
        # 연결 확인
        if not self.check_connections():
            logger.error("❌ 데이터베이스 연결에 실패했습니다. 설정을 확인해주세요.")
            return False
        
        # 마이그레이션 전 통계
        logger.info("\n📊 마이그레이션 전 통계:")
        pre_stats = self.get_migration_statistics()
        if pre_stats:
            logger.info(f"소스 DB (localhost): {pre_stats['source']}")
            logger.info(f"대상 DB (gabia.io): {pre_stats['target']}")
        
        # 순서대로 마이그레이션 실행
        migration_steps = [
            ("커뮤니티", self.migrate_communities),
            ("게시글", self.migrate_articles),
            ("댓글", self.migrate_comments),
            ("후기", self.migrate_reviews)
        ]
        
        for step_name, step_function in migration_steps:
            logger.info(f"\n📋 {step_name} 마이그레이션 시작...")
            if not step_function():
                logger.error(f"❌ {step_name} 마이그레이션에 실패했습니다.")
                return False
        
        # 마이그레이션 후 통계
        logger.info("\n📊 마이그레이션 후 통계:")
        post_stats = self.get_migration_statistics()
        if post_stats:
            logger.info(f"소스 DB (localhost): {post_stats['source']}")
            logger.info(f"대상 DB (gabia.io): {post_stats['target']}")
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 모든 데이터 마이그레이션이 성공적으로 완료되었습니다!")
        logger.info("💡 이제 애플리케이션에서 대상 DB를 사용할 수 있습니다.")
        
        return True

def main():
    """메인 함수"""
    logger.info("localhost → db.hellobdd2.gabia.io 데이터 마이그레이션 도구")
    logger.info("=" * 80)
    
    # 사용자 확인
    response = input("\n⚠️  대상 DB의 기존 데이터가 있다면 중복 체크 후 추가됩니다. 계속하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        logger.info("❌ 마이그레이션이 취소되었습니다.")
        return
    
    # 마이그레이션 실행
    migrator = DatabaseMigrator()
    success = migrator.run_migration()
    
    if success:
        logger.info("\n🎯 마이그레이션 완료!")
        logger.info("💡 다음 단계:")
        logger.info("1. 애플리케이션 설정을 대상 DB로 변경")
        logger.info("2. 애플리케이션 재시작")
        logger.info("3. 데이터가 정상적으로 마이그레이션되었는지 확인")
    else:
        logger.error("\n❌ 마이그레이션 중 오류가 발생했습니다. 로그를 확인해주세요.")

if __name__ == "__main__":
    main()