#!/usr/bin/env python3
"""
최소 쿠키 테스트 스크립트
"""

import asyncio
import aiohttp

async def test_minimal_cookies():
    """최소한의 쿠키로 API 테스트"""
    
    url = "https://www.gangnamunni.com/api/solar/search/document"
    params = {
        "start": 0,
        "length": 5,
        "sort": "createTime",
        "categoryIds": 1
    }
    
    headers = {
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
    
    # 테스트할 쿠키 조합들
    cookie_tests = [
        # 1. 쿠키 없음
        {
            "name": "쿠키 없음",
            "cookies": {}
        },
        # 2. token만
        {
            "name": "token만",
            "cookies": {"token": "456c327614a94565b61f40f6683cda6c"}
        },
        # 3. hashedToken만
        {
            "name": "hashedToken만",
            "cookies": {"hashedToken": "hjxB9PmncQ1FNf7OvZp48Z"}
        },
        # 4. token + hashedToken
        {
            "name": "token + hashedToken",
            "cookies": {
                "token": "456c327614a94565b61f40f6683cda6c",
                "hashedToken": "hjxB9PmncQ1FNf7OvZp48Z"
            }
        },
        # 5. 전체 쿠키
        {
            "name": "전체 쿠키",
            "cookies": {
                "_fbp": "fb.1.1751322802419.438588862558612109",
                "ab180ClientId": "2db4dd16-0b3e-4faa-8903-fa2c651a7baa",
                "_gac_UA-58727275-12": "1.1752412715.Cj0KCQjwss3DBhC3ARIsALdgYxNkVLyyvXzCPkV-TeFScrniSrCr287w8vdYNZDZQC8pcj8bg6CUnhQaAmF0EALw_wcB",
                "_gcl_aw": "GCL.1752412715.Cj0KCQjwss3DBhC3ARIsALdgYxNkVLyyvXzCPkV-TeFScrniSrCr287w8vdYNZDZQC8pcj8bg6CUnhQaAmF0EALw_wcB",
                "_gcl_gs": "2.1.k1$i1752412714$u93608715",
                "_ga_CSSV6M063P": "GS2.1.s1756398823$o1$g1$t1756398910$j57$l0$h0",
                "_ga_9PR0S0FHB6": "GS2.1.s1756398824$o1$g1$t1756398910$j57$l0$h0",
                "airbridge_user": "%7B%22externalUserID%22%3A%225106188%22%2C%22attributes%22%3A%7B%22myHospitalDistrictId%22%3A%22N1107%22%2C%22country%22%3A%22KR%22%2C%22age%22%3A29%7D%7D",
                "airbridge_migration_metadata__gangnamunni": "%7B%22version%22%3A%221.10.77%22%7D",
                "AMP_MKTG_6d6736a26b": "JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRnd3dy5nb29nbGUuY29tJTJGJTIyJTJDJTIycmVmZXJyaW5nX2RvbWFpbiUyMiUzQSUyMnd3dy5nb29nbGUuY29tJTIyJTdE",
                "_gcl_au": "1.1.43307539.1751322803.1630846055.1757565523.1757566205",
                "token": "456c327614a94565b61f40f6683cda6c",
                "hashedToken": "hjxB9PmncQ1FNf7OvZp48Z",
                "_gid": "GA1.2.1799227454.1757658031",
                "_gat_gtag_UA_58727275_12": "1",
                "AMP_6d6736a26b": "JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJhM2RiMjA0My05YWUwLTQ0YTAtOGEzYy03MDQ3Y2Q5Njg5ZWUlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzU3NjU4MDMwOTg0JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc1NzY1OTg5MzM3MyUyQyUyMmxhc3RFdmVudElkJTIyJTNBMjUzOSUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBNSU3RA==",
                "_ga": "GA1.1.819100200.1751322802",
                "_ga_GXB8082VP1": "GS2.1.s1757658031$o178$g1$t1757659894$j58$l0$h1423112411",
                "cto_bundle": "zyIP018lMkJFYUp5eGd2QWQ0dXBGaVlWbTNLVjVmU0pMNE8yYnNHN3BFMXJMRE1MUHVxUDF1aEl3OElycVRIVUpkUXNPS0M1Rm4lMkJGaUpqUXdzSGc5JTJCJTJCeEFZOXJaV1VoMnFxcG9IS2NmRlhlMGhCYkZNMUhTeXlPOUJtMSUyRlptdG1kMjAwMVVkY1VVWFNENiUyQnFGUkhGajhaeDhweWZ4d1RySDA2JTJCOFhEV2FPZXhpWG91NE9kMXVqSnVWNjA4WmRaNnNvJTJCTUVRNGRvQU9oa1FNbEdLTyUyRkR6dkozNGlma2JaTGo4TkRuSTBlaUZkb1clMkJlc1h6SU4lMkIzTFVESiUyQnZ2UW02SDFiS2NjNXBVeW1RZ2Jkc0xrcjhtVElMMWNqMUJ1emViWHZjYVBpVzNuVEtQMW83UU9UOXdjV2x1Uk1QZTFNS21BZE9veQ",
                "airbridge_touchpoint": "%7B%22channel%22%3A%22www.google.com%22%2C%22parameter%22%3A%7B%7D%2C%22generationType%22%3A1224%2C%22url%22%3A%22https%3A//www.gangnamunni.com/community%3Fcategory%3Dfree_talk%22%2C%22timestamp%22%3A1757659894917%7D",
                "airbridge_device_alias": "%7B%22amplitude_device_id%22%3A%22%22%7D",
                "airbridge_session": "%7B%22id%22%3A%226ec52060-abb1-4c45-a4f5-0fef70f71ca8%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1757658032746%2C%22end%22%3A1757659894931%7D",
                "_dd_s": "rum=0&expire=1757660796209"
            }
        }
    ]
    
    print("🧪 최소 쿠키 테스트")
    print("=" * 60)
    
    for test in cookie_tests:
        print(f"\n📋 {test['name']} 테스트")
        print("-" * 40)
        
        try:
            # 쿠키를 Cookie 헤더로 변환
            cookie_header = "; ".join([f"{k}={v}" for k, v in test['cookies'].items()])
            test_headers = headers.copy()
            if cookie_header:
                test_headers["Cookie"] = cookie_header
            
            async with aiohttp.ClientSession(headers=test_headers) as session:
                async with session.get(url, params=params) as response:
                    print(f"   📊 HTTP 상태: {response.status}")
                    
                    if response.status == 200:
                        json_data = await response.json()
                        if json_data.get("reason") == "SUCCESS":
                            data_count = len(json_data.get("data", []))
                            print(f"   ✅ 성공! 데이터: {data_count}개")
                        else:
                            print(f"   ❌ API 오류: {json_data.get('reason')}")
                    else:
                        text = await response.text()
                        print(f"   ❌ 실패: {response.status} - {response.reason}")
                        if "401" in str(response.status):
                            print(f"   🔑 인증 실패 - 쿠키가 필요합니다")
                        elif "403" in str(response.status):
                            print(f"   🚫 접근 거부 - 권한이 없습니다")
                        else:
                            print(f"   📋 응답: {text[:100]}...")
                            
        except Exception as e:
            print(f"   ❌ 오류: {e}")
        
        await asyncio.sleep(1)  # 요청 간 딜레이
    
    print(f"\n💡 결론:")
    print(f"   - API 접근에는 특정 쿠키가 필수입니다")
    print(f"   - 가장 중요한 쿠키를 찾아보세요!")

if __name__ == "__main__":
    asyncio.run(test_minimal_cookies())
