#!/usr/bin/env python3
"""
데이터 수집 플랫폼 메인 실행 파일

사용법:
    python main.py                    # 기본 설정으로 실행
    uvicorn main:app --reload         # uvicorn으로 직접 실행
    uvicorn main:app --host 0.0.0.0 --port 8080  # 특정 호스트/포트로 실행
"""

import uvicorn
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

from utils.logger import get_logger
from api.main import app  # FastAPI 앱 임포트

# 로거 설정
logger = get_logger("MAIN")

def main():
    """메인 실행 함수"""
    logger.info("🚀 데이터 수집 플랫폼을 시작합니다...")
    logger.info("=" * 50)
    
    # 환경 변수 설정
    apps_env = os.getenv("APPS_ENV", "local")
    db_type = os.getenv("DB_TYPE", "sqlite")
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level = os.getenv("API_LOG_LEVEL", "info")
    
    # 환경 정보 출력
    logger.info(f"🌍 애플리케이션 환경: {apps_env}")
    logger.info(f"🗄️ 데이터베이스: {db_type}")
    logger.info(f"📍 서버 주소: http://{host}:{port}")
    logger.info(f"📚 API 문서: http://{host}:{port}/docs")
    logger.info(f"📖 ReDoc 문서: http://{host}:{port}/redoc")
    logger.info(f"💚 헬스 체크: http://{host}:{port}/health")
    logger.info(f"🔄 자동 재시작: {reload}")
    logger.info(f"📝 로그 레벨: {log_level}")
    
    # 테이블 자동 생성 여부 표시
    if apps_env == "local":
        logger.info("✅ 테이블 자동 생성: 활성화 (local 환경)")
    else:
        logger.info("⚠️ 테이블 자동 생성: 비활성화 (수동 관리 필요)")
    
    logger.info("=" * 50)
    
    try:
        # uvicorn으로 서버 실행
        uvicorn.run(
            "main:app",  # 현재 파일의 app 객체 참조
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 서버가 중지되었습니다.")
    except Exception as e:
        logger.error(f"❌ 서버 실행 중 오류 발생: {e}")
        sys.exit(1)

def get_app():
    """FastAPI 앱 인스턴스를 반환합니다 (uvicorn 직접 실행용)"""
    return app

# uvicorn이 직접 참조할 수 있도록 app 객체를 모듈 레벨에 노출
app = get_app()

if __name__ == "__main__":
    main()
