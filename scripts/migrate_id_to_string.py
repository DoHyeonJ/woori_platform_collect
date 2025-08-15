#!/usr/bin/env python3
"""
ID 필드들을 문자열로 변경하는 마이그레이션 스크립트
"""

import sqlite3
import os
import sys
from datetime import datetime

# utils 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger("ID_MIGRATION")

def migrate_id_fields_to_string(db_path: str = "data/collect_data.db"):
    """
    데이터베이스의 ID 필드들을 문자열로 변경합니다.
    """
    logger.info("🔄 ID 필드들을 문자열로 마이그레이션 시작")
    
    if not os.path.exists(db_path):
        logger.error(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 1. articles 테이블의 community_article_id를 TEXT로 변경
            logger.info("📝 articles 테이블의 community_article_id를 TEXT로 변경 중...")
            
            # 임시 테이블 생성
            cursor.execute('''
                CREATE TABLE articles_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id TEXT NOT NULL,
                    community_article_id TEXT NOT NULL,
                    community_id INTEGER NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    images TEXT,
                    writer_nickname TEXT NOT NULL,
                    writer_id TEXT NOT NULL,
                    like_count INTEGER DEFAULT 0,
                    comment_count INTEGER DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    category_name TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (community_id) REFERENCES communities (id),
                    UNIQUE(platform_id, community_article_id)
                )
            ''')
            
            # 기존 데이터를 임시 테이블로 복사 (ID를 문자열로 변환)
            cursor.execute('''
                INSERT INTO articles_temp 
                SELECT 
                    id,
                    platform_id,
                    CAST(community_article_id AS TEXT) as community_article_id,
                    community_id,
                    title,
                    content,
                    images,
                    writer_nickname,
                    writer_id,
                    like_count,
                    comment_count,
                    view_count,
                    created_at,
                    category_name,
                    collected_at
                FROM articles
            ''')
            
            # 기존 테이블 삭제
            cursor.execute('DROP TABLE articles')
            
            # 임시 테이블을 원래 이름으로 변경
            cursor.execute('ALTER TABLE articles_temp RENAME TO articles')
            
            # 인덱스 재생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_community_id ON articles(community_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at)')
            
            logger.info("✅ articles 테이블 마이그레이션 완료")
            
            # 2. reviews 테이블의 platform_review_id를 TEXT로 변경
            logger.info("📝 reviews 테이블의 platform_review_id를 TEXT로 변경 중...")
            
            # 임시 테이블 생성
            cursor.execute('''
                CREATE TABLE reviews_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id TEXT NOT NULL,
                    platform_review_id TEXT NOT NULL,
                    community_id INTEGER NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    images TEXT,
                    writer_nickname TEXT NOT NULL,
                    writer_id TEXT NOT NULL,
                    like_count INTEGER DEFAULT 0,
                    rating INTEGER DEFAULT 0,
                    price INTEGER DEFAULT 0,
                    categories TEXT,
                    sub_categories TEXT,
                    surgery_date TEXT,
                    hospital_name TEXT,
                    doctor_name TEXT,
                    is_blind BOOLEAN DEFAULT FALSE,
                    is_image_blur BOOLEAN DEFAULT FALSE,
                    is_certificated_review BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (community_id) REFERENCES communities (id),
                    UNIQUE(platform_id, platform_review_id)
                )
            ''')
            
            # 기존 데이터를 임시 테이블로 복사 (ID를 문자열로 변환)
            cursor.execute('''
                INSERT INTO reviews_temp 
                SELECT 
                    id,
                    platform_id,
                    CAST(platform_review_id AS TEXT) as platform_review_id,
                    community_id,
                    title,
                    content,
                    images,
                    writer_nickname,
                    writer_id,
                    like_count,
                    rating,
                    price,
                    categories,
                    sub_categories,
                    surgery_date,
                    hospital_name,
                    doctor_name,
                    is_blind,
                    is_image_blur,
                    is_certificated_review,
                    created_at,
                    collected_at
                FROM reviews
            ''')
            
            # 기존 테이블 삭제
            cursor.execute('DROP TABLE reviews')
            
            # 임시 테이블을 원래 이름으로 변경
            cursor.execute('ALTER TABLE reviews_temp RENAME TO reviews')
            
            # 인덱스 재생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_platform_id ON reviews(platform_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_platform_review_id ON reviews(platform_review_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_community_id ON reviews(community_id)')
            
            logger.info("✅ reviews 테이블 마이그레이션 완료")
            
            # 변경사항 커밋
            conn.commit()
            
            logger.info("🎉 모든 ID 필드 마이그레이션 완료!")
            return True
            
    except Exception as e:
        logger.error(f"❌ 마이그레이션 중 오류 발생: {e}")
        return False

def verify_migration(db_path: str = "data/collect_data.db"):
    """
    마이그레이션 결과를 확인합니다.
    """
    logger.info("🔍 마이그레이션 결과 확인 중...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # articles 테이블 스키마 확인
            cursor.execute("PRAGMA table_info(articles)")
            articles_schema = cursor.fetchall()
            
            # reviews 테이블 스키마 확인
            cursor.execute("PRAGMA table_info(reviews)")
            reviews_schema = cursor.fetchall()
            
            # community_article_id가 TEXT인지 확인
            article_id_field = next((field for field in articles_schema if field[1] == 'community_article_id'), None)
            if article_id_field and article_id_field[2] == 'TEXT':
                logger.info("✅ articles.community_article_id: TEXT")
            else:
                logger.error("❌ articles.community_article_id: TEXT가 아님")
                return False
            
            # platform_review_id가 TEXT인지 확인
            review_id_field = next((field for field in reviews_schema if field[1] == 'platform_review_id'), None)
            if review_id_field and review_id_field[2] == 'TEXT':
                logger.info("✅ reviews.platform_review_id: TEXT")
            else:
                logger.error("❌ reviews.platform_review_id: TEXT가 아님")
                return False
            
            # 샘플 데이터 확인
            cursor.execute("SELECT platform_id, community_article_id FROM articles LIMIT 3")
            sample_articles = cursor.fetchall()
            logger.info(f"📋 articles 샘플 데이터: {sample_articles}")
            
            cursor.execute("SELECT platform_id, platform_review_id FROM reviews LIMIT 3")
            sample_reviews = cursor.fetchall()
            logger.info(f"📋 reviews 샘플 데이터: {sample_reviews}")
            
            logger.info("✅ 마이그레이션 검증 완료")
            return True
            
    except Exception as e:
        logger.error(f"❌ 검증 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 ID 필드 문자열 마이그레이션 시작")
    logger.info("=" * 50)
    
    # 마이그레이션 실행
    success = migrate_id_fields_to_string()
    
    if success:
        logger.info("✅ 마이그레이션 성공!")
        
        # 결과 검증
        verify_migration()
    else:
        logger.error("❌ 마이그레이션 실패!")
    
    logger.info("=" * 50)
    logger.info("🏁 ID 필드 문자열 마이그레이션 완료")
