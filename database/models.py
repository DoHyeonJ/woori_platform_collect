import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Community:
    id: Optional[int]
    name: str
    created_at: datetime
    description: str

@dataclass
class Client:
    id: Optional[int]
    hospital_name: str
    created_at: datetime
    description: str

@dataclass
class Article:
    id: Optional[int]
    platform_id: str
    community_article_id: int
    community_id: int
    title: str
    content: str
    images: str  # JSON 문자열로 저장
    writer_nickname: str
    writer_id: str
    like_count: int
    comment_count: int
    view_count: int
    created_at: datetime
    category_name: str

@dataclass
class Comment:
    id: Optional[int]
    article_id: int
    content: str
    writer_nickname: str
    writer_id: str
    created_at: datetime
    parent_comment_id: Optional[int] = None  # 대댓글인 경우 부모 댓글 ID

@dataclass
class ExcludedArticle:
    id: Optional[int]
    client_id: int
    article_id: int
    created_at: datetime

class DatabaseManager:
    def __init__(self, db_path: str = "gangnamunni.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 커뮤니티 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS communities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            ''')
            
            # 클라이언트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hospital_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            ''')
            
            # 게시글 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id TEXT NOT NULL,
                    community_article_id INTEGER NOT NULL,
                    community_id INTEGER NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    images TEXT,  -- JSON 문자열
                    writer_nickname TEXT NOT NULL,
                    writer_id TEXT NOT NULL,
                    like_count INTEGER DEFAULT 0,
                    comment_count INTEGER DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    category_name TEXT,
                    FOREIGN KEY (community_id) REFERENCES communities (id),
                    UNIQUE(platform_id, community_article_id)
                )
            ''')
            
            # 댓글 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    writer_nickname TEXT NOT NULL,
                    writer_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parent_comment_id INTEGER,
                    FOREIGN KEY (article_id) REFERENCES articles (id),
                    FOREIGN KEY (parent_comment_id) REFERENCES comments (id)
                )
            ''')
            
            # 제외 게시글 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS excluded_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    article_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (article_id) REFERENCES articles (id)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_community_id ON articles(community_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_article_id ON comments(article_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON comments(parent_comment_id)')
            
            conn.commit()
    
    def insert_community(self, community: Community) -> int:
        """커뮤니티 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO communities (name, created_at, description)
                VALUES (?, ?, ?)
            ''', (community.name, community.created_at, community.description))
            return cursor.lastrowid
    
    def insert_client(self, client: Client) -> int:
        """클라이언트 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clients (hospital_name, created_at, description)
                VALUES (?, ?, ?)
            ''', (client.hospital_name, client.created_at, client.description))
            return cursor.lastrowid
    
    def insert_article(self, article: Article) -> int:
        """게시글 추가 (중복 체크 포함)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO articles (
                        platform_id, community_article_id, community_id, title, content,
                        images, writer_nickname, writer_id, like_count, comment_count,
                        view_count, created_at, category_name
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article.platform_id, article.community_article_id, article.community_id,
                    article.title, article.content, article.images, article.writer_nickname,
                    article.writer_id, article.like_count, article.comment_count,
                    article.view_count, article.created_at, article.category_name
                ))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # 중복된 게시글이면 기존 ID 반환
                cursor.execute('''
                    SELECT id FROM articles 
                    WHERE platform_id = ? AND community_article_id = ?
                ''', (article.platform_id, article.community_article_id))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def insert_comment(self, comment: Comment) -> int:
        """댓글 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO comments (article_id, content, writer_nickname, writer_id, created_at, parent_comment_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comment.article_id, comment.content, comment.writer_nickname,
                comment.writer_id, comment.created_at, comment.parent_comment_id
            ))
            return cursor.lastrowid
    
    def get_articles_by_date(self, date: str, community_id: Optional[int] = None) -> List[Dict]:
        """특정 날짜의 게시글 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if community_id:
                cursor.execute('''
                    SELECT * FROM articles 
                    WHERE DATE(created_at) = ? AND community_id = ?
                    ORDER BY created_at DESC
                ''', (date, community_id))
            else:
                cursor.execute('''
                    SELECT * FROM articles 
                    WHERE DATE(created_at) = ?
                    ORDER BY created_at DESC
                ''', (date,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_comments_by_article_id(self, article_id: int) -> List[Dict]:
        """특정 게시글의 댓글 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM comments 
                WHERE article_id = ?
                ORDER BY created_at ASC
            ''', (article_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """데이터베이스 통계 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 전체 게시글 수
            cursor.execute('SELECT COUNT(*) FROM articles')
            total_articles = cursor.fetchone()[0]
            
            # 전체 댓글 수
            cursor.execute('SELECT COUNT(*) FROM comments')
            total_comments = cursor.fetchone()[0]
            
            # 카테고리별 게시글 수
            cursor.execute('''
                SELECT category_name, COUNT(*) as count 
                FROM articles 
                GROUP BY category_name
            ''')
            category_stats = dict(cursor.fetchall())
            
            # 최근 게시글 수 (오늘)
            cursor.execute('''
                SELECT COUNT(*) FROM articles 
                WHERE DATE(created_at) = DATE('now')
            ''')
            today_articles = cursor.fetchone()[0]
            
            return {
                'total_articles': total_articles,
                'total_comments': total_comments,
                'category_stats': category_stats,
                'today_articles': today_articles
            } 