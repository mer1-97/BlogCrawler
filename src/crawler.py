import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.logger import crawler_logger

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
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-software-rasterizer')
        
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

    def _extract_publish_date(self, driver):
        try:
            date_element = driver.find_element(By.CSS_SELECTOR, '.blog_date, .se_publishDate, .date, .se_date, .date_time, .writer_info .date')
            return date_element.text.strip()
        except NoSuchElementException:
            return ""

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

    def _extract_sticker_count(self, driver):
        try:
            stickers = driver.find_elements(By.CSS_SELECTOR, 'img.se-sticker-image, img.se-sticker-imgae, .se-sticker-image')
            return len(stickers)
        except Exception:
            return 0

    def _extract_comment_count(self, driver):
        try:
            comment_label = driver.find_element(By.XPATH, "//span[@class='sp ico'][contains(text(), '댓글')]")
            comment_count_element = comment_label.find_element(By.XPATH, "./following-sibling::em")
            comment_text = comment_count_element.text.strip()
            return int(''.join(filter(str.isdigit, comment_text)))
        except Exception:
            return 0

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

    def _extract_map_count(self, driver):
        try:
            maps = driver.find_elements(By.CSS_SELECTOR, 'a.se-map-info, .se-module-map')
            return len(maps)
        except Exception:
            return 0

    def _extract_image_count(self, driver):
        try:
            images = driver.find_elements(By.CSS_SELECTOR, 'img[id^="img_"]')
            return len(images)
        except Exception:
            return 0 