#!/usr/bin/env python3
"""
강남언니 리뷰 상세 수집 테스트 스크립트
"""

import asyncio
import sys
import os
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from platforms.gannamunni import GangnamUnniAPI
from collectors.gannamunni_collector import GangnamUnniDataCollector
from database.sqlalchemy_manager import DatabaseManager

async def test_review_detail_api():
    """리뷰 상세 API 테스트"""
    print("🧪 강남언니 리뷰 상세 API 테스트 시작...")
    
    api = GangnamUnniAPI()
    
    # 테스트용 리뷰 ID (실제 존재하는 ID 사용)
    test_review_id = 102125020
    
    try:
        # print(f"📋 리뷰 상세 정보 조회 중... (ID: {test_review_id})")
        review_detail = await api.get_review_detail(test_review_id)
        
        if review_detail:
            print("✅ 리뷰 상세 정보 조회 성공!")
            print(f"   - 리뷰 ID: {review_detail.get('id')}")
            print(f"   - 작성자: {review_detail.get('author', {}).get('nickname', 'N/A')}")
            print(f"   - 병원명: {review_detail.get('hospital', {}).get('name', 'N/A')}")
            print(f"   - 의사명: {review_detail.get('doctors', [{}])[0].get('name', 'N/A') if review_detail.get('doctors') else 'N/A'}")
            print(f"   - 시술: {[t.get('name', '') for t in review_detail.get('treatments', [])]}")
            print(f"   - 평점: {review_detail.get('totalRating', 'N/A')}")
            print(f"   - 내용 길이: {len(review_detail.get('description', {}).get('source', {}).get('contents', ''))}")
        else:
            print("❌ 리뷰 상세 정보 조회 실패")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

async def test_review_collection():
    """리뷰 수집 테스트"""
    print("\n🧪 강남언니 리뷰 수집 테스트 시작...")
    
    try:
        # 데이터베이스 연결
        db = DatabaseManager()
        
        # 수집기 초기화
        collector = GangnamUnniDataCollector(db)
        
        # 테스트 날짜 (최근 날짜)
        test_date = "2025-09-19"
        
        print(f"📅 {test_date} 날짜 리뷰 수집 테스트...")
        
        # 리뷰 수집 (소량 테스트)
        result = await collector.collect_articles_by_date(
            target_date=test_date,
            category="hospital_question",
            include_reviews=True
        )
        
        print(f"📊 수집 결과:")
        print(f"   - 게시글: {result['articles']}개")
        print(f"   - 댓글: {result['comments']}개")
        print(f"   - 리뷰: {result['reviews']}개")
        
        # 데이터베이스에서 저장된 리뷰 확인
        if result['reviews'] > 0:
            print("\n🔍 저장된 리뷰 상세 정보 확인...")
            # 최근 저장된 리뷰 조회
            recent_reviews = db.get_recent_reviews(limit=3)
            for review in recent_reviews:
                print(f"   - ID: {review.id}")
                print(f"   - 제목: {review.title}")
                print(f"   - 병원명: {review.hospital_name}")
                print(f"   - 의사명: {review.doctor_name}")
                print(f"   - 평점: {review.rating}")
                print(f"   - 가격: {review.price}")
                print(f"   - 카테고리: {review.categories}")
                print("   ---")
        
    except Exception as e:
        print(f"❌ 리뷰 수집 테스트 중 오류 발생: {e}")

async def main():
    """메인 테스트 함수"""
    print("🚀 강남언니 리뷰 상세 수집 시스템 테스트")
    print("=" * 50)
    
    # 1. 리뷰 상세 API 테스트
    await test_review_detail_api()
    
    # 2. 리뷰 수집 테스트
    await test_review_collection()
    
    print("\n✅ 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
