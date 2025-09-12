#!/usr/bin/env python3
"""
모든 카테고리 테스트 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.gannamunni import GangnamUnniAPI

async def test_all_categories():
    """모든 카테고리 테스트"""
    print("🧪 모든 카테고리 테스트")
    print("=" * 60)
    
    api = GangnamUnniAPI()
    
    categories = {
        "hospital_question": "병원질문",
        "surgery_question": "시술/수술질문", 
        "free_chat": "자유수다",
        "review": "발품후기",
        "ask_doctor": "의사에게 물어보세요"
    }
    
    results = {}
    
    for category_key, category_name in categories.items():
        print(f"\n📂 {category_name} 카테고리 테스트")
        print("-" * 40)
        
        try:
            articles = await api.get_article_list(category_key, 1)
            print(f"   ✅ 성공: {len(articles)}개 게시글 수집")
            
            if articles:
                first_article = articles[0]
                print(f"   📝 첫 번째 게시글:")
                print(f"     - ID: {first_article.id}")
                print(f"     - 작성자: {first_article.writer.nickname}")
                print(f"     - 내용: {first_article.contents[:30]}...")
                print(f"     - 작성시간: {first_article.create_time}")
            
            results[category_key] = {
                'success': True,
                'count': len(articles)
            }
            
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            results[category_key] = {
                'success': False,
                'error': str(e)
            }
        
        # 카테고리 간 딜레이
        await asyncio.sleep(2)
    
    print(f"\n📊 전체 테스트 결과:")
    print("=" * 60)
    
    total_success = 0
    total_articles = 0
    
    for category_key, result in results.items():
        category_name = categories[category_key]
        if result['success']:
            print(f"   ✅ {category_name}: {result['count']}개")
            total_success += 1
            total_articles += result['count']
        else:
            print(f"   ❌ {category_name}: {result['error']}")
    
    print(f"\n🎯 요약:")
    print(f"   - 성공한 카테고리: {total_success}/{len(categories)}개")
    print(f"   - 총 수집된 게시글: {total_articles}개")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_categories())
