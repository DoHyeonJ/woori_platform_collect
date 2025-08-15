#!/usr/bin/env python3
"""
네이버 커뮤니티 추가 스크립트
community_id를 3으로 설정하여 네이버 데이터 수집이 정상적으로 작동하도록 함
"""
import os
import sys
import sqlite3
from datetime import datetime

# utils 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_naver_community(db_path: str = "data/collect_data.db"):
    """네이버 커뮤니티를 추가하고 community_id를 3으로 설정"""
    try:
        print(f"🔧 네이버 커뮤니티 추가 시작: {db_path}")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 1. 현재 커뮤니티 목록 확인
            print("📋 현재 커뮤니티 목록:")
            cursor.execute("SELECT * FROM communities ORDER BY id")
            communities = cursor.fetchall()
            
            for community in communities:
                print(f"  - ID: {community[0]}, 이름: {community[1]}, 생성일: {community[2]}")
            
            # 2. 네이버 커뮤니티가 이미 존재하는지 확인
            cursor.execute("SELECT * FROM communities WHERE name = '네이버'")
            existing_naver = cursor.fetchone()
            
            if existing_naver:
                print(f"⚠️ 네이버 커뮤니티가 이미 존재합니다 (ID: {existing_naver[0]})")
                
                # community_id가 3이 아닌 경우 업데이트
                if existing_naver[0] != 3:
                    print(f"🔄 네이버 커뮤니티 ID를 3으로 변경 중...")
                    
                    # 임시 ID로 변경 (충돌 방지)
                    temp_id = 999
                    cursor.execute("UPDATE communities SET id = ? WHERE name = '네이버'", (temp_id,))
                    
                    # ID를 3으로 설정
                    cursor.execute("UPDATE communities SET id = 3 WHERE name = '네이버'")
                    print("✅ 네이버 커뮤니티 ID를 3으로 변경 완료")
                else:
                    print("✅ 네이버 커뮤니티 ID가 이미 3입니다")
            else:
                print("📝 네이버 커뮤니티 추가 중...")
                
                # ID 3이 사용 중인지 확인
                cursor.execute("SELECT * FROM communities WHERE id = 3")
                if cursor.fetchone():
                    print("⚠️ ID 3이 이미 사용 중입니다. 다른 ID로 설정합니다")
                    # 자동으로 다음 사용 가능한 ID 사용
                    cursor.execute('''
                        INSERT INTO communities (name, created_at, description)
                        VALUES (?, ?, ?)
                    ''', ('네이버', datetime.now(), '네이버 카페 데이터 수집을 위한 커뮤니티'))
                else:
                    # ID 3으로 직접 삽입
                    cursor.execute('''
                        INSERT INTO communities (id, name, created_at, description)
                        VALUES (?, ?, ?, ?)
                    ''', (3, '네이버', datetime.now(), '네이버 카페 데이터 수집을 위한 커뮤니티'))
                    print("✅ 네이버 커뮤니티를 ID 3으로 추가 완료")
            
            # 3. 최종 커뮤니티 목록 확인
            print("\n📋 최종 커뮤니티 목록:")
            cursor.execute("SELECT * FROM communities ORDER BY id")
            final_communities = cursor.fetchall()
            
            for community in final_communities:
                print(f"  - ID: {community[0]}, 이름: {community[1]}, 생성일: {community[2]}")
            
            # 4. 네이버 커뮤니티 정보 확인
            cursor.execute("SELECT * FROM communities WHERE name = '네이버'")
            naver_community = cursor.fetchone()
            
            if naver_community:
                print(f"\n✅ 네이버 커뮤니티 설정 완료:")
                print(f"  - ID: {naver_community[0]}")
                print(f"  - 이름: {naver_community[1]}")
                print(f"  - 생성일: {naver_community[2]}")
                print(f"  - 설명: {naver_community[3]}")
            else:
                print("❌ 네이버 커뮤니티 설정 실패")
            
            conn.commit()
            print("\n🎉 네이버 커뮤니티 설정 완료!")
            
    except Exception as e:
        print(f"❌ 네이버 커뮤니티 추가 실패: {str(e)}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    print("=== 네이버 커뮤니티 추가 ===")
    
    # 데이터베이스 경로 확인
    db_path = "data/collect_data.db"
    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        sys.exit(1)
    
    # 네이버 커뮤니티 추가
    add_naver_community(db_path)
