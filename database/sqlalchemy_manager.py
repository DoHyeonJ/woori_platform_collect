from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text
from database.config import db_config
from database.sqlalchemy_models import (
    Community, Client, Article, Comment, ExcludedArticle, Review
)
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SQLAlchemyDatabaseManager:
    """SQLAlchemy 기반 데이터베이스 매니저"""
    
    def __init__(self):
        self.db_config = db_config
    
    def get_session(self) -> Session:
        """데이터베이스 세션 반환"""
        return next(self.db_config.get_session())
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            self.db_config.create_tables()
            logger.info("데이터베이스가 성공적으로 초기화되었습니다.")
        except Exception as e:
            logger.error(f"데이터베이스 초기화 중 오류 발생: {e}")
            raise
    
    # Community 관련 메서드
    def insert_community(self, name: str, description: str = "") -> int:
        """커뮤니티 추가 (중복 체크 포함)"""
        session = self.get_session()
        try:
            # 기존 커뮤니티 확인
            existing = session.query(Community).filter(Community.name == name).first()
            if existing:
                return existing.id
            
            # 새 커뮤니티 생성
            community = Community(
                name=name,
                description=description,
                created_at=datetime.now()
            )
            session.add(community)
            session.commit()
            return community.id
        except Exception as e:
            session.rollback()
            logger.error(f"커뮤니티 추가 중 오류 발생: {e}")
            raise
        finally:
            session.close()
    
    def get_community_by_name(self, name: str) -> Optional[Dict]:
        """이름으로 커뮤니티 조회"""
        session = self.get_session()
        try:
            community = session.query(Community).filter(Community.name == name).first()
            if community:
                return {
                    'id': community.id,
                    'name': community.name,
                    'created_at': community.created_at.isoformat() if community.created_at else None,
                    'description': community.description
                }
            return None
        finally:
            session.close()
    
    # Client 관련 메서드
    def insert_client(self, hospital_name: str, description: str = "") -> int:
        """클라이언트 추가"""
        session = self.get_session()
        try:
            client = Client(
                hospital_name=hospital_name,
                description=description,
                created_at=datetime.now()
            )
            session.add(client)
            session.commit()
            return client.id
        except Exception as e:
            session.rollback()
            logger.error(f"클라이언트 추가 중 오류 발생: {e}")
            raise
        finally:
            session.close()
    
    # Article 관련 메서드
    def insert_article(self, article_data: Dict) -> int:
        """게시글 추가 (중복 체크 포함)"""
        session = self.get_session()
        try:
            # 기존 게시글 확인
            existing = session.query(Article).filter(
                and_(
                    Article.platform_id == article_data['platform_id'],
                    Article.community_article_id == article_data['community_article_id']
                )
            ).first()
            
            if existing:
                return existing.id
            
            # 새 게시글 생성
            article = Article(
                platform_id=article_data['platform_id'],
                community_article_id=article_data['community_article_id'],
                community_id=article_data['community_id'],
                title=article_data.get('title'),
                content=article_data['content'],
                images=article_data.get('images'),
                writer_nickname=article_data['writer_nickname'],
                writer_id=article_data['writer_id'],
                like_count=article_data.get('like_count', 0),
                comment_count=article_data.get('comment_count', 0),
                view_count=article_data.get('view_count', 0),
                created_at=article_data.get('created_at', datetime.now()),
                category_name=article_data.get('category_name'),
                collected_at=article_data.get('collected_at', datetime.now())
            )
            session.add(article)
            session.commit()
            return article.id
        except Exception as e:
            session.rollback()
            logger.error(f"게시글 추가 중 오류 발생: {e}")
            raise
        finally:
            session.close()
    
    def get_articles_by_date(self, date: str, community_id: Optional[int] = None) -> List[Dict]:
        """특정 날짜의 게시글 조회"""
        session = self.get_session()
        try:
            query = session.query(Article).filter(func.date(Article.created_at) == date)
            
            if community_id:
                query = query.filter(Article.community_id == community_id)
            
            articles = query.order_by(desc(Article.created_at)).all()
            
            return [self._article_to_dict(article) for article in articles]
        finally:
            session.close()
    
    def get_article_by_platform_id_and_community_article_id(self, platform_id: str, community_article_id: str) -> Optional[Dict]:
        """플랫폼 ID와 커뮤니티 게시글 ID로 게시글 조회"""
        session = self.get_session()
        try:
            article = session.query(Article).filter(
                and_(
                    Article.platform_id == platform_id,
                    Article.community_article_id == community_article_id
                )
            ).first()
            
            if article:
                return self._article_to_dict(article)
            return None
        finally:
            session.close()
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """ID로 게시글 조회"""
        session = self.get_session()
        try:
            article = session.query(Article).filter(Article.id == article_id).first()
            if article:
                return self._article_to_dict(article)
            return None
        finally:
            session.close()
    
    def get_review_by_id(self, review_id: int) -> Optional[Dict]:
        """ID로 후기 조회"""
        session = self.get_session()
        try:
            review = session.query(Review).filter(Review.id == review_id).first()
            if review:
                return self._review_to_dict(review)
            return None
        finally:
            session.close()
    
    def get_review_by_platform_id_and_platform_review_id(self, platform_id: str, platform_review_id: str) -> Optional[Dict]:
        """플랫폼 ID와 플랫폼 후기 ID로 후기 조회"""
        session = self.get_session()
        try:
            review = session.query(Review).filter(
                and_(
                    Review.platform_id == platform_id,
                    Review.platform_review_id == platform_review_id
                )
            ).first()
            
            if review:
                return self._review_to_dict(review)
            return None
        finally:
            session.close()
    
    def get_articles_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Dict]:
        """필터 조건에 따라 게시글 조회"""
        session = self.get_session()
        try:
            query = session.query(Article)
            
            if "platform_id" in filters:
                query = query.filter(Article.platform_id == filters["platform_id"])
            
            if "category_name" in filters:
                query = query.filter(Article.category_name == filters["category_name"])
            
            articles = query.order_by(desc(Article.created_at)).offset(offset).limit(limit).all()
            
            return [self._article_to_dict(article) for article in articles]
        finally:
            session.close()
    
    def get_articles_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 게시글 수 반환"""
        session = self.get_session()
        try:
            query = session.query(Article)
            
            if "platform_id" in filters:
                query = query.filter(Article.platform_id == filters["platform_id"])
            
            if "category_name" in filters:
                query = query.filter(Article.category_name == filters["category_name"])
            
            return query.count()
        finally:
            session.close()
    
    # Comment 관련 메서드
    def insert_comment(self, comment_data: Dict) -> int:
        """댓글 추가 (중복 체크 포함)"""
        session = self.get_session()
        try:
            # article_id가 직접 제공된 경우 (추천 방식)
            if 'article_id' in comment_data and comment_data['article_id']:
                article_id = comment_data['article_id']
                
                # article이 존재하는지 확인
                article = session.query(Article).filter(Article.id == article_id).first()
                if not article:
                    raise ValueError(f"article_id {article_id}에 해당하는 게시글을 찾을 수 없습니다.")
                
                platform_id = article.platform_id
                community_article_id = article.community_article_id
                
            else:
                # 레거시 방식: platform_id와 community_article_id로 검색
                if 'platform_id' not in comment_data or 'community_article_id' not in comment_data:
                    raise ValueError("article_id 또는 (platform_id, community_article_id)가 필요합니다.")
                
                platform_id = comment_data['platform_id']
                community_article_id = comment_data['community_article_id']
                
                # 해당 게시글 찾기
                article = session.query(Article).filter(
                    and_(
                        Article.platform_id == platform_id,
                        Article.community_article_id == community_article_id
                    )
                ).first()
                
                if not article:
                    raise ValueError(f"플랫폼 ID '{platform_id}', 게시글 ID '{community_article_id}'에 해당하는 게시글을 찾을 수 없습니다.")
                
                article_id = article.id
            
            # 댓글 중복 체크
            community_comment_id = comment_data.get('community_comment_id', '')
            if community_comment_id:
                existing_comment = session.query(Comment).filter(
                    and_(
                        Comment.platform_id == platform_id,
                        Comment.community_comment_id == community_comment_id
                    )
                ).first()
                
                if existing_comment:
                    logger.info(f"댓글이 이미 존재합니다: {community_comment_id}")
                    return existing_comment.id
            
            # 새 댓글 생성
            comment = Comment(
                platform_id=platform_id,
                community_article_id=community_article_id,
                community_comment_id=community_comment_id,
                content=comment_data['content'],
                writer_nickname=comment_data['writer_nickname'],
                writer_id=comment_data['writer_id'],
                created_at=comment_data.get('created_at', datetime.now()),
                parent_comment_id=comment_data.get('parent_comment_id'),
                collected_at=comment_data.get('collected_at', datetime.now()),
                article_id=article_id
            )
            session.add(comment)
            session.commit()
            # logger.info(f"댓글 저장 완료: ID {comment.id}, 게시글 ID {article_id}")
            return comment.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"댓글 추가 중 오류 발생: {e}")
            raise
        finally:
            session.close()
    
    def get_comments_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Dict]:
        """필터 조건에 따라 댓글 조회"""
        session = self.get_session()
        try:
            query = session.query(Comment)
            
            if "platform_id" in filters:
                query = query.filter(Comment.platform_id == filters["platform_id"])
            
            if "community_article_id" in filters:
                query = query.filter(Comment.community_article_id == filters["community_article_id"])
            
            if "article_id" in filters:
                query = query.filter(Comment.article_id == filters["article_id"])
            
            comments = query.order_by(desc(Comment.created_at)).offset(offset).limit(limit).all()
            
            return [self._comment_to_dict(comment) for comment in comments]
        finally:
            session.close()
    
    def get_comment_by_id(self, comment_id: int) -> Optional[Dict]:
        """ID로 댓글 조회"""
        session = self.get_session()
        try:
            comment = session.query(Comment).filter(Comment.id == comment_id).first()
            if comment:
                return self._comment_to_dict(comment)
            return None
        finally:
            session.close()
    
    def get_comments_count_by_article_id(self, article_id: int) -> int:
        """특정 게시글의 댓글 수 조회"""
        session = self.get_session()
        try:
            return session.query(Comment).filter(Comment.article_id == article_id).count()
        finally:
            session.close()
    
    def get_comments_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 댓글 수 반환"""
        session = self.get_session()
        try:
            query = session.query(Comment)
            
            if "platform_id" in filters:
                query = query.filter(Comment.platform_id == filters["platform_id"])
            
            if "community_article_id" in filters:
                query = query.filter(Comment.community_article_id == filters["community_article_id"])
            
            if "article_id" in filters:
                query = query.filter(Comment.article_id == filters["article_id"])
            
            return query.count()
        finally:
            session.close()
    
    # Review 관련 메서드
    def insert_review(self, review_data: Dict) -> int:
        """후기 추가 (중복 체크 포함)"""
        session = self.get_session()
        try:
            # 기존 후기 확인
            existing = session.query(Review).filter(
                and_(
                    Review.platform_id == review_data['platform_id'],
                    Review.platform_review_id == review_data['platform_review_id']
                )
            ).first()
            
            if existing:
                return existing.id
            
            # 새 후기 생성
            review = Review(
                platform_id=review_data['platform_id'],
                platform_review_id=review_data['platform_review_id'],
                community_id=review_data['community_id'],
                title=review_data.get('title'),
                content=review_data['content'],
                images=review_data.get('images'),
                writer_nickname=review_data['writer_nickname'],
                writer_id=review_data['writer_id'],
                like_count=review_data.get('like_count', 0),
                rating=review_data.get('rating', 0),
                price=review_data.get('price', 0),
                categories=review_data.get('categories'),
                sub_categories=review_data.get('sub_categories'),
                surgery_date=review_data.get('surgery_date'),
                hospital_name=review_data.get('hospital_name'),
                doctor_name=review_data.get('doctor_name'),
                is_blind=review_data.get('is_blind', False),
                is_image_blur=review_data.get('is_image_blur', False),
                is_certificated_review=review_data.get('is_certificated_review', False),
                created_at=review_data.get('created_at', datetime.now()),
                collected_at=review_data.get('collected_at', datetime.now())
            )
            session.add(review)
            session.commit()
            return review.id
        except Exception as e:
            session.rollback()
            logger.error(f"후기 추가 중 오류 발생: {e}")
            raise
        finally:
            session.close()
    
    def get_reviews_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Dict]:
        """필터 조건에 따라 후기 조회"""
        session = self.get_session()
        try:
            query = session.query(Review)
            
            if "platform_id" in filters:
                query = query.filter(Review.platform_id == filters["platform_id"])
            
            if "category_name" in filters:
                query = query.filter(Review.title.contains(filters["category_name"]))
            
            reviews = query.order_by(desc(Review.created_at)).offset(offset).limit(limit).all()
            
            return [self._review_to_dict(review) for review in reviews]
        finally:
            session.close()
    
    def get_recent_reviews(self, limit: int = 10) -> List[Dict]:
        """최근 후기들을 조회합니다."""
        session = self.get_session()
        try:
            reviews = session.query(Review).order_by(desc(Review.created_at)).limit(limit).all()
            return [self._review_to_dict(review) for review in reviews]
        finally:
            session.close()
    
    def get_reviews_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 후기 수 반환"""
        session = self.get_session()
        try:
            query = session.query(Review)
            
            if "platform_id" in filters:
                query = query.filter(Review.platform_id == filters["platform_id"])
            
            if "category_name" in filters:
                query = query.filter(Review.title.contains(filters["category_name"]))
            
            return query.count()
        finally:
            session.close()
    
    # 통계 관련 메서드
    def get_statistics(self) -> Dict:
        """데이터베이스 통계 조회"""
        session = self.get_session()
        try:
            # 전체 게시글 수
            total_articles = session.query(Article).count()
            
            # 전체 댓글 수
            total_comments = session.query(Comment).count()
            
            # 카테고리별 게시글 수
            category_stats = session.query(
                Article.category_name, func.count(Article.id)
            ).group_by(Article.category_name).all()
            category_stats = {cat: count for cat, count in category_stats if cat}
            
            # 오늘 게시글 수
            today = datetime.now().date()
            today_articles = session.query(Article).filter(
                func.date(Article.created_at) == today
            ).count()
            
            return {
                'total_articles': total_articles,
                'total_comments': total_comments,
                'category_stats': category_stats,
                'today_articles': today_articles
            }
        finally:
            session.close()
    
    # 헬퍼 메서드들
    def _article_to_dict(self, article: Article) -> Dict:
        """Article 객체를 딕셔너리로 변환"""
        return {
            'id': article.id,
            'platform_id': article.platform_id,
            'community_article_id': article.community_article_id,
            'community_id': article.community_id,
            'title': article.title,
            'content': article.content,
            'images': article.images,
            'writer_nickname': article.writer_nickname,
            'writer_id': article.writer_id,
            'like_count': article.like_count,
            'comment_count': article.comment_count,
            'view_count': article.view_count,
            'created_at': article.created_at.isoformat() if article.created_at else None,
            'category_name': article.category_name,
            'collected_at': article.collected_at.isoformat() if article.collected_at else None
        }
    
    def _comment_to_dict(self, comment: Comment) -> Dict:
        """Comment 객체를 딕셔너리로 변환"""
        return {
            'id': comment.id,
            'platform_id': comment.platform_id,
            'community_article_id': comment.community_article_id,
            'community_comment_id': comment.community_comment_id,
            'content': comment.content,
            'writer_nickname': comment.writer_nickname,
            'writer_id': comment.writer_id,
            'created_at': comment.created_at.isoformat() if comment.created_at else None,
            'parent_comment_id': comment.parent_comment_id,
            'collected_at': comment.collected_at.isoformat() if comment.collected_at else None,
            'article_id': comment.article_id,  # 관계 정보 추가
            # 연관 게시글 정보 (선택적으로 포함)
            'article_title': comment.article.title if comment.article else None,
            'article_platform_id': comment.article.platform_id if comment.article else None
        }
    
    def _review_to_dict(self, review: Review) -> Dict:
        """Review 객체를 딕셔너리로 변환"""
        return {
            'id': review.id,
            'platform_id': review.platform_id,
            'platform_review_id': review.platform_review_id,
            'community_id': review.community_id,
            'title': review.title,
            'content': review.content,
            'images': review.images,
            'writer_nickname': review.writer_nickname,
            'writer_id': review.writer_id,
            'like_count': review.like_count,
            'rating': review.rating,
            'price': review.price,
            'categories': review.categories,
            'sub_categories': review.sub_categories,
            'surgery_date': review.surgery_date,
            'hospital_name': review.hospital_name,
            'doctor_name': review.doctor_name,
            'is_blind': review.is_blind,
            'is_image_blur': review.is_image_blur,
            'is_certificated_review': review.is_certificated_review,
            'created_at': review.created_at.isoformat() if review.created_at else None,
            'collected_at': review.collected_at.isoformat() if review.collected_at else None
        }
    
    def get_comment_by_article_id_and_comment_id(self, article_id: str, comment_id: str) -> Optional[Dict[str, Any]]:
        """게시글 ID와 댓글 ID로 댓글 조회"""
        session = self.get_session()
        try:
            comment = session.query(Comment).filter(
                and_(
                    Comment.article_id == int(article_id),
                    Comment.community_comment_id == comment_id
                )
            ).first()
            
            if comment:
                return self._comment_to_dict(comment)
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"댓글 조회 실패: {e}")
            raise
        finally:
            session.close()
    
    def search_data_by_keywords(self, keywords: List[str], platforms: List[str] = None, 
                               data_types: List[str] = None, start_date: str = None, 
                               end_date: str = None, limit: int = 100, offset: int = 0) -> Dict[str, List[Dict]]:
        """키워드로 게시글, 댓글, 후기를 검색합니다."""
        session = self.get_session()
        try:
            results = {
                'articles': [],
                'comments': [],
                'reviews': []
            }
            
            if not keywords:
                return results
            
            # 게시글 검색
            if not data_types or 'article' in data_types:
                article_query = session.query(Article)
                
                # 게시글용 키워드 조건 (title과 content 모두 검색)
                article_keyword_conditions = []
                for keyword in keywords:
                    article_keyword_conditions.append(
                        or_(
                            Article.title.like(f'%{keyword}%'),
                            Article.content.like(f'%{keyword}%')
                        )
                    )
                
                if article_keyword_conditions:
                    article_query = article_query.filter(or_(*article_keyword_conditions))
                
                if platforms:
                    article_query = article_query.filter(Article.platform_id.in_(platforms))
                
                if start_date:
                    article_query = article_query.filter(func.date(Article.created_at) >= start_date)
                
                if end_date:
                    article_query = article_query.filter(func.date(Article.created_at) <= end_date)
                
                articles = article_query.order_by(desc(Article.created_at)).offset(offset).limit(limit).all()
                results['articles'] = [self._article_to_dict(article) for article in articles]
            
            # 댓글 검색
            if not data_types or 'comment' in data_types:
                comment_query = session.query(Comment)
                
                # 댓글용 키워드 조건 (content만 검색, title 없음)
                comment_keyword_conditions = []
                for keyword in keywords:
                    comment_keyword_conditions.append(
                        Comment.content.like(f'%{keyword}%')
                    )
                
                if comment_keyword_conditions:
                    comment_query = comment_query.filter(or_(*comment_keyword_conditions))
                
                if platforms:
                    comment_query = comment_query.filter(Comment.platform_id.in_(platforms))
                
                if start_date:
                    comment_query = comment_query.filter(func.date(Comment.created_at) >= start_date)
                
                if end_date:
                    comment_query = comment_query.filter(func.date(Comment.created_at) <= end_date)
                
                comments = comment_query.order_by(desc(Comment.created_at)).offset(offset).limit(limit).all()
                results['comments'] = [self._comment_to_dict(comment) for comment in comments]
            
            # 후기 검색
            if not data_types or 'review' in data_types:
                review_query = session.query(Review)
                
                # 후기용 키워드 조건 (title과 content 모두 검색)
                review_keyword_conditions = []
                for keyword in keywords:
                    review_keyword_conditions.append(
                        or_(
                            Review.title.like(f'%{keyword}%'),
                            Review.content.like(f'%{keyword}%')
                        )
                    )
                
                if review_keyword_conditions:
                    review_query = review_query.filter(or_(*review_keyword_conditions))
                
                if platforms:
                    review_query = review_query.filter(Review.platform_id.in_(platforms))
                
                if start_date:
                    review_query = review_query.filter(func.date(Review.created_at) >= start_date)
                
                if end_date:
                    review_query = review_query.filter(func.date(Review.created_at) <= end_date)
                
                reviews = review_query.order_by(desc(Review.created_at)).offset(offset).limit(limit).all()
                results['reviews'] = [self._review_to_dict(review) for review in reviews]
            
            return results
            
        except Exception as e:
            logger.error(f"키워드 검색 중 오류 발생: {e}")
            raise
        finally:
            session.close()
    
    def search_data_count_by_keywords(self, keywords: List[str], platforms: List[str] = None, 
                                     data_types: List[str] = None, start_date: str = None, 
                                     end_date: str = None) -> Dict[str, int]:
        """키워드 검색 결과의 개수를 반환합니다."""
        session = self.get_session()
        try:
            counts = {
                'articles': 0,
                'comments': 0,
                'reviews': 0
            }
            
            if not keywords:
                return counts
            
            # 게시글 개수
            if not data_types or 'article' in data_types:
                article_query = session.query(Article)
                
                # 게시글용 키워드 조건 (title과 content 모두 검색)
                article_keyword_conditions = []
                for keyword in keywords:
                    article_keyword_conditions.append(
                        or_(
                            Article.title.like(f'%{keyword}%'),
                            Article.content.like(f'%{keyword}%')
                        )
                    )
                
                if article_keyword_conditions:
                    article_query = article_query.filter(or_(*article_keyword_conditions))
                
                if platforms:
                    article_query = article_query.filter(Article.platform_id.in_(platforms))
                
                if start_date:
                    article_query = article_query.filter(func.date(Article.created_at) >= start_date)
                
                if end_date:
                    article_query = article_query.filter(func.date(Article.created_at) <= end_date)
                
                counts['articles'] = article_query.count()
            
            # 댓글 개수
            if not data_types or 'comment' in data_types:
                comment_query = session.query(Comment)
                
                # 댓글용 키워드 조건 (content만 검색, title 없음)
                comment_keyword_conditions = []
                for keyword in keywords:
                    comment_keyword_conditions.append(
                        Comment.content.like(f'%{keyword}%')
                    )
                
                if comment_keyword_conditions:
                    comment_query = comment_query.filter(or_(*comment_keyword_conditions))
                
                if platforms:
                    comment_query = comment_query.filter(Comment.platform_id.in_(platforms))
                
                if start_date:
                    comment_query = comment_query.filter(func.date(Comment.created_at) >= start_date)
                
                if end_date:
                    comment_query = comment_query.filter(func.date(Comment.created_at) <= end_date)
                
                counts['comments'] = comment_query.count()
            
            # 후기 개수
            if not data_types or 'review' in data_types:
                review_query = session.query(Review)
                
                # 후기용 키워드 조건 (title과 content 모두 검색)
                review_keyword_conditions = []
                for keyword in keywords:
                    review_keyword_conditions.append(
                        or_(
                            Review.title.like(f'%{keyword}%'),
                            Review.content.like(f'%{keyword}%')
                        )
                    )
                
                if review_keyword_conditions:
                    review_query = review_query.filter(or_(*review_keyword_conditions))
                
                if platforms:
                    review_query = review_query.filter(Review.platform_id.in_(platforms))
                
                if start_date:
                    review_query = review_query.filter(func.date(Review.created_at) >= start_date)
                
                if end_date:
                    review_query = review_query.filter(func.date(Review.created_at) <= end_date)
                
                counts['reviews'] = review_query.count()
            
            return counts
            
        except Exception as e:
            logger.error(f"키워드 검색 개수 조회 중 오류 발생: {e}")
            raise
        finally:
            session.close()