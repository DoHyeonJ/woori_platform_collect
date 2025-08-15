#!/usr/bin/env python3
"""
네이버 수집기 테스트 스크립트
"""
import os
import sys
import asyncio
from datetime import datetime

# utils 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from collectors.naver_collector import NaverDataCollector

logger = get_logger("NAVER_TEST")

async def test_naver_collector():
    """네이버 수집기 테스트"""
    try:
        logger.info("🚀 네이버 수집기 테스트 시작")
        logger.info("=" * 50)
        
        # 네이버 쿠키 입력 받기
        logger.info("네이버 로그인 쿠키를 입력하세요 (예: NID_AUT=...; NID_SES=...)")
        naver_cookies = input("쿠키: ").strip()
        if not naver_cookies:
            logger.error("❌ 네이버 쿠키가 입력되지 않았습니다.")
            return
        
        # 테스트할 카페 ID
        test_cafe_id = "10912875"  # 여우야
        
        logger.info(f"📍 테스트 카페 ID: {test_cafe_id}")
        logger.info(f"🍪 쿠키: {naver_cookies[:30]}...")
        
        # 수집기 생성
        collector = NaverDataCollector("data/collect_data.db", naver_cookies)
        
        # 1. 게시판 목록 조회 테스트
        logger.info("\n📋 1. 게시판 목록 조회 테스트")
        logger.info("-" * 30)
        
        boards = await collector.collect_board_list(test_cafe_id)
        if boards:
            logger.info(f"✅ 게시판 {len(boards)}개 조회 성공")
            for i, board in enumerate(boards[:5], 1):  # 처음 5개만 출력
                logger.info(f"  {i}. {board.menu_name} (ID: {board.menu_id}, 타입: {board.menu_type})")
            if len(boards) > 5:
                logger.info(f"  ... 외 {len(boards) - 5}개")
        else:
            logger.warning("⚠️ 게시판 목록 조회 실패")
            return
        
        # 2. 특정 게시판 게시글 수집 테스트
        if boards:
            logger.info("\n📝 2. 특정 게시판 게시글 수집 테스트")
            logger.info("-" * 30)
            
            first_board = boards[0]
            logger.info(f"게시판: {first_board.menu_name} (ID: {first_board.menu_id})")
            
            # 게시글 5개만 테스트 수집
            articles_count = await collector.collect_articles_by_menu(
                cafe_id=test_cafe_id,
                menu_id=first_board.menu_id,
                per_page=5
            )
            
            if articles_count > 0:
                logger.info(f"✅ 게시글 {articles_count}개 수집 성공")
            else:
                logger.warning("⚠️ 게시글 수집 실패")
        
        # 3. 통계 조회 테스트
        logger.info("\n📊 3. 수집 통계 조회 테스트")
        logger.info("-" * 30)
        
        stats = collector.get_collection_stats()
        if stats:
            logger.info(f"✅ 전체 게시글 수: {stats.get('total_articles', 0)}개")
            logger.info("카페별 통계:")
            for cafe_name, count in stats.get('by_cafe', {}).items():
                logger.info(f"  - {cafe_name}: {count}개")
        else:
            logger.warning("⚠️ 통계 조회 실패")
        
        # 4. 전체 게시판 수집 테스트 (선택사항)
        logger.info("\n🔄 4. 전체 게시판 수집 테스트 (선택사항)")
        logger.info("-" * 30)
        
        choice = input("전체 게시판 수집을 테스트하시겠습니까? (y/N): ").strip().lower()
        if choice == 'y':
            logger.info("전체 게시판 수집 시작...")
            results = await collector.collect_all_boards_articles(
                cafe_id=test_cafe_id,
                per_page=3  # 각 게시판당 3개씩만 테스트
            )
            
            if results:
                total = sum(results.values())
                logger.info(f"✅ 전체 게시판 수집 완료: 총 {total}개")
                for board_name, count in results.items():
                    logger.info(f"  - {board_name}: {count}개")
            else:
                logger.warning("⚠️ 전체 게시판 수집 실패")
        
        logger.info("\n🎉 네이버 수집기 테스트 완료!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def test_naver_api_only():
    """네이버 API만 테스트 (데이터베이스 저장 없이)"""
    try:
        logger.info("🚀 네이버 API 테스트 시작")
        logger.info("=" * 50)
        
        # 네이버 쿠키 입력 받기
        logger.info("네이버 로그인 쿠키를 입력하세요 (예: NID_AUT=...; NID_SES=...)")
        naver_cookies = input("쿠키: ").strip()
        if not naver_cookies:
            logger.error("❌ 네이버 쿠키가 입력되지 않았습니다.")
            return
        
        # 테스트할 카페 ID
        test_cafe_id = "10912875"  # 여우야
        
        logger.info(f"📍 테스트 카페 ID: {test_cafe_id}")
        
        # 수집기 생성 (데이터베이스 경로는 None으로 설정하여 API만 테스트)
        collector = NaverDataCollector("data/collect_data.db", naver_cookies)
        
        # 1. 게시판 목록 조회 테스트
        logger.info("\n📋 1. 게시판 목록 조회 테스트")
        logger.info("-" * 30)
        
        boards = await collector.collect_board_list(test_cafe_id)
        if boards:
            logger.info(f"✅ 게시판 {len(boards)}개 조회 성공")
            for i, board in enumerate(boards[:5], 1):
                logger.info(f"  {i}. {board.menu_name} (ID: {board.menu_id}, 타입: {board.menu_type})")
        else:
            logger.warning("⚠️ 게시판 목록 조회 실패")
            return
        
        # 2. 게시글 목록 조회 테스트 (내용 없이)
        if boards:
            logger.info("\n📝 2. 게시글 목록 조회 테스트 (내용 없이)")
            logger.info("-" * 30)
            
            first_board = boards[0]
            logger.info(f"게시판: {first_board.menu_name} (ID: {first_board.menu_id})")
            
            # 게시글 목록만 조회 (내용은 조회하지 않음)
            articles = await collector.api.get_article_list(
                cafe_id=test_cafe_id,
                menu_id=first_board.menu_id,
                per_page=5
            )
            
            if articles:
                logger.info(f"✅ 게시글 {len(articles)}개 조회 성공")
                for i, article in enumerate(articles[:3], 1):
                    logger.info(f"  {i}. {article.subject} (작성자: {article.writer_nickname})")
            else:
                logger.warning("⚠️ 게시글 목록 조회 실패")
        
        # 3. 지원하는 카페 목록 조회
        logger.info("\n🏠 3. 지원하는 카페 목록 조회")
        logger.info("-" * 30)
        
        cafes = collector.api.list_cafes()
        if cafes:
            logger.info(f"✅ 지원하는 카페 {len(cafes)}개")
            for cafe_name, cafe_id in cafes.items():
                logger.info(f"  - {cafe_name}: {cafe_id}")
        
        logger.info("\n🎉 네이버 API 테스트 완료!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def test_board_list_only():
    """게시판 목록만 테스트"""
    try:
        logger.info("🚀 네이버 게시판 목록 테스트 시작")
        logger.info("=" * 50)
        
        # 쿠키 입력 (선택사항)
        logger.info("네이버 로그인 쿠키를 입력하세요 (선택사항, 엔터만 누르면 쿠키 없이 테스트)")
        logger.info("예: NID_AUT=...; NID_SES=...")
        naver_cookies = input("쿠키 (선택사항): ").strip()
        
        # 테스트할 카페 ID들
        test_cafes = {
            "여우야": "10912875",
            "A+여우야": "12285441",
            "성형위키백과": "11498714"
        }
        
        # 수집기 생성 (쿠키가 없어도 생성 가능)
        collector = NaverDataCollector("data/collect_data.db", naver_cookies)
        
        for cafe_name, cafe_id in test_cafes.items():
            logger.info(f"\n🏠 {cafe_name} (ID: {cafe_id}) 게시판 목록 조회")
            logger.info("-" * 40)
            
            try:
                boards = await collector.collect_board_list(cafe_id)
                if boards:
                    logger.info(f"✅ 게시판 {len(boards)}개 조회 성공")
                    for i, board in enumerate(boards[:3], 1):  # 처음 3개만 출력
                        logger.info(f"  {i}. {board.menu_name} (ID: {board.menu_id}, 타입: {board.menu_type})")
                    if len(boards) > 3:
                        logger.info(f"  ... 외 {len(boards) - 3}개")
                else:
                    logger.warning("⚠️ 게시판 목록 조회 실패")
                    
            except Exception as e:
                logger.error(f"❌ {cafe_name} 게시판 목록 조회 실패: {str(e)}")
                continue
            
            # API 호출 간격 조절
            await asyncio.sleep(1)
        
        logger.info("\n🎉 네이버 게시판 목록 테스트 완료!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    logger.info("네이버 수집기 테스트를 시작합니다.")
    logger.info("1. 전체 테스트 (API + 수집 + DB 저장)")
    logger.info("2. API만 테스트 (수집 및 DB 저장 없음)")
    logger.info("3. 게시판 목록만 테스트")
    
    choice = input("\n테스트 유형을 선택하세요 (1, 2 또는 3): ").strip()
    
    if choice == "1":
        asyncio.run(test_naver_collector())
    elif choice == "2":
        asyncio.run(test_naver_api_only())
    elif choice == "3":
        asyncio.run(test_board_list_only())
    else:
        logger.error("잘못된 선택입니다. 1, 2 또는 3을 입력해주세요.")
