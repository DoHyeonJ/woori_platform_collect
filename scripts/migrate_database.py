#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
데이터베이스를 백업하고 새로운 스키마로 초기화합니다.
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.models import DatabaseManager

def backup_database(db_path: str):
    """데이터베이스를 백업합니다."""
    if not os.path.exists(db_path):
        print(f"⚠️  데이터베이스 파일이 존재하지 않습니다: {db_path}")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ 데이터베이스 백업 완료: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ 백업 실패: {e}")
        return None

def delete_database(db_path: str):
    """데이터베이스를 삭제합니다."""
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✅ 데이터베이스 삭제 완료: {db_path}")
            return True
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")
            return False
    else:
        print(f"⚠️  데이터베이스 파일이 존재하지 않습니다: {db_path}")
        return True

def create_database(db_path: str):
    """새로운 데이터베이스를 생성합니다."""
    try:
        db = DatabaseManager(db_path)
        print(f"✅ 새로운 데이터베이스 생성 완료: {db_path}")
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 생성 실패: {e}")
        return False

def verify_database(db_path: str):
    """데이터베이스 구조를 확인합니다."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 테이블 목록 조회
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print("📋 데이터베이스 테이블 구조:")
            print("=" * 50)
            
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                print(f"\n📊 테이블: {table}")
                print(f"   컬럼 수: {len(columns)}")
                for col in columns:
                    print(f"   - {col[1]} ({col[2]})")
            
            return True
            
    except Exception as e:
        print(f"❌ 데이터베이스 확인 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🔄 데이터베이스 마이그레이션")
    print("=" * 50)
    
    # 환경 변수 설정
    db_path = os.getenv("DB_PATH", "test_collect_data.db")
    
    print(f"📁 대상 데이터베이스: {db_path}")
    print()
    
    # 사용자 확인
    confirm = input("⚠️  이 작업은 기존 데이터를 백업하고 새로운 스키마로 초기화합니다. 계속하시겠습니까? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ 작업이 취소되었습니다.")
        return
    
    print("\n🔄 마이그레이션 시작...")
    
    # 1. 백업
    print("\n1️⃣ 데이터베이스 백업 중...")
    backup_path = backup_database(db_path)
    
    # 2. 삭제
    print("\n2️⃣ 기존 데이터베이스 삭제 중...")
    if not delete_database(db_path):
        print("❌ 삭제 실패로 마이그레이션이 중단되었습니다.")
        return
    
    # 3. 생성
    print("\n3️⃣ 새로운 데이터베이스 생성 중...")
    if not create_database(db_path):
        print("❌ 생성 실패로 마이그레이션이 중단되었습니다.")
        return
    
    # 4. 확인
    print("\n4️⃣ 데이터베이스 구조 확인 중...")
    if not verify_database(db_path):
        print("❌ 확인 실패로 마이그레이션이 중단되었습니다.")
        return
    
    print("\n🎉 마이그레이션이 성공적으로 완료되었습니다!")
    
    if backup_path:
        print(f"💾 백업 파일: {backup_path}")

if __name__ == "__main__":
    main() 