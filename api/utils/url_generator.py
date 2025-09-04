#!/usr/bin/env python3
"""
플랫폼별 원문 URL 생성 유틸리티
"""
from typing import Optional, Dict, Any


class ArticleURLGenerator:
    """게시글 원문 URL 생성기"""
    
    # 네이버 카페 ID 매핑 (카페 이름 -> 카페 URL ID)
    # 실제 카페 URL에서 사용되는 ID (숫자 ID -> URL ID)
    NAVER_CAFE_IDS = {
        "10912875": "fox5282",      # 여우야
        "12285441": "aplusfox",     # A+여우야
        "11498714": "plasticwiki",  # 성형위키백과
        "13067396": "foxlife",      # 여생남정
        "23451561": "chicment",     # 시크먼트
        "15880379": "gaasa",        # 가아사
        "10050813": "powderroom"    # 파우더룸
    }
    
    # 카페 이름 -> 숫자 ID 매핑 (기존 매핑 유지)
    NAVER_CAFE_NAME_TO_ID = {
        "여우야": "10912875",
        "A+여우야": "12285441", 
        "성형위키백과": "11498714",
        "여생남정": "13067396",
        "시크먼트": "23451561",
        "가아사": "15880379",
        "파우더룸": "10050813"
    }
    
    @staticmethod
    def generate_article_url(platform_id: str, community_article_id: str, 
                           category_name: Optional[str] = None, 
                           additional_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        플랫폼별 게시글 원문 URL 생성
        
        Args:
            platform_id: 플랫폼 ID (gangnamunni, babitalk, babitalk_talk, babitalk_event_ask, naver)
            community_article_id: 커뮤니티 게시글 ID
            category_name: 카테고리명 (네이버의 경우 카페명, 바비톡의 경우 카테고리 구분용)
            additional_data: 추가 데이터 (바비톡 카테고리 구분 등)
        
        Returns:
            생성된 URL 또는 None
        """
        if not community_article_id:
            return None
            
        try:
            if platform_id == "gangnamunni":
                return ArticleURLGenerator._generate_gangnamunni_url(community_article_id)
            elif platform_id == "babitalk":
                return ArticleURLGenerator._generate_babitalk_review_url(community_article_id)
            elif platform_id == "babitalk_talk":
                return ArticleURLGenerator._generate_babitalk_talk_url(community_article_id)
            elif platform_id == "babitalk_event_ask":
                return ArticleURLGenerator._generate_babitalk_event_ask_url(community_article_id)
            elif platform_id == "naver":
                return ArticleURLGenerator._generate_naver_url(community_article_id, category_name)
            else:
                return None
        except Exception:
            return None
    
    @staticmethod
    def generate_review_url(platform_id: str, platform_review_id: str, 
                          category_name: Optional[str] = None, 
                          additional_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        플랫폼별 리뷰 원문 URL 생성
        
        Args:
            platform_id: 플랫폼 ID (babitalk 등)
            platform_review_id: 플랫폼 리뷰 ID
            category_name: 카테고리명
            additional_data: 추가 데이터
        
        Returns:
            생성된 URL 또는 None
        """
        if not platform_review_id:
            return None
            
        try:
            if platform_id == "babitalk":
                return ArticleURLGenerator._generate_babitalk_review_url(platform_review_id)
            else:
                return None
        except Exception:
            return None
    
    @staticmethod
    def _generate_gangnamunni_url(article_id: str) -> str:
        """강남언니 URL 생성"""
        return f"https://www.gangnamunni.com/community/{article_id}"
    
    @staticmethod
    def _generate_babitalk_review_url(article_id: str) -> str:
        """바비톡 시술후기 URL 생성"""
        return f"https://web.babitalk.com/reviews/{article_id}"
    
    @staticmethod
    def _generate_babitalk_talk_url(article_id: str) -> str:
        """바비톡 자유톡 URL 생성"""
        return f"https://web.babitalk.com/community/{article_id}"
    
    @staticmethod
    def _generate_babitalk_event_ask_url(article_id: str) -> str:
        """바비톡 발품후기 URL 생성"""
        return f"https://web.babitalk.com/ask-memos/{article_id}"
    
    @staticmethod
    def _generate_naver_url(article_id: str, category_name: Optional[str] = None) -> Optional[str]:
        """네이버 카페 URL 생성"""
        if not category_name:
            return None
            
        # 카페 이름으로 숫자 ID 찾기
        cafe_numeric_id = ArticleURLGenerator.NAVER_CAFE_NAME_TO_ID.get(category_name)
        if not cafe_numeric_id:
            # 카페 이름이 매핑에 없는 경우 기본값 사용
            return f"https://cafe.naver.com/unknown/{article_id}"
            
        # 숫자 ID로 URL ID 찾기
        cafe_url_id = ArticleURLGenerator.NAVER_CAFE_IDS.get(cafe_numeric_id)
        if not cafe_url_id:
            # URL ID가 매핑에 없는 경우 기본값 사용
            cafe_url_id = "unknown"
            
        return f"https://cafe.naver.com/{cafe_url_id}/{article_id}"
    
    @staticmethod
    def get_platform_display_name(platform_id: str) -> str:
        """플랫폼 ID를 표시용 이름으로 변환"""
        platform_names = {
            "gangnamunni": "강남언니",
            "babitalk": "바비톡(시술후기)",
            "babitalk_talk": "바비톡(자유톡)",
            "babitalk_event_ask": "바비톡(발품후기)",
            "naver": "네이버카페"
        }
        return platform_names.get(platform_id, platform_id)
