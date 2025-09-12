#!/usr/bin/env python3
"""
쿠키 분석 스크립트
"""

def analyze_cookies():
    """쿠키 문자열을 분석하여 주요 값들을 찾습니다."""
    
    cookie_string = "_fbp=fb.1.1751322802419.438588862558612109; ab180ClientId=2db4dd16-0b3e-4faa-8903-fa2c651a7baa; _gac_UA-58727275-12=1.1752412715.Cj0KCQjwss3DBhC3ARIsALdgYxNkVLyyvXzCPkV-TeFScrniSrCr287w8vdYNZDZQC8pcj8bg6CUnhQaAmF0EALw_wcB; _gcl_aw=GCL.1752412715.Cj0KCQjwss3DBhC3ARIsALdgYxNkVLyyvXzCPkV-TeFScrniSrCr287w8vdYNZDZQC8pcj8bg6CUnhQaAmF0EALw_wcB; _gcl_gs=2.1.k1$i1752412714$u93608715; _ga_CSSV6M063P=GS2.1.s1756398823$o1$g1$t1756398910$j57$l0$h0; _ga_9PR0S0FHB6=GS2.1.s1756398824$o1$g1$t1756398910$j57$l0$h0; airbridge_user=%7B%22externalUserID%22%3A%225106188%22%2C%22attributes%22%3A%7B%22myHospitalDistrictId%22%3A%22N1107%22%2C%22country%22%3A%22KR%22%2C%22age%22%3A29%7D%7D; airbridge_migration_metadata__gangnamunni=%7B%22version%22%3A%221.10.77%22%7D; AMP_MKTG_6d6736a26b=JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRnd3dy5nb29nbGUuY29tJTJGJTIyJTJDJTIycmVmZXJyaW5nX2RvbWFpbiUyMiUzQSUyMnd3dy5nb29nbGUuY29tJTIyJTdE; _gcl_au=1.1.43307539.1751322803.1630846055.1757565523.1757566205; token=456c327614a94565b61f40f6683cda6c; hashedToken=hjxB9PmncQ1FNf7OvZp48Z; _gid=GA1.2.1799227454.1757658031; _gat_gtag_UA_58727275_12=1; AMP_6d6736a26b=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJhM2RiMjA0My05YWUwLTQ0YTAtOGEzYy03MDQ3Y2Q5Njg5ZWUlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzU3NjU4MDMwOTg0JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc1NzY1OTg5MzM3MyUyQyUyMmxhc3RFdmVudElkJTIyJTNBMjUzOSUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBNSU3RA==; _ga=GA1.1.819100200.1751322802; _ga_GXB8082VP1=GS2.1.s1757658031$o178$g1$t1757659894$j58$l0$h1423112411; cto_bundle=zyIP018lMkJFYUp5eGd2QWQ0dXBGaVlWbTNLVjVmU0pMNE8yYnNHN3BFMXJMRE1MUHVxUDF1aEl3OElycVRIVUpkUXNPS0M1Rm4lMkJGaUpqUXdzSGc5JTJCJTJCeEFZOXJaV1VoMnFxcG9IS2NmRlhlMGhCYkZNMUhTeXlPOUJtMSUyRlptdG1kMjAwMVVkY1VVWFNENiUyQnFGUkhGajhaeDhweWZ4d1RySDA2JTJCOFhEV2FPZXhpWG91NE9kMXVqSnVWNjA4WmRaNnNvJTJCTUVRNGRvQU9oa1FNbEdLTyUyRkR6dkozNGlma2JaTGo4TkRuSTBlaUZkb1clMkJlc1h6SU4lMkIzTFVESiUyQnZ2UW02SDFiS2NjNXBVeW1RZ2Jkc0xrcjhtVElMMWNqMUJ1emViWHZjYVBpVzNuVEtQMW83UU9UOXdjV2x1Uk1QZTFNS21BZE9veQ; airbridge_touchpoint=%7B%22channel%22%3A%22www.google.com%22%2C%22parameter%22%3A%7B%7D%2C%22generationType%22%3A1224%2C%22url%22%3A%22https%3A//www.gangnamunni.com/community%3Fcategory%3Dfree_talk%22%2C%22timestamp%22%3A1757659894917%7D; airbridge_device_alias=%7B%22amplitude_device_id%22%3A%22%22%7D; airbridge_session=%7B%22id%22%3A%226ec52060-abb1-4c45-a4f5-0fef70f71ca8%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1757658032746%2C%22end%22%3A1757659894931%7D; _dd_s=rum=0&expire=1757660796209"
    
    # 쿠키를 파싱
    cookies = {}
    for cookie in cookie_string.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookies[key] = value
    
    print("🍪 쿠키 분석 결과")
    print("=" * 60)
    print(f"총 쿠키 개수: {len(cookies)}개")
    print()
    
    # 주요 쿠키들 분류
    categories = {
        "인증 관련": [],
        "추적/분석": [],
        "세션 관련": [],
        "기타": []
    }
    
    for key, value in cookies.items():
        if key in ['token', 'hashedToken']:
            categories["인증 관련"].append((key, value))
        elif key.startswith(('_ga', '_gcl', '_fbp', '_gid', 'airbridge')):
            categories["추적/분석"].append((key, value))
        elif key.startswith(('AMP_', 'cto_bundle', '_dd_s')):
            categories["세션 관련"].append((key, value))
        else:
            categories["기타"].append((key, value))
    
    # 각 카테고리별 출력
    for category, items in categories.items():
        if items:
            print(f"📂 {category} ({len(items)}개)")
            print("-" * 40)
            for key, value in items:
                if len(value) > 50:
                    display_value = value[:50] + "..."
                else:
                    display_value = value
                print(f"   {key}: {display_value}")
            print()
    
    # 주요 인증 쿠키 강조
    print("🔑 주요 인증 쿠키 (API 접근에 필수)")
    print("=" * 60)
    if 'token' in cookies:
        print(f"   token: {cookies['token']}")
    if 'hashedToken' in cookies:
        print(f"   hashedToken: {cookies['hashedToken']}")
    
    print()
    print("💡 분석 결과:")
    print("   - token: 강남언니 API 인증에 사용되는 주요 토큰")
    print("   - hashedToken: 토큰의 해시된 버전 (보안용)")
    print("   - 나머지는 주로 Google Analytics, Facebook Pixel 등의 추적용 쿠키")
    
    return cookies

if __name__ == "__main__":
    analyze_cookies()
