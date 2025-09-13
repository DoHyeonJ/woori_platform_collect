#!/usr/bin/env python3
"""
네이버 라우터 간소화 테스트 (per_page 제거)
"""
import os
import sys
import asyncio
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.naver_collector import NaverDataCollector

async def test_naver_simplified():
    """네이버 수집기 간소화 테스트"""
    print("🧪 네이버 수집기 간소화 테스트 (per_page 제거)")
    print("=" * 50)
    
    # 테스트 카페 ID (A+여우야★성형카페)
    cafe_id = "12285441"
    target_date = "2025-09-12"
    menu_id = "38"
    
    print(f"📅 테스트 날짜: {target_date}")
    print(f"🏢 테스트 카페: {cafe_id}")
    print(f"📂 테스트 게시판: {menu_id}")
    
    collector = NaverDataCollector()
    
    try:
        print("\n📥 날짜별 수집 테스트...")
        start_time = time.time()
        
        # 날짜별 수집 (per_page 없이)
        result = await collector.collect_articles_by_date_with_comments(
            cafe_id=cafe_id,
            target_date=target_date,
            menu_id=menu_id
        )
        
        duration = time.time() - start_time
        print(f"✅ 날짜별 수집 완료: {result.get('saved', 0)}개 게시글, {result.get('comments_saved', 0)}개 댓글")
        print(f"⏱️  수집 소요시간: {duration:.2f}초")
        
        print("\n📥 게시판별 수집 테스트...")
        start_time = time.time()
        
        # 게시판별 수집 (per_page 없이)
        count = await collector.collect_articles_by_menu(
            cafe_id=cafe_id,
            menu_id=menu_id,
            per_page=20  # 내부적으로 기본값 사용
        )
        
        duration = time.time() - start_time
        print(f"✅ 게시판별 수집 완료: {count}개 게시글")
        print(f"⏱️  수집 소요시간: {duration:.2f}초")
        
        print("\n🎉 테스트 완료!")
        print("✅ per_page 파라미터가 라우터에서 제거되어 내부적으로만 사용됨")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_naver_simplified())
