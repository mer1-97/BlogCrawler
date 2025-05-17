import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
from src.crawler import NaverBlogCrawler
from src.parser import NaverBlogParser
from src.utils import export_to_csv, print_result

def setup_driver():
    """Selenium WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # 새로운 headless 모드
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=412,915')  # 모바일 화면 크기
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
    
    # Chrome 경로들을 순차적으로 시도
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        None  # 기본 설치 위치
    ]
    
    for chrome_path in chrome_paths:
        try:
            if chrome_path:
                chrome_options.binary_location = chrome_path
            
            # 현재 디렉토리의 chromedriver.exe 사용
            service = Service("chromedriver.exe")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            print(f"Chrome 경로 {chrome_path} 시도 실패: {str(e)}")
            continue
    
    raise Exception("Chrome 브라우저를 시작할 수 없습니다. Chrome이 설치되어 있는지 확인해주세요.")

def get_blog_info(blog_url):
    """블로그 정보를 Selenium으로 파싱하는 함수"""
    # 모바일 버전 URL로 변환 (이미 모바일 버전이면 변환하지 않음)
    mobile_url = blog_url if 'm.blog.naver.com' in blog_url else blog_url.replace('blog.naver.com', 'm.blog.naver.com')
    print(f"\n[URL 분석 시작]: {mobile_url}")
    
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)  # 최대 10초 대기
    
    try:
        driver.get(mobile_url)
        
        # 페이지 로딩 대기
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(3)  # 추가 대기로 동적 콘텐츠 로딩
        
        print("페이지 로딩 완료")
        
        # 1. 본문 추출
        content = ""
        try:
            # 새로운 버전 블로그
            content_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.se-main-container'))
            )
            content = content_element.text
            print("본문 추출 완료")
        except TimeoutException:
            try:
                # 옛날 버전 블로그
                content_element = driver.find_element(By.CSS_SELECTOR, '#viewTypeSelector, .post-view, .se_component_wrap')
                content = content_element.text
                print("본문 추출 완료 (옛날 버전)")
            except NoSuchElementException:
                print("본문을 찾을 수 없습니다")

        # 2. 작성일 추출
        publish_date = ""
        try:
            date_element = driver.find_element(By.CSS_SELECTOR, '.blog_date, .se_publishDate, .date, .se_date, .date_time, .writer_info .date')
            publish_date = date_element.text.strip()
            print(f"작성일: {publish_date}")
        except NoSuchElementException:
            print("작성일을 찾을 수 없습니다")

        # 3. 해시태그 추출
        try:
            # 모바일 버전의 해시태그는 .tag_wrap 내부의 a 태그에 있음
            hashtag_elements = driver.find_elements(By.CSS_SELECTOR, '.tag_wrap a')
            if not hashtag_elements:  # 다른 클래스도 시도
                hashtag_elements = driver.find_elements(By.CSS_SELECTOR, '.post_tag_wrap a, .tag__tFC3j')
            
            hashtag_texts = [tag.text.strip() for tag in hashtag_elements if tag.text.strip()]
            
            # 해시태그 수 계산
            visible_hashtag_count = sum(1 for text in hashtag_texts if text.startswith('#'))
            additional_count = 0
            
            # +숫자 형식의 추가 해시태그 수 확인
            for text in hashtag_texts:
                if text.startswith('+'):
                    try:
                        additional_count = int(text[1:])  # '+' 제외하고 숫자만 추출
                        break
                    except ValueError:
                        continue
            
            total_hashtag_count = visible_hashtag_count + additional_count
            
            print(f"해시태그 수: {total_hashtag_count}")

        except Exception as e:
            print(f"해시태그 추출 중 오류: {str(e)}")

        # 4. 스티커 수 계산
        sticker_count = 0
        try:
            # 여러 가지 스티커 클래스 시도
            stickers = driver.find_elements(By.CSS_SELECTOR, 'img.se-sticker-image, img.se-sticker-imgae, .se-sticker-image')
            sticker_count = len(stickers)
            print(f"스티커 수: {sticker_count}")
        except Exception as e:
            print(f"스티커 수 계산 중 오류: {str(e)}")

        # 5. 댓글 수 추출
        comment_count = 0
        try:
            # 모바일 버전 댓글 수 추출 - 댓글 텍스트가 있는 span 다음의 em 태그 찾기
            comment_label = driver.find_element(By.XPATH, "//span[@class='sp ico'][contains(text(), '댓글')]")
            comment_count_element = comment_label.find_element(By.XPATH, "./following-sibling::em")
            comment_text = comment_count_element.text.strip()
            comment_count = int(''.join(filter(str.isdigit, comment_text)))
            print(f"댓글 수: {comment_count}")
        except NoSuchElementException:
            print("댓글 수 요소를 찾을 수 없습니다")
        except ValueError:
            print("댓글 수를 숫자로 변환할 수 없습니다")
        except Exception as e:
            print(f"댓글 수 추출 중 오류: {str(e)}")

        # 6. 공감 수 추출
        like_count = 0
        try:
            like_elements = driver.find_elements(By.CSS_SELECTOR, '.like_count, .btn_like .num, .u_cnt._count')
            for element in like_elements:
                try:
                    count_text = element.text.strip()
                    count = int(''.join(filter(str.isdigit, count_text)))
                    if count > like_count:  # 가장 큰 수를 공감 수로 사용
                        like_count = count
                except ValueError:
                    continue
            print(f"공감 수: {like_count}")
        except Exception as e:
            print(f"공감 수 추출 중 오류: {str(e)}")

        # 7. 지도 정보 수 계산
        map_count = 0
        try:
            maps = driver.find_elements(By.CSS_SELECTOR, 'a.se-map-info, .se-module-map')
            map_count = len(maps)
            print(f"지도 정보 수: {map_count}")
        except Exception as e:
            print(f"지도 정보 수 계산 중 오류: {str(e)}")

        # 8. 이미지 수 계산
        image_count = 0
        try:
            # img_숫자 형식의 id를 가진 모든 이미지 찾기
            images = driver.find_elements(By.CSS_SELECTOR, 'img[id^="img_"]')
            # 단순히 img_숫자 패턴을 가진 이미지의 개수를 세기
            image_count = len(images)
            print(f"이미지 수: {image_count}")
        except Exception as e:
            print(f"이미지 수 계산 중 오류: {str(e)}")

        # 결과 반환
        result = {
            'URL': blog_url,
            'Content': content,
            'PublishDate': publish_date,
            'HashtagCount': total_hashtag_count if 'total_hashtag_count' in locals() else 0,
            'StickerCount': sticker_count,
            'CommentCount': comment_count,
            'LikeCount': like_count,
            'MapCount': map_count,
            'ImageCount': image_count
        }
        
        return result
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None
    
    finally:
        driver.quit()  # 브라우저 종료

def main():
    # 분석할 URL 목록
    urls = [
        "https://blog.naver.com/starship89/223012792282",
        "https://m.blog.naver.com/ppppcoral/223738468893"
    ]
    
    print("블로그 정보 수집을 시작합니다...")
    
    # 크롤러 초기화
    crawler = NaverBlogCrawler()
    if not crawler.setup_driver():
        print("크롤러 초기화 실패")
        return
    
    # 결과를 저장할 리스트
    results = []
    
    try:
        # 각 URL 처리
        for url in urls:
            # 페이지 크롤링
            page_source = crawler.crawl_blog(url)
            if not page_source:
                continue
            
            # 데이터 파싱
            parser = NaverBlogParser(crawler.driver, crawler.wait)
            result = parser.parse_all()
            result['URL'] = url
            
            # 결과 출력 및 저장
            print_result(result)
            results.append(result)
        
        # CSV 파일로 저장
        if results:
            filename = export_to_csv(results)
            if filename:
                print(f"\nCSV 파일이 생성되었습니다: {filename}")
    
    finally:
        # 크롤러 종료
        crawler.close()

if __name__ == "__main__":
    main() 