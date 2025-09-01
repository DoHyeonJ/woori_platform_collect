from fastapi import Depends
from database.models import DatabaseManager  # 기존 SQLite 매니저 (호환성 유지)
from database.sqlalchemy_manager import SQLAlchemyDatabaseManager  # 새 SQLAlchemy 매니저
from database.config import get_db
from sqlalchemy.orm import Session
import os

# 데이터베이스 경로 설정 (SQLite용)
DB_PATH = os.getenv("DB_PATH", "data/collect_data.db")

def get_database_manager() -> DatabaseManager:
    """기존 SQLite 데이터베이스 매니저 인스턴스를 반환합니다. (호환성 유지용)"""
    return DatabaseManager(DB_PATH)

def get_sqlalchemy_database_manager() -> SQLAlchemyDatabaseManager:
    """새로운 SQLAlchemy 데이터베이스 매니저 인스턴스를 반환합니다."""
    return SQLAlchemyDatabaseManager()

def get_database_session() -> Session:
    """SQLAlchemy 데이터베이스 세션을 반환합니다."""
    return get_db() 