#!/usr/bin/env python3
"""
데이터 수집 플랫폼 API 서버 실행 스크립트
"""

import uvicorn
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """API 서버를 실행합니다."""
    print("🚀 데이터 수집 플랫폼 API 서버를 시작합니다...")
    print("=" * 50)
    
    # 환경 변수 설정
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level = os.getenv("API_LOG_LEVEL", "info")
    
    print(f"📍 서버 주소: http://{host}:{port}")
    print(f"📚 API 문서: http://{host}:{port}/docs")
    print(f"📖 ReDoc 문서: http://{host}:{port}/redoc")
    print(f"💚 헬스 체크: http://{host}:{port}/health")
    print(f"🔄 자동 재시작: {reload}")
    print(f"📝 로그 레벨: {log_level}")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 API 서버가 중지되었습니다.")
    except Exception as e:
        print(f"❌ API 서버 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 