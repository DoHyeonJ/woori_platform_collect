import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict
from database import DatabaseManager

class DatabaseViewer:
    def __init__(self, db_path: str = "gangnamunni.db"):
        self.db = DatabaseManager(db_path)
    
    def show_statistics(self):
        """전체 통계 보기"""
        stats = self.db.get_statistics()
        
        print("=" * 50)
        print("📊 데이터베이스 통계")
        print("=" * 50)
        print(f"📝 전체 게시글: {stats['total_articles']:,}개")
        print(f"💬 전체 댓글: {stats['total_comments']:,}개")
        print(f"📅 오늘 게시글: {stats['today_articles']:,}개")
        print()
        
        print("📂 카테고리별 통계:")
        for category, count in stats['category_stats'].items():
            print(f"   • {category}: {count:,}개")
        print("=" * 50)
    
    def show_recent_articles(self, limit: int = 10):
        """최근 게시글 보기"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM articles 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            articles = [dict(row) for row in cursor.fetchall()]
        
        print(f"\n📋 최근 게시글 (상위 {len(articles)}개)")
        print("-" * 50)
        
        for i, article in enumerate(articles, 1):
            print(f"{i:2d}. [{article['category_name']}] {article['title'] or '제목 없음'}")
            print(f"     작성자: {article['writer_nickname']} | 댓글: {article['comment_count']} | 조회: {article['view_count']}")
            print(f"     작성시간: {article['created_at']}")
            print()
    
    def show_articles_by_date(self, date: str):
        """특정 날짜 게시글 보기"""
        articles = self.db.get_articles_by_date(date)
        
        print(f"\n📅 {date} 게시글 목록 (총 {len(articles)}개)")
        print("-" * 50)
        
        for i, article in enumerate(articles, 1):
            print(f"{i:2d}. [{article['category_name']}] {article['title'] or '제목 없음'}")
            print(f"     내용: {article['content'][:80]}...")
            print(f"     작성자: {article['writer_nickname']} | 댓글: {article['comment_count']} | 조회: {article['view_count']}")
            print(f"     작성시간: {article['created_at']}")
            print()
    
    def show_articles_by_category(self, category_name: str, limit: int = 10):
        """카테고리별 게시글 보기"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM articles 
                WHERE category_name = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (category_name, limit))
            
            articles = [dict(row) for row in cursor.fetchall()]
        
        print(f"\n📂 {category_name} 게시글 (상위 {len(articles)}개)")
        print("-" * 50)
        
        for i, article in enumerate(articles, 1):
            print(f"{i:2d}. {article['title'] or '제목 없음'}")
            print(f"     내용: {article['content'][:80]}...")
            print(f"     작성자: {article['writer_nickname']} | 댓글: {article['comment_count']} | 조회: {article['view_count']}")
            print(f"     작성시간: {article['created_at']}")
            print()
    
    def show_article_detail(self, article_id: int):
        """특정 게시글 상세 보기"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 게시글 정보 조회
            cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
            article = cursor.fetchone()
            
            if not article:
                print(f"❌ 게시글 ID {article_id}를 찾을 수 없습니다.")
                return
            
            article = dict(article)
            
            # 댓글 조회
            comments = self.db.get_comments_by_article_id(article_id)
        
        print("=" * 60)
        print(f"📝 게시글 상세 정보 (ID: {article_id})")
        print("=" * 60)
        print(f"제목: {article['title'] or '제목 없음'}")
        print(f"카테고리: {article['category_name']}")
        print(f"작성자: {article['writer_nickname']} (ID: {article['writer_id']})")
        print(f"작성시간: {article['created_at']}")
        print(f"조회수: {article['view_count']:,} | 댓글: {article['comment_count']:,} | 좋아요: {article['like_count']:,}")
        print()
        print("내용:")
        print("-" * 40)
        print(article['content'])
        print("-" * 40)
        
        if comments:
            print(f"\n💬 댓글 목록 (총 {len(comments)}개)")
            print("-" * 40)
            
            for i, comment in enumerate(comments, 1):
                indent = "" if comment['parent_comment_id'] is None else "  "
                print(f"{indent}{i:2d}. {comment['writer_nickname']} (ID: {comment['writer_id']})")
                print(f"{indent}    {comment['content']}")
                print(f"{indent}    작성시간: {comment['created_at']}")
                print()
        else:
            print("\n💬 댓글이 없습니다.")
        
        print("=" * 60)
    
    def search_articles(self, keyword: str, limit: int = 10):
        """게시글 검색"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM articles 
                WHERE title LIKE ? OR content LIKE ? OR writer_nickname LIKE ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
            
            articles = [dict(row) for row in cursor.fetchall()]
        
        print(f"\n🔍 '{keyword}' 검색 결과 (상위 {len(articles)}개)")
        print("-" * 50)
        
        for i, article in enumerate(articles, 1):
            print(f"{i:2d}. [{article['category_name']}] {article['title'] or '제목 없음'}")
            print(f"     내용: {article['content'][:80]}...")
            print(f"     작성자: {article['writer_nickname']} | 댓글: {article['comment_count']} | 조회: {article['view_count']}")
            print(f"     작성시간: {article['created_at']}")
            print()
    
    def show_daily_summary(self, days: int = 7):
        """일별 요약 보기"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as article_count,
                    SUM(comment_count) as total_comments,
                    SUM(view_count) as total_views
                FROM articles 
                WHERE created_at >= DATE('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            '''.format(days))
            
            results = cursor.fetchall()
        
        print(f"\n📊 최근 {days}일 일별 요약")
        print("-" * 50)
        print(f"{'날짜':<12} {'게시글':<8} {'댓글':<8} {'조회수':<10}")
        print("-" * 50)
        
        for date, article_count, total_comments, total_views in results:
            print(f"{date:<12} {article_count:<8} {total_comments or 0:<8} {total_views or 0:<10}")
        
        print("-" * 50)

def main():
    viewer = DatabaseViewer()
    
    while True:
        print("\n" + "=" * 50)
        print("🗄️  강남언니 데이터베이스 뷰어")
        print("=" * 50)
        print("1. 📊 전체 통계 보기")
        print("2. 📋 최근 게시글 보기")
        print("3. 📅 특정 날짜 게시글 보기")
        print("4. 📂 카테고리별 게시글 보기")
        print("5. 📝 게시글 상세 보기")
        print("6. 🔍 게시글 검색")
        print("7. 📊 일별 요약 보기")
        print("0. 종료")
        print("-" * 50)
        
        choice = input("선택하세요: ").strip()
        
        if choice == "1":
            viewer.show_statistics()
        
        elif choice == "2":
            limit = input("보여줄 개수 (기본값: 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            viewer.show_recent_articles(limit)
        
        elif choice == "3":
            date = input("날짜 (YYYY-MM-DD): ").strip()
            if date:
                viewer.show_articles_by_date(date)
            else:
                print("❌ 날짜를 입력해주세요.")
        
        elif choice == "4":
            print("카테고리: 병원질문, 시술/수술질문, 자유수다, 발품후기, 의사에게 물어보세요")
            category = input("카테고리명: ").strip()
            if category:
                limit = input("보여줄 개수 (기본값: 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                viewer.show_articles_by_category(category, limit)
            else:
                print("❌ 카테고리를 입력해주세요.")
        
        elif choice == "5":
            article_id = input("게시글 ID: ").strip()
            if article_id.isdigit():
                viewer.show_article_detail(int(article_id))
            else:
                print("❌ 올바른 게시글 ID를 입력해주세요.")
        
        elif choice == "6":
            keyword = input("검색어: ").strip()
            if keyword:
                limit = input("보여줄 개수 (기본값: 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                viewer.search_articles(keyword, limit)
            else:
                print("❌ 검색어를 입력해주세요.")
        
        elif choice == "7":
            days = input("보여줄 일수 (기본값: 7): ").strip()
            days = int(days) if days.isdigit() else 7
            viewer.show_daily_summary(days)
        
        elif choice == "0":
            print("👋 프로그램을 종료합니다.")
            break
        
        else:
            print("❌ 올바른 선택지를 입력해주세요.")
        
        input("\nEnter를 누르면 계속...")

if __name__ == "__main__":
    main() 