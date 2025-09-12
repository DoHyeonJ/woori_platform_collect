#!/usr/bin/env python3
"""
간단한 API 테스트 스크립트
"""

import asyncio
import aiohttp
import json

async def test_simple_api():
    """간단한 API 테스트"""
    url = "https://www.gangnamunni.com/api/solar/search/document"
    params = {
        "start": 0,
        "length": 5,
        "sort": "createTime",
        "categoryIds": 1
    }
    
    # 다양한 헤더 조합 시도
    header_combinations = [
        # 1. 기본 헤더
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
        # 2. Referer 추가
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.gangnamunni.com/",
        },
        # 3. 더 많은 헤더
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Referer": "https://www.gangnamunni.com/",
            "Origin": "https://www.gangnamunni.com",
        },
        # 4. 기존 API와 동일한 헤더
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Authorization": "a70ba5dec9424aeb99e956a19cba87a3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    ]
    
    for i, headers in enumerate(header_combinations):
        print(f"\n🧪 헤더 조합 {i+1} 테스트:")
        print(f"   헤더: {headers}")
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params) as response:
                    print(f"   📊 HTTP 상태: {response.status}")
                    print(f"   📋 응답 헤더: {dict(response.headers)}")
                    
                    if response.status == 200:
                        json_data = await response.json()
                        print(f"   ✅ 성공!")
                        print(f"   📋 응답 데이터: {json.dumps(json_data, ensure_ascii=False, indent=2)[:500]}...")
                        return json_data
                    else:
                        text = await response.text()
                        print(f"   ❌ 실패: {response.status} - {response.reason}")
                        print(f"   📋 응답 내용: {text[:200]}...")
                        
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print(f"\n❌ 모든 헤더 조합이 실패했습니다.")
    return None

if __name__ == "__main__":
    asyncio.run(test_simple_api())
