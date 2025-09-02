import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.babitalk import BabitalkAPI, BabitalkReview, BabitalkEventAskMemo, BabitalkTalk, BabitalkComment
from database.models import DatabaseManager, Review, Community, Article
from utils.logger import LoggedClass

class BabitalkDataCollector(LoggedClass):
    def __init__(self):
        super().__init__("BabitalkCollector")
        self.api = BabitalkAPI()
        self.db = DatabaseManager()  # db_path 파라미터 제거
    
    async def collect_and_save_reviews(self, limit_per_page: int = 24, max_pages: int = 10) -> int:
        """
        바비톡 시술 후기를 수집하고 데이터베이스에 저장합니다.
        
        Args:
            limit_per_page: 페이지당 후기 수 (기본값: 24)
            max_pages: 최대 수집할 페이지 수 (기본값: 10)
        
        Returns:
            int: 수집된 후기 수
        """
        self.log_info("🚀 바비톡 시술 후기 수집 시작")
        
        # 바비톡 커뮤니티 생성 또는 조회
        babitalk_community = await self._get_or_create_babitalk_community()
        
        total_reviews = 0
        page = 1
        search_after = None
        
        try:
            while page <= max_pages:
                # API에서 후기 데이터 가져오기
                reviews, pagination = await self.api.get_surgery_reviews(
                    limit=limit_per_page,
                    search_after=search_after,
                    sort="popular"
                )
                
                if not reviews:
                    break
                
                # 각 후기 처리
                for review in reviews:
                    try:
                        # 후기 정보 저장
                        review_id = await self._save_review(review, babitalk_community['id'])
                        if review_id:
                            total_reviews += 1
                    except Exception:
                        continue
                
                # 다음 페이지 확인
                if not pagination.has_next or not pagination.search_after:
                    break
                
                search_after = pagination.search_after
                page += 1
                
                # 페이지 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(1)
            
            self.log_info(f"✅ 바비톡 시술 후기 수집 완료: {total_reviews}개")
            return total_reviews
            
        except Exception as e:
            self.log_error(f"❌ 수집 중 오류 발생: {e}")
            return total_reviews
    
    async def collect_reviews_by_date(self, target_date: str, limit_per_page: int = 24) -> int:
        """
        특정 날짜의 바비톡 시술 후기를 수집하고 데이터베이스에 저장합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            limit_per_page: 페이지당 후기 수 (기본값: 24)
        
        Returns:
            int: 수집된 후기 수
        """
        self.log_info(f"🚀 {target_date} 날짜 바비톡 시술 후기 수집 시작")
        self.log_info("=" * 50)
        
        # 바비톡 커뮤니티 생성 또는 조회
        babitalk_community = await self._get_or_create_babitalk_community()
        
        try:
            # API에서 해당 날짜의 후기 데이터 가져오기
            reviews = await self.api.get_reviews_by_date(target_date, limit=limit_per_page)
            
            if not reviews:
                self.log_info(f"📭 {target_date} 날짜에 수집할 후기가 없습니다.")
                return 0
            
            self.log_info(f"📋 {target_date} 날짜: {len(reviews)}개 후기 수집됨")
            
            # 각 후기 처리 및 저장
            total_reviews = 0
            for review in reviews:
                try:
                    # 후기 정보 저장
                    review_id = await self._save_review(review, babitalk_community['id'])
                    if review_id:
                        total_reviews += 1
                except Exception:
                    continue
            
            self.log_info(f"✅ {target_date} 날짜 후기 수집 완료: {total_reviews}개")
            return total_reviews
            
        except Exception as e:
            self.log_error(f"❌ 날짜별 후기 수집 중 오류 발생: {e}")
            return 0
    
    async def collect_event_ask_memos_by_date(self, target_date: str, category_id: int, limit_per_page: int = 24) -> int:
        """
        특정 날짜의 바비톡 발품후기를 수집하고 데이터베이스에 저장합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            category_id: 카테고리 ID (3000: 눈, 3100: 코, 3200: 지방흡입/이식, 3300: 안면윤곽/양악, 3400: 가슴, 3500: 남자성형, 3600: 기타)
            limit_per_page: 페이지당 후기 수 (기본값: 24)
        
        Returns:
            int: 수집된 발품후기 수
        """
        category_name = self.api.EVENT_ASK_CATEGORIES.get(category_id, f"카테고리{category_id}")
        self.log_info(f"📅 {target_date} 날짜 바비톡 {category_name} 발품후기 수집 시작")
        
        # 바비톡 커뮤니티 생성 또는 조회
        babitalk_community = await self._get_or_create_babitalk_community()
        
        try:
            # API에서 해당 날짜의 발품후기 데이터 가져오기
            memos = await self.api.get_event_ask_memos_by_date(target_date, category_id, limit_per_page)
            
            if not memos:
                self.log_info(f"📭 {target_date} 날짜에 수집할 {category_name} 발품후기가 없습니다.")
                return 0
            
            # 각 발품후기 처리 및 저장
            total_memos = 0
            for memo in memos:
                try:
                    # 발품후기 정보 저장
                    memo_id = await self._save_event_ask_memo(memo, babitalk_community['id'])
                    if memo_id:
                        total_memos += 1
                except Exception:
                    continue
            
            self.log_info(f"✅ {target_date} 날짜 {category_name} 발품후기 수집 완료: {total_memos}개")
            return total_memos
            
        except Exception as e:
            self.log_error(f"❌ 날짜별 발품후기 수집 중 오류 발생: {e}")
            return 0
    
    async def collect_all_event_ask_memos_by_date(self, target_date: str, limit_per_page: int = 24) -> Dict[int, int]:
        """
        특정 날짜의 모든 카테고리 발품후기를 수집하고 데이터베이스에 저장합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            limit_per_page: 페이지당 후기 수 (기본값: 24)
        
        Returns:
            Dict[int, int]: 카테고리별 수집된 발품후기 수
        """
        self.log_info(f"📅 {target_date} 날짜 바비톡 모든 카테고리 발품후기 수집 시작")
        
        results = {}
        
        # 모든 카테고리 순회
        for category_id, category_name in self.api.EVENT_ASK_CATEGORIES.items():
            try:
                count = await self.collect_event_ask_memos_by_date(target_date, category_id, limit_per_page)
                results[category_id] = count
                
                # 카테고리 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(2)
                
            except Exception as e:
                self.log_error(f"❌ {category_name} 카테고리 수집 실패: {e}")
                results[category_id] = 0
        
        # 전체 결과 요약
        total_memos = sum(results.values())
        self.log_info(f"✅ 모든 카테고리 발품후기 수집 완료: {total_memos}개")
        
        return results
    
    async def collect_talks_by_date(self, target_date: str, service_id: int, limit_per_page: int = 24) -> int:
        """
        특정 날짜의 바비톡 자유톡을 수집하고 데이터베이스에 저장합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            service_id: 서비스 ID (79: 성형, 71: 쁘띠/피부, 72: 일상)
            limit_per_page: 페이지당 게시글 수 (기본값: 24)
        
        Returns:
            int: 수집된 자유톡 수
        """
        self.log_info(f"📅 {target_date} 날짜 바비톡 자유톡 수집 시작 (서비스 ID: {service_id})")
        
        # 바비톡 커뮤니티 생성 또는 조회
        babitalk_community = await self._get_or_create_babitalk_community()
        
        try:
            # API에서 해당 날짜의 자유톡 데이터 가져오기
            talks = await self.api.get_talks_by_date(target_date, service_id, limit_per_page)
            
            if not talks:
                self.log_info(f"📭 {target_date} 날짜의 자유톡이 없습니다.")
                return 0
            
            # 각 자유톡 처리
            total_talks = 0
            for talk in talks:
                try:
                    # 자유톡 정보 저장
                    talk_id = await self._save_talk(talk, babitalk_community['id'])
                    if talk_id:
                        total_talks += 1
                except Exception:
                    continue
            
            self.log_info(f"✅ {target_date} 날짜 자유톡 수집 완료: {total_talks}개")
            return total_talks
            
        except Exception as e:
            self.log_error(f"❌ 자유톡 수집 중 오류 발생: {e}")
            return 0
    
    async def collect_all_talks_by_date(self, target_date: str, limit_per_page: int = 24) -> Dict[int, int]:
        """
        특정 날짜의 모든 바비톡 자유톡 카테고리를 수집하고 데이터베이스에 저장합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            limit_per_page: 페이지당 게시글 수 (기본값: 24)
        
        Returns:
            Dict[int, int]: 카테고리별 수집된 자유톡 수
        """
        self.log_info(f"📅 {target_date} 날짜 바비톡 모든 자유톡 카테고리 수집 시작")
        
        results = {}
        
        # 모든 자유톡 카테고리 수집
        for service_id, category_name in self.api.TALK_SERVICE_CATEGORIES.items():
            try:
                count = await self.collect_talks_by_date(target_date, service_id, limit_per_page)
                results[service_id] = count
                
            except Exception as e:
                print(f"❌ {category_name} 카테고리 수집 실패: {e}")
                results[service_id] = 0
                continue
        
        # 전체 결과 요약
        total_talks = sum(results.values())
        print(f"✅ 모든 자유톡 카테고리 수집 완료: {total_talks}개")
        
        return results
    
    async def collect_comments_for_talk(self, talk_id: int) -> int:
        """
        특정 자유톡의 댓글을 수집하고 데이터베이스에 저장합니다.
        
        Args:
            talk_id: 자유톡 ID
        
        Returns:
            int: 수집된 댓글 수
        """
        print(f"💬 자유톡 ID {talk_id} 댓글 수집 시작")
        
        try:
            # 먼저 해당 자유톡이 데이터베이스에 있는지 확인
            article = self.db.get_article_by_platform_id_and_community_article_id("babitalk_talk", str(talk_id))
            
            if not article:
                print(f"⚠️  자유톡 ID {talk_id}가 데이터베이스에 없습니다. 먼저 자유톡을 수집해주세요.")
                return 0
            
            # 페이지 1에서 댓글 수집
            comments_page1, pagination = await self.api.get_comments(talk_id, page=1)
            
            if not comments_page1:
                print(f"📭 자유톡 ID {talk_id}에 댓글이 없습니다.")
                return 0
            
            total_comments = 0
            
            # 페이지 1 댓글 저장
            saved_count = await self._save_comments(comments_page1, article['id'])
            total_comments += saved_count
            
            # 댓글이 50개를 초과하는 경우 페이지 2도 수집
            if len(comments_page1) >= 50 and pagination.has_next:
                print(f"📄 댓글이 50개를 초과하여 페이지 2를 수집합니다.")
                
                # 페이지 2에서 댓글 수집
                comments_page2, _ = await self.api.get_comments(talk_id, page=2)
                
                if comments_page2:
                    saved_count = await self._save_comments(comments_page2, article['id'])
                    total_comments += saved_count
            
            print(f"✅ 자유톡 ID {talk_id} 댓글 수집 완료: {total_comments}개")
            return total_comments
            
        except Exception as e:
            print(f"❌ 댓글 수집 중 오류 발생: {e}")
            return 0
    
    async def collect_comments_for_talks_by_date(self, target_date: str, service_id: int, limit_per_page: int = 24) -> int:
        """
        특정 날짜의 자유톡들의 댓글을 수집하고 데이터베이스에 저장합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            service_id: 서비스 ID (79: 성형, 71: 쁘띠/피부, 72: 일상)
            limit_per_page: 페이지당 게시글 수 (기본값: 24)
        
        Returns:
            int: 수집된 댓글 수
        """
        print(f"💬 {target_date} 날짜 자유톡 댓글 수집 시작 (서비스 ID: {service_id})")
        
        try:
            # 해당 날짜의 자유톡 데이터 가져오기
            talks = await self.api.get_talks_by_date(target_date, service_id, limit_per_page)
            
            if not talks:
                print(f"📭 {target_date} 날짜의 자유톡이 없습니다.")
                return 0
            
            total_comments = 0
            
            # 각 자유톡의 댓글 수집
            for talk in talks:
                try:
                    comments_count = await self.collect_comments_for_talk(talk.id)
                    total_comments += comments_count
                    
                    # 자유톡 간 딜레이 (서버 부하 방지)
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"⚠️  자유톡 ID {talk.id} 댓글 수집 실패: {e}")
                    continue
            
            print(f"✅ {target_date} 날짜 자유톡 댓글 수집 완료: {total_comments}개")
            return total_comments
            
        except Exception as e:
            print(f"❌ 날짜별 댓글 수집 중 오류 발생: {e}")
            return 0
    
    async def _get_or_create_babitalk_community(self) -> Dict:
        """바비톡 커뮤니티 생성 또는 조회"""
        try:
            # 기존 바비톡 커뮤니티 조회
            existing_community = self.db.get_community_by_name("바비톡")
            
            if existing_community:
                return existing_community
            
            # 새 바비톡 커뮤니티 생성
            babitalk_community = Community(
                id=None,
                name="바비톡",
                created_at=datetime.now(),
                description="바비톡 시술 후기 커뮤니티"
            )
            
            community_id = self.db.insert_community(babitalk_community)
            
            return {
                'id': community_id,
                'name': '바비톡',
                'created_at': babitalk_community.created_at,
                'description': babitalk_community.description
            }
            
        except Exception as e:
            print(f"    ⚠️  바비톡 커뮤니티 생성 실패: {e}")
            raise e
    
    async def _save_review(self, review: BabitalkReview, community_id: int) -> Optional[int]:
        """후기 정보를 데이터베이스에 저장"""
        try:
            # JSON 데이터 변환
            categories_json = json.dumps(review.categories, ensure_ascii=False)
            sub_categories_json = json.dumps(review.sub_categories, ensure_ascii=False)
            images_json = json.dumps([{
                'id': img.id,
                'url': img.url,
                'small_url': img.small_url,
                'is_after': img.is_after,
                'order': img.order,
                'is_main': img.is_main,
                'is_blur': img.is_blur
            } for img in review.images], ensure_ascii=False)
            
            # 날짜 파싱
            try:
                created_at = datetime.strptime(review.created_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                created_at = datetime.now()
            
            # 후기 제목 생성 (카테고리 정보 활용)
            title = f"{', '.join(review.categories)} - {', '.join(review.sub_categories)}"
            
            # 병원명과 담당의명 추출
            hospital_name = review.hospital.name if review.hospital else ""
            doctor_name = review.search_doctor.name if review.search_doctor else ""
            
            db_review = Review(
                id=None,
                platform_id="babitalk",
                platform_review_id=str(review.id),
                community_id=community_id,
                title=title,
                content=review.text,
                images=images_json,
                writer_nickname=review.user.name,
                writer_id=str(review.user.id),
                like_count=0,  # 바비톡 API에는 좋아요 수가 없음
                rating=review.rating,
                price=review.price,
                categories=categories_json,
                sub_categories=sub_categories_json,
                surgery_date=review.surgery_date,
                hospital_name=hospital_name,
                doctor_name=doctor_name,
                is_blind=review.is_blind,
                is_image_blur=review.is_image_blur,
                is_certificated_review=review.is_certificated_review,
                created_at=created_at,
                collected_at=datetime.now()  # 수집 시간 기록
            )
            
            review_id = self.db.insert_review(db_review)
            return review_id
            
        except Exception as e:
            print(f"    ⚠️  후기 저장 실패: {e}")
            return None
    
    async def _save_event_ask_memo(self, memo: BabitalkEventAskMemo, community_id: int) -> Optional[int]:
        """발품후기 정보를 데이터베이스에 저장"""
        try:
            # 날짜 파싱 (first_write_at은 "20분전", "17시간전" 등의 형식이므로 현재 시간 기준으로 계산)
            try:
                created_at = self.api._parse_relative_time_to_date(memo.first_write_at)
            except Exception:
                created_at = datetime.now()
            
            # 발품후기 제목 생성 (카테고리 정보 활용)
            title = f"{memo.category} - {memo.region}"
            
            # 카테고리 정보를 JSON으로 변환
            categories_json = json.dumps([memo.category], ensure_ascii=False)
            sub_categories_json = json.dumps([], ensure_ascii=False)  # 발품후기에는 서브카테고리가 없음
            
            # 이미지는 빈 배열 (발품후기에는 이미지가 없음)
            images_json = json.dumps([], ensure_ascii=False)
            
            db_memo = Review(
                id=None,
                platform_id="babitalk_event_ask",  # 발품후기임을 구분하기 위한 플랫폼 ID
                platform_review_id=str(memo.id),
                community_id=community_id,
                title=title,
                content=memo.text,
                images=images_json,
                writer_nickname=memo.user.name,
                writer_id=str(memo.user.id),
                like_count=0,  # 바비톡 API에는 좋아요 수가 없음
                rating=memo.star_score,
                price=memo.real_price,
                categories=categories_json,
                sub_categories=sub_categories_json,
                surgery_date="",  # 발품후기에는 수술 날짜가 없음
                hospital_name=memo.hospital_name,
                doctor_name="",  # 발품후기에는 담당의 정보가 없음
                is_blind=False,  # 발품후기에는 블라인드 정보가 없음
                is_image_blur=False,  # 발품후기에는 이미지 블러 정보가 없음
                is_certificated_review=False,  # 발품후기에는 인증 후기 정보가 없음
                created_at=created_at,
                collected_at=datetime.now()  # 수집 시간 기록
            )
            
            memo_id = self.db.insert_review(db_memo)
            return memo_id
            
        except Exception as e:
            print(f"    ⚠️  발품후기 저장 실패: {e}")
            return None
    
    async def _save_talk(self, talk: BabitalkTalk, community_id: int) -> Optional[int]:
        """자유톡 정보를 데이터베이스에 저장"""
        try:
            # 날짜 파싱
            try:
                created_at = datetime.strptime(talk.created_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                created_at = datetime.now()
            
            # 이미지 정보를 JSON으로 변환
            images_json = json.dumps([{
                'id': img.id,
                'url': img.url,
                'small_url': img.small_url,
                'is_after': img.is_after,
                'order': img.order,
                'is_main': img.is_main,
                'is_blur': img.is_blur
            } for img in talk.images], ensure_ascii=False)
            
            # 서비스 카테고리명 가져오기
            service_category = self.api.TALK_SERVICE_CATEGORIES.get(talk.service_id, f"서비스{talk.service_id}")
            
            # 자유톡을 Article로 저장
            db_article = Article(
                id=None,
                platform_id="babitalk_talk",
                community_article_id=str(talk.id),
                community_id=community_id,
                title=talk.title,
                content=talk.text,
                writer_nickname=talk.user.name,
                writer_id=str(talk.user.id),
                like_count=0,  # 바비톡 API에는 좋아요 수가 없음
                comment_count=talk.total_comment,
                view_count=0,  # 바비톡 API에는 조회수가 없음
                images=images_json,
                created_at=created_at,
                category_name=service_category,
                collected_at=datetime.now()  # 수집 시간 기록
            )
            
            article_id = self.db.insert_article(db_article)
            return article_id
            
        except Exception as e:
            print(f"    ⚠️  자유톡 저장 실패: {e}")
            return None
    
    async def _save_comments(self, comments: List[BabitalkComment], article_id: int) -> int:
        """댓글 정보를 데이터베이스에 저장"""
        from database.models import Comment as DBComment
        
        saved_count = 0
        
        for comment in comments:
            try:
                # 삭제된 댓글이나 블라인드된 댓글은 건너뛰기
                if comment.is_del == 1 or comment.blind_at:
                    continue
                
                # 날짜 파싱
                try:
                    created_at = datetime.strptime(comment.created_at, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    created_at = datetime.now()
                
                # 댓글 저장
                db_comment = DBComment(
                    id=None,
                    article_id=article_id,
                    content=comment.text,
                    writer_nickname=comment.user.name,
                    writer_id=str(comment.user.id),
                    created_at=created_at,
                    parent_comment_id=comment.parent_id if not comment.is_parent else None,
                    collected_at=datetime.now()  # 수집 시간 기록
                )
                
                self.db.insert_comment(db_comment)
                saved_count += 1
                
            except Exception as e:
                print(f"        ⚠️  댓글 저장 실패: {e}")
                continue
        
        return saved_count
    
    def get_statistics(self) -> Dict:
        """바비톡 데이터 통계 조회"""
        return self.db.get_review_statistics()

# 테스트 함수
async def test_babitalk_collector():
    """바비톡 데이터 수집기 테스트"""
    print("🧪 바비톡 데이터 수집기 테스트 시작")
    print("=" * 50)
    
    collector = BabitalkDataCollector()
    
    try:
        # 자유톡 수집 테스트 (성형 카테고리, 오늘 날짜)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"📅 오늘 날짜({today}) 자유톡 수집 테스트")
        
        # 성형 카테고리 자유톡 수집 테스트
        talks_count = await collector.collect_talks_by_date(today, 79, limit_per_page=5)
        
        print(f"\n📊 자유톡 테스트 결과:")
        print(f"   저장된 자유톡: {talks_count}개")
        
        # 발품후기 수집 테스트 (눈 카테고리, 오늘 날짜)
        print(f"\n📅 오늘 날짜({today}) 발품후기 수집 테스트")
        
        # 눈 카테고리 발품후기 수집 테스트
        memos_count = await collector.collect_event_ask_memos_by_date(today, 3000, limit_per_page=5)
        
        print(f"\n📊 발품후기 테스트 결과:")
        print(f"   저장된 발품후기: {memos_count}개")
        
        # 통계 조회
        stats = collector.get_statistics()
        print(f"\n📈 데이터베이스 통계:")
        print(f"   전체 후기: {stats.get('total_reviews', 0)}개")
        print(f"   플랫폼별 후기: {stats.get('platform_stats', {})}")
        print(f"   오늘 후기: {stats.get('today_reviews', 0)}개")
        platform_stats = stats.get('platform_stats', {})
        if 'babitalk' in platform_stats:
            print(f"   바비톡 시술후기: {platform_stats['babitalk']}개")
        if 'babitalk_event_ask' in platform_stats:
            print(f"   바비톡 발품후기: {platform_stats['babitalk_event_ask']}개")
        print(f"   평점별 후기: {stats.get('rating_stats', {})}")
        
        # 댓글 수집 테스트
        if talks_count > 0:
            print(f"\n💬 댓글 수집 테스트")
            print(f"📝 수집된 자유톡 중 첫 번째 자유톡의 댓글을 수집합니다.")
            
            # 첫 번째 자유톡의 댓글 수집 테스트
            comments_count = await collector.collect_comments_for_talks_by_date(today, 79, limit_per_page=1)
            
            print(f"\n📊 댓글 테스트 결과:")
            print(f"   수집된 댓글: {comments_count}개")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print("=" * 50)
    print("🧪 바비톡 데이터 수집기 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_babitalk_collector()) 