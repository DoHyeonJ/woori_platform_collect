from fastapi import Depends
from database.models import DatabaseManager
import os

# 데이터베이스 경로 설정
DB_PATH = os.getenv("DB_PATH", "data/collect_data.db")

def get_database_manager() -> DatabaseManager:
    """데이터베이스 매니저 인스턴스를 반환합니다."""
    return DatabaseManager(DB_PATH) 