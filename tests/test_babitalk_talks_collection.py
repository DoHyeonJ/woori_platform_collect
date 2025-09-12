#!/usr/bin/env python3
"""
바비톡 자유톡 수집 상세 테스트 스크립트
자유톡 게시글과 댓글 수집 과정을 상세히 로깅하여 문제점을 파악합니다.
"""

import asyncio
import sys
import os
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.babitalk import BabitalkAPI
from collectors.babitalk_collector import BabitalkDataCollector
from utils.logger import get_logger

class BabitalkTalksCollectionTester:
    def __init__(self):
        self.logger = get_logger("BabitalkTalksTester")
        self.api = BabitalkAPI()
        self.collector = BabitalkDataCollector()
        
    async def test_talks_api_detailed(self, service_id: int, limit: int = 24):
        """자유톡 API 상세 테스트"""
        self.logger.info(f"🔍 자유톡 API 상세 테스트 시작 (서비스 ID: {service_id}, limit: {limit})")
        
        try:
            # API 호출
            talks, pagination = await self.api.get_talks(
                service_id=service_id,
                limit=limit,
                search_after=0,
                sort="recent"
            )
            
            self.logger.info(f"📊 API 응답 결과:")
            self.logger.info(f"   수집된 자유톡: {len(talks)}개")
            self.logger.info(f"   페이지네이션: has_next={pagination.has_next}, search_after={pagination.search_after}")
            
            if talks:
                self.logger.info(f"📝 첫 번째 자유톡 상세 정보:")
                first_talk = talks[0]
                self.logger.info(f"   ID: {first_talk.id}")
                self.logger.info(f"   제목: {first_talk.title}")
                self.logger.info(f"   작성자: {first_talk.user.name}")
                self.logger.info(f"   서비스 ID: {first_talk.service_id}")
                self.logger.info(f"   댓글 수: {first_talk.total_comment}")
                self.logger.info(f"   작성일: {first_talk.created_at}")
                self.logger.info(f"   내용 미리보기: {first_talk.text[:100]}...")
                
                # 모든 자유톡의 작성일 확인
                self.logger.info(f"📅 모든 자유톡 작성일:")
                for i, talk in enumerate(talks[:10]):  # 처음 10개만
                    self.logger.info(f"   {i+1}. ID {talk.id}: {talk.created_at}")
            
            return talks, pagination
            
        except Exception as e:
            self.logger.error(f"❌ API 호출 실패: {e}")
            return [], None
    
    async def test_talks_by_date_detailed(self, target_date: str, service_id: int):
        """날짜별 자유톡 수집 상세 테스트"""
        self.logger.info(f"🔍 날짜별 자유톡 수집 상세 테스트 시작")
        self.logger.info(f"   대상 날짜: {target_date}")
        self.logger.info(f"   서비스 ID: {service_id}")
        
        try:
            # API에서 자유톡 데이터 가져오기
            talks = await self.api.get_talks_by_date(target_date, service_id)
            
            self.logger.info(f"📊 날짜별 수집 결과:")
            self.logger.info(f"   수집된 자유톡: {len(talks)}개")
            
            if talks:
                self.logger.info(f"📝 수집된 자유톡 상세 정보:")
                for i, talk in enumerate(talks):
                    self.logger.info(f"   {i+1}. ID: {talk.id}, 제목: {talk.title[:50]}..., 작성일: {talk.created_at}, 댓글수: {talk.total_comment}")
            else:
                self.logger.warning(f"⚠️  {target_date} 날짜의 자유톡이 없습니다.")
            
            return talks
            
        except Exception as e:
            self.logger.error(f"❌ 날짜별 수집 실패: {e}")
            return []
    
    async def test_all_service_categories(self, target_date: str):
        """모든 서비스 카테고리 테스트"""
        self.logger.info(f"🔍 모든 서비스 카테고리 테스트 시작")
        self.logger.info(f"   대상 날짜: {target_date}")
        
        total_talks = 0
        service_results = {}
        
        for service_id, category_name in self.api.TALK_SERVICE_CATEGORIES.items():
            self.logger.info(f"📅 {category_name} 카테고리 (서비스 ID: {service_id}) 테스트 시작")
            
            try:
                # 1. 일반 API 호출 테스트
                talks, pagination = await self.api.get_talks(service_id=service_id, limit=24)
                self.logger.info(f"   일반 API: {len(talks)}개 수집, 페이지네이션: {pagination.has_next}")
                
                # 2. 날짜별 수집 테스트
                date_talks = await self.api.get_talks_by_date(target_date, service_id)
                self.logger.info(f"   날짜별 수집: {len(date_talks)}개")
                
                service_results[service_id] = {
                    'category_name': category_name,
                    'general_api_count': len(talks),
                    'date_specific_count': len(date_talks),
                    'pagination_has_next': pagination.has_next
                }
                
                total_talks += len(date_talks)
                
                # 3. 페이지네이션 테스트 (첫 번째 페이지만)
                if pagination.has_next:
                    self.logger.info(f"   페이지네이션 테스트: 다음 페이지 존재 (search_after: {pagination.search_after})")
                    
                    # 다음 페이지 호출
                    next_talks, next_pagination = await self.api.get_talks(
                        service_id=service_id,
                        limit=24,
                        search_after=pagination.search_after,
                        sort="recent"
                    )
                    self.logger.info(f"   다음 페이지: {len(next_talks)}개 수집")
                
            except Exception as e:
                self.logger.error(f"❌ {category_name} 카테고리 테스트 실패: {e}")
                service_results[service_id] = {
                    'category_name': category_name,
                    'error': str(e)
                }
        
        # 결과 요약
        self.logger.info(f"📊 전체 서비스 카테고리 테스트 결과:")
        self.logger.info(f"   총 수집된 자유톡: {total_talks}개")
        
        for service_id, result in service_results.items():
            if 'error' in result:
                self.logger.info(f"   {result['category_name']} (ID: {service_id}): ❌ 오류 - {result['error']}")
            else:
                self.logger.info(f"   {result['category_name']} (ID: {service_id}): 일반 {result['general_api_count']}개, 날짜별 {result['date_specific_count']}개")
        
        return service_results, total_talks
    
    async def test_comments_collection(self, target_date: str, service_id: int):
        """댓글 수집 상세 테스트"""
        self.logger.info(f"🔍 댓글 수집 상세 테스트 시작")
        self.logger.info(f"   대상 날짜: {target_date}")
        self.logger.info(f"   서비스 ID: {service_id}")
        
        try:
            # 해당 날짜의 자유톡 가져오기
            talks = await self.api.get_talks_by_date(target_date, service_id)
            
            if not talks:
                self.logger.warning(f"⚠️  {target_date} 날짜의 자유톡이 없어서 댓글 수집을 건너뜁니다.")
                return 0
            
            self.logger.info(f"📝 댓글 수집 대상 자유톡: {len(talks)}개")
            
            total_comments = 0
            
            for i, talk in enumerate(talks):
                self.logger.info(f"💬 자유톡 {i+1}/{len(talks)} 댓글 수집 시작 (ID: {talk.id})")
                self.logger.info(f"   제목: {talk.title[:50]}...")
                self.logger.info(f"   댓글 수: {talk.total_comment}개")
                
                try:
                    # 댓글 수집
                    comments_count = await self.collector.collect_comments_for_talk(talk.id)
                    total_comments += comments_count
                    
                    self.logger.info(f"   ✅ 댓글 수집 완료: {comments_count}개")
                    
                except Exception as e:
                    self.logger.error(f"   ❌ 댓글 수집 실패: {e}")
                    continue
            
            self.logger.info(f"📊 댓글 수집 결과:")
            self.logger.info(f"   총 수집된 댓글: {total_comments}개")
            
            return total_comments
            
        except Exception as e:
            self.logger.error(f"❌ 댓글 수집 테스트 실패: {e}")
            return 0
    
    async def run_comprehensive_test(self, target_date: str = None):
        """종합 테스트 실행"""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        self.logger.info(f"🚀 바비톡 자유톡 수집 종합 테스트 시작")
        self.logger.info(f"   대상 날짜: {target_date}")
        self.logger.info("=" * 80)
        
        # 1. 모든 서비스 카테고리 테스트
        self.logger.info("1️⃣ 모든 서비스 카테고리 테스트")
        service_results, total_talks = await self.test_all_service_categories(target_date)
        
        # 2. 개별 서비스 상세 테스트
        self.logger.info("\n2️⃣ 개별 서비스 상세 테스트")
        for service_id, category_name in self.api.TALK_SERVICE_CATEGORIES.items():
            self.logger.info(f"\n📅 {category_name} 카테고리 상세 테스트")
            
            # 일반 API 테스트
            talks, pagination = await self.test_talks_api_detailed(service_id, 24)
            
            # 날짜별 수집 테스트
            date_talks = await self.test_talks_by_date_detailed(target_date, service_id)
            
            # 댓글 수집 테스트
            if date_talks:
                comments_count = await self.test_comments_collection(target_date, service_id)
            else:
                self.logger.info(f"   댓글 수집 건너뜀 (자유톡 없음)")
        
        # 3. 최종 요약
        self.logger.info("\n3️⃣ 최종 테스트 요약")
        self.logger.info("=" * 80)
        self.logger.info(f"🎯 테스트 완료!")
        self.logger.info(f"   대상 날짜: {target_date}")
        self.logger.info(f"   총 수집된 자유톡: {total_talks}개")
        
        for service_id, result in service_results.items():
            if 'error' in result:
                self.logger.info(f"   {result['category_name']}: ❌ 오류")
            else:
                self.logger.info(f"   {result['category_name']}: {result['date_specific_count']}개")

async def main():
    """메인 함수"""
    tester = BabitalkTalksCollectionTester()
    
    # 오늘 날짜로 테스트
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        await tester.run_comprehensive_test(today)
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
