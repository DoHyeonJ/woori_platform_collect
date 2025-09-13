#!/usr/bin/env python3
"""
네이버 중복 체크 테스트
"""
import os
import sys
import asyncio
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.naver_collector import NaverDataCollector

async def test_naver_duplicate_check():
    """네이버 중복 체크 테스트"""
    print("🧪 네이버 중복 체크 테스트")
    print("=" * 50)
    
    # 테스트 카페 ID (A+여우야★성형카페)
    cafe_id = "12285441"
    target_date = "2025-09-12"  # 어제 날짜로 변경
    
    print(f"📅 테스트 날짜: {target_date}")
    print(f"🏢 테스트 카페: {cafe_id}")
    
    collector = NaverDataCollector()
    
    try:
        print("\n📥 첫 번째 수집 시작 (게시글 + 댓글)...")
        start_time = time.time()
        
        # 첫 번째 수집
        result1 = await collector.collect_articles_by_date_with_comments(
            cafe_id=cafe_id,
            target_date=target_date,
            menu_id="38"  # 자유게시판
        )
        
        first_duration = time.time() - start_time
        print(f"✅ 첫 번째 수집 완료: {result1.get('saved', 0)}개")
        print(f"⏱️  첫 번째 수집 소요시간: {first_duration:.2f}초")
        
        print("\n📥 두 번째 수집 시작 (중복 체크 테스트)...")
        start_time = time.time()
        
        # 두 번째 수집 (중복 체크)
        result2 = await collector.collect_articles_by_date_with_comments(
            cafe_id=cafe_id,
            target_date=target_date,
            menu_id="38"  # 자유게시판
        )
        
        second_duration = time.time() - start_time
        print(f"✅ 두 번째 수집 완료: {result2.get('saved', 0)}개")
        print(f"⏱️  두 번째 수집 소요시간: {second_duration:.2f}초")
        
        # 성능 비교
        if first_duration > 0:
            improvement = ((first_duration - second_duration) / first_duration) * 100
            print(f"🚀 성능 개선: {improvement:.1f}% 빨라짐!")
        
        print("\n🎉 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_naver_duplicate_check())
