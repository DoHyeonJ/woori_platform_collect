#!/usr/bin/env python3
"""
중복 댓글 수집 체크 테스트
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.babitalk_collector import BabitalkDataCollector

async def test_duplicate_comment_check():
    """중복 댓글 수집 체크 테스트"""
    print("🧪 중복 댓글 수집 체크 테스트")
    print("=" * 50)
    
    # 테스트 날짜 (오늘)
    target_date = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 테스트 날짜: {target_date}")
    
    print(f"\n🔄 바비톡 중복 댓글 수집 체크 테스트...")
    
    try:
        # 바비톡 컬렉터 생성
        collector = BabitalkDataCollector()
        
        # 첫 번째 수집 (게시글 + 댓글)
        print("📥 첫 번째 수집 시작 (게시글 + 댓글)...")
        start_time = time.time()
        result1 = await collector.collect_talks_by_date(target_date, 79)  # 성형 카테고리
        first_time = time.time() - start_time
        print(f"✅ 첫 번째 수집 완료: {result1}개")
        print(f"⏱️  첫 번째 수집 소요시간: {first_time:.2f}초")
        
        # 댓글만 수집 (중복 체크 테스트)
        print("\n📥 댓글만 수집 시작 (중복 체크 테스트)...")
        start_time = time.time()
        result2 = await collector.collect_comments_for_talks_by_date(target_date, 79)  # 성형 카테고리
        second_time = time.time() - start_time
        print(f"✅ 댓글 수집 완료: {result2}개")
        print(f"⏱️  댓글 수집 소요시간: {second_time:.2f}초")
        
        # 성능 비교
        if second_time < first_time:
            improvement = ((first_time - second_time) / first_time) * 100
            print(f"🚀 성능 개선: {improvement:.1f}% 빨라짐!")
        else:
            print(f"⚠️  성능 개선 효과가 없음")
            
    except Exception as e:
        print(f"❌ 바비톡 테스트 실패: {e}")
    
    print(f"\n🎉 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_duplicate_comment_check())
