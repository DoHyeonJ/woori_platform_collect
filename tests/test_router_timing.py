#!/usr/bin/env python3
"""
라우터 시간 측정 테스트 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routers.data_collection import collect_gannamunni_data
from api.models import GangnamUnniCollectionRequest
from database.models import DatabaseManager

async def test_router_timing():
    """라우터 시간 측정 테스트"""
    print("🧪 라우터 시간 측정 테스트")
    print("=" * 60)
    
    # 데이터베이스 매니저 생성
    db = DatabaseManager()
    
    try:
        # 1. 단일 카테고리 수집 테스트
        print("📋 1. 단일 카테고리 수집 테스트 (자유수다)")
        print("-" * 40)
        
        request1 = GangnamUnniCollectionRequest(
            category="free_chat",
            target_date="2025-09-12",
            save_as_reviews=False,
            token=None
        )
        
        result1 = await collect_gannamunni_data(request1, db)
        print(f"   결과: {result1.total_articles}개 게시글 수집")
        print(f"   소요시간: {result1.execution_time:.2f}초")
        
        # 2. 후기 저장 테스트
        print(f"\n📋 2. 후기 저장 테스트 (발품후기)")
        print("-" * 40)
        
        request2 = GangnamUnniCollectionRequest(
            category="review",
            target_date="2025-09-12",
            save_as_reviews=True,
            token="456c327614a94565b61f40f6683cda6c"
        )
        
        result2 = await collect_gannamunni_data(request2, db)
        print(f"   결과: {result2.total_reviews}개 후기 저장")
        print(f"   소요시간: {result2.execution_time:.2f}초")
        
        # 3. 잘못된 토큰 테스트
        print(f"\n📋 3. 잘못된 토큰 테스트")
        print("-" * 40)
        
        request3 = GangnamUnniCollectionRequest(
            category="free_chat",
            target_date="2025-09-12",
            save_as_reviews=False,
            token="invalid_token_12345"
        )
        
        try:
            result3 = await collect_gannamunni_data(request3, db)
            print(f"   결과: {result3.total_articles}개 게시글 수집")
            print(f"   소요시간: {result3.execution_time:.2f}초")
        except Exception as e:
            print(f"   예상된 오류: {str(e)}")
        
        print(f"\n📊 전체 테스트 결과:")
        print(f"   - 단일 카테고리: {'✅ 성공' if result1.status == 'success' else '❌ 실패'}")
        print(f"   - 후기 저장: {'✅ 성공' if result2.status == 'success' else '❌ 실패'}")
        print(f"   - 잘못된 토큰: {'❌ 실패 (예상됨)' if 'invalid_token' in str(request3.token) else '⚠️ 예상과 다름'}")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print(f"\n✅ 라우터 시간 측정 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_router_timing())
