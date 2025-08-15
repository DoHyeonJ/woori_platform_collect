#!/usr/bin/env python3
"""
comments 테이블 마이그레이션 스크립트
기존 구조에서 새로운 구조로 변경
"""
import os
import sys
import sqlite3
from datetime import datetime

# utils 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_comments_table(db_path: str = "data/collect_data.db"):
    """comments 테이블을 새로운 구조로 마이그레이션"""
    try:
        print(f"🔧 comments 테이블 마이그레이션 시작: {db_path}")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 1. 기존 테이블 구조 확인
            cursor.execute("PRAGMA table_info(comments)")
            columns = cursor.fetchall()
            print(f"현재 comments 테이블 컬럼: {[col[1] for col in columns]}")
            
            # 2. 임시 테이블 생성 (새로운 구조)
            print("📋 새로운 구조의 임시 테이블 생성 중...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id TEXT NOT NULL,
                    community_article_id TEXT NOT NULL,
                    community_comment_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    writer_nickname TEXT NOT NULL,
                    writer_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parent_comment_id TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 3. 기존 데이터 마이그레이션
            print("🔄 기존 데이터 마이그레이션 중...")
            
            # 기존 comments 테이블이 있는지 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'")
            if cursor.fetchone():
                # 기존 데이터 조회
                cursor.execute("SELECT * FROM comments")
                old_comments = cursor.fetchall()
                print(f"기존 댓글 수: {len(old_comments)}개")
                
                if old_comments:
                    # 기존 데이터를 새로운 구조로 변환
                    for old_comment in old_comments:
                        try:
                            # 기존 구조: (id, article_id, content, writer_nickname, writer_id, created_at, parent_comment_id, collected_at)
                            # 새로운 구조: (platform_id, community_article_id, community_comment_id, content, writer_nickname, writer_id, created_at, parent_comment_id, collected_at)
                            
                            # article_id로 articles 테이블에서 platform_id와 community_article_id 조회
                            cursor.execute("""
                                SELECT platform_id, community_article_id 
                                FROM articles 
                                WHERE id = ?
                            """, (old_comment[1],))  # old_comment[1]은 article_id
                            
                            article_info = cursor.fetchone()
                            if article_info:
                                platform_id, community_article_id = article_info
                                
                                # 새로운 테이블에 데이터 삽입
                                cursor.execute('''
                                    INSERT INTO comments_new (
                                        platform_id, community_article_id, community_comment_id,
                                        content, writer_nickname, writer_id, created_at, 
                                        parent_comment_id, collected_at
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    platform_id,
                                    community_article_id,
                                    str(old_comment[0]),  # 기존 id를 community_comment_id로 사용
                                    old_comment[2],  # content
                                    old_comment[3],  # writer_nickname
                                    old_comment[4],  # writer_id
                                    old_comment[5],  # created_at
                                    str(old_comment[6]) if old_comment[6] else None,  # parent_comment_id
                                    old_comment[7] if old_comment[7] else datetime.now()  # collected_at
                                ))
                            else:
                                print(f"⚠️ 댓글 ID {old_comment[0]}의 게시글 정보를 찾을 수 없습니다")
                                
                        except Exception as e:
                            print(f"❌ 댓글 ID {old_comment[0]} 마이그레이션 실패: {str(e)}")
                            continue
                    
                    print(f"✅ {len(old_comments)}개 댓글 마이그레이션 완료")
                else:
                    print("ℹ️ 마이그레이션할 기존 댓글이 없습니다")
            
            # 4. 기존 테이블 삭제 및 새 테이블 이름 변경
            print("🔄 테이블 교체 중...")
            cursor.execute("DROP TABLE IF EXISTS comments")
            cursor.execute("ALTER TABLE comments_new RENAME TO comments")
            
            # 5. 인덱스 생성
            print("📊 인덱스 생성 중...")
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_platform_article ON comments(platform_id, community_article_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_platform_comment ON comments(platform_id, community_comment_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON comments(parent_comment_id)')
            
            # 6. 외래키 제약 조건 추가
            print("🔗 외래키 제약 조건 추가 중...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments_with_fk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id TEXT NOT NULL,
                    community_article_id TEXT NOT NULL,
                    community_comment_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    writer_nickname TEXT NOT NULL,
                    writer_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parent_comment_id TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (platform_id, community_article_id) REFERENCES articles (platform_id, community_article_id),
                    FOREIGN KEY (parent_comment_id) REFERENCES comments (community_comment_id)
                )
            ''')
            
            # 데이터 복사
            cursor.execute("INSERT INTO comments_with_fk SELECT * FROM comments")
            cursor.execute("DROP TABLE comments")
            cursor.execute("ALTER TABLE comments_with_fk RENAME TO comments")
            
            # 7. 최종 확인
            cursor.execute("PRAGMA table_info(comments)")
            final_columns = cursor.fetchall()
            print(f"✅ 마이그레이션 완료! 최종 comments 테이블 컬럼: {[col[1] for col in final_columns]}")
            
            # 댓글 수 확인
            cursor.execute("SELECT COUNT(*) FROM comments")
            comment_count = cursor.fetchone()[0]
            print(f"📊 최종 댓글 수: {comment_count}개")
            
            conn.commit()
            print("🎉 comments 테이블 마이그레이션 완료!")
            
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {str(e)}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    print("=== comments 테이블 마이그레이션 ===")
    
    # 데이터베이스 경로 확인
    db_path = "data/collect_data.db"
    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        sys.exit(1)
    
    # 마이그레이션 실행
    migrate_comments_table(db_path)
