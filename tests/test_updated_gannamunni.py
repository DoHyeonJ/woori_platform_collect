#!/usr/bin/env python3
"""
업데이트된 강남언니 API 테스트 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.gannamunni import GangnamUnniAPI

async def test_updated_api():
    """업데이트된 API 테스트"""
    print("🧪 업데이트된 강남언니 API 테스트")
    print("=" * 50)
    
    api = GangnamUnniAPI()
    
    try:
        # 1. 자유수다 카테고리 테스트
        print("📂 자유수다 카테고리 테스트")
        articles = await api.get_article_list('free_chat', 1)
        print(f"   수집된 게시글: {len(articles)}개")
        
        if articles:
            first_article = articles[0]
            print(f"   첫 번째 게시글:")
            print(f"     - ID: {first_article.id}")
            print(f"     - 작성자: {first_article.writer.nickname}")
            print(f"     - 내용: {first_article.contents[:50]}...")
            print(f"     - 작성시간: {first_article.create_time}")
            print(f"     - 댓글수: {first_article.comment_count}")
        
        # 2. 병원질문 카테고리 테스트
        print(f"\n📂 병원질문 카테고리 테스트")
        articles2 = await api.get_article_list('hospital_question', 1)
        print(f"   수집된 게시글: {len(articles2)}개")
        
        # 3. 날짜별 수집 테스트
        print(f"\n📅 날짜별 수집 테스트 (2025-09-12)")
        date_articles = await api.get_articles_by_date('2025-09-12', 'free_chat')
        print(f"   수집된 게시글: {len(date_articles)}개")
        
        if date_articles:
            print(f"   첫 번째 날짜별 게시글:")
            first_date_article = date_articles[0]
            print(f"     - ID: {first_date_article.id}")
            print(f"     - 작성자: {first_date_article.writer.nickname}")
            print(f"     - 내용: {first_date_article.contents[:50]}...")
            print(f"     - 작성시간: {first_date_article.create_time}")
        
        print(f"\n✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_updated_api())
