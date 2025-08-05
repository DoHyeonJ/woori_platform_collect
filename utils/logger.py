import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class LoggerManager:
    """통합 로깅 관리자"""
    
    def __init__(self, name: str = "woori_platform_collect"):
        self.name = name
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """로거 설정"""
        # 로그 디렉토리 생성
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 오늘 날짜로 로그 파일명 생성
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"{today}.log"
        
        # 로거 생성
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # 기존 핸들러 제거 (중복 방지)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 파일 핸들러 설정
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """로거 반환"""
        if name:
            return logging.getLogger(f"{self.name}.{name}")
        return self.logger
    
    def info(self, message: str):
        """정보 로그"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """디버그 로그"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """경고 로그"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """에러 로그"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """치명적 에러 로그"""
        self.logger.critical(message)


# 전역 로거 인스턴스
_logger_manager = LoggerManager()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """로거 반환 함수"""
    return _logger_manager.get_logger(name)


def log_info(message: str):
    """정보 로그"""
    _logger_manager.info(message)


def log_debug(message: str):
    """디버그 로그"""
    _logger_manager.debug(message)


def log_warning(message: str):
    """경고 로그"""
    _logger_manager.warning(message)


def log_error(message: str):
    """에러 로그"""
    _logger_manager.error(message)


def log_critical(message: str):
    """치명적 에러 로그"""
    _logger_manager.critical(message)


class LoggedClass:
    """로깅 기능이 포함된 기본 클래스"""
    
    def __init__(self, logger_name: Optional[str] = None):
        self.logger = get_logger(logger_name or self.__class__.__name__)
    
    def log_info(self, message: str):
        """정보 로그"""
        self.logger.info(message)
    
    def log_debug(self, message: str):
        """디버그 로그"""
        self.logger.debug(message)
    
    def log_warning(self, message: str):
        """경고 로그"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """에러 로그"""
        self.logger.error(message)
    
    def log_critical(self, message: str):
        """치명적 에러 로그"""
        self.logger.critical(message) 