import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
from platforms.gannamunni import GangnamUnniAPI, Article, Comment, Review
from database.models import DatabaseManager, Community, Article as DBArticle, Comment as DBComment
from utils.logger import LoggedClass

class GangnamUnniDataCollector(LoggedClass):
    def __init__(self, token: str = None):
        super().__init__("GangnamUnniCollector")
        self.api = GangnamUnniAPI(token=token)
        self.db = DatabaseManager()  # db_path 파라미터 제거
    
    async def collect_articles_by_date(self, target_date: str, category: str = "hospital_question", include_reviews: bool = True) -> Dict[str, int]:
        """
        특정 날짜의 강남언니 게시글과 리뷰를 수집하고 데이터베이스에 저장합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            category: 카테고리 (기본값: "hospital_question")
            include_reviews: True이면 실제 리뷰 API에서도 리뷰를 수집 (기본값: True)
        
        Returns:
            Dict[str, int]: {"articles": 수집된 게시글 수, "comments": 수집된 댓글 수, "reviews": 수집된 리뷰 수}
        """
        import time
        start_time = time.time()
        last_progress_time = start_time
        
        self.log_info(f"🚀 강남언니 {category} 수집 시작 - {target_date}")
        
        # 강남언니 커뮤니티 생성 또는 조회
        gangnamunni_community = await self._get_or_create_gannamunni_community()
        
        try:
            # API에서 해당 날짜의 게시글 데이터 가져오기
            articles = await self.api.get_articles_by_date(target_date, category=category)
            
            # 실제 리뷰 API에서 리뷰 수집 (include_reviews가 True인 경우)
            reviews = []
            if include_reviews:
                reviews = await self.api.get_reviews_by_date(target_date)
            
            if not articles and not reviews:
                end_time = time.time()
                elapsed_time = end_time - start_time
                self.log_info(f"📭 {target_date} 수집할 데이터 없음 (소요시간: {elapsed_time:.2f}초)")
                return {"articles": 0, "comments": 0, "reviews": 0}
            
            # 1. 리뷰 먼저 저장 (실제 리뷰 데이터만)
            total_articles = 0
            total_comments = 0
            total_reviews = 0
            
            if reviews:
                batch_size = 3  # 한 번에 처리할 리뷰 수 (상세 API 호출로 인해 작게 설정)
                for i in range(0, len(reviews), batch_size):
                    batch_reviews = reviews[i:i + batch_size]
                    
                    # 배치 내에서 순차 처리 (API 부하 방지)
                    for review in batch_reviews:
                        try:
                            # 중복 체크: 이미 저장된 리뷰인지 확인
                            existing_review = self.db.get_review_by_platform_id_and_platform_review_id("gangnamunni_review", str(review.id))
                            if existing_review:
                                continue
                            
                            # 리뷰 정보 저장
                            review_id = await self._save_review(review, gangnamunni_community['id'])
                            if review_id:
                                total_reviews += 1
                            
                        except Exception as e:
                            self.log_error(f"❌ 리뷰 처리 실패 (ID: {review.id}): {e}")
                            continue
                    
                    # 배치 간 딜레이 (API 부하 방지)
                    if i + batch_size < len(reviews):
                        await asyncio.sleep(3)
                    
                    # 10분마다 진행상태 로그
                    current_time = time.time()
                    if current_time - last_progress_time >= 600:  # 10분 = 600초
                        self.log_info(f"📊 리뷰 수집 진행중... {i+1}/{len(reviews)} (저장: {total_reviews}개)")
                        last_progress_time = current_time
            
            # 2. 게시글 저장 (리뷰가 아닌 일반 게시글)
            if articles:
                for i, article in enumerate(articles):
                    try:
                        # 중복 체크: 이미 저장된 게시글인지 확인
                        existing_article = self.db.get_article_by_platform_id_and_community_article_id("gangnamunni", str(article.id))
                        article_id = None
                        
                        if existing_article:
                            article_id = existing_article['id']  # 기존 게시글의 DB ID 사용
                        else:
                            # 게시글 정보 저장 (리뷰가 아닌 일반 게시글)
                            article_id = await self._save_article(article, gangnamunni_community['id'])
                            if article_id:
                                total_articles += 1
                        
                        # 댓글이 있는 경우 댓글 수집 (게시글이 중복이어도 댓글은 수집)
                        if article_id and article.comment_count > 0:
                            try:
                                comments = await self.api.get_comments(article.id)
                                if comments:
                                    saved_comments = await self._save_comments(comments, article_id)
                                    total_comments += saved_comments
                            except Exception as e:
                                # 404 에러 발생 시 failover 처리
                                if "404" in str(e) or "Not Found" in str(e):
                                    self.log_error(f"❌ 404 에러 발생: 게시글 ID {article.id} 댓글 수집 실패")
                                    await self._handle_404_failover(target_date, category, gangnamunni_community, articles, i)
                                    return {"articles": total_articles, "comments": total_comments, "reviews": total_reviews}
                                else:
                                    self.log_error(f"❌ 댓글 수집 실패 (게시글 ID: {article.id}): {e}")
                        
                        # 10분마다 진행상태 로그
                        current_time = time.time()
                        if current_time - last_progress_time >= 600:  # 10분 = 600초
                            self.log_info(f"📊 게시글 수집 진행중... {i+1}/{len(articles)} (게시글: {total_articles}개, 댓글: {total_comments}개)")
                            last_progress_time = current_time
                        
                    except Exception as e:
                        # 404 에러 발생 시 failover 처리
                        if "404" in str(e) or "Not Found" in str(e):
                            self.log_error(f"❌ 404 에러 발생: 게시글 ID {article.id} 처리 실패")
                            await self._handle_404_failover(target_date, category, gangnamunni_community, articles, i)
                            return {"articles": total_articles, "comments": total_comments, "reviews": total_reviews}
                        else:
                            self.log_error(f"❌ 게시글 처리 실패 (ID: {article.id}): {e}")
                            continue
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 수집 완료 로그
            self.log_info(f"✅ 강남언니 {category} 수집 완료 - {target_date}")
            self.log_info(f"📊 결과: 게시글 {total_articles}개, 댓글 {total_comments}개, 리뷰 {total_reviews}개 (소요시간: {elapsed_time:.2f}초)")
            
            return {"articles": total_articles, "comments": total_comments, "reviews": total_reviews}
            
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 404 에러 발생 시 failover 처리
            if "404" in str(e) or "Not Found" in str(e):
                self.log_error(f"❌ 404 에러 발생: {target_date} 날짜 게시글 목록 조회 실패 (소요시간: {elapsed_time:.2f}초)")
                await self._handle_404_failover(target_date, category, gangnamunni_community, [], 0)
                return {"articles": 0, "comments": 0}
            else:
                self.log_error(f"❌ 날짜별 게시글 수집 중 오류 발생: {e} (소요시간: {elapsed_time:.2f}초)")
                return {"articles": 0, "comments": 0}
    
    async def _handle_404_failover(self, target_date: str, category: str, 
                                 gangnamunni_community: Dict, articles: List[Article], failed_index: int):
        """
        404 에러 발생 시 failover 처리를 수행합니다.
        
        Args:
            target_date: 수집할 날짜
            category: 카테고리
            gangnamunni_community: 강남언니 커뮤니티 정보
            articles: 수집된 게시글 목록
            failed_index: 실패한 게시글의 인덱스
        """
        import time
        failover_start_time = time.time()
        
        self.log_error(f"🔄 404 에러로 인한 수집 중단. 15분 후 실패 지점부터 재시작합니다.")
        self.log_error(f"📊 실패 지점: {failed_index + 1}번째 게시글 (총 {len(articles)}개 중)")
        
        # 15분 대기
        self.log_info("⏰ 15분 대기 중...")
        await asyncio.sleep(15 * 60)  # 15분 = 900초
        
        self.log_info("🔄 수집 재개를 시작합니다.")
        
        # 실패한 게시글부터 다시 수집
        remaining_articles = articles[failed_index:]
        total_articles = len(articles) - failed_index
        total_comments = 0
        
        for i, article in enumerate(remaining_articles):
            try:
                self.log_info(f"🔄 재시작 수집 진행 중: {i + 1}/{total_articles} (게시글 ID: {article.id})")
                
                # 게시글 정보 저장 (일반 게시글로 저장)
                article_id = await self._save_article(article, gangnamunni_community['id'])
                
                if article_id:
                    # 댓글이 있는 경우 댓글도 수집
                    if article.comment_count > 0:
                        try:
                            comments = await self.api.get_comments(article.id)
                            if comments:
                                saved_comments = await self._save_comments(comments, article_id)
                                total_comments += saved_comments
                        except Exception as e:
                            if "404" in str(e) or "Not Found" in str(e):
                                self.log_error(f"❌ 재시작 중에도 404 에러 발생: 게시글 ID {article.id} 댓글 수집 실패")
                                # 재시작 중에도 404 에러가 발생하면 다시 failover 처리
                                await self._handle_404_failover(target_date, category, gangnamunni_community, remaining_articles, i)
                                return
                            else:
                                self.log_error(f"❌ 재시작 중 댓글 수집 실패 (게시글 ID: {article.id}): {e}")
                
            except Exception as e:
                if "404" in str(e) or "Not Found" in str(e):
                    self.log_error(f"❌ 재시작 중에도 404 에러 발생: 게시글 ID {article.id} 처리 실패")
                    # 재시작 중에도 404 에러가 발생하면 다시 failover 처리
                    await self._handle_404_failover(target_date, category, gangnamunni_community, remaining_articles, i)
                    return
                else:
                    self.log_error(f"❌ 재시작 중 게시글 처리 실패 (ID: {article.id}): {e}")
                    continue
        
        failover_end_time = time.time()
        failover_elapsed_time = failover_end_time - failover_start_time
        
        self.log_info(f"✅ 재시작 수집 완료!")
        self.log_info(f"📊 재시작 수집 결과: 게시글 {total_articles}개, 댓글 {total_comments}개")
        self.log_info(f"⏱️  재시작 소요시간: {failover_elapsed_time:.2f}초")

    async def collect_all_categories_by_date(self, target_date: str, include_reviews: bool = True) -> Dict[str, int]:
        """
        특정 날짜의 모든 카테고리 게시글과 리뷰를 수집하고 데이터베이스에 저장합니다.
        
        Args:
            target_date: 수집할 날짜 (YYYY-MM-DD 형식)
            include_reviews: True이면 실제 리뷰 API에서도 리뷰를 수집 (기본값: True)
        
        Returns:
            Dict[str, int]: 카테고리별 수집된 게시글 수
        """
        import time
        start_time = time.time()
        self.log_info(f"📅 {target_date} 날짜 강남언니 모든 카테고리 게시글 수집 시작...")
        
        categories = {
            "hospital_question": "병원질문",
            "surgery_question": "시술/수술질문", 
            "free_chat": "자유수다",
            "review": "발품후기",
            "ask_doctor": "의사에게 물어보세요"
        }
        
        results = {}
        total_articles = 0
        total_comments = 0
        total_reviews = 0
        
        # 모든 카테고리 순회
        for category_key, category_name in categories.items():
            try:
                self.log_info(f"🔄 {category_name} 카테고리 수집 중...")
                result = await self.collect_articles_by_date(target_date, category_key, include_reviews)
                results[category_key] = result["articles"]
                total_articles += result["articles"]
                total_comments += result["comments"]
                total_reviews += result.get("reviews", 0)
                
                # 카테고리 간 딜레이 (서버 부하 방지)
                await asyncio.sleep(2)
                
            except Exception as e:
                # 404 에러 발생 시 failover 처리
                if "404" in str(e) or "Not Found" in str(e):
                    self.log_error(f"❌ 404 에러 발생: {category_name} 카테고리 수집 실패")
                    self.log_error(f"🔄 15분 후 {category_name} 카테고리부터 재시작합니다.")
                    
                    # 15분 대기
                    self.log_info("⏰ 15분 대기 중...")
                    await asyncio.sleep(15 * 60)  # 15분 = 900초
                    
                    self.log_info(f"🔄 {category_name} 카테고리 수집 재개를 시작합니다.")
                    
                    try:
                        result = await self.collect_articles_by_date(target_date, category_key, include_reviews)
                        results[category_key] = result["articles"]
                        total_articles += result["articles"]
                        total_comments += result["comments"]
                        total_reviews += result.get("reviews", 0)
                    except Exception as retry_e:
                        self.log_error(f"❌ 재시작 후에도 {category_name} 카테고리 수집 실패: {retry_e}")
                        results[category_key] = 0
                else:
                    self.log_error(f"❌ {category_name} 카테고리 수집 실패: {e}")
                    results[category_key] = 0
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 전체 결과 요약
        self.log_info(f"✅ 모든 카테고리 게시글 및 리뷰 수집 완료!")
        self.log_info(f"📊 전체 수집 결과: 게시글 {total_articles}개, 댓글 {total_comments}개, 리뷰 {total_reviews}개")
        self.log_info(f"⏱️  총 소요시간: {elapsed_time:.2f}초")
        
        # 카테고리별 상세 결과
        self.log_info(f"📋 카테고리별 수집 결과:")
        for category_key, category_name in categories.items():
            count = results.get(category_key, 0)
            self.log_info(f"   - {category_name}: {count}개")
        
        return results
    
    async def _get_or_create_gannamunni_community(self) -> Dict:
        """강남언니 커뮤니티 생성 또는 조회"""
        try:
            # 기존 강남언니 커뮤니티 조회
            existing_community = self.db.get_community_by_name("강남언니")
            
            if existing_community:
                return existing_community
            
            # 새 강남언니 커뮤니티 생성
            gangnamunni_community = Community(
                id=None,
                name="강남언니",
                created_at=datetime.now(),
                description="강남언니 커뮤니티"
            )
            
            community_id = self.db.insert_community(gangnamunni_community)
            
            return {
                'id': community_id,
                'name': '강남언니',
                'created_at': gangnamunni_community.created_at,
                'description': gangnamunni_community.description
            }
            
        except Exception as e:
            print(f"    ⚠️  강남언니 커뮤니티 생성 실패: {e}")
            raise e
    
    async def _save_article(self, article: Article, community_id: int) -> Optional[int]:
        """게시글 정보를 데이터베이스에 저장"""
        try:
            # 날짜 파싱
            try:
                created_at = datetime.strptime(article.create_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                created_at = datetime.now()
            
            # 이미지 정보를 JSON으로 변환
            images_json = json.dumps([{'url': photo.url} for photo in article.photos], ensure_ascii=False)
            
            # 게시글을 Article로 저장
            db_article = DBArticle(
                id=None,
                platform_id="gangnamunni",
                community_article_id=str(article.id),
                community_id=community_id,
                title=article.title or f"강남언니 게시글 {article.id}",
                content=article.contents,
                writer_nickname=article.writer.nickname,
                writer_id=str(article.writer.id),
                like_count=article.thumb_up_count,
                comment_count=article.comment_count,
                view_count=article.view_count,
                images=images_json,
                created_at=created_at,
                category_name=article.category_name,
                collected_at=datetime.now()  # 수집 시간 기록
            )
            
            article_id = self.db.insert_article(db_article)
            return article_id
            
        except Exception as e:
            print(f"    ⚠️  게시글 저장 실패: {e}")
            return None
    
    async def _save_as_review(self, article: Article, community_id: int) -> Optional[int]:
        """게시글을 후기로 저장 (강남언니 후기 데이터용)"""
        try:
            from database.models import Review
            
            # 날짜 파싱
            try:
                created_at = datetime.strptime(article.create_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                created_at = datetime.now()
            
            # 이미지 정보를 JSON으로 변환
            images_json = json.dumps([{'url': photo.url} for photo in article.photos], ensure_ascii=False)
            
            # 게시글을 Review로 저장
            db_review = Review(
                id=None,
                platform_id="gangnamunni",
                platform_review_id=str(article.id),
                community_id=community_id,
                title=article.title or f"강남언니 후기 {article.id}",
                content=article.contents,
                images=images_json,
                writer_nickname=article.writer.nickname,
                writer_id=str(article.writer.id),
                like_count=article.thumb_up_count,
                rating=0,  # 강남언니에는 평점이 없음
                price=0,   # 강남언니에는 가격이 없음
                categories=json.dumps([article.category_name], ensure_ascii=False),
                sub_categories=json.dumps([], ensure_ascii=False),
                surgery_date="",  # 강남언니에는 수술 날짜가 없음
                hospital_name="",  # 강남언니에는 병원명이 없음
                doctor_name="",    # 강남언니에는 담당의명이 없음
                is_blind=False,
                is_image_blur=False,
                is_certificated_review=False,
                created_at=created_at,
                collected_at=datetime.now()  # 수집 시간 기록
            )
            
            review_id = self.db.insert_review(db_review)
            return review_id
            
        except Exception as e:
            print(f"    ⚠️  후기 저장 실패: {e}")
            return None
    
    async def _save_comments(self, comments: List[Comment], article_id: int) -> int:
        """댓글 정보를 데이터베이스에 저장"""
        saved_count = 0
        
        for comment in comments:
            try:
                # 중복 체크: 이미 저장된 댓글인지 확인
                existing_comment = self.db.get_comment_by_article_id_and_comment_id(str(article_id), str(comment.id))
                if existing_comment:
                    continue
                
                # 날짜 파싱
                try:
                    created_at = datetime.strptime(comment.create_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    created_at = datetime.now()
                
                # 댓글 저장 - 개선된 방식 사용
                db_comment = DBComment(
                    id=str(comment.id),  # 강남언니 댓글 ID
                    article_id=article_id,  # 데이터베이스의 article ID (숫자)
                    content=comment.contents,
                    writer_nickname=comment.writer.nickname,
                    writer_id=str(comment.writer.id),
                    created_at=created_at,
                    parent_comment_id=str(comment.reply_comment_id) if comment.reply_comment_id else None,
                    collected_at=datetime.now()
                )
                
                # 플랫폼 정보 추가
                db_comment.platform_id = "gangnamunni"
                
                self.db.insert_comment(db_comment)
                saved_count += 1
                
                # 대댓글이 있는 경우 재귀적으로 저장
                if comment.replies:
                    replies_saved = await self._save_comments(comment.replies, article_id)
                    saved_count += replies_saved
                
            except Exception as e:
                self.log_error(f"        ❌ 댓글 저장 실패 (ID: {comment.id}): {e}")
                continue
        
        return saved_count
    
    async def _save_review(self, review: Review, community_id: int) -> Optional[int]:
        """리뷰 정보를 데이터베이스에 저장 (상세 API 호출)"""
        try:
            from database.models import Review as DBReview
            
            # 리뷰 상세 정보 조회
            self.log_info(f"🔍 리뷰 상세 정보 조회 중... (ID: {review.id})")
            review_detail = await self.api.get_review_detail(review.id)
            
            if not review_detail:
                self.log_error(f"❌ 리뷰 상세 정보 조회 실패 (ID: {review.id})")
                return None
            
            # 날짜 파싱
            try:
                created_at = datetime.fromisoformat(review.postedAtUtc.replace('Z', '+00:00'))
            except ValueError:
                created_at = datetime.now()
            
            # 상세 정보에서 데이터 추출
            hospital_info = review_detail.get("hospital", {})
            doctors_info = review_detail.get("doctors", [])
            description_info = review_detail.get("description", {})
            
            # 시술 정보를 JSON으로 변환
            treatments_json = json.dumps([{
                'id': treatment.id,
                'name': treatment.name
            } for treatment in review.treatments], ensure_ascii=False)
            
            # 병원 정보를 JSON으로 변환
            hospital_json = json.dumps({
                'id': hospital_info.get('id', 0),
                'name': hospital_info.get('name', ''),
                'districtName': hospital_info.get('district', ''),
                'country': hospital_info.get('country', '')
            }, ensure_ascii=False)
            
            # 이미지 정보를 JSON으로 변환
            before_photos = review_detail.get("beforePhotos", [])
            after_photos = review_detail.get("afterPhotos", [])
            progress_photos = review_detail.get("progressPhotos", [])
            
            images_json = json.dumps({
                'beforePhotos': [photo.get('url', '') for photo in before_photos],
                'afterPhotos': [photo.get('url', '') for photo in after_photos],
                'progressReviewPhotos': [{
                    'url': photo.get('url', ''),
                    'progressDate': photo.get('progressDate', '')
                } for photo in progress_photos]
            }, ensure_ascii=False)
            
            # 시술 정보를 JSON으로 변환
            amplitude_info = review.amplitudeTreatmentInfo
            categories_json = json.dumps(amplitude_info.treatmentCategoryTagLabelList, ensure_ascii=False)
            sub_categories_json = json.dumps(amplitude_info.treatmentGroupTagLabelList, ensure_ascii=False)
            
            # 비용 정보
            price = 0
            if review.totalCost:
                price = review.totalCost.amount
            
            # 리뷰 제목 생성
            treatment_names = [t.name for t in review.treatments]
            title = f"{', '.join(treatment_names)} - {hospital_info.get('name', '')}"
            
            # 의사명 추출
            doctor_name = ""
            if doctors_info:
                doctor_name = doctors_info[0].get('name', '')
            
            # 리뷰 내용 (상세 API의 description.source.contents 사용)
            content = review.description
            if description_info and description_info.get('source'):
                content = description_info['source'].get('contents', review.description)
            
            # 리뷰를 Review로 저장
            db_review = DBReview(
                id=None,
                platform_id="gangnamunni_review",
                platform_review_id=str(review.id),
                community_id=community_id,
                title=title,
                content=content,
                images=images_json,
                writer_nickname=review.author.nickName,
                writer_id=str(review.author.id),
                like_count=0,  # 강남언니 리뷰에는 좋아요 수가 없음
                rating=review.totalRating,
                price=price,
                categories=categories_json,
                sub_categories=sub_categories_json,
                surgery_date=review.treatmentReceivedAtUtc,
                hospital_name=hospital_info.get('name', ''),
                doctor_name=doctor_name,
                is_blind=False,
                is_image_blur=False,
                is_certificated_review=review.procedureProofApproved,
                created_at=created_at,
                collected_at=datetime.now()  # 수집 시간 기록
            )
            
            review_id = self.db.insert_review(db_review)
            self.log_info(f"✅ 리뷰 저장 완료 (ID: {review.id}, DB ID: {review_id})")
            return review_id
            
        except Exception as e:
            self.log_error(f"❌ 리뷰 저장 실패 (ID: {review.id}): {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """강남언니 데이터 통계 조회"""
        return self.db.get_statistics()

# 테스트 함수
async def test_gannamunni_collector():
    """강남언니 데이터 수집기 테스트"""
    print("🧪 강남언니 데이터 수집기 테스트 시작")
    print("=" * 50)
    
    collector = GangnamUnniDataCollector()
    
    try:
        # 게시글 수집 테스트 (오늘 날짜, 병원질문 카테고리)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"📅 오늘 날짜({today}) 게시글 수집 테스트")
        
        # 병원질문 카테고리 게시글 수집 테스트
        articles_count = await collector.collect_articles_by_date(today, "hospital_question", include_reviews=False)
        
        print(f"\n📊 게시글 테스트 결과:")
        print(f"   저장된 게시글: {articles_count['articles']}개")
        
        # 리뷰 수집 테스트
        print(f"\n📅 오늘 날짜({today}) 리뷰 수집 테스트")
        
        reviews_count = await collector.collect_articles_by_date(today, "review", include_reviews=True)
        
        print(f"\n📊 리뷰 테스트 결과:")
        print(f"   저장된 리뷰: {reviews_count['reviews']}개")
        
        # 통계 조회
        stats = collector.get_statistics()
        print(f"\n📈 데이터베이스 통계:")
        print(f"   전체 게시글: {stats['total_articles']}개")
        print(f"   전체 댓글: {stats['total_comments']}개")
        print(f"   전체 커뮤니티: {stats['total_communities']}개")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print("=" * 50)
    print("🧪 강남언니 데이터 수집기 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_gannamunni_collector()) 