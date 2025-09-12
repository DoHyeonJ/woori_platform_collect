#!/usr/bin/env python3
"""
강남언니 댓글 수 집계 테스트
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.gannamunni_collector import GangnamUnniDataCollector

async def test_comment_count():
    """댓글 수 집계 테스트"""
    print("🧪 강남언니 댓글 수 집계 테스트")
    print("=" * 50)
    
    # 테스트 날짜 (오늘)
    target_date = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 테스트 날짜: {target_date}")
    
    # 강남언니 컬렉터 생성 (기본 토큰 사용)
    collector = GangnamUnniDataCollector(token="456c327614a94565b61f40f6683cda6c")
    
    # 테스트할 카테고리
    test_categories = ["hospital_question", "free_chat"]
    
    for category in test_categories:
        print(f"\n🔄 {category} 카테고리 테스트...")
        
        try:
            start_time = time.time()
            
            # 게시글 수집 (댓글 포함)
            result = await collector.collect_articles_by_date(
                target_date=target_date,
                category=category,
                save_as_reviews=False
            )
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            print(f"✅ {category} 수집 완료!")
            print(f"📊 결과: {result}")
            print(f"⏱️  소요시간: {elapsed_time:.2f}초")
            
            # 결과 검증
            if isinstance(result, dict) and "articles" in result and "comments" in result:
                print(f"✅ 댓글 수 집계 정상: 게시글 {result['articles']}개, 댓글 {result['comments']}개")
            else:
                print(f"❌ 댓글 수 집계 실패: 예상된 형식이 아님")
                
        except Exception as e:
            print(f"❌ {category} 수집 실패: {e}")
            import traceback
            print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print(f"\n🎉 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_comment_count())
