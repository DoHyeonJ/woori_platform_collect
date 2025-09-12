#!/usr/bin/env python3
"""
쿠키를 사용한 API 테스트 스크립트
"""

import asyncio
import aiohttp
import json

async def test_with_cookies():
    """쿠키를 사용한 API 테스트"""
    
    # 1단계: 메인 페이지에 접속해서 쿠키 얻기
    print("🍪 1단계: 메인 페이지 접속하여 쿠키 획득")
    print("=" * 50)
    
    main_url = "https://www.gangnamunni.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    cookies = None
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(main_url) as response:
                print(f"📊 메인 페이지 HTTP 상태: {response.status}")
                print(f"📋 응답 헤더: {dict(response.headers)}")
                
                if response.status == 200:
                    cookies = session.cookie_jar
                    print(f"✅ 쿠키 획득 성공!")
                    print(f"🍪 쿠키 개수: {len(cookies)}")
                    
                    # 쿠키 내용 출력
                    for cookie in cookies:
                        print(f"   - {cookie.key}: {cookie.value}")
                else:
                    print(f"❌ 메인 페이지 접속 실패: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ 메인 페이지 접속 오류: {e}")
        return None
    
    # 2단계: 획득한 쿠키로 API 호출
    print(f"\n🚀 2단계: 획득한 쿠키로 API 호출")
    print("=" * 50)
    
    api_url = "https://www.gangnamunni.com/api/solar/search/document"
    params = {
        "start": 0,
        "length": 5,
        "sort": "createTime",
        "categoryIds": 1
    }
    
    api_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.gangnamunni.com/",
        "Origin": "https://www.gangnamunni.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    
    try:
        async with aiohttp.ClientSession(headers=api_headers, cookie_jar=cookies) as session:
            async with session.get(api_url, params=params) as response:
                print(f"📊 API HTTP 상태: {response.status}")
                print(f"📋 응답 헤더: {dict(response.headers)}")
                
                if response.status == 200:
                    json_data = await response.json()
                    print(f"✅ API 호출 성공!")
                    print(f"📋 응답 데이터:")
                    print(json.dumps(json_data, ensure_ascii=False, indent=2)[:1000] + "...")
                    return json_data
                else:
                    text = await response.text()
                    print(f"❌ API 호출 실패: {response.status} - {response.reason}")
                    print(f"📋 응답 내용: {text[:500]}...")
                    return None
                    
    except Exception as e:
        print(f"❌ API 호출 오류: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_with_cookies())
