#!/usr/bin/env python3
"""
네이버 게시판 목록 조회 테스트
"""
import os
import sys
import asyncio

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.naver import NaverCafeAPI

async def test_naver_board_list():
    """네이버 게시판 목록 조회 테스트"""
    print("🧪 네이버 게시판 목록 조회 테스트")
    print("=" * 50)
    
    # 테스트 카페 ID (A+여우야★성형카페)
    cafe_id = "12285441"
    
    print(f"🏢 테스트 카페: {cafe_id}")
    
    api = NaverCafeAPI()
    
    try:
        print("\n📋 게시판 목록 조회 중...")
        
        # 게시판 목록 조회
        boards = await api.get_board_list(cafe_id)
        
        if boards:
            print(f"✅ {len(boards)}개 게시판 발견:")
            for board in boards:
                print(f"   - ID: {board.menu_id}, 이름: {board.menu_name}, 타입: {board.menu_type}")
        else:
            print("❌ 게시판 목록을 가져올 수 없습니다.")
        
        print("\n🎉 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_naver_board_list())
