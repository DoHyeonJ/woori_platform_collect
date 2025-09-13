#!/usr/bin/env python3
"""
네이버 여러 게시판 수집 테스트
"""
import os
import sys
import asyncio
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.naver_collector import NaverDataCollector

async def test_naver_multi_menu():
    """네이버 여러 게시판 수집 테스트"""
    print("🧪 네이버 여러 게시판 수집 테스트")
    print("=" * 50)
    
    # 테스트 카페 ID (A+여우야★성형카페)
    cafe_id = "12285441"
    target_date = "2025-09-12"
    
    # 여러 게시판 ID (자유게시판, 질문게시판 등)
    single_menu = "38"  # 자유게시판
    multi_menus = "38,38"  # 자유게시판을 두 번 (중복 테스트)
    
    print(f"📅 테스트 날짜: {target_date}")
    print(f"🏢 테스트 카페: {cafe_id}")
    print(f"📂 단일 게시판: {single_menu}")
    print(f"📂 여러 게시판: {multi_menus}")
    
    collector = NaverDataCollector()
    
    try:
        print("\n📥 단일 게시판 수집 테스트...")
        start_time = time.time()
        
        # 단일 게시판 수집
        result1 = await collector.collect_articles_by_date_with_comments(
            cafe_id=cafe_id,
            target_date=target_date,
            menu_id=single_menu
        )
        
        single_duration = time.time() - start_time
        print(f"✅ 단일 게시판 수집 완료: {result1.get('saved', 0)}개")
        print(f"⏱️  단일 게시판 수집 소요시간: {single_duration:.2f}초")
        
        print("\n📥 여러 게시판 수집 테스트...")
        start_time = time.time()
        
        # 여러 게시판 수집
        result2 = await collector.collect_articles_by_date_with_comments(
            cafe_id=cafe_id,
            target_date=target_date,
            menu_id=multi_menus
        )
        
        multi_duration = time.time() - start_time
        print(f"✅ 여러 게시판 수집 완료: {result2.get('saved', 0)}개")
        print(f"⏱️  여러 게시판 수집 소요시간: {multi_duration:.2f}초")
        
        # 결과 비교
        print(f"\n📊 수집 결과 비교:")
        print(f"   단일 게시판: {result1.get('saved', 0)}개 게시글, {result1.get('comments_saved', 0)}개 댓글")
        print(f"   여러 게시판: {result2.get('saved', 0)}개 게시글, {result2.get('comments_saved', 0)}개 댓글")
        
        if result2.get('saved', 0) > result1.get('saved', 0):
            print("✅ 여러 게시판 수집이 더 많은 데이터를 수집했습니다!")
        else:
            print("⚠️  여러 게시판 수집 결과가 예상과 다릅니다.")
        
        print("\n🎉 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_naver_multi_menu())
