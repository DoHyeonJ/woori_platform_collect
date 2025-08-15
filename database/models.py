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
    community_article_id: str
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
    collected_at: Optional[datetime] = None  # 수집 시간

@dataclass
class Comment:
    id: Optional[int]
    article_id: int
    content: str
    writer_nickname: str
    writer_id: str
    created_at: datetime
    parent_comment_id: Optional[int] = None  # 대댓글인 경우 부모 댓글 ID
    collected_at: Optional[datetime] = None  # 수집 시간

@dataclass
class ExcludedArticle:
    id: Optional[int]
    client_id: int
    article_id: int
    created_at: datetime

@dataclass
class Review:
    id: Optional[int]
    platform_id: str  # "gangnamunni" 또는 "babitalk"
    platform_review_id: str  # 각 플랫폼의 고유 후기 ID
    community_id: int  # 커뮤니티 ID (바비톡의 경우 별도 커뮤니티 생성)
    title: str  # 후기 제목 (바비톡의 경우 카테고리 정보)
    content: str  # 후기 내용
    images: str  # JSON 문자열로 저장
    writer_nickname: str
    writer_id: str
    like_count: int
    rating: int  # 평점 (바비톡용)
    price: int  # 가격 (바비톡용)
    categories: str  # JSON 문자열로 저장 (바비톡용)
    sub_categories: str  # JSON 문자열로 저장 (바비톡용)
    surgery_date: str  # 수술 날짜 (바비톡용)
    hospital_name: str  # 병원명
    doctor_name: str  # 담당의명
    is_blind: bool  # 블라인드 여부 (바비톡용)
    is_image_blur: bool  # 이미지 블러 여부 (바비톡용)
    is_certificated_review: bool  # 인증 후기 여부 (바비톡용)
    created_at: datetime
    collected_at: Optional[datetime] = None  # 수집 시간

class DatabaseManager:
    def __init__(self, db_path: str = "data/collect_data.db"):
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
                    name TEXT NOT NULL UNIQUE,
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
                    community_article_id TEXT NOT NULL,
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
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 수집 시간
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
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 수집 시간
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
            
            # 후기 테이블 (통합)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id TEXT NOT NULL,  -- "gangnamun니" 또는 "babitalk"
                    platform_review_id TEXT NOT NULL,  -- 각 플랫폼의 고유 후기 ID
                    community_id INTEGER NOT NULL,
                    title TEXT,  -- 후기 제목 (바비톡의 경우 카테고리 정보)
                    content TEXT NOT NULL,  -- 후기 내용
                    images TEXT,  -- JSON 문자열
                    writer_nickname TEXT NOT NULL,
                    writer_id TEXT NOT NULL,
                    like_count INTEGER DEFAULT 0,
                    rating INTEGER DEFAULT 0,  -- 평점 (바비톡용)
                    price INTEGER DEFAULT 0,  -- 가격 (바비톡용)
                    categories TEXT,  -- JSON 문자열 (바비톡용)
                    sub_categories TEXT,  -- JSON 문자열 (바비톡용)
                    surgery_date TEXT,  -- 수술 날짜 (바비톡용)
                    hospital_name TEXT,  -- 병원명
                    doctor_name TEXT,  -- 담당의명
                    is_blind BOOLEAN DEFAULT FALSE,  -- 블라인드 여부 (바비톡용)
                    is_image_blur BOOLEAN DEFAULT FALSE,  -- 이미지 블러 여부 (바비톡용)
                    is_certificated_review BOOLEAN DEFAULT FALSE,  -- 인증 후기 여부 (바비톡용)
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 수집 시간
                    FOREIGN KEY (community_id) REFERENCES communities (id),
                    UNIQUE(platform_id, platform_review_id)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_community_id ON articles(community_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_article_id ON comments(article_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON comments(parent_comment_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_communities_name ON communities(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_platform_id ON reviews(platform_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_platform_review_id ON reviews(platform_review_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_community_id ON reviews(community_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at)')
            
            conn.commit()
    
    def insert_community(self, community: Community) -> int:
        """커뮤니티 추가 (중복 체크 포함)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO communities (name, created_at, description)
                    VALUES (?, ?, ?)
                ''', (community.name, community.created_at, community.description))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # 중복된 커뮤니티가면 기존 ID 반환
                cursor.execute('SELECT id FROM communities WHERE name = ?', (community.name,))
                result = cursor.fetchone()
                return result[0] if result else None
    
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
                        view_count, created_at, category_name, collected_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article.platform_id, article.community_article_id, article.community_id,
                    article.title, article.content, article.images, article.writer_nickname,
                    article.writer_id, article.like_count, article.comment_count,
                    article.view_count, article.created_at, article.category_name, 
                    article.collected_at or datetime.now()
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
                INSERT INTO comments (article_id, content, writer_nickname, writer_id, created_at, parent_comment_id, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                comment.article_id, comment.content, comment.writer_nickname,
                comment.writer_id, comment.created_at, comment.parent_comment_id, 
                comment.collected_at or datetime.now()
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
    
    def get_community_by_name(self, name: str) -> Optional[Dict]:
        """이름으로 커뮤니티 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM communities WHERE name = ?', (name,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def insert_review(self, review: Review) -> int:
        """후기 추가 (중복 체크 포함)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO reviews (
                        platform_id, platform_review_id, community_id, title, content,
                        images, writer_nickname, writer_id, like_count, rating,
                        price, categories, sub_categories, surgery_date, hospital_name,
                        doctor_name, is_blind, is_image_blur, is_certificated_review, created_at, collected_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    review.platform_id, review.platform_review_id, review.community_id,
                    review.title, review.content, review.images, review.writer_nickname,
                    review.writer_id, review.like_count, review.rating, review.price,
                    review.categories, review.sub_categories, review.surgery_date,
                    review.hospital_name, review.doctor_name, review.is_blind, 
                    review.is_image_blur, review.is_certificated_review, review.created_at, 
                    review.collected_at or datetime.now()
                ))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # 중복된 후기이면 기존 ID 반환
                cursor.execute('''
                    SELECT id FROM reviews 
                    WHERE platform_id = ? AND platform_review_id = ?
                ''', (review.platform_id, review.platform_review_id))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def get_reviews_by_platform(self, platform_id: str, community_id: Optional[int] = None, limit: Optional[int] = None) -> List[Dict]:
        """플랫폼별 후기 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if community_id:
                query = '''
                    SELECT * FROM reviews 
                    WHERE platform_id = ? AND community_id = ?
                    ORDER BY created_at DESC
                '''
                params = (platform_id, community_id)
            else:
                query = '''
                    SELECT * FROM reviews 
                    WHERE platform_id = ?
                    ORDER BY created_at DESC
                '''
                params = (platform_id,)
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_reviews_by_date(self, date: str, platform_id: Optional[str] = None) -> List[Dict]:
        """특정 날짜의 후기 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if platform_id:
                cursor.execute('''
                    SELECT * FROM reviews 
                    WHERE DATE(created_at) = ? AND platform_id = ?
                    ORDER BY created_at DESC
                ''', (date, platform_id))
            else:
                cursor.execute('''
                    SELECT * FROM reviews 
                    WHERE DATE(created_at) = ?
                    ORDER BY created_at DESC
                ''', (date,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_review_statistics(self) -> Dict:
        """후기 통계 정보를 반환합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 플랫폼별 후기 수
            cursor.execute('''
                SELECT platform_id, COUNT(*) as count
                FROM reviews
                GROUP BY platform_id
            ''')
            platform_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 카테고리별 후기 수 (바비톡)
            cursor.execute('''
                SELECT categories, COUNT(*) as count
                FROM reviews
                WHERE platform_id = 'babitalk'
                GROUP BY categories
            ''')
            category_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "platform_statistics": platform_stats,
                "category_statistics": category_stats
            }
    
    # API용 메서드들 추가
    def get_articles_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Article]:
        """필터 조건에 따라 게시글을 조회합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM articles WHERE 1=1"
            params = []
            
            if "platform_id" in filters:
                query += " AND platform_id = ?"
                params.append(filters["platform_id"])
            
            if "category_name" in filters:
                query += " AND category_name = ?"
                params.append(filters["category_name"])
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            articles = []
            for row in rows:
                articles.append(Article(
                    id=row[0],
                    platform_id=row[1],
                    community_article_id=row[2],
                    community_id=row[3],
                    title=row[4],
                    content=row[5],
                    images=row[6],
                    writer_nickname=row[7],
                    writer_id=row[8],
                    like_count=row[9],
                    comment_count=row[10],
                    view_count=row[11],
                    created_at=datetime.fromisoformat(row[12]),
                    category_name=row[13]
                ))
            
            return articles
    
    def get_articles_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 게시글 수를 반환합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM articles WHERE 1=1"
            params = []
            
            if "platform_id" in filters:
                query += " AND platform_id = ?"
                params.append(filters["platform_id"])
            
            if "category_name" in filters:
                query += " AND category_name = ?"
                params.append(filters["category_name"])
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    def get_reviews_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Review]:
        """필터 조건에 따라 후기를 조회합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM reviews WHERE 1=1"
            params = []
            
            if "platform_id" in filters:
                query += " AND platform_id = ?"
                params.append(filters["platform_id"])
            
            if "category_name" in filters:
                query += " AND title LIKE ?"
                params.append(f"%{filters['category_name']}%")
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            reviews = []
            for row in rows:
                reviews.append(Review(
                    id=row[0],
                    platform_id=row[1],
                    platform_review_id=row[2],
                    community_id=row[3],
                    title=row[4],
                    content=row[5],
                    images=row[6],
                    writer_nickname=row[7],
                    writer_id=row[8],
                    like_count=row[9],
                    rating=row[10],
                    price=row[11],
                    categories=row[12],
                    sub_categories=row[13],
                    surgery_date=row[14],
                    hospital_name=row[15],
                    doctor_name=row[16],
                    is_blind=bool(row[17]),
                    is_image_blur=bool(row[18]),
                    is_certificated_review=bool(row[19]),
                    created_at=datetime.fromisoformat(row[20])
                ))
            
            return reviews
    
    def get_reviews_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 후기 수를 반환합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM reviews WHERE 1=1"
            params = []
            
            if "platform_id" in filters:
                query += " AND platform_id = ?"
                params.append(filters["platform_id"])
            
            if "category_name" in filters:
                query += " AND title LIKE ?"
                params.append(f"%{filters['category_name']}%")
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    def get_comments_by_filters(self, filters: Dict, limit: int = 20, offset: int = 0) -> List[Comment]:
        """필터 조건에 따라 댓글을 조회합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM comments WHERE 1=1"
            params = []
            
            if "article_id" in filters:
                query += " AND article_id = ?"
                params.append(filters["article_id"])
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            comments = []
            for row in rows:
                comments.append(Comment(
                    id=row[0],
                    article_id=row[1],
                    content=row[2],
                    writer_nickname=row[3],
                    writer_id=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    parent_comment_id=row[6]
                ))
            
            return comments
    
    def get_comments_count_by_filters(self, filters: Dict) -> int:
        """필터 조건에 따른 댓글 수를 반환합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM comments WHERE 1=1"
            params = []
            
            if "article_id" in filters:
                query += " AND article_id = ?"
                params.append(filters["article_id"])
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """ID로 게시글을 조회합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            
            if row:
                return Article(
                    id=row[0],
                    platform_id=row[1],
                    community_article_id=row[2],
                    community_id=row[3],
                    title=row[4],
                    content=row[5],
                    images=row[6],
                    writer_nickname=row[7],
                    writer_id=row[8],
                    like_count=row[9],
                    comment_count=row[10],
                    view_count=row[11],
                    created_at=datetime.fromisoformat(row[12]),
                    category_name=row[13]
                )
            return None
    
    def get_article_by_platform_id_and_community_article_id(self, platform_id: str, community_article_id: str) -> Optional[Dict]:
        """플랫폼 ID와 커뮤니티 게시글 ID로 게시글 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, platform_id, community_article_id, community_id, title, content, 
                       images, writer_nickname, writer_id, like_count, comment_count, 
                       view_count, created_at, category_name
                FROM articles 
                WHERE platform_id = ? AND community_article_id = ?
            ''', (platform_id, community_article_id))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'platform_id': row[1],
                    'community_article_id': row[2],
                    'community_id': row[3],
                    'title': row[4],
                    'content': row[5],
                    'images': row[6],
                    'writer_nickname': row[7],
                    'writer_id': row[8],
                    'like_count': row[9],
                    'comment_count': row[10],
                    'view_count': row[11],
                    'created_at': row[12],
                    'category_name': row[13]
                }
            
            return None
    
    def get_review_by_id(self, review_id: int) -> Optional[Review]:
        """ID로 후기를 조회합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM reviews WHERE id = ?", (review_id,))
            row = cursor.fetchone()
            
            if row:
                return Review(
                    id=row[0],
                    platform_id=row[1],
                    platform_review_id=row[2],
                    community_id=row[3],
                    title=row[4],
                    content=row[5],
                    images=row[6],
                    writer_nickname=row[7],
                    writer_id=row[8],
                    like_count=row[9],
                    rating=row[10],
                    price=row[11],
                    categories=row[12],
                    sub_categories=row[13],
                    surgery_date=row[14],
                    hospital_name=row[15],
                    doctor_name=row[16],
                    is_blind=bool(row[17]),
                    is_image_blur=bool(row[18]),
                    is_certificated_review=bool(row[19]),
                    created_at=datetime.fromisoformat(row[20])
                )
            return None
    
    def get_platform_statistics(self, platform_id: str) -> Dict:
        """특정 플랫폼의 통계를 반환합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 게시글 수
            cursor.execute("SELECT COUNT(*) FROM articles WHERE platform_id = ?", (platform_id,))
            article_count = cursor.fetchone()[0]
            
            # 후기 수
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE platform_id = ?", (platform_id,))
            review_count = cursor.fetchone()[0]
            
            # 댓글 수 (해당 플랫폼의 게시글에 달린 댓글)
            cursor.execute('''
                SELECT COUNT(*) FROM comments c
                JOIN articles a ON c.article_id = a.id
                WHERE a.platform_id = ?
            ''', (platform_id,))
            comment_count = cursor.fetchone()[0]
            
            return {
                "articles": article_count,
                "reviews": review_count,
                "comments": comment_count
            }
    
    def get_daily_statistics(self, date: str) -> Dict:
        """특정 날짜의 통계를 반환합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 해당 날짜의 게시글 수
            cursor.execute('''
                SELECT COUNT(*) FROM articles 
                WHERE DATE(created_at) = ?
            ''', (date,))
            article_count = cursor.fetchone()[0]
            
            # 해당 날짜의 후기 수
            cursor.execute('''
                SELECT COUNT(*) FROM reviews 
                WHERE DATE(created_at) = ?
            ''', (date,))
            review_count = cursor.fetchone()[0]
            
            # 해당 날짜의 댓글 수
            cursor.execute('''
                SELECT COUNT(*) FROM comments 
                WHERE DATE(created_at) = ?
            ''', (date,))
            comment_count = cursor.fetchone()[0]
            
            return {
                "articles": article_count,
                "reviews": review_count,
                "comments": comment_count
            }
    
    def get_trend_statistics(self, days: int) -> Dict:
        """최근 N일간의 트렌드 통계를 반환합니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 최근 N일간의 일별 통계
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM articles 
                WHERE created_at >= DATE('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date
            '''.format(days))
            article_trends = cursor.fetchall()
            
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM reviews 
                WHERE created_at >= DATE('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date
            '''.format(days))
            review_trends = cursor.fetchall()
            
            return {
                "article_trends": [{"date": row[0], "count": row[1]} for row in article_trends],
                "review_trends": [{"date": row[0], "count": row[1]} for row in review_trends]
            }
    
    def get_connection(self):
        """데이터베이스 연결을 반환합니다."""
        return sqlite3.connect(self.db_path) 