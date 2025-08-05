import os
import sqlite3
from datetime import datetime
from database import DatabaseManager

def backup_existing_database(db_path: str = "collect_data.db"):
    """기존 데이터베이스 백업"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            os.rename(db_path, backup_path)
            print(f"✅ 기존 데이터베이스가 백업되었습니다: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ 백업 실패: {e}")
            return None
    else:
        print("ℹ️  기존 데이터베이스 파일이 없습니다.")
        return None

def delete_existing_database(db_path: str = "collect_data.db"):
    """기존 데이터베이스 삭제"""
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✅ 기존 데이터베이스가 삭제되었습니다: {db_path}")
            return True
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")
            return False
    else:
        print("ℹ️  삭제할 데이터베이스 파일이 없습니다.")
        return True

def create_fresh_database(db_path: str = "collect_data.db"):
    """새로운 데이터베이스 생성"""
    try:
        db = DatabaseManager(db_path)
        print(f"✅ 새로운 데이터베이스가 생성되었습니다: {db_path}")
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 생성 실패: {e}")
        return False

def verify_database_structure(db_path: str = "collect_data.db"):
    """데이터베이스 구조 검증"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 테이블 목록 조회
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print("\n📋 생성된 테이블 목록:")
            for table in tables:
                print(f"   • {table}")
            
            # 커뮤니티 테이블 구조 확인
            cursor.execute("PRAGMA table_info(communities)")
            columns = cursor.fetchall()
            
            print("\n🔍 커뮤니티 테이블 구조:")
            for col in columns:
                col_name, col_type, not_null, default_val, pk, unique = col
                unique_text = "UNIQUE" if unique else ""
                print(f"   • {col_name} ({col_type}) {unique_text}")
            
            # 인덱스 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            print("\n📊 생성된 인덱스:")
            for index in indexes:
                print(f"   • {index}")
            
            return True
            
    except Exception as e:
        print(f"❌ 데이터베이스 구조 검증 실패: {e}")
        return False

def main():
    """메인 마이그레이션 함수"""
    print("🔄 데이터베이스 마이그레이션 시작")
    print("=" * 50)
    
    db_path = "collect_data.db"
    
    # 1. 백업 옵션 확인
    print("\n1️⃣ 백업 옵션을 선택하세요:")
    print("1. 기존 데이터베이스 백업 후 초기화")
    print("2. 기존 데이터베이스 삭제 후 초기화 (백업 없음)")
    print("3. 취소")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice == "1":
        # 백업 후 초기화
        backup_path = backup_existing_database(db_path)
        if backup_path:
            if delete_existing_database(db_path):
                if create_fresh_database(db_path):
                    verify_database_structure(db_path)
                    print(f"\n✅ 마이그레이션 완료!")
                    print(f"📁 백업 파일: {backup_path}")
                    print(f"📁 새 데이터베이스: {db_path}")
                else:
                    print("❌ 새 데이터베이스 생성에 실패했습니다.")
            else:
                print("❌ 기존 데이터베이스 삭제에 실패했습니다.")
        else:
            print("❌ 백업에 실패했습니다.")
    
    elif choice == "2":
        # 백업 없이 초기화
        print("\n⚠️  경고: 기존 데이터베이스가 영구적으로 삭제됩니다!")
        confirm = input("정말로 진행하시겠습니까? (yes/no): ").strip().lower()
        
        if confirm == "yes":
            if delete_existing_database(db_path):
                if create_fresh_database(db_path):
                    verify_database_structure(db_path)
                    print(f"\n✅ 마이그레이션 완료!")
                    print(f"📁 새 데이터베이스: {db_path}")
                else:
                    print("❌ 새 데이터베이스 생성에 실패했습니다.")
            else:
                print("❌ 기존 데이터베이스 삭제에 실패했습니다.")
        else:
            print("❌ 마이그레이션이 취소되었습니다.")
    
    elif choice == "3":
        print("❌ 마이그레이션이 취소되었습니다.")
    
    else:
        print("❌ 올바른 선택지를 입력해주세요.")

if __name__ == "__main__":
    main() 