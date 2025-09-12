import asyncio
import aiohttp
import json
import sys
import os
from typing import Dict, Any, Optional

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import LoggedClass
from platforms.babitalk import BabitalkAPI


class BabitalkAPITester(LoggedClass):
    """바비톡 API 테스트 클래스"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://web-api.babitalk.com/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        self.api = BabitalkAPI()
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            },
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def test_event_ask_memos_recommendation(self) -> Dict[str, Any]:
        """추천 정렬로 이벤트 질문 메모 API 테스트"""
        url = f"{self.base_url}/event-ask-memos"
        params = {
            'limit': 24,
            'search_after': 0,
            'category_type': 305,
            'sort': 'recommendation'
        }
        
        self.logger.info(f"API 호출: {url}")
        self.logger.info(f"파라미터: {params}")
        
        try:
            async with self.session.get(url, params=params) as response:
                status_code = response.status
                response_text = await response.text()
                
                self.logger.info(f"응답 상태 코드: {status_code}")
                
                if status_code == 200:
                    try:
                        data = await response.json()
                        self.logger.info(f"응답 데이터 크기: {len(response_text)} bytes")
                        self.logger.info(f"응답 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        return {
                            'success': True,
                            'status_code': status_code,
                            'data': data,
                            'response_size': len(response_text)
                        }
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON 파싱 오류: {e}")
                        return {
                            'success': False,
                            'status_code': status_code,
                            'error': f"JSON 파싱 오류: {e}",
                            'raw_response': response_text[:500]  # 처음 500자만
                        }
                else:
                    self.logger.error(f"API 호출 실패: {status_code}")
                    return {
                        'success': False,
                        'status_code': status_code,
                        'error': f"HTTP {status_code}",
                        'raw_response': response_text[:500]
                    }
                    
        except aiohttp.ClientError as e:
            self.logger.error(f"네트워크 오류: {e}")
            return {
                'success': False,
                'error': f"네트워크 오류: {e}"
            }
        except Exception as e:
            self.logger.error(f"예상치 못한 오류: {e}")
            return {
                'success': False,
                'error': f"예상치 못한 오류: {e}"
            }
    
    async def test_event_ask_memos_recent(self) -> Dict[str, Any]:
        """최신 정렬로 이벤트 질문 메모 API 테스트"""
        url = f"{self.base_url}/event-ask-memos"
        params = {
            'limit': 24,
            'category_type': 305,
            'sort': 'recent',
            'category_id': 3000,
            'search_after': 0
        }
        
        self.logger.info(f"API 호출: {url}")
        self.logger.info(f"파라미터: {params}")
        
        try:
            async with self.session.get(url, params=params) as response:
                status_code = response.status
                response_text = await response.text()
                
                self.logger.info(f"응답 상태 코드: {status_code}")
                
                if status_code == 200:
                    try:
                        data = await response.json()
                        self.logger.info(f"응답 데이터 크기: {len(response_text)} bytes")
                        self.logger.info(f"응답 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        return {
                            'success': True,
                            'status_code': status_code,
                            'data': data,
                            'response_size': len(response_text)
                        }
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON 파싱 오류: {e}")
                        return {
                            'success': False,
                            'status_code': status_code,
                            'error': f"JSON 파싱 오류: {e}",
                            'raw_response': response_text[:500]
                        }
                else:
                    self.logger.error(f"API 호출 실패: {status_code}")
                    return {
                        'success': False,
                        'status_code': status_code,
                        'error': f"HTTP {status_code}",
                        'raw_response': response_text[:500]
                    }
                    
        except aiohttp.ClientError as e:
            self.logger.error(f"네트워크 오류: {e}")
            return {
                'success': False,
                'error': f"네트워크 오류: {e}"
            }
        except Exception as e:
            self.logger.error(f"예상치 못한 오류: {e}")
            return {
                'success': False,
                'error': f"예상치 못한 오류: {e}"
            }
    
    async def test_event_ask_memos_unlimited(self) -> Dict[str, Any]:
        """전체 데이터 수집 테스트 (limit=0)"""
        url = f"{self.base_url}/event-ask-memos"
        params = {
            'limit': 0,  # 전체 데이터 수집
            'category_type': 305,
            'sort': 'recent',
            'category_id': 3000,
            'search_after': 0
        }
        
        self.logger.info(f"API 호출: {url}")
        self.logger.info(f"파라미터: {params}")
        
        try:
            async with self.session.get(url, params=params) as response:
                status_code = response.status
                response_text = await response.text()
                
                self.logger.info(f"응답 상태 코드: {status_code}")
                
                if status_code == 200:
                    try:
                        data = await response.json()
                        self.logger.info(f"응답 데이터 크기: {len(response_text)} bytes")
                        self.logger.info(f"응답 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        return {
                            'success': True,
                            'status_code': status_code,
                            'data': data,
                            'response_size': len(response_text)
                        }
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON 파싱 오류: {e}")
                        return {
                            'success': False,
                            'status_code': status_code,
                            'error': f"JSON 파싱 오류: {e}",
                            'raw_response': response_text[:500]
                        }
                else:
                    self.logger.error(f"API 호출 실패: {status_code}")
                    return {
                        'success': False,
                        'status_code': status_code,
                        'error': f"HTTP {status_code}",
                        'raw_response': response_text[:500]
                    }
                    
        except aiohttp.ClientError as e:
            self.logger.error(f"네트워크 오류: {e}")
            return {
                'success': False,
                'error': f"네트워크 오류: {e}"
            }
        except Exception as e:
            self.logger.error(f"예상치 못한 오류: {e}")
            return {
                'success': False,
                'error': f"예상치 못한 오류: {e}"
            }
    
    async def test_event_ask_memos_by_date(self) -> Dict[str, Any]:
        """날짜별 발품후기 수집 테스트"""
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            self.logger.info(f"🔄 {today} 날짜 발품후기 수집 테스트 시작")
            memos = await self.api.get_event_ask_memos_by_date(
                target_date=today,
                category_id=3000
            )
            
            self.logger.info(f"✅ 날짜별 수집 완료: {len(memos)}개")
            
            return {
                'success': True,
                'count': len(memos),
                'sample_data': {
                    'id': memos[0].id,
                    'star_score': memos[0].star_score,
                    'category': memos[0].category,
                    'region': memos[0].region,
                    'hospital_name': memos[0].hospital_name,
                    'real_price': memos[0].real_price,
                    'text': memos[0].text[:100] + '...' if len(memos[0].text) > 100 else memos[0].text
                } if memos else None
            }
        except Exception as e:
            self.logger.error(f"❌ 테스트 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def print_result(self, test_name: str, result: Dict[str, Any]):
        """테스트 결과 출력"""
        print(f"\n{'='*50}")
        print(f"테스트: {test_name}")
        print(f"{'='*50}")
        
        if result['success']:
            print(f"✅ 성공!")
            if 'status_code' in result:
                print(f"상태 코드: {result['status_code']}")
            if 'response_size' in result:
                print(f"응답 크기: {result['response_size']} bytes")
            if 'count' in result:
                print(f"수집된 데이터 수: {result['count']}")
            
            if 'data' in result and isinstance(result['data'], dict):
                print(f"응답 데이터 키: {list(result['data'].keys())}")
                
                # 데이터 구조 분석
                if 'data' in result['data'] and isinstance(result['data']['data'], list):
                    print(f"데이터 항목 수: {len(result['data']['data'])}")
                    if result['data']['data']:
                        print(f"첫 번째 항목 키: {list(result['data']['data'][0].keys()) if isinstance(result['data']['data'][0], dict) else 'Not a dict'}")
            
            if 'sample_data' in result and result['sample_data']:
                print(f"샘플 데이터 키: {list(result['sample_data'].keys())}")
        else:
            print(f"❌ 실패!")
            print(f"오류: {result.get('error', 'Unknown error')}")
            if 'raw_response' in result:
                print(f"원본 응답 (일부): {result['raw_response']}")


class BabitalkPlatformTester(LoggedClass):
    """바비톡 플랫폼 클래스 테스트"""
    
    def __init__(self):
        super().__init__()
        self.api = BabitalkAPI()
    
    async def test_get_event_ask_memos_with_limit(self) -> Dict[str, Any]:
        """limit=24로 발품후기 수집 테스트"""
        try:
            self.logger.info("🔄 limit=24로 발품후기 수집 테스트 시작")
            memos, pagination = await self.api.get_event_ask_memos(
                category_id=3000,
                limit=24,
                sort="recent"
            )
            
            self.logger.info(f"✅ 수집 완료: {len(memos)}개")
            self.logger.info(f"📄 페이지네이션: has_next={pagination.has_next}, search_after={pagination.search_after}")
            
            return {
                'success': True,
                'count': len(memos),
                'pagination': {
                    'has_next': pagination.has_next,
                    'search_after': pagination.search_after
                },
                'sample_data': {
                    'id': memos[0].id,
                    'star_score': memos[0].star_score,
                    'category': memos[0].category,
                    'region': memos[0].region,
                    'hospital_name': memos[0].hospital_name,
                    'real_price': memos[0].real_price,
                    'text': memos[0].text[:100] + '...' if len(memos[0].text) > 100 else memos[0].text
                } if memos else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ 테스트 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def test_get_event_ask_memos_by_date(self) -> Dict[str, Any]:
        """날짜별 발품후기 수집 테스트"""
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            self.logger.info(f"🔄 {today} 날짜 발품후기 수집 테스트 시작")
            memos = await self.api.get_event_ask_memos_by_date(
                target_date=today,
                category_id=3000
            )
            
            self.logger.info(f"✅ 날짜별 수집 완료: {len(memos)}개")
            
            return {
                'success': True,
                'count': len(memos),
                'sample_data': {
                    'id': memos[0].id,
                    'star_score': memos[0].star_score,
                    'category': memos[0].category,
                    'region': memos[0].region,
                    'hospital_name': memos[0].hospital_name,
                    'real_price': memos[0].real_price,
                    'text': memos[0].text[:100] + '...' if len(memos[0].text) > 100 else memos[0].text
                } if memos else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ 테스트 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def test_get_event_ask_memos_by_date(self) -> Dict[str, Any]:
        """날짜별 발품후기 수집 테스트"""
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            self.logger.info(f"🔄 {today} 날짜 발품후기 수집 테스트 시작")
            memos = await self.api.get_event_ask_memos_by_date(
                target_date=today,
                category_id=3000
            )
            
            self.logger.info(f"✅ 날짜별 수집 완료: {len(memos)}개")
            
            return {
                'success': True,
                'count': len(memos),
                'sample_data': memos[0].__dict__ if memos else None
            }
        except Exception as e:
            self.logger.error(f"❌ 테스트 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def print_result(self, test_name: str, result: Dict[str, Any]):
        """테스트 결과 출력"""
        print(f"\n{'='*50}")
        print(f"테스트: {test_name}")
        print(f"{'='*50}")
        
        if result['success']:
            print(f"✅ 성공!")
            print(f"수집된 데이터 수: {result['count']}")
            if 'pagination' in result:
                print(f"페이지네이션: {result['pagination']}")
            if result.get('sample_data'):
                print(f"샘플 데이터 키: {list(result['sample_data'].keys())}")
        else:
            print(f"❌ 실패!")
            print(f"오류: {result.get('error', 'Unknown error')}")


async def main():
    """메인 테스트 함수"""
    print("바비톡 API 테스트 시작")
    print("="*50)
    
    # 1. 직접 API 호출 테스트
    print("\n🔧 직접 API 호출 테스트")
    print("-" * 30)
    async with BabitalkAPITester() as tester:
        # 테스트 1: 최신 정렬 API (limit=24)
        result1 = await tester.test_event_ask_memos_recent()
        tester.print_result("이벤트 질문 메모 (최신 정렬, limit=24)", result1)
        
        # 테스트 2: 날짜별 데이터 수집 API
        result2 = await tester.test_event_ask_memos_by_date()
        tester.print_result("이벤트 질문 메모 (날짜별 수집)", result2)
        
        # 성공한 테스트의 데이터 저장
        if result1['success']:
            with open('babitalk_recent_response.json', 'w', encoding='utf-8') as f:
                json.dump(result1['data'], f, ensure_ascii=False, indent=2)
            print("최신 정렬 응답 데이터가 'babitalk_recent_response.json'에 저장되었습니다.")
        
        if result2['success']:
            with open('babitalk_date_response.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'count': result2['count'],
                    'sample_data': result2['sample_data']
                }, f, ensure_ascii=False, indent=2)
            print("날짜별 수집 응답이 'babitalk_date_response.json'에 저장되었습니다.")
    
    # 2. 플랫폼 클래스 테스트
    print("\n🏗️ 바비톡 플랫폼 클래스 테스트")
    print("-" * 30)
    platform_tester = BabitalkPlatformTester()
    
    # 테스트 3: 플랫폼 클래스로 limit=24 테스트
    result3 = await platform_tester.test_get_event_ask_memos_with_limit()
    platform_tester.print_result("플랫폼 클래스 - 발품후기 수집 (limit=24)", result3)
    
    # 테스트 4: 플랫폼 클래스로 limit=0 테스트
    result4 = await platform_tester.test_get_event_ask_memos_by_date()
    platform_tester.print_result("플랫폼 클래스 - 발품후기 날짜별 수집", result4)
    
    # 전체 결과 요약
    print(f"\n{'='*60}")
    print("전체 테스트 결과 요약")
    print(f"{'='*60}")
    print(f"직접 API - 최신 정렬 (limit=24): {'✅ 성공' if result1['success'] else '❌ 실패'}")
    print(f"직접 API - 날짜별 수집: {'✅ 성공' if result2['success'] else '❌ 실패'}")
    print(f"플랫폼 클래스 - limit=24: {'✅ 성공' if result3['success'] else '❌ 실패'}")
    print(f"플랫폼 클래스 - 날짜별 수집: {'✅ 성공' if result4['success'] else '❌ 실패'}")
    
    # 성공한 플랫폼 클래스 테스트의 데이터 저장
    if result3['success']:
        with open('babitalk_platform_limit24.json', 'w', encoding='utf-8') as f:
            json.dump({
                'count': result3['count'],
                'pagination': result3['pagination'],
                'sample_data': result3['sample_data']
            }, f, ensure_ascii=False, indent=2)
        print("플랫폼 클래스 limit=24 결과가 'babitalk_platform_limit24.json'에 저장되었습니다.")
    
    if result4['success']:
        with open('babitalk_platform_date.json', 'w', encoding='utf-8') as f:
            json.dump({
                'count': result4['count'],
                'sample_data': result4['sample_data']
            }, f, ensure_ascii=False, indent=2)
        print("플랫폼 클래스 날짜별 수집 결과가 'babitalk_platform_date.json'에 저장되었습니다.")


if __name__ == "__main__":
    asyncio.run(main())
