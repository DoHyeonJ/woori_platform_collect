#!/usr/bin/env python3
"""
데이터 수집 실행 스크립트
기존 data_collector.py의 기능을 실행합니다.
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_collector import DataCollector
from utils.logger import get_logger

async def main():
    """메인 실행 함수"""
    logger = get_logger("DATA_COLLECTOR")
    
    logger.info("🚀 데이터 수집을 시작합니다...")
    logger.info("=" * 50)
    
    # 환경 변수 설정
    db_path = os.getenv("DB_PATH", "data/collect_data.db")
    target_date = os.getenv("TARGET_DATE", "2025-01-15")
    save_as_reviews = os.getenv("SAVE_AS_REVIEWS", "false").lower() == "true"
    
    logger.info(f"📅 수집 날짜: {target_date}")
    logger.info(f"💾 데이터베이스: {db_path}")
    logger.info(f"📝 후기 테이블 저장: {save_as_reviews}")
    logger.info("=" * 50)
    
    try:
        # 데이터 수집기 초기화
        collector = DataCollector(db_path=db_path)
        
        # 강남언니 데이터 수집
        logger.info("📱 강남언니 데이터 수집 시작...")
        gangnamunni_stats = await collector.collect_and_save_articles(
            target_date=target_date,
            save_as_reviews=save_as_reviews
        )
        
        logger.info(f"✅ 강남언니 수집 완료: {gangnamunni_stats}")
        
        # 통계 출력
        logger.info("📊 수집 통계:")
        stats = collector.get_statistics()
        logger.info(f"   커뮤니티: {stats['total_communities']}개")
        logger.info(f"   게시글: {stats['total_articles']}개")
        logger.info(f"   댓글: {stats['total_comments']}개")
        logger.info(f"   후기: {stats['total_reviews']}개")
        
        if 'review_statistics' in stats:
            logger.info(f"   플랫폼별 후기: {stats['review_statistics']}")
        
    except Exception as e:
        logger.error(f"❌ 데이터 수집 중 오류 발생: {e}")
        import traceback
        logger.error(f"📋 상세 오류: {traceback.format_exc()}")
        sys.exit(1)
    
    logger.info("🎉 데이터 수집이 완료되었습니다!")

if __name__ == "__main__":
    asyncio.run(main()) 