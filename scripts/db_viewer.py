#!/usr/bin/env python3
"""
데이터베이스 뷰어 스크립트
수집된 데이터를 조회하고 통계를 확인합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.models import DatabaseManager
from utils.logger import get_logger

def show_statistics():
    """통계 정보를 출력합니다."""
    logger = get_logger("DB_VIEWER")
    db_path = os.getenv("DB_PATH", "data/collect_data.db")
    db = DatabaseManager(db_path)
    
    logger.info("📊 데이터베이스 통계")
    logger.info("=" * 50)
    
    stats = db.get_statistics()
    
    logger.info(f"커뮤니티: {stats['total_communities']}개")
    logger.info(f"게시글: {stats['total_articles']}개")
    logger.info(f"댓글: {stats['total_comments']}개")
    logger.info(f"후기: {stats['total_reviews']}개")
    
    if 'platform_statistics' in stats:
        logger.info("📱 플랫폼별 통계:")
        for platform, count in stats['platform_statistics'].items():
            logger.info(f"  {platform}: {count}개")
    
    if 'review_statistics' in stats:
        logger.info("⭐ 후기 통계:")
        for platform, count in stats['review_statistics'].items():
            logger.info(f"  {platform}: {count}개")

def show_articles(limit=10):
    """최근 게시글을 출력합니다."""
    logger = get_logger("DB_VIEWER")
    db_path = os.getenv("DB_PATH", "data/collect_data.db")
    db = DatabaseManager(db_path)
    
    logger.info(f"📝 최근 게시글 (상위 {limit}개)")
    logger.info("=" * 50)
    
    articles = db.get_articles_by_date("2025-01-15", limit=limit)
    
    for i, article in enumerate(articles, 1):
        logger.info(f"{i}. [{article['platform_id']}] {article['title'][:50]}...")
        logger.info(f"   작성자: {article['writer_nickname']}")
        logger.info(f"   작성일: {article['created_at']}")
        logger.info("")

def show_reviews(limit=10):
    """최근 후기를 출력합니다."""
    logger = get_logger("DB_VIEWER")
    db_path = os.getenv("DB_PATH", "data/collect_data.db")
    db = DatabaseManager(db_path)
    
    logger.info(f"⭐ 최근 후기 (상위 {limit}개)")
    logger.info("=" * 50)
    
    reviews = db.get_reviews_by_platform("babitalk", limit=limit)
    
    for i, review in enumerate(reviews, 1):
        logger.info(f"{i}. [{review['platform_id']}] {review['title'][:50]}...")
        logger.info(f"   작성자: {review['writer_nickname']}")
        logger.info(f"   평점: {review['rating']}/5")
        logger.info(f"   병원: {review['hospital_name']}")
        logger.info(f"   작성일: {review['created_at']}")
        logger.info("")

def main():
    """메인 함수"""
    logger = get_logger("DB_VIEWER")
    
    logger.info("🔍 데이터베이스 뷰어")
    logger.info("=" * 50)
    
    while True:
        logger.info("📋 메뉴:")
        logger.info("1. 통계 보기")
        logger.info("2. 최근 게시글 보기")
        logger.info("3. 최근 후기 보기")
        logger.info("4. 종료")
        
        choice = input("\n선택하세요 (1-4): ").strip()
        
        if choice == "1":
            show_statistics()
        elif choice == "2":
            limit = input("몇 개를 보시겠습니까? (기본값: 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            show_articles(limit)
        elif choice == "3":
            limit = input("몇 개를 보시겠습니까? (기본값: 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            show_reviews(limit)
        elif choice == "4":
            logger.info("👋 종료합니다.")
            break
        else:
            logger.warning("❌ 잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    main() 