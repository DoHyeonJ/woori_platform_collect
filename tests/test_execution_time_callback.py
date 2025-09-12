#!/usr/bin/env python3
"""
실행시간 콜백 테스트
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services.async_collection_service import AsyncCollectionService

async def test_execution_time():
    """실행시간 콜백 테스트"""
    print("🧪 실행시간 콜백 테스트")
    print("=" * 50)
    
    # 테스트 날짜 (오늘)
    target_date = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 테스트 날짜: {target_date}")
    
    # 테스트용 콜백 URL (실제로는 호출되지 않음)
    test_callback_url = "http://localhost:8080/test/callback"
    
    print(f"\n🔄 바비톡 실행시간 테스트...")
    
    try:
        # 바비톡 데이터 수집 (실행시간 측정)
        start_time = time.time()
        
        result = await AsyncCollectionService.collect_babitalk_data(
            target_date=target_date,
            categories=["talks"],  # 빠른 테스트를 위해 자유톡만
            callback_url=test_callback_url
        )
        
        end_time = time.time()
        actual_elapsed = end_time - start_time
        
        print(f"✅ 바비톡 수집 완료!")
        print(f"📊 결과: {result}")
        print(f"⏱️  실제 소요시간: {actual_elapsed:.2f}초")
        
        # 콜백에 포함된 실행시간 확인
        if "execution_time" in result:
            print(f"✅ 콜백 실행시간: {result['execution_time']:.2f}초")
        else:
            print(f"❌ 콜백에 실행시간이 없습니다!")
            
    except Exception as e:
        print(f"❌ 바비톡 테스트 실패: {e}")
    
    print(f"\n🔄 네이버 실행시간 테스트...")
    
    try:
        # 네이버 데이터 수집 (실행시간 측정)
        start_time = time.time()
        
        result = await AsyncCollectionService.collect_naver_data(
            cafe_id="12285441",
            target_date=target_date,
            menu_id="38",
            per_page=5,  # 빠른 테스트를 위해 5개만
            naver_cookies="",
            callback_url=test_callback_url
        )
        
        end_time = time.time()
        actual_elapsed = end_time - start_time
        
        print(f"✅ 네이버 수집 완료!")
        print(f"📊 결과: {result}")
        print(f"⏱️  실제 소요시간: {actual_elapsed:.2f}초")
        
        # 콜백에 포함된 실행시간 확인
        if "execution_time" in result:
            print(f"✅ 콜백 실행시간: {result['execution_time']:.2f}초")
        else:
            print(f"❌ 콜백에 실행시간이 없습니다!")
            
    except Exception as e:
        print(f"❌ 네이버 테스트 실패: {e}")
    
    print(f"\n🎉 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_execution_time())
