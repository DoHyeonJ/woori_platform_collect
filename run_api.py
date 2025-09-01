#!/usr/bin/env python3
"""
데이터 수집 플랫폼 API 서버 실행 스크립트 (호환성 유지용)

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
새로운 실행 방법은 main.py를 사용하세요.

사용법:
    python run_api.py    # 기존 방식 (호환성 유지)
    python main.py       # 새로운 방식 (권장)
"""

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

def main():
    """기존 호환성을 위한 래퍼 함수"""
    logger = get_logger("RUN_API")
    
    logger.info("📋 run_api.py는 호환성을 위해 유지됩니다.")
    logger.info("💡 새로운 실행 방법: python main.py")
    logger.info("🔄 main.py로 실행을 전달합니다...")
    
    # main.py의 main() 함수 호출
    try:
        from main import main as main_function
        main_function()
    except ImportError as e:
        logger.error(f"❌ main.py를 찾을 수 없습니다: {e}")
        logger.info("💡 프로젝트 루트에서 실행해주세요.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 