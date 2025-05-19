import logging
import os
from datetime import datetime

class Logger:
    _timestamp = None
    
    @classmethod
    def _get_timestamp(cls):
        if cls._timestamp is None:
            cls._timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        return cls._timestamp
    
    def __init__(self, name, log_type):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 이미 핸들러가 있다면 제거
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 로그 디렉토리 생성
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 로그 파일명 생성 (프로그램 실행 시점의 타임스탬프 사용)
        timestamp = self._get_timestamp()
        log_file = os.path.join(log_dir, f'{timestamp}_{log_type}_logs.txt')
        
        # 파일 핸들러 설정
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러 설정 (ERROR 레벨만 표시)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        
        # 포매터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger

# 프로그램 로거 생성
program_logger = Logger('program', 'program').get_logger()

# 크롤러 로거 생성
crawler_logger = Logger('crawler', 'crawler').get_logger() 