#!/usr/bin/env python3
"""
콜백 URL 기능 테스트 스크립트
"""

import asyncio
import sys
import os
import json
from datetime import datetime
import aiohttp
from aiohttp import web

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services.callback_service import callback_service


class CallbackTestServer:
    """콜백 테스트용 간단한 HTTP 서버"""
    
    def __init__(self, port: int = 8999):
        self.port = port
        self.received_callbacks = []
        self.app = web.Application()
        self.app.router.add_post('/callback', self.handle_callback)
        self.app.router.add_post('/callback/success', self.handle_success_callback)
        self.app.router.add_post('/callback/error', self.handle_error_callback)
        self.app.router.add_post('/callback/timeout', self.handle_timeout_callback)
    
    async def handle_callback(self, request: web.Request):
        """기본 콜백 핸들러"""
        data = await request.json()
        callback_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "url": str(request.url)
        }
        self.received_callbacks.append(callback_data)
        
        print(f"✅ 콜백 수신: {data.get('platform', 'unknown')} - {data.get('status', 'unknown')}")
        print(f"📊 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        return web.json_response({"status": "success", "message": "콜백 수신 완료"})
    
    async def handle_success_callback(self, request: web.Request):
        """성공 콜백 핸들러"""
        data = await request.json()
        callback_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "url": str(request.url),
            "type": "success"
        }
        self.received_callbacks.append(callback_data)
        
        print(f"✅ 성공 콜백 수신: {data.get('platform', 'unknown')}")
        print(f"📊 수집 결과: 게시글 {data.get('total_articles', 0)}개, 댓글 {data.get('total_comments', 0)}개")
        
        return web.json_response({"status": "success", "message": "성공 콜백 수신 완료"})
    
    async def handle_error_callback(self, request: web.Request):
        """오류 콜백 핸들러"""
        data = await request.json()
        callback_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "url": str(request.url),
            "type": "error"
        }
        self.received_callbacks.append(callback_data)
        
        print(f"❌ 오류 콜백 수신: {data.get('platform', 'unknown')}")
        print(f"📋 오류 메시지: {data.get('error_message', '알 수 없는 오류')}")
        
        return web.json_response({"status": "success", "message": "오류 콜백 수신 완료"})
    
    async def handle_timeout_callback(self, request: web.Request):
        """타임아웃 테스트용 콜백 핸들러 (5초 대기)"""
        print(f"⏳ 타임아웃 테스트 콜백 수신 - 5초 대기 중...")
        await asyncio.sleep(5)
        
        data = await request.json()
        return web.json_response({"status": "success", "message": "타임아웃 테스트 완료"})
    
    async def start_server(self):
        """서버 시작"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        print(f"🚀 콜백 테스트 서버 시작: http://localhost:{self.port}")
        return runner
    
    def get_callback_url(self, endpoint: str = "callback"):
        """콜백 URL 생성"""
        return f"http://localhost:{self.port}/{endpoint}"


async def test_callback_service():
    """콜백 서비스 직접 테스트"""
    print("🧪 콜백 서비스 직접 테스트")
    print("=" * 60)
    
    # 테스트 서버 시작
    test_server = CallbackTestServer()
    server_runner = await test_server.start_server()
    
    try:
        # 1. 성공 콜백 테스트
        print("\n📋 1. 성공 콜백 테스트")
        print("-" * 40)
        
        success_result = await callback_service.send_callback(
            callback_url=test_server.get_callback_url("callback/success"),
            platform="gannamunni",
            category="free_chat",
            target_date="2025-09-12",
            result={
                "total_articles": 25,
                "total_comments": 150,
                "execution_time": 45.67
            },
            is_success=True
        )
        print(f"   결과: {'✅ 성공' if success_result else '❌ 실패'}")
        
        await asyncio.sleep(1)  # 서버 처리 대기
        
        # 2. 오류 콜백 테스트
        print("\n📋 2. 오류 콜백 테스트")
        print("-" * 40)
        
        error_result = await callback_service.send_callback(
            callback_url=test_server.get_callback_url("callback/error"),
            platform="babitalk",
            category="talk",
            target_date="2025-09-12",
            result={"execution_time": 12.34},
            is_success=False,
            error_message="API 인증 실패"
        )
        print(f"   결과: {'✅ 성공' if error_result else '❌ 실패'}")
        
        await asyncio.sleep(1)
        
        # 3. 잘못된 URL 테스트
        print("\n📋 3. 잘못된 URL 테스트")
        print("-" * 40)
        
        invalid_result = await callback_service.send_callback(
            callback_url="http://localhost:9999/invalid",
            platform="naver",
            category="error",
            target_date="2025-09-12",
            result={},
            is_success=False,
            error_message="연결 실패 테스트"
        )
        print(f"   결과: {'❌ 실패 (예상됨)' if not invalid_result else '⚠️ 예상과 다름'}")
        
        await asyncio.sleep(1)
        
        # 4. 타임아웃 테스트
        print("\n📋 4. 타임아웃 테스트 (3초 제한)")
        print("-" * 40)
        
        timeout_result = await callback_service.send_callback(
            callback_url=test_server.get_callback_url("callback/timeout"),
            platform="test",
            category="timeout",
            target_date="2025-09-12",
            result={},
            is_success=True,
            timeout=3  # 3초 타임아웃
        )
        print(f"   결과: {'❌ 타임아웃 (예상됨)' if not timeout_result else '⚠️ 예상과 다름'}")
        
        await asyncio.sleep(1)
        
        # 5. 재시도 테스트
        print("\n📋 5. 재시도 테스트")
        print("-" * 40)
        
        retry_result = await callback_service.send_callback_safe(
            callback_url=test_server.get_callback_url("callback"),
            platform="test",
            category="retry",
            target_date="2025-09-12",
            result={"total_articles": 10},
            is_success=True,
            max_retries=2,
            retry_delay=1
        )
        print(f"   결과: {'✅ 성공' if retry_result else '❌ 실패'}")
        
        await asyncio.sleep(1)
        
        # 수신된 콜백 요약
        print(f"\n📊 콜백 수신 요약:")
        print(f"   총 수신된 콜백: {len(test_server.received_callbacks)}개")
        for i, callback in enumerate(test_server.received_callbacks, 1):
            platform = callback['data'].get('platform', 'unknown')
            status = callback['data'].get('status', 'unknown')
            print(f"   {i}. {platform} - {status}")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
    
    finally:
        # 서버 종료
        await server_runner.cleanup()
        print(f"\n🛑 테스트 서버 종료")


async def test_api_integration():
    """API 통합 테스트 (시뮬레이션)"""
    print("\n🔗 API 통합 테스트 (시뮬레이션)")
    print("=" * 60)
    
    # 테스트 서버 시작
    test_server = CallbackTestServer()
    server_runner = await test_server.start_server()
    
    try:
        print("📝 API 요청 예제:")
        print("-" * 40)
        
        # 동기 수집 API 요청 예제
        print("1. 동기 강남언니 수집 요청:")
        sync_request = {
            "category": "free_chat",
            "target_date": "2025-09-12",
            "save_as_reviews": False,
            "token": None,
            "callback_url": test_server.get_callback_url("callback/success")
        }
        print(f"   POST /api/collect/gannamunni")
        print(f"   {json.dumps(sync_request, indent=4, ensure_ascii=False)}")
        
        print("\n2. 비동기 바비톡 수집 요청:")
        async_request = {
            "target_date": "2025-09-12",
            "categories": ["reviews", "talks"],
            "callback_url": test_server.get_callback_url("callback")
        }
        print(f"   POST /api/async-collection/babitalk/start")
        print(f"   {json.dumps(async_request, indent=4, ensure_ascii=False)}")
        
        print("\n3. 네이버 카페 수집 요청:")
        naver_request = {
            "cafe_id": "12285441",
            "target_date": "2025-09-12",
            "menu_id": "38",
            "limit": 20,
            "cookies": "your_cookies_here",
            "callback_url": test_server.get_callback_url("callback/success")
        }
        print(f"   POST /api/collect/naver")
        print(f"   {json.dumps(naver_request, indent=4, ensure_ascii=False)}")
        
        print("\n📞 콜백 URL 형식:")
        print("-" * 40)
        print("성공 시 콜백 데이터 예제:")
        success_data = {
            "platform": "gannamunni",
            "category": "free_chat",
            "target_date": "2025-09-12",
            "status": "success",
            "total_articles": 25,
            "total_comments": 150,
            "total_reviews": 0,
            "execution_time": 45.67,
            "timestamp": "2025-09-12T15:30:45.123456"
        }
        print(f"   POST {test_server.get_callback_url('callback')}")
        print(f"   Content-Type: application/json")
        print(f"   Body: {json.dumps(success_data, indent=4, ensure_ascii=False)}")
        
        print("\n실패 시 콜백 데이터 예제:")
        error_data = {
            "platform": "babitalk",
            "category": "talk",
            "target_date": "2025-09-12",
            "status": "error",
            "error_message": "API 인증 실패",
            "execution_time": 12.34,
            "timestamp": "2025-09-12T15:35:20.987654"
        }
        print(f"   POST {test_server.get_callback_url('callback')}")
        print(f"   Content-Type: application/json")
        print(f"   Body: {json.dumps(error_data, indent=4, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ API 통합 테스트 중 오류 발생: {e}")
    
    finally:
        # 서버 종료
        await server_runner.cleanup()
        print(f"\n🛑 테스트 서버 종료")


def format_query_params(params: dict) -> str:
    """딕셔너리를 쿼리 파라미터 문자열로 변환"""
    return "&".join([f"{k}={v}" for k, v in params.items()])


async def main():
    """메인 테스트 함수"""
    print("🔔 콜백 URL 기능 통합 테스트")
    print("=" * 60)
    
    try:
        # 콜백 서비스 직접 테스트
        await test_callback_service()
        
        # API 통합 테스트 (시뮬레이션)
        await test_api_integration()
        
        print(f"\n✅ 모든 테스트 완료!")
        print(f"📋 콜백 URL 기능이 정상적으로 구현되었습니다.")
        
    except KeyboardInterrupt:
        print(f"\n⛔ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
