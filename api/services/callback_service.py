"""
콜백 URL 호출 서비스
"""

import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime
from utils.logger import LoggedClass


class CallbackService(LoggedClass):
    """콜백 URL 호출 서비스"""
    
    def __init__(self):
        super().__init__("CallbackService")
    
    async def send_callback(
        self,
        callback_url: str,
        platform: str,
        category: str,
        target_date: str,
        result: Dict[str, Any],
        is_success: bool = True,
        error_message: Optional[str] = None,
        timeout: int = 30
    ) -> bool:
        """
        콜백 URL로 POST 요청 전송
        
        Args:
            callback_url: 콜백 URL
            platform: 플랫폼명 (gannamunni, babitalk, naver)
            category: 카테고리
            target_date: 수집 날짜
            result: 수집 결과
            is_success: 성공 여부
            error_message: 오류 메시지 (실패 시)
            timeout: 타임아웃 (초)
            
        Returns:
            bool: 콜백 전송 성공 여부
        """
        if not callback_url:
            self.log_warning("콜백 URL이 제공되지 않았습니다.")
            return False
        
        try:
            # 콜백 URL에 전송할 데이터 구성
            callback_data = {
                "platform": platform,
                "category": category,
                "target_date": target_date,
                "status": "success" if is_success else "error",
                "timestamp": datetime.now().isoformat()
            }
            
            # 성공 시 결과 정보 추가
            if is_success and result:
                callback_data.update({
                    "total_articles": result.get("total_articles", 0),
                    "total_comments": result.get("total_comments", 0),
                    "total_reviews": result.get("total_reviews", 0),
                    "execution_time": result.get("execution_time", 0)
                })
                
                # 카테고리별 결과가 있는 경우 JSON 문자열로 변환
                if "category_results" in result:
                    for cat, count in result["category_results"].items():
                        if isinstance(count, dict):
                            # 딕셔너리인 경우 JSON 문자열로 변환
                            import json
                            callback_data[f"category_{cat}_count"] = json.dumps(count, ensure_ascii=False)
                        else:
                            callback_data[f"category_{cat}_count"] = count
            
            # 실패 시 오류 메시지 추가
            if not is_success and error_message:
                callback_data["error_message"] = error_message
            
            self.log_info(f"🔔 콜백 URL 호출 시작: {callback_url}")
            self.log_info(f"📊 전송 데이터: {callback_data}")
            
            # 비동기 HTTP POST 요청 전송
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(callback_url, json=callback_data) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        self.log_info(f"✅ 콜백 URL 호출 성공 (상태: {response.status})")
                        self.log_info(f"📝 응답 내용: {response_text[:200]}...")
                        return True
                    else:
                        self.log_warning(f"⚠️ 콜백 URL 호출 실패 (상태: {response.status})")
                        self.log_warning(f"📝 응답 내용: {response_text[:200]}...")
                        return False
                        
        except asyncio.TimeoutError:
            self.log_error(f"❌ 콜백 URL 호출 타임아웃: {callback_url} ({timeout}초)")
            return False
        except Exception as e:
            self.log_error(f"❌ 콜백 URL 호출 중 오류 발생: {e}")
            return False
    
    async def send_callback_safe(
        self,
        callback_url: str,
        platform: str,
        category: str,
        target_date: str,
        result: Dict[str, Any],
        is_success: bool = True,
        error_message: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> bool:
        """
        콜백 URL 호출 (재시도 포함)
        
        Args:
            callback_url: 콜백 URL
            platform: 플랫폼명
            category: 카테고리
            target_date: 수집 날짜
            result: 수집 결과
            is_success: 성공 여부
            error_message: 오류 메시지
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간격 (초)
            
        Returns:
            bool: 콜백 전송 성공 여부
        """
        if not callback_url:
            return False
        
        for attempt in range(max_retries + 1):
            try:
                success = await self.send_callback(
                    callback_url=callback_url,
                    platform=platform,
                    category=category,
                    target_date=target_date,
                    result=result,
                    is_success=is_success,
                    error_message=error_message
                )
                
                if success:
                    if attempt > 0:
                        self.log_info(f"✅ 콜백 URL 호출 성공 (재시도 {attempt}회 후)")
                    return True
                    
            except Exception as e:
                self.log_warning(f"⚠️ 콜백 URL 호출 시도 {attempt + 1}/{max_retries + 1} 실패: {e}")
            
            # 마지막 시도가 아닌 경우 대기
            if attempt < max_retries:
                self.log_info(f"🔄 {retry_delay}초 후 재시도...")
                await asyncio.sleep(retry_delay)
        
        self.log_error(f"❌ 콜백 URL 호출 최종 실패: {callback_url} ({max_retries}회 재시도 후)")
        return False
    
    def send_callback_background(
        self,
        callback_url: str,
        platform: str,
        category: str,
        target_date: str,
        result: Dict[str, Any],
        is_success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        백그라운드에서 콜백 URL 호출
        
        Args:
            callback_url: 콜백 URL
            platform: 플랫폼명
            category: 카테고리
            target_date: 수집 날짜
            result: 수집 결과
            is_success: 성공 여부
            error_message: 오류 메시지
        """
        if not callback_url:
            return
        
        async def _background_callback():
            await self.send_callback_safe(
                callback_url=callback_url,
                platform=platform,
                category=category,
                target_date=target_date,
                result=result,
                is_success=is_success,
                error_message=error_message
            )
        
        # 백그라운드 태스크로 실행
        try:
            asyncio.create_task(_background_callback())
            self.log_info(f"🚀 백그라운드 콜백 태스크 생성: {callback_url}")
        except Exception as e:
            self.log_error(f"❌ 백그라운드 콜백 태스크 생성 실패: {e}")


# 전역 콜백 서비스 인스턴스
callback_service = CallbackService()
