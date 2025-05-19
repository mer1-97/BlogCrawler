import urllib.request
import json
import time
from src.logger import program_logger

class NaverBlogAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def search_blog(self, keyword, display=8):
        """네이버 블로그 검색 API를 사용하여 검색 결과를 가져오는 함수"""
        program_logger.info(f"API 검색 시작: 키워드='{keyword}', display={display}")
        start_time = time.time()
        
        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display={display}"
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)
        
        try:
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            
            if rescode == 200:
                response_body = response.read()
                result = json.loads(response_body.decode('utf-8'))
                elapsed_time = time.time() - start_time
                program_logger.info(f"API 검색 성공: {len(result['items'])}개 결과 (소요시간: {elapsed_time:.2f}초)")
                return result['items']
            else:
                elapsed_time = time.time() - start_time
                program_logger.error(f"API 검색 실패: Error Code {rescode} (소요시간: {elapsed_time:.2f}초)")
                return []
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            program_logger.error(f"API 검색 실패: {str(e)} (소요시간: {elapsed_time:.2f}초)")
            return [] 