#!/usr/bin/env python3
"""
강남언니 수집 시간 측정 테스트 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.gannamunni_collector import GangnamUnniDataCollector

async def test_gannamunni_timing():
    """강남언니 수집 시간 측정 테스트"""
    print("🧪 강남언니 수집 시간 측정 테스트")
    print("=" * 60)
    
    # 수집기 생성
    collector = GangnamUnniDataCollector()
    
    try:
        # 1. 단일 카테고리 수집 테스트
        print("📋 1. 단일 카테고리 수집 테스트 (자유수다)")
        print("-" * 40)
        
        result1 = await collector.collect_articles_by_date(
            target_date="2025-09-12",
            category="free_chat",
            save_as_reviews=False
        )
        
        print(f"   결과: {result1}개 게시글 수집")
        
        # 2. 모든 카테고리 수집 테스트
        print(f"\n📋 2. 모든 카테고리 수집 테스트")
        print("-" * 40)
        
        result2 = await collector.collect_all_categories_by_date(
            target_date="2025-09-12",
            save_as_reviews=False
        )
        
        print(f"   카테고리별 결과:")
        for category, count in result2.items():
            print(f"     - {category}: {count}개")
        
        # 3. 후기 저장 테스트
        print(f"\n📋 3. 후기 저장 테스트 (발품후기)")
        print("-" * 40)
        
        result3 = await collector.collect_articles_by_date(
            target_date="2025-09-12",
            category="review",
            save_as_reviews=True
        )
        
        print(f"   결과: {result3}개 후기 저장")
        
        # 4. 통계 조회
        print(f"\n📋 4. 데이터베이스 통계")
        print("-" * 40)
        
        stats = collector.get_statistics()
        print(f"   전체 게시글: {stats['total_articles']}개")
        print(f"   전체 댓글: {stats['total_comments']}개")
        print(f"   전체 커뮤니티: {stats['total_communities']}개")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print(f"\n✅ 시간 측정 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_gannamunni_timing())
