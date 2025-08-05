import asyncio
import json
from datetime import datetime
from typing import List, Dict
from gannamunni import GangnamUnniAPI
from database import DatabaseManager, Community, Client, Article, Comment, Review

class DataCollector:
    def __init__(self, db_path: str = "collect_data.db"):
        self.api = GangnamUnniAPI()
        self.db = DatabaseManager(db_path)
        self.platform_id = "gangnamunni"
        
        # 커뮤니티 정보 초기화
        self.community_id = self._init_community()
    
    def _init_community(self) -> int:
        """커뮤니티 정보 초기화"""
        community = Community(
            id=None,
            name="강남언니",
            created_at=datetime.now(),
            description="강남언니 커뮤니티"
        )
        return self.db.insert_community(community)
    
    def _convert_article_to_db_format(self, api_article, category_name: str) -> Article:
        """API 게시글을 DB 형식으로 변환"""
        # 이미지를 JSON 문자열로 변환
        images = json.dumps([photo.url for photo in api_article.photos])
        
        # 작성시간을 datetime으로 변환
        try:
            created_at = datetime.strptime(api_article.create_time, "%Y-%m-%d %H:%M:%S")
        except:
            created_at = datetime.now()
        
        return Article(
            id=None,
            platform_id=self.platform_id,
            community_article_id=api_article.id,
            community_id=self.community_id,
            title=api_article.title or "",
            content=api_article.contents,
            images=images,
            writer_nickname=api_article.writer.nickname,
            writer_id=str(api_article.writer.id),
            like_count=api_article.thumb_up_count,
            comment_count=api_article.comment_count,
            view_count=api_article.view_count,
            created_at=created_at,
            category_name=category_name
        )
    
    def _convert_comment_to_db_format(self, api_comment, article_db_id: int, parent_comment_id: int = None) -> Comment:
        """API 댓글을 DB 형식으로 변환"""
        try:
            created_at = datetime.strptime(api_comment.create_time, "%Y-%m-%d %H:%M:%S")
        except:
            created_at = datetime.now()
        
        return Comment(
            id=None,
            article_id=article_db_id,
            content=api_comment.contents,
            writer_nickname=api_comment.writer.nickname,
            writer_id=str(api_comment.writer.id),
            created_at=created_at,
            parent_comment_id=parent_comment_id
        )
    
    def _convert_article_to_review_format(self, api_article, category_name: str) -> Review:
        """API 게시글을 후기 형식으로 변환 (후기 테이블에 저장용)"""
        # 이미지를 JSON 문자열로 변환
        images = json.dumps([photo.url for photo in api_article.photos])
        
        # 작성시간을 datetime으로 변환
        try:
            created_at = datetime.strptime(api_article.create_time, "%Y-%m-%d %H:%M:%S")
        except:
            created_at = datetime.now()
        
        return Review(
            id=None,
            platform_id=self.platform_id,
            platform_review_id=api_article.id,
            community_id=self.community_id,
            title=api_article.title or f"{category_name} 게시글",
            content=api_article.contents,
            images=images,
            writer_nickname=api_article.writer.nickname,
            writer_id=str(api_article.writer.id),
            like_count=api_article.thumb_up_count,
            rating=0,  # 강남언니는 평점 시스템이 없음
            price=0,  # 강남언니는 가격 정보가 없음
            categories=json.dumps([category_name], ensure_ascii=False),
            sub_categories="",
            surgery_date="",
            is_blind=False,
            is_image_blur=False,
            is_certificated_review=False,
            created_at=created_at
        )
    
    async def collect_and_save_articles(self, target_date: str, categories: Dict[str, str], save_as_reviews: bool = False):
        """
        특정 날짜의 모든 카테고리 게시글을 수집하고 DB에 저장
        
        Args:
            target_date: 수집할 날짜
            categories: 카테고리 정보
            save_as_reviews: True면 후기 테이블에 저장, False면 기존 게시글 테이블에 저장
        """
        print(f"📅 {target_date} 게시글 수집 시작")
        
        total_articles = 0
        total_comments = 0
        
        for category_key, category_name in categories.items():
            # API에서 게시글 수집
            api_articles = await self.api.get_articles_by_date(target_date, category=category_key)
            
            category_articles = 0
            category_comments = 0
            
            for api_article in api_articles:
                if save_as_reviews:
                    # 후기 테이블에 저장
                    db_review = self._convert_article_to_review_format(api_article, category_name)
                    self.db.insert_review(db_review)
                    category_articles += 1
                else:
                    # 기존 게시글 테이블에 저장
                    db_article = self._convert_article_to_db_format(api_article, category_name)
                    article_db_id = self.db.insert_article(db_article)
                    category_articles += 1
                
                # 댓글 수집 (후기 테이블에 저장할 때는 댓글 수집 안함)
                if not save_as_reviews and api_article.comment_count > 0:
                    try:
                        api_comments = await self.api.get_comments(api_article.id)
                        
                        for api_comment in api_comments:
                            # 메인 댓글 저장
                            db_comment = self._convert_comment_to_db_format(api_comment, article_db_id)
                            self.db.insert_comment(db_comment)
                            category_comments += 1
                            
                            # 대댓글이 있는 경우 대댓글도 저장
                            if api_comment.replies:
                                for reply in api_comment.replies:
                                    db_reply = self._convert_comment_to_db_format(reply, article_db_id, self.db.insert_comment(db_comment))
                                    self.db.insert_comment(db_reply)
                                    category_comments += 1
                    except Exception:
                        pass
            
            total_articles += category_articles
            total_comments += category_comments
        
        print(f"✅ {target_date} 게시글 수집 완료: {total_articles}개 게시글, {total_comments}개 댓글")
        
        return total_articles, total_comments
    
    def get_statistics(self) -> Dict:
        """데이터베이스 통계 조회"""
        stats = self.db.get_statistics()
        review_stats = self.db.get_review_statistics()
        
        # 통합 통계
        stats.update({
            'review_stats': review_stats
        })
        
        return stats
    
    def view_articles_by_date(self, date: str):
        """특정 날짜의 게시글 조회 및 출력"""
        articles = self.db.get_articles_by_date(date)
        
        print(f"\n=== {date} 저장된 게시글 목록 (총 {len(articles)}개) ===")
        
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. 게시글 ID: {article['id']}")
            print(f"   원본 ID: {article['community_article_id']}")
            print(f"   카테고리: {article['category_name']}")
            print(f"   제목: {article['title']}")
            print(f"   내용: {article['content'][:100]}...")
            print(f"   작성자: {article['writer_nickname']} (ID: {article['writer_id']})")
            print(f"   조회수: {article['view_count']}, 댓글: {article['comment_count']}, 좋아요: {article['like_count']}")
            print(f"   작성시간: {article['created_at']}")
            
            # 댓글 조회
            comments = self.db.get_comments_by_article_id(article['id'])
            if comments:
                print(f"   === 댓글 목록 (총 {len(comments)}개) ===")
                for j, comment in enumerate(comments, 1):
                    indent = "     " if comment['parent_comment_id'] is None else "       "
                    print(f"{indent}{j}. 댓글 ID: {comment['id']}")
                    print(f"{indent}   작성자: {comment['writer_nickname']} (ID: {comment['writer_id']})")
                    print(f"{indent}   내용: {comment['content'][:50]}...")
                    print(f"{indent}   작성시간: {comment['created_at']}")
            else:
                print("   댓글 없음")

# 사용 예시
async def main():
    collector = DataCollector()
    
    # 카테고리 정의
    categories = {
        "hospital_question": "병원질문",
        "surgery_question": "시술/수술질문", 
        "free_chat": "자유수다",
        "review": "발품후기",
        "ask_doctor": "의사에게 물어보세요"
    }
    
    # 특정 날짜 데이터 수집
    target_date = "2025-08-03"
    articles_count, comments_count = await collector.collect_and_save_articles(target_date, categories)
    
    # 통계 조회
    stats = collector.get_statistics()
    print(f"\n=== 데이터베이스 통계 ===")
    print(f"전체 게시글: {stats['total_articles']}개")
    print(f"전체 댓글: {stats['total_comments']}개")
    print(f"오늘 게시글: {stats['today_articles']}개")
    print(f"카테고리별 통계: {stats['category_stats']}")
    
    # 저장된 데이터 조회
    collector.view_articles_by_date(target_date)

if __name__ == "__main__":
    asyncio.run(main()) 