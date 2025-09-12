#!/usr/bin/env python3
"""
개선된 강남언니 API 테스트 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.gannamunni import GangnamUnniAPI

async def test_improved_api():
    """개선된 API 테스트"""
    print("🧪 개선된 강남언니 API 테스트")
    print("=" * 60)
    
    # 1. 기본 토큰으로 테스트
    print("📋 1. 기본 토큰으로 테스트")
    print("-" * 40)
    
    api_default = GangnamUnniAPI()  # 기본 토큰 사용
    articles1 = await api_default.get_article_list('free_chat', 1)
    print(f"   수집된 게시글: {len(articles1)}개")
    
    if articles1:
        first_article = articles1[0]
        print(f"   첫 번째 게시글:")
        print(f"     - ID: {first_article.id}")
        print(f"     - 작성자: {first_article.writer.nickname}")
        print(f"     - 내용: {first_article.contents[:50]}...")
        print(f"     - 작성시간: {first_article.create_time}")
    
    # 2. 사용자 지정 토큰으로 테스트
    print(f"\n📋 2. 사용자 지정 토큰으로 테스트")
    print("-" * 40)
    
    custom_token = "456c327614a94565b61f40f6683cda6c"  # 동일한 토큰
    api_custom = GangnamUnniAPI(token=custom_token)
    articles2 = await api_custom.get_article_list('free_chat', 1)
    print(f"   수집된 게시글: {len(articles2)}개")
    
    if articles2:
        first_article = articles2[0]
        print(f"   첫 번째 게시글:")
        print(f"     - ID: {first_article.id}")
        print(f"     - 작성자: {first_article.writer.nickname}")
        print(f"     - 내용: {first_article.contents[:50]}...")
        print(f"     - 작성시간: {first_article.create_time}")
    
    # 3. 잘못된 토큰으로 테스트
    print(f"\n📋 3. 잘못된 토큰으로 테스트")
    print("-" * 40)
    
    wrong_token = "invalid_token_12345"
    api_wrong = GangnamUnniAPI(token=wrong_token)
    articles3 = await api_wrong.get_article_list('free_chat', 1)
    print(f"   수집된 게시글: {len(articles3)}개")
    
    # 4. 날짜별 수집 테스트
    print(f"\n📋 4. 날짜별 수집 테스트")
    print("-" * 40)
    
    date_articles = await api_default.get_articles_by_date('2025-09-12', 'free_chat')
    print(f"   2025-09-12 날짜 게시글: {len(date_articles)}개")
    
    if date_articles:
        print(f"   첫 번째 날짜별 게시글:")
        first_date_article = date_articles[0]
        print(f"     - ID: {first_date_article.id}")
        print(f"     - 작성자: {first_date_article.writer.nickname}")
        print(f"     - 내용: {first_date_article.contents[:50]}...")
        print(f"     - 작성시간: {first_date_article.create_time}")
    
    # 5. 모든 카테고리 테스트
    print(f"\n📋 5. 모든 카테고리 테스트")
    print("-" * 40)
    
    categories = {
        "hospital_question": "병원질문",
        "surgery_question": "시술/수술질문", 
        "free_chat": "자유수다",
        "review": "발품후기",
        "ask_doctor": "의사에게 물어보세요"
    }
    
    total_articles = 0
    for category_key, category_name in categories.items():
        try:
            articles = await api_default.get_article_list(category_key, 1)
            print(f"   {category_name}: {len(articles)}개")
            total_articles += len(articles)
        except Exception as e:
            print(f"   {category_name}: 오류 - {e}")
    
    print(f"\n📊 전체 수집 결과:")
    print(f"   - 총 게시글: {total_articles}개")
    print(f"   - 기본 토큰: {'✅ 작동' if len(articles1) > 0 else '❌ 실패'}")
    print(f"   - 사용자 토큰: {'✅ 작동' if len(articles2) > 0 else '❌ 실패'}")
    print(f"   - 잘못된 토큰: {'❌ 실패' if len(articles3) == 0 else '⚠️ 예상과 다름'}")
    
    print(f"\n✅ 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_improved_api())
