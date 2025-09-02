from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime, date
from typing import List, Optional
import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routers import data_collection, data_viewer, async_collection
from api.dependencies import get_database_manager, get_sqlalchemy_database_manager
from database.models import DatabaseManager
from database.config import db_config
from utils.logger import get_logger

# 로거 설정
logger = get_logger("API_MAIN")

# 데이터베이스 초기화 함수
def initialize_database():
    """서버 시작 시 데이터베이스 테이블을 초기화합니다."""
    apps_env = os.getenv("APPS_ENV", "local")
    
    try:
        logger.info(f"🗄️ 데이터베이스 초기화 시작 (환경: {apps_env})...")
        
        # SQLAlchemy 기반 테이블 생성 (local 환경에서만)
        db_config.create_tables()
        
        # 기존 SQLite 매니저도 초기화 (local 환경에서만)
        if apps_env == "local":
            db_manager = get_database_manager()
            db_manager.init_database()
        
        logger.info("✅ 데이터베이스 초기화 완료")
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")
        raise

# FastAPI 앱 생성
app = FastAPI(
    title="데이터 수집 플랫폼 API",
    description="강남언니, 바비톡 등 다양한 플랫폼의 데이터를 수집하고 관리하는 API 서버",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 서버 시작 시 이벤트
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 이벤트"""
    logger.info("🚀 API 서버 시작 중...")
    initialize_database()
    logger.info("🎉 API 서버 준비 완료!")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(data_collection.router, prefix="/api/v1/collection", tags=["데이터 수집"])
app.include_router(data_viewer.router, prefix="/api/v1/data", tags=["데이터 조회"])
app.include_router(async_collection.router, prefix="/api/v1", tags=["비동기 수집"])

@app.get("/")
async def root():
    """API 서버 상태 확인"""
    return {
        "message": "데이터 수집 플랫폼 API 서버",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 확인
        db = get_database_manager()
        db.get_connection()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"서비스 상태 불량: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 