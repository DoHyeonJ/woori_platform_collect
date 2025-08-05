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

async def main():
    """메인 실행 함수"""
    print("🚀 데이터 수집을 시작합니다...")
    print("=" * 50)
    
    # 환경 변수 설정
    db_path = os.getenv("DB_PATH", "test_collect_data.db")
    target_date = os.getenv("TARGET_DATE", "2025-01-15")
    save_as_reviews = os.getenv("SAVE_AS_REVIEWS", "false").lower() == "true"
    
    print(f"📅 수집 날짜: {target_date}")
    print(f"💾 데이터베이스: {db_path}")
    print(f"📝 후기 테이블 저장: {save_as_reviews}")
    print("=" * 50)
    
    try:
        # 데이터 수집기 초기화
        collector = DataCollector(db_path=db_path)
        
        # 강남언니 데이터 수집
        print("\n📱 강남언니 데이터 수집 시작...")
        gangnamunni_stats = await collector.collect_and_save_articles(
            target_date=target_date,
            save_as_reviews=save_as_reviews
        )
        
        print(f"✅ 강남언니 수집 완료: {gangnamunni_stats}")
        
        # 통계 출력
        print("\n📊 수집 통계:")
        stats = collector.get_statistics()
        print(f"   커뮤니티: {stats['total_communities']}개")
        print(f"   게시글: {stats['total_articles']}개")
        print(f"   댓글: {stats['total_comments']}개")
        print(f"   후기: {stats['total_reviews']}개")
        
        if 'review_statistics' in stats:
            print(f"   플랫폼별 후기: {stats['review_statistics']}")
        
    except Exception as e:
        print(f"❌ 데이터 수집 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
        sys.exit(1)
    
    print("\n🎉 데이터 수집이 완료되었습니다!")

if __name__ == "__main__":
    asyncio.run(main()) 