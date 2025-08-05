#!/usr/bin/env python3
"""
기존 테이블에 collected_at 컬럼을 추가하는 마이그레이션 스크립트
"""

import sqlite3
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger

logger = get_logger("migrate_collected_at")

def migrate_collected_at():
    """기존 테이블에 collected_at 컬럼을 추가합니다."""
    db_path = "data/collect_data.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # articles 테이블에 collected_at 컬럼 추가
            try:
                cursor.execute('ALTER TABLE articles ADD COLUMN collected_at TIMESTAMP')
                logger.info("articles 테이블에 collected_at 컬럼을 추가했습니다.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("articles 테이블의 collected_at 컬럼이 이미 존재합니다.")
                else:
                    raise
            
            # comments 테이블에 collected_at 컬럼 추가
            try:
                cursor.execute('ALTER TABLE comments ADD COLUMN collected_at TIMESTAMP')
                logger.info("comments 테이블에 collected_at 컬럼을 추가했습니다.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("comments 테이블의 collected_at 컬럼이 이미 존재합니다.")
                else:
                    raise
            
            # reviews 테이블에 collected_at 컬럼 추가
            try:
                cursor.execute('ALTER TABLE reviews ADD COLUMN collected_at TIMESTAMP')
                logger.info("reviews 테이블에 collected_at 컬럼을 추가했습니다.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("reviews 테이블의 collected_at 컬럼이 이미 존재합니다.")
                else:
                    raise
            
            # 기존 데이터의 collected_at을 created_at으로 업데이트
            cursor.execute('UPDATE articles SET collected_at = created_at WHERE collected_at IS NULL')
            cursor.execute('UPDATE comments SET collected_at = created_at WHERE collected_at IS NULL')
            cursor.execute('UPDATE reviews SET collected_at = created_at WHERE collected_at IS NULL')
            
            logger.info("기존 데이터의 collected_at을 created_at으로 업데이트했습니다.")
            
            conn.commit()
            logger.info("마이그레이션이 성공적으로 완료되었습니다.")
            
    except Exception as e:
        logger.error(f"마이그레이션 중 오류가 발생했습니다: {e}")
        raise

if __name__ == "__main__":
    migrate_collected_at() 