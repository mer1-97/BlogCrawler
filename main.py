import time
import random
import urllib.request
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import multiprocessing
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm
from src.logger import program_logger, crawler_logger
from src.api import NaverBlogAPI
from src.crawler import NaverBlogCrawler
from src.processor import BlogProcessor

class NaverBlogCrawler:
    def __init__(self):
        self.chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            None
        ]

    def setup_driver(self):
        """Selenium WebDriver 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=412,915')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        
        # 개발자 도구 및 WebGL 경고 메시지 숨기기
        chrome_options.add_argument('--log-level=3')  # 로그 레벨을 최소화
        chrome_options.add_argument('--silent')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # DevTools 로그 숨기기
        chrome_options.add_argument('--disable-logging')  # 로깅 비활성화
        chrome_options.add_argument('--disable-web-security')  # WebGL 관련 경고 숨기기
        chrome_options.add_argument('--disable-software-rasterizer')  # SwiftShader 관련 경고 숨기기
        
        for chrome_path in self.chrome_paths:
            try:
                if chrome_path:
                    chrome_options.binary_location = chrome_path
                
                service = Service("chromedriver.exe")
                return webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                continue
        
        raise Exception("Chrome 브라우저를 시작할 수 없습니다.")

    def get_blog_info(self, blog_url):
        """블로그 정보를 Selenium으로 파싱하는 함수"""
        crawler_logger.info(f"크롤링 시작: {blog_url}")
        start_time = time.time()
        
        time.sleep(random.uniform(0.5, 1.5))
        
        mobile_url = blog_url if 'm.blog.naver.com' in blog_url else blog_url.replace('blog.naver.com', 'm.blog.naver.com')
        
        driver = self.setup_driver()
        wait = WebDriverWait(driver, 10)
        
        try:
            driver.get(mobile_url)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(random.uniform(0.5, 1))
            
            content = self._extract_content(driver, wait)
            publish_date = self._extract_publish_date(driver)
            hashtag_count = self._extract_hashtag_count(driver)
            sticker_count = self._extract_sticker_count(driver)
            comment_count = self._extract_comment_count(driver)
            like_count = self._extract_like_count(driver)
            map_count = self._extract_map_count(driver)
            image_count = self._extract_image_count(driver)
            
            elapsed_time = time.time() - start_time
            crawler_logger.info(f"크롤링 성공: {blog_url} (소요시간: {elapsed_time:.2f}초)")
            
            return {
                'URL': blog_url,
                'Content': content,
                'PublishDate': publish_date,
                'HashtagCount': hashtag_count,
                'StickerCount': sticker_count,
                'CommentCount': comment_count,
                'LikeCount': like_count,
                'MapCount': map_count,
                'ImageCount': image_count
            }
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            crawler_logger.error(f"크롤링 실패: {blog_url} (소요시간: {elapsed_time:.2f}초) - 오류: {str(e)}")
            return None
        
        finally:
            driver.quit()

    # 1. 본문 추출
    def _extract_content(self, driver, wait):
        try:
            content_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.se-main-container'))
            )
            return content_element.text
        except TimeoutException:
            try:
                content_element = driver.find_element(By.CSS_SELECTOR, '#viewTypeSelector, .post-view, .se_component_wrap')
                return content_element.text
            except NoSuchElementException:
                return ""

    # 2. 작성일 추출
    def _extract_publish_date(self, driver):
        try:
            date_element = driver.find_element(By.CSS_SELECTOR, '.blog_date, .se_publishDate, .date, .se_date, .date_time, .writer_info .date')
            return date_element.text.strip()
        except NoSuchElementException:
            return ""

    # 3. 해시태그 수 추출
    def _extract_hashtag_count(self, driver):
        try:
            hashtag_elements = driver.find_elements(By.CSS_SELECTOR, '.tag_wrap a')
            if not hashtag_elements:
                hashtag_elements = driver.find_elements(By.CSS_SELECTOR, '.post_tag_wrap a, .tag__tFC3j')
            
            hashtag_texts = [tag.text.strip() for tag in hashtag_elements if tag.text.strip()]
            visible_hashtag_count = sum(1 for text in hashtag_texts if text.startswith('#'))
            additional_count = 0
            
            for text in hashtag_texts:
                if text.startswith('+'):
                    try:
                        additional_count = int(text[1:])
                        break
                    except ValueError:
                        continue
            
            return visible_hashtag_count + additional_count
        except Exception:
            return 0

    # 4. 스티커 수 추출
    def _extract_sticker_count(self, driver):
        try:
            stickers = driver.find_elements(By.CSS_SELECTOR, 'img.se-sticker-image, img.se-sticker-imgae, .se-sticker-image')
            return len(stickers)
        except Exception:
            return 0

    # 5. 댓글 수 추출
    def _extract_comment_count(self, driver):
        try:
            comment_label = driver.find_element(By.XPATH, "//span[@class='sp ico'][contains(text(), '댓글')]")
            comment_count_element = comment_label.find_element(By.XPATH, "./following-sibling::em")
            comment_text = comment_count_element.text.strip()
            return int(''.join(filter(str.isdigit, comment_text)))
        except Exception:
            return 0

    # 6. 공감 수 추출
    def _extract_like_count(self, driver):
        try:
            like_elements = driver.find_elements(By.CSS_SELECTOR, '.like_count, .btn_like .num, .u_cnt._count')
            max_count = 0
            for element in like_elements:
                try:
                    count_text = element.text.strip()
                    count = int(''.join(filter(str.isdigit, count_text)))
                    max_count = max(max_count, count)
                except ValueError:
                    continue
            return max_count
        except Exception:
            return 0

    # 7. 지도 수 추출
    def _extract_map_count(self, driver):
        try:
            maps = driver.find_elements(By.CSS_SELECTOR, 'a.se-map-info, .se-module-map')
            return len(maps)
        except Exception:
            return 0

    # 8. 이미지 수 추출
    def _extract_image_count(self, driver):
        try:
            images = driver.find_elements(By.CSS_SELECTOR, 'img[id^="img_"]')
            return len(images)
        except Exception:
            return 0

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

def process_blog_item(item, crawler):
    """멀티프로세싱을 위한 블로그 아이템 처리 함수"""
    blog_url = item['link']
    result = crawler.get_blog_info(blog_url)
    
    if result:
        result['Title'] = item['title'].replace('<b>', '').replace('</b>', '')
        result['APIPostDate'] = item['postdate']
        return result
    return None

def main():
    program_logger.info("프로그램 시작")
    
    # API 인증 정보 입력 받기
    client_id = input("네이버 API Client ID를 입력하세요: ")
    client_secret = input("네이버 API Client Secret을 입력하세요: ")
    
    # API 검색 실행
    api = NaverBlogAPI(client_id, client_secret)
    blog_items = api.search_blog("맛집")
    
    if not blog_items:
        program_logger.warning("검색 결과가 없습니다.")
        return
    
    # 크롤러와 프로세서 초기화
    crawler = NaverBlogCrawler()
    processor = BlogProcessor(crawler)
    
    # 블로그 아이템 처리
    results = processor.process_items(blog_items)
    
    # 결과 저장
    filename = processor.save_results(results)
    
    program_logger.info("프로그램 종료")
    if filename:
        print(f"\n크롤링이 완료되었습니다. 결과는 {filename}에 저장되었습니다.")
        print(f"상세 로그는 logs 디렉토리에서 확인할 수 있습니다.")

if __name__ == "__main__":
    main() 