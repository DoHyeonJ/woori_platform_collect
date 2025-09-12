#!/usr/bin/env python3
"""
강남언니 라우터 테스트 스크립트
"""

import asyncio
import sys
import os
import json

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routers.async_collection import GangnamunniCollectionRequest
from api.services.async_collection_service import AsyncCollectionService

async def test_router_integration():
    """라우터 통합 테스트"""
    print("🧪 강남언니 라우터 통합 테스트")
    print("=" * 60)
    
    # 1. 기본 토큰으로 테스트
    print("📋 1. 기본 토큰으로 테스트 (token=None)")
    print("-" * 40)
    
    request1 = GangnamunniCollectionRequest(
        target_date="2025-09-12",
        categories=["free_chat"],
        save_as_reviews=False,
        token=None  # 기본 토큰 사용
    )
    
    result1 = await AsyncCollectionService.collect_gangnamunni_data(
        target_date=request1.target_date,
        categories=request1.categories,
        save_as_reviews=request1.save_as_reviews,
        token=request1.token
    )
    
    print(f"   수집 결과:")
    print(f"     - 상태: {result1.get('status', 'unknown')}")
    print(f"     - 총 게시글: {result1.get('total_articles', 0)}개")
    print(f"     - 카테고리별 결과: {result1.get('category_results', {})}")
    
    # 2. 사용자 지정 토큰으로 테스트
    print(f"\n📋 2. 사용자 지정 토큰으로 테스트")
    print("-" * 40)
    
    request2 = GangnamunniCollectionRequest(
        target_date="2025-09-12",
        categories=["free_chat", "hospital_question"],
        save_as_reviews=False,
        token="456c327614a94565b61f40f6683cda6c"  # 사용자 지정 토큰
    )
    
    result2 = await AsyncCollectionService.collect_gangnamunni_data(
        target_date=request2.target_date,
        categories=request2.categories,
        save_as_reviews=request2.save_as_reviews,
        token=request2.token
    )
    
    print(f"   수집 결과:")
    print(f"     - 상태: {result2.get('status', 'unknown')}")
    print(f"     - 총 게시글: {result2.get('total_articles', 0)}개")
    print(f"     - 카테고리별 결과: {result2.get('category_results', {})}")
    
    # 3. 잘못된 토큰으로 테스트
    print(f"\n📋 3. 잘못된 토큰으로 테스트")
    print("-" * 40)
    
    request3 = GangnamunniCollectionRequest(
        target_date="2025-09-12",
        categories=["free_chat"],
        save_as_reviews=False,
        token="invalid_token_12345"  # 잘못된 토큰
    )
    
    result3 = await AsyncCollectionService.collect_gangnamunni_data(
        target_date=request3.target_date,
        categories=request3.categories,
        save_as_reviews=request3.save_as_reviews,
        token=request3.token
    )
    
    print(f"   수집 결과:")
    print(f"     - 상태: {result3.get('status', 'unknown')}")
    print(f"     - 총 게시글: {result3.get('total_articles', 0)}개")
    print(f"     - 오류: {result3.get('error', 'None')}")
    
    # 4. 요청 모델 검증
    print(f"\n📋 4. 요청 모델 검증")
    print("-" * 40)
    
    # 유효한 요청
    valid_request = GangnamunniCollectionRequest(
        target_date="2025-09-12",
        categories=["free_chat"],
        save_as_reviews=False,
        token="456c327614a94565b61f40f6683cda6c"
    )
    
    print(f"   유효한 요청:")
    print(f"     - target_date: {valid_request.target_date}")
    print(f"     - categories: {valid_request.categories}")
    print(f"     - save_as_reviews: {valid_request.save_as_reviews}")
    print(f"     - token: {valid_request.token}")
    
    # JSON 직렬화 테스트
    try:
        json_data = valid_request.dict()
        print(f"   JSON 직렬화: ✅ 성공")
        print(f"   JSON 데이터: {json.dumps(json_data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"   JSON 직렬화: ❌ 실패 - {e}")
    
    print(f"\n📊 전체 테스트 결과:")
    print(f"   - 기본 토큰: {'✅ 성공' if result1.get('status') == 'success' else '❌ 실패'}")
    print(f"   - 사용자 토큰: {'✅ 성공' if result2.get('status') == 'success' else '❌ 실패'}")
    print(f"   - 잘못된 토큰: {'❌ 실패 (예상됨)' if result3.get('status') == 'error' else '⚠️ 예상과 다름'}")
    print(f"   - 요청 모델: ✅ 정상")
    
    print(f"\n✅ 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_router_integration())
