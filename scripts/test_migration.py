#!/usr/bin/env python3
"""
마이그레이션 스크립트 테스트 도구
연결 테스트 및 데이터 검증을 수행합니다.
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger("MIGRATION_TEST")

class MigrationTester:
    """마이그레이션 테스트 클래스"""
    
    def __init__(self):
        # 소스 DB 설정 (localhost)
        self.source_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '1234',  # 실제 비밀번호로 변경
            'database': 'woori_collect',
            'charset': 'utf8mb4'
        }
        
        # 대상 DB 설정 (db.hellobdd2.gabia.io)
        self.target_config = {
            'host': 'db.hellobdd2.gabia.io',
            'port': 3306,
            'user': 'hellobdd2',
            'password': 'ahdtlfcjstk0805!',  # 실제 비밀번호로 변경
            'database': 'hellobdd2',
            'charset': 'utf8mb4'
        }
        
        # SQLAlchemy 엔진 생성
        self.source_engine = self._create_engine(self.source_config)
        self.target_engine = self._create_engine(self.target_config)
    
    def _create_engine(self, config: dict) -> create_engine:
        """SQLAlchemy 엔진 생성"""
        connection_string = (
            f"mysql+pymysql://{config['user']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
            f"?charset={config['charset']}"
        )
        
        return create_engine(
            connection_string,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    def test_connections(self) -> bool:
        """데이터베이스 연결 테스트"""
        logger.info("🔍 데이터베이스 연결 테스트 시작...")
        
        try:
            # 소스 DB 테스트
            with self.source_engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                if result.fetchone()[0] == 1:
                    logger.info("✅ 소스 DB (localhost) 연결 성공")
                else:
                    logger.error("❌ 소스 DB 연결 테스트 실패")
                    return False
            
            # 대상 DB 테스트
            with self.target_engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                if result.fetchone()[0] == 1:
                    logger.info("✅ 대상 DB (db.hellobdd2.gabia.io) 연결 성공")
                else:
                    logger.error("❌ 대상 DB 연결 테스트 실패")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 연결 테스트 중 오류: {e}")
            return False
    
    def test_table_structures(self) -> bool:
        """테이블 구조 테스트"""
        logger.info("🔍 테이블 구조 테스트 시작...")
        
        try:
            # 소스 DB 테이블 확인
            with self.source_engine.connect() as conn:
                result = conn.execute(text("SHOW TABLES"))
                source_tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"소스 DB 테이블: {source_tables}")
            
            # 대상 DB 테이블 확인
            with self.target_engine.connect() as conn:
                result = conn.execute(text("SHOW TABLES"))
                target_tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"대상 DB 테이블: {target_tables}")
            
            # 필수 테이블 확인
            required_tables = ['articles', 'comments', 'reviews', 'communities']
            
            for table in required_tables:
                source_has_table = table in source_tables
                target_has_table = table in target_tables
                
                if source_has_table:
                    logger.info(f"✅ 소스 DB에 {table} 테이블 존재")
                else:
                    logger.warning(f"⚠️ 소스 DB에 {table} 테이블 없음")
                
                if target_has_table:
                    logger.info(f"✅ 대상 DB에 {table} 테이블 존재")
                else:
                    logger.warning(f"⚠️ 대상 DB에 {table} 테이블 없음")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 테이블 구조 테스트 중 오류: {e}")
            return False
    
    def get_table_count(self, engine: create_engine, table_name: str) -> int:
        """테이블의 레코드 수 조회"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.fetchone()[0]
        except Exception as e:
            logger.error(f"테이블 {table_name} 카운트 조회 실패: {e}")
            return 0
    
    def get_data_statistics(self) -> dict:
        """데이터 통계 조회"""
        logger.info("📊 데이터 통계 조회 중...")
        
        try:
            # 소스 DB 통계
            source_stats = {
                'communities': self.get_table_count(self.source_engine, 'communities'),
                'articles': self.get_table_count(self.source_engine, 'articles'),
                'comments': self.get_table_count(self.source_engine, 'comments'),
                'reviews': self.get_table_count(self.source_engine, 'reviews')
            }
            
            # 대상 DB 통계
            target_stats = {
                'communities': self.get_table_count(self.target_engine, 'communities'),
                'articles': self.get_table_count(self.target_engine, 'articles'),
                'comments': self.get_table_count(self.target_engine, 'comments'),
                'reviews': self.get_table_count(self.target_engine, 'reviews')
            }
            
            return {
                'source': source_stats,
                'target': target_stats
            }
            
        except Exception as e:
            logger.error(f"❌ 통계 조회 중 오류: {e}")
            return {}
    
    def test_sample_data(self) -> bool:
        """샘플 데이터 테스트"""
        logger.info("🔍 샘플 데이터 테스트 시작...")
        
        try:
            # 소스 DB에서 샘플 데이터 조회
            with self.source_engine.connect() as conn:
                # 최신 게시글 1개 조회
                result = conn.execute(text("""
                    SELECT title FROM articles 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """))
                latest_article = result.fetchone()
                if latest_article:
                    logger.info(f"소스 DB 최신 게시글: {latest_article[0][:50]}...")
                
                # 최신 댓글 1개 조회
                result = conn.execute(text("""
                    SELECT content FROM comments 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """))
                latest_comment = result.fetchone()
                if latest_comment:
                    logger.info(f"소스 DB 최신 댓글: {latest_comment[0][:50]}...")
                
                # 최신 후기 1개 조회
                result = conn.execute(text("""
                    SELECT title FROM reviews 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """))
                latest_review = result.fetchone()
                if latest_review:
                    logger.info(f"소스 DB 최신 후기: {latest_review[0][:50]}...")
            
            logger.info("✅ 샘플 데이터 조회 성공")
            return True
            
        except Exception as e:
            logger.error(f"❌ 샘플 데이터 테스트 중 오류: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """모든 테스트 실행"""
        logger.info("🧪 마이그레이션 테스트 시작")
        logger.info("=" * 60)
        
        tests = [
            ("연결 테스트", self.test_connections),
            ("테이블 구조 테스트", self.test_table_structures),
            ("샘플 데이터 테스트", self.test_sample_data)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            logger.info(f"\n📋 {test_name} 실행 중...")
            if not test_func():
                logger.error(f"❌ {test_name} 실패")
                all_passed = False
            else:
                logger.info(f"✅ {test_name} 성공")
        
        # 통계 출력
        logger.info("\n📊 데이터 통계:")
        stats = self.get_data_statistics()
        if stats:
            logger.info(f"소스 DB: {stats['source']}")
            logger.info(f"대상 DB: {stats['target']}")
        
        logger.info("\n" + "=" * 60)
        if all_passed:
            logger.info("🎉 모든 테스트가 성공적으로 완료되었습니다!")
            logger.info("💡 이제 마이그레이션을 실행할 수 있습니다.")
        else:
            logger.error("❌ 일부 테스트가 실패했습니다.")
            logger.info("💡 문제를 해결한 후 다시 테스트해주세요.")
        
        return all_passed

def main():
    """메인 함수"""
    logger.info("마이그레이션 테스트 도구")
    logger.info("=" * 60)
    
    # 테스트 실행
    tester = MigrationTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("\n🎯 테스트 완료! 마이그레이션을 진행할 수 있습니다.")
    else:
        logger.error("\n❌ 테스트 실패! 문제를 해결한 후 다시 시도해주세요.")

if __name__ == "__main__":
    main()