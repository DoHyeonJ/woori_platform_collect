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

async def test_with_comments():
    """댓글 포함 수집 테스트"""
    try:
        logger.info("=== 댓글 포함 수집 테스트 시작 ===")
        
        # 쿠키 입력 받기
        cookies = input("네이버 로그인 쿠키를 입력하세요: ").strip()
        if not cookies:
            logger.error("쿠키가 필요합니다.")
            return
        
        # 수집기 생성
        collector = NaverDataCollector("data/collect_data.db", cookies)
        
        # 테스트 카페 ID
        cafe_id = "12285441"  # A+여우야
        logger.info(f"테스트 카페 ID: {cafe_id}")
        
        # 댓글 포함 수집 실행
        logger.info("댓글 포함 수집 시작...")
        result = await collector.collect_articles_with_content_and_comments(
            cafe_id=cafe_id,
            per_page=3  # 테스트용으로 3개만
        )
        
        # 결과 출력
        logger.info("=== 수집 결과 ===")
        logger.info(f"총 게시글: {result.get('total', 0)}개")
        logger.info(f"저장된 게시글: {result.get('saved', 0)}개")
        logger.info(f"실패한 게시글: {result.get('failed', 0)}개")
        logger.info(f"저장된 댓글: {result.get('comments_saved', 0)}개")
        
        # 상세 결과 출력
        details = result.get('details', [])
        for detail in details:
            logger.info(f"게시글 {detail.get('article_id')}: {detail.get('status')}")
            if detail.get('status') == 'success':
                logger.info(f"  - 댓글 {detail.get('comments_saved', 0)}개 저장됨")
        
        logger.info("=== 댓글 포함 수집 테스트 완료 ===")
        
    except Exception as e:
        logger.error(f"댓글 포함 수집 테스트 실패: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def test_date_collection():
    """날짜별 전체 수집 테스트"""
    try:
        logger.info("=== 날짜별 전체 수집 테스트 시작 ===")
        
        # 쿠키 입력 받기
        cookies = input("네이버 로그인 쿠키를 입력하세요: ").strip()
        if not cookies:
            logger.error("쿠키가 필요합니다.")
            return
        
        # 수집기 생성
        collector = NaverDataCollector("data/collect_data.db", cookies)
        
        # 테스트 카페 ID
        cafe_id = "12285441"  # A+여우야
        logger.info(f"테스트 카페 ID: {cafe_id}")
        
        # 테스트 날짜 입력
        test_date = input("테스트할 날짜를 입력하세요 (YYYY-MM-DD 형식, 엔터시 어제 날짜): ").strip()
        if not test_date:
            from datetime import datetime, timedelta
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            test_date = yesterday
            logger.info(f"어제 날짜로 설정: {test_date}")
        
        # 날짜별 전체 수집 실행
        logger.info(f"날짜별 전체 수집 시작... (날짜: {test_date})")
        result = await collector.collect_articles_by_date_with_comments(
            cafe_id=cafe_id,
            target_date=test_date,
            menu_id=""  # 전체 게시판
        )
        
        # 결과 출력
        logger.info("=== 수집 결과 ===")
        logger.info(f"대상 날짜: {result.get('target_date', 'N/A')}")
        logger.info(f"총 게시글: {result.get('total', 0)}개")
        logger.info(f"저장된 게시글: {result.get('saved', 0)}개")
        logger.info(f"실패한 게시글: {result.get('failed', 0)}개")
        logger.info(f"저장된 댓글: {result.get('comments_saved', 0)}개")
        
        # 상세 결과 출력
        details = result.get('details', [])
        if details:
            logger.info("\n📋 상세 결과")
            logger.info("-" * 30)
            for i, detail in enumerate(details[:10], 1):  # 처음 10개만 출력
                logger.info(f"{i}. 게시글 {detail.get('article_id')}: {detail.get('status')}")
                if detail.get('status') == 'success':
                    logger.info(f"   - 제목: {detail.get('title', 'N/A')}")
                    logger.info(f"   - 댓글: {detail.get('comments_saved', 0)}개")
                    logger.info(f"   - 생성일: {detail.get('created_at', 'N/A')}")
                elif detail.get('status') == 'failed':
                    logger.info(f"   - 실패 사유: {detail.get('reason', 'N/A')}")
                elif detail.get('status') == 'error':
                    logger.info(f"   - 오류: {detail.get('reason', 'N/A')}")
            
            if len(details) > 10:
                logger.info(f"   ... 외 {len(details) - 10}개")
        
        logger.info("=== 날짜별 전체 수집 테스트 완료 ===")
        
    except Exception as e:
        logger.error(f"날짜별 전체 수집 테스트 실패: {str(e)}")
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

async def test_content_only():
    """게시글 내용만 테스트 (쿠키 불필요)"""
    try:
        logger.info("🚀 네이버 게시글 내용 테스트 시작")
        logger.info("=" * 50)
        
        # 테스트할 카페 ID
        test_cafe_id = "10912875"  # 여우야
        
        logger.info(f"📍 테스트 카페 ID: {test_cafe_id}")
        
        # 수집기 생성 (쿠키 없이)
        collector = NaverDataCollector("data/collect_data.db", "")
        
        # 1. 게시판 목록 조회
        logger.info("\n📋 1. 게시판 목록 조회")
        logger.info("-" * 30)
        
        boards = await collector.collect_board_list(test_cafe_id)
        if boards:
            logger.info(f"✅ 게시판 {len(boards)}개 조회 성공")
            
            # 첫 번째 게시판 선택
            first_board = boards[0]
            logger.info(f"테스트할 게시판: {first_board.menu_name} (ID: {first_board.menu_id})")
            
            # 2. 게시글 제목과 내용 조회 (5개)
            logger.info("\n📝 2. 게시글 제목과 내용 조회 (5개)")
            logger.info("-" * 30)
            
            content_result = await collector.collect_board_title_and_content(
                cafe_id=test_cafe_id,
                menu_id=str(first_board.menu_id),
                per_page=5
            )
            
            if content_result:
                logger.info("✅ 게시글 제목과 내용 조회 성공")
                logger.info("내용 미리보기:")
                logger.info("-" * 40)
                
                # 내용이 너무 길면 잘라서 표시
                preview = content_result[:500] + "..." if len(content_result) > 500 else content_result
                logger.info(preview)
                
                logger.info(f"\n전체 내용 길이: {len(content_result)}자")
            else:
                logger.warning("⚠️ 게시글 제목과 내용 조회 실패")
        
        logger.info("\n🎉 네이버 게시글 내용 테스트 완료!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def test_detailed_logging():
    """상세 로깅 테스트"""
    try:
        logger.info("🚀 네이버 상세 로깅 테스트 시작")
        logger.info("=" * 50)
        
        # 테스트할 카페 ID
        test_cafe_id = "12285441"  # A+여우야
        
        logger.info(f"📍 테스트 카페 ID: {test_cafe_id}")
        
        # 수집기 생성 (쿠키 없이)
        collector = NaverDataCollector("data/collect_data.db", "")
        
        # 1. 게시판 목록 조회 (상세 로깅)
        logger.info("\n📋 1. 게시판 목록 조회 (상세 로깅)")
        logger.info("-" * 40)
        
        boards = await collector.collect_board_list(test_cafe_id)
        if boards:
            logger.info(f"✅ 게시판 {len(boards)}개 조회 성공")
            
            # 첫 번째 게시판 선택
            first_board = boards[0]
            logger.info(f"테스트할 게시판: {first_board.menu_name} (ID: {first_board.menu_id})")
            
            # 2. 게시글 목록 조회 (상세 로깅)
            logger.info("\n📝 2. 게시글 목록 조회 (상세 로깅)")
            logger.info("-" * 40)
            
            articles = await collector.api.get_article_list(
                cafe_id=test_cafe_id,
                menu_id=str(first_board.menu_id),
                per_page=3
            )
            
            if articles:
                logger.info(f"✅ 게시글 {len(articles)}개 조회 성공")
                
                # 3. 첫 번째 게시글 내용 조회 (상세 로깅)
                if articles:
                    first_article = articles[0]
                    logger.info(f"\n📄 3. 첫 번째 게시글 내용 조회 (상세 로깅)")
                    logger.info("-" * 40)
                    logger.info(f"게시글 ID: {first_article.article_id}")
                    logger.info(f"제목: {first_article.subject}")
                    
                    content = await collector.api.get_article_content(
                        cafe_id=test_cafe_id,
                        article_id=first_article.article_id
                    )
                    
                    if content:
                        logger.info(f"✅ 게시글 내용 조회 성공 (길이: {len(content)}자)")
                        logger.info("내용 미리보기:")
                        logger.info("-" * 30)
                        preview = content[:200] + "..." if len(content) > 200 else content
                        logger.info(preview)
                    else:
                        logger.warning("⚠️ 게시글 내용 조회 실패")
            else:
                logger.warning("⚠️ 게시글 목록 조회 실패")
        
        logger.info("\n🎉 네이버 상세 로깅 테스트 완료!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def test_default_values():
    """기본값으로 네이버 수집 테스트"""
    try:
        logger.info("🚀 네이버 수집 기본값 테스트 시작")
        logger.info("=" * 50)
        
        # 기본값으로 수집기 생성
        collector = NaverDataCollector("data/collect_data.db", "")
        
        # 기본값 설정
        cafe_id = "12285441"  # A+여우야★성형카페
        target_date = datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜
        menu_id = "38"  # 기본 게시판
        limit = 20  # 기본 제한
        
        logger.info(f"📍 기본값 설정:")
        logger.info(f"  - 카페 ID: {cafe_id}")
        logger.info(f"  - 날짜: {target_date}")
        logger.info(f"  - 게시판 ID: {menu_id}")
        logger.info(f"  - 제한: {limit}")
        logger.info(f"  - 쿠키: 빈 값 (공개 정보만)")
        
        # 1. 게시판 목록 조회 테스트
        logger.info("\n📋 1. 게시판 목록 조회 테스트")
        logger.info("-" * 30)
        
        boards = await collector.collect_board_list(cafe_id)
        if boards:
            logger.info(f"✅ 게시판 {len(boards)}개 조회 성공")
            for i, board in enumerate(boards[:5], 1):
                logger.info(f"  {i}. {board.menu_name} (ID: {board.menu_id}, 타입: {board.menu_type})")
            if len(boards) > 5:
                logger.info(f"  ... 외 {len(boards) - 5}개")
        else:
            logger.warning("⚠️ 게시판 목록 조회 실패")
            return
        
        # 2. 기본값으로 게시글 수집 테스트
        logger.info("\n📝 2. 기본값으로 게시글 수집 테스트")
        logger.info("-" * 30)
        
        # 날짜별 제한 수집 (기본값)
        result = await collector.collect_articles_with_content_and_comments(
            cafe_id=cafe_id,
            menu_id=menu_id,
            per_page=limit
        )
        
        if result.get('saved', 0) > 0:
            logger.info(f"✅ 기본값 수집 성공: 게시글 {result.get('saved', 0)}개, 댓글 {result.get('comments_saved', 0)}개")
        else:
            logger.warning("⚠️ 기본값 수집 실패")
        
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
        
        logger.info("\n🎉 기본값 테스트 완료!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ 기본값 테스트 중 오류 발생: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def test_created_at():
    """네이버 created_at 저장 테스트"""
    try:
        logger.info("🚀 네이버 created_at 저장 테스트 시작")
        logger.info("=" * 50)
        
        # 기본값으로 수집기 생성
        collector = NaverDataCollector("data/collect_data.db", "")
        
        # 기본값 설정
        cafe_id = "12285441"  # A+여우야★성형카페
        target_date = datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜
        menu_id = "38"  # 기본 게시판
        limit = 5  # 테스트용으로 5개만
        
        logger.info(f"📍 테스트 설정:")
        logger.info(f"  - 카페 ID: {cafe_id}")
        logger.info(f"  - 날짜: {target_date}")
        logger.info(f"  - 게시판 ID: {menu_id}")
        logger.info(f"  - 제한: {limit}")
        
        # 1. 게시글 수집 테스트 (댓글 포함)
        logger.info("\n📝 1. 게시글 수집 테스트 (댓글 포함)")
        logger.info("-" * 30)
        
        result = await collector.collect_articles_with_content_and_comments(
            cafe_id=cafe_id,
            menu_id=menu_id,
            per_page=limit
        )
        
        if result.get('saved', 0) > 0:
            logger.info(f"✅ 게시글 수집 성공: {result.get('saved', 0)}개")
            logger.info(f"✅ 댓글 수집 성공: {result.get('comments_saved', 0)}개")
            
            # 상세 정보 출력
            for detail in result.get('details', [])[:3]:  # 처음 3개만
                logger.info(f"  - 게시글 ID: {detail.get('article_id')}")
                logger.info(f"    제목: {detail.get('title')}")
                logger.info(f"    내용 길이: {detail.get('content_length')}")
                logger.info(f"    댓글 수: {detail.get('comments_saved')}")
        else:
            logger.warning("⚠️ 게시글 수집 실패")
        
        # 2. 데이터베이스에서 created_at 확인
        logger.info("\n🗄️ 2. 데이터베이스 created_at 확인")
        logger.info("-" * 30)
        
        # 최근 수집된 네이버 게시글 조회
        try:
            from database.models import DatabaseManager
            db = DatabaseManager("data/collect_data.db")
            
            # 최근 수집된 네이버 게시글 5개 조회
            query = """
            SELECT id, community_article_id, title, created_at, collected_at 
            FROM articles 
            WHERE platform_id = 'naver' 
            ORDER BY collected_at DESC 
            LIMIT 5
            """
            
            cursor = db.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if rows:
                logger.info(f"✅ 최근 수집된 네이버 게시글 {len(rows)}개:")
                for row in rows:
                    db_id, article_id, title, created_at, collected_at = row
                    logger.info(f"  - DB ID: {db_id}")
                    logger.info(f"    게시글 ID: {article_id}")
                    logger.info(f"    제목: {title[:50]}...")
                    logger.info(f"    생성일: {created_at}")
                    logger.info(f"    수집일: {collected_at}")
                    logger.info("")
            else:
                logger.warning("⚠️ 데이터베이스에 네이버 게시글이 없습니다")
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 조회 실패: {str(e)}")
        
        logger.info("\n🎉 created_at 테스트 완료!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ created_at 테스트 중 오류 발생: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    print("=== 네이버 수집기 테스트 ===")
    print("1. 게시판 목록 조회 테스트")
    print("2. 게시글 수집 테스트")
    print("3. 게시글 내용만 테스트 (쿠키 불필요)")
    print("4. 상세 로깅 테스트")
    print("5. 댓글 포함 수집 테스트")
    print("6. 날짜별 전체 수집 테스트")
    print("7. 기본값 테스트")
    print("8. created_at 저장 테스트")
    
    choice = input("선택하세요 (1-8): ").strip()
    
    if choice == "1":
        asyncio.run(test_board_list_only())
    elif choice == "2":
        asyncio.run(test_naver_collector())
    elif choice == "3":
        asyncio.run(test_content_only())
    elif choice == "4":
        asyncio.run(test_detailed_logging())
    elif choice == "5":
        asyncio.run(test_with_comments())
    elif choice == "6":
        asyncio.run(test_date_collection())
    elif choice == "7":
        asyncio.run(test_default_values())
    elif choice == "8":
        asyncio.run(test_created_at())
    else:
        logger.error("잘못된 선택입니다. 1, 2, 3, 4, 5, 6, 7 또는 8을 입력해주세요.")
