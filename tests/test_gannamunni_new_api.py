#!/usr/bin/env python3
"""
강남언니 새로운 API 테스트 스크립트
새로운 solar API 엔드포인트를 사용하여 데이터 수집을 테스트합니다.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import List, Dict, Optional

class GangnamUnniNewAPITest:
    def __init__(self):
        self.base_url = "https://www.gangnamunni.com"
        
        # 여러 헤더 조합을 시도해보기 위한 리스트
        self.header_combinations = [
            # 기존 API 헤더
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Cookie": "token=456c327614a94565b61f40f6683cda6c;"
            },
            # Authorization 없이
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
            # Referer 추가
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Referer": "https://www.gangnamunni.com/",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
            # 간단한 헤더
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json",
            }
        ]
        
        self.headers = self.header_combinations[0]  # 기본값
        
        # 카테고리 ID 매핑
        self.category_ids = {
            "hospital_question": 11,  # 병원질문
            "surgery_question": 2,    # 시술/수술질문
            "free_chat": 1,           # 자유수다
            "review": 5,              # 발품후기
            "ask_doctor": 13,         # 의사에게 물어보세요
        }
    
    async def test_header_combinations(self, category: str = "free_chat"):
        """다양한 헤더 조합 테스트"""
        print(f"🧪 헤더 조합 테스트 - 카테고리: {category}")
        print("=" * 60)
        
        for i, headers in enumerate(self.header_combinations):
            print(f"\n📋 헤더 조합 {i+1} 테스트:")
            print(f"   - Authorization: {'있음' if 'Authorization' in headers else '없음'}")
            print(f"   - Referer: {'있음' if 'Referer' in headers else '없음'}")
            
            try:
                async with aiohttp.ClientSession(headers=headers) as session:
                    url = f"{self.base_url}/api/solar/search/document"
                    
                    category_id = self.category_ids.get(category, 1)
                    params = {
                        "start": 0,
                        "length": 5,  # 적은 수로 테스트
                        "sort": "createTime",
                        "categoryIds": category_id
                    }
                    
                    async with session.get(url, params=params) as response:
                        print(f"   📊 HTTP 상태: {response.status}")
                        
                        if response.status == 200:
                            json_data = await response.json()
                            print(f"   ✅ 성공! reason: {json_data.get('reason')}")
                            print(f"   📋 데이터 개수: {len(json_data.get('data', []))}")
                            
                            # 성공한 헤더를 기본값으로 설정
                            self.headers = headers
                            print(f"   🎉 성공한 헤더를 기본값으로 설정했습니다!")
                            return True
                        else:
                            print(f"   ❌ 실패: {response.status} - {response.reason}")
                            
            except Exception as e:
                print(f"   ❌ 오류: {e}")
        
        print(f"\n❌ 모든 헤더 조합이 실패했습니다.")
        return False
    
    async def test_single_page(self, category: str = "free_chat", page: int = 1):
        """단일 페이지 테스트"""
        print(f"🧪 단일 페이지 테스트 - 카테고리: {category}, 페이지: {page}")
        print("=" * 60)
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                url = f"{self.base_url}/api/solar/search/document"
                
                start = (page - 1) * 20
                category_id = self.category_ids.get(category, 1)
                
                params = {
                    "start": start,
                    "length": 20,
                    "sort": "createTime",
                    "categoryIds": category_id
                }
                
                print(f"📡 요청 URL: {url}")
                print(f"📋 요청 파라미터: {params}")
                
                async with session.get(url, params=params) as response:
                    print(f"📊 HTTP 상태: {response.status}")
                    
                    if response.status != 200:
                        print(f"❌ HTTP 오류: {response.status} - {response.reason}")
                        return None
                    
                    json_data = await response.json()
                    
                    print(f"✅ 응답 성공")
                    print(f"📋 응답 구조:")
                    print(f"   - reason: {json_data.get('reason')}")
                    print(f"   - succeeded: {json_data.get('succeeded')}")
                    print(f"   - recordsTotal: {json_data.get('recordsTotal')}")
                    print(f"   - recordsFiltered: {json_data.get('recordsFiltered')}")
                    print(f"   - data 개수: {len(json_data.get('data', []))}")
                    
                    # 데이터 샘플 출력
                    data = json_data.get('data', [])
                    if data:
                        print(f"\n📝 첫 번째 게시글 샘플:")
                        first_item = data[0]
                        print(f"   - ID: {first_item.get('id')}")
                        print(f"   - 작성자: {first_item.get('writerNickName')}")
                        print(f"   - 카테고리: {first_item.get('categoryName')}")
                        print(f"   - 내용: {first_item.get('contents', '')[:50]}...")
                        print(f"   - 작성시간: {first_item.get('createTime')}")
                        print(f"   - 댓글수: {first_item.get('commentCount')}")
                        print(f"   - 조회수: {first_item.get('viewCount')}")
                    
                    return json_data
                    
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
            import traceback
            print(f"📋 상세 오류: {traceback.format_exc()}")
            return None
    
    async def test_multiple_pages(self, category: str = "free_chat", max_pages: int = 3):
        """여러 페이지 테스트"""
        print(f"\n🧪 여러 페이지 테스트 - 카테고리: {category}, 최대 페이지: {max_pages}")
        print("=" * 60)
        
        all_data = []
        
        for page in range(1, max_pages + 1):
            print(f"\n📄 페이지 {page} 수집 중...")
            
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    url = f"{self.base_url}/api/solar/search/document"
                    
                    start = (page - 1) * 20
                    category_id = self.category_ids.get(category, 1)
                    
                    params = {
                        "start": start,
                        "length": 20,
                        "sort": "createTime",
                        "categoryIds": category_id
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status != 200:
                            print(f"❌ 페이지 {page} HTTP 오류: {response.status}")
                            break
                        
                        json_data = await response.json()
                        
                        if json_data.get('reason') != 'SUCCESS':
                            print(f"❌ 페이지 {page} API 오류: {json_data.get('reason')}")
                            break
                        
                        data = json_data.get('data', [])
                        if not data:
                            print(f"📭 페이지 {page}에 데이터가 없습니다.")
                            break
                        
                        all_data.extend(data)
                        print(f"✅ 페이지 {page}: {len(data)}개 게시글 수집")
                        
                        # 페이지 간 딜레이
                        await asyncio.sleep(1)
                        
            except Exception as e:
                print(f"❌ 페이지 {page} 수집 실패: {e}")
                break
        
        print(f"\n📊 전체 수집 결과:")
        print(f"   - 총 수집된 게시글: {len(all_data)}개")
        
        # 시간대별 분석
        if all_data:
            print(f"\n⏰ 시간대별 분석:")
            time_analysis = {}
            for item in all_data:
                create_time = item.get('createTime', 0)
                if create_time:
                    # 타임스탬프를 날짜로 변환
                    from datetime import datetime
                    dt = datetime.fromtimestamp(create_time / 1000)
                    date_str = dt.strftime("%Y-%m-%d")
                    time_analysis[date_str] = time_analysis.get(date_str, 0) + 1
            
            for date_str, count in sorted(time_analysis.items()):
                print(f"   - {date_str}: {count}개")
        
        return all_data
    
    async def test_date_filtering(self, target_date: str = "2025-09-12", category: str = "free_chat"):
        """날짜 필터링 테스트"""
        print(f"\n🧪 날짜 필터링 테스트 - 대상 날짜: {target_date}, 카테고리: {category}")
        print("=" * 60)
        
        try:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            print(f"❌ 잘못된 날짜 형식: {target_date}")
            return []
        
        all_articles = []
        page = 1
        max_pages = 10
        consecutive_empty_pages = 0
        max_consecutive_empty = 3
        
        while page <= max_pages and consecutive_empty_pages < max_consecutive_empty:
            print(f"\n📄 페이지 {page} 수집 중...")
            
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    url = f"{self.base_url}/api/solar/search/document"
                    
                    start = (page - 1) * 20
                    category_id = self.category_ids.get(category, 1)
                    
                    params = {
                        "start": start,
                        "length": 20,
                        "sort": "createTime",
                        "categoryIds": category_id
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status != 200:
                            print(f"❌ 페이지 {page} HTTP 오류: {response.status}")
                            break
                        
                        json_data = await response.json()
                        
                        if json_data.get('reason') != 'SUCCESS':
                            print(f"❌ 페이지 {page} API 오류: {json_data.get('reason')}")
                            break
                        
                        data = json_data.get('data', [])
                        if not data:
                            consecutive_empty_pages += 1
                            print(f"📭 페이지 {page}에 데이터가 없습니다. (연속 빈 페이지: {consecutive_empty_pages})")
                            page += 1
                            continue
                        
                        # 날짜 필터링
                        target_date_articles = []
                        older_articles_found = False
                        
                        for item in data:
                            try:
                                create_time = item.get('createTime', 0)
                                if create_time:
                                    dt = datetime.fromtimestamp(create_time / 1000)
                                    article_date = dt.date()
                                    
                                    if article_date == target_date_obj:
                                        target_date_articles.append(item)
                                        print(f"   ✅ {target_date} 게시글 발견: ID {item.get('id')}")
                                    elif article_date < target_date_obj:
                                        older_articles_found = True
                                        print(f"   📅 과거 게시글 발견: {article_date} (ID: {item.get('id')})")
                                        break
                                    else:
                                        print(f"   🔮 미래 게시글: {article_date} (ID: {item.get('id')})")
                                        
                            except Exception as e:
                                print(f"   ⚠️  날짜 파싱 오류: {e}")
                                continue
                        
                        if target_date_articles:
                            all_articles.extend(target_date_articles)
                            print(f"   📊 페이지 {page}에서 {len(target_date_articles)}개 {target_date} 게시글 수집")
                        
                        # 더 오래된 게시글이 발견되면 수집 중단
                        if older_articles_found:
                            print(f"   🛑 과거 게시글 발견으로 수집 중단")
                            break
                        
                        consecutive_empty_pages = 0  # 데이터가 있으면 리셋
                        page += 1
                        await asyncio.sleep(1)
                        
            except Exception as e:
                print(f"❌ 페이지 {page} 수집 실패: {e}")
                consecutive_empty_pages += 1
                page += 1
        
        print(f"\n📊 날짜 필터링 결과:")
        print(f"   - {target_date} 날짜 게시글: {len(all_articles)}개")
        
        if all_articles:
            print(f"\n📝 수집된 게시글 샘플:")
            for i, article in enumerate(all_articles[:3]):  # 처음 3개만 출력
                create_time = article.get('createTime', 0)
                dt = datetime.fromtimestamp(create_time / 1000)
                print(f"   {i+1}. ID: {article.get('id')}, 작성자: {article.get('writerNickName')}, 시간: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return all_articles
    
    async def test_all_categories(self):
        """모든 카테고리 테스트"""
        print(f"\n🧪 모든 카테고리 테스트")
        print("=" * 60)
        
        results = {}
        
        for category_name, category_id in self.category_ids.items():
            print(f"\n📂 {category_name} 카테고리 테스트 (ID: {category_id})")
            
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    url = f"{self.base_url}/api/solar/search/document"
                    
                    params = {
                        "start": 0,
                        "length": 20,
                        "sort": "createTime",
                        "categoryIds": category_id
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            json_data = await response.json()
                            if json_data.get('reason') == 'SUCCESS':
                                data_count = len(json_data.get('data', []))
                                total_count = json_data.get('recordsTotal', 0)
                                print(f"   ✅ 성공: {data_count}개 게시글 (전체: {total_count}개)")
                                results[category_name] = {
                                    'success': True,
                                    'data_count': data_count,
                                    'total_count': total_count
                                }
                            else:
                                print(f"   ❌ API 오류: {json_data.get('reason')}")
                                results[category_name] = {'success': False, 'error': json_data.get('reason')}
                        else:
                            print(f"   ❌ HTTP 오류: {response.status}")
                            results[category_name] = {'success': False, 'error': f'HTTP {response.status}'}
                        
                        await asyncio.sleep(1)  # 카테고리 간 딜레이
                        
            except Exception as e:
                print(f"   ❌ 테스트 실패: {e}")
                results[category_name] = {'success': False, 'error': str(e)}
        
        print(f"\n📊 전체 카테고리 테스트 결과:")
        for category, result in results.items():
            if result['success']:
                print(f"   ✅ {category}: {result['data_count']}개 (전체: {result['total_count']}개)")
            else:
                print(f"   ❌ {category}: {result['error']}")
        
        return results

async def main():
    """메인 테스트 함수"""
    print("🚀 강남언니 새로운 API 테스트 시작")
    print("=" * 80)
    
    tester = GangnamUnniNewAPITest()
    
    try:
        # 0. 헤더 조합 테스트 (먼저 실행)
        header_success = await tester.test_header_combinations("free_chat")
        
        if not header_success:
            print("❌ 유효한 헤더를 찾지 못했습니다. 테스트를 중단합니다.")
            return
        
        # 1. 단일 페이지 테스트
        await tester.test_single_page("free_chat", 1)
        
        # 2. 여러 페이지 테스트
        await tester.test_multiple_pages("free_chat", 3)
        
        # 3. 날짜 필터링 테스트
        await tester.test_date_filtering("2025-09-12", "free_chat")
        
        # 4. 모든 카테고리 테스트
        await tester.test_all_categories()
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print("\n" + "=" * 80)
    print("🏁 강남언니 새로운 API 테스트 완료")

if __name__ == "__main__":
    asyncio.run(main())
