import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
import logging

from dotenv import load_dotenv

load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)

# Base 클래스 생성
Base = declarative_base()

class DatabaseConfig:
    """데이터베이스 설정 클래스"""
    
    def __init__(self):
        self.apps_env = os.getenv("APPS_ENV", "local")
        self.db_type = os.getenv("DB_TYPE", "sqlite")
        self.db_url = self._get_database_url()
        self.engine = create_engine(
            self.db_url,
            echo=os.getenv("ENVIRONMENT", "development") == "development",
            pool_pre_ping=True if self.db_type == "mysql" else False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _get_database_url(self) -> str:
        """환경 변수에 따라 데이터베이스 URL 생성"""
        if self.db_type == "mysql":
            host = os.getenv("MYSQL_HOST", "localhost")
            port = os.getenv("MYSQL_PORT", "3306")
            user = os.getenv("MYSQL_USER", "root")
            password = os.getenv("MYSQL_PASSWORD", "")
            database = os.getenv("MYSQL_DATABASE", "woori_collect")
            
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4&collation=utf8mb4_unicode_ci"
        else:
            # SQLite (기본값)
            db_path = os.getenv("DB_PATH", "data/collect_data.db")
            return f"sqlite:///{db_path}"
    
    def create_tables(self):
        """테이블 생성 (local 환경에서만 자동 생성)"""
        if self.apps_env != "local":
            logger.info(f"🚫 현재 환경({self.apps_env})에서는 자동 테이블 생성을 건너뜁니다.")
            logger.info("💡 프로덕션 환경에서는 수동으로 테이블을 생성하거나 마이그레이션을 실행하세요.")
            return
            
        try:
            logger.info(f"🗄️ local 환경에서 데이터베이스 테이블 자동 생성 중...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ 데이터베이스 테이블이 성공적으로 생성되었습니다.")
        except Exception as e:
            logger.error(f"❌ 테이블 생성 중 오류 발생: {e}")
            raise
    
    def get_session(self) -> Generator:
        """데이터베이스 세션 생성"""
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"데이터베이스 세션 오류: {e}")
            raise
        finally:
            session.close()

# 전역 데이터베이스 설정 인스턴스
db_config = DatabaseConfig()

# 의존성 주입용 함수
def get_db():
    """FastAPI 의존성 주입을 위한 데이터베이스 세션 함수"""
    return next(db_config.get_session())
