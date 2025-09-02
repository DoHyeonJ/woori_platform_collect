from fastapi import Depends
from database.models import DatabaseManager  # 하위 호환성을 위해 유지 (내부적으로 SQLAlchemy 사용)
from database.sqlalchemy_manager import SQLAlchemyDatabaseManager  # SQLAlchemy 매니저
from database.config import get_db
from sqlalchemy.orm import Session

def get_database_manager() -> DatabaseManager:
    """
    데이터베이스 매니저 인스턴스를 반환합니다.
    하위 호환성을 위해 DatabaseManager 인터페이스를 유지하되,
    내부적으로는 SQLAlchemy를 사용합니다.
    """
    return DatabaseManager()  # db_path 파라미터 제거

def get_sqlalchemy_database_manager() -> SQLAlchemyDatabaseManager:
    """SQLAlchemy 데이터베이스 매니저 인스턴스를 반환합니다."""
    return SQLAlchemyDatabaseManager()

def get_database_session() -> Session:
    """SQLAlchemy 데이터베이스 세션을 반환합니다."""
    return get_db() 