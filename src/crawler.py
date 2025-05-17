from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class NaverBlogCrawler:
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup_driver(self):
        """Selenium WebDriver 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=412,915')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        
        try:
            service = Service("chromedriver.exe")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            return True
        except Exception as e:
            print(f"WebDriver 설정 중 오류 발생: {str(e)}")
            return False
    
    def close(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
    
    def crawl_blog(self, url):
        """블로그 포스트 크롤링"""
        if not self.driver:
            if not self.setup_driver():
                return None
        
        try:
            mobile_url = url if 'm.blog.naver.com' in url else url.replace('blog.naver.com', 'm.blog.naver.com')
            print(f"\n[URL 분석 시작]: {mobile_url}")
            
            self.driver.get(mobile_url)
            return self.driver.page_source
        except Exception as e:
            print(f"크롤링 중 오류 발생: {str(e)}")
            return None 