from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class NaverBlogParser:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
    
    def parse_content(self):
        """본문 내용 파싱"""
        try:
            content_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.se-main-container'))
            )
            return content_element.text
        except TimeoutException:
            try:
                content_element = self.driver.find_element(By.CSS_SELECTOR, '#viewTypeSelector, .post-view, .se_component_wrap')
                return content_element.text
            except NoSuchElementException:
                print("본문을 찾을 수 없습니다")
                return ""
    
    def parse_publish_date(self):
        """작성일 파싱"""
        try:
            date_element = self.driver.find_element(By.CSS_SELECTOR, '.blog_date, .se_publishDate, .date, .se_date, .date_time, .writer_info .date')
            return date_element.text.strip()
        except NoSuchElementException:
            print("작성일을 찾을 수 없습니다")
            return ""
    
    def parse_hashtags(self):
        """해시태그 파싱"""
        try:
            hashtag_elements = self.driver.find_elements(By.CSS_SELECTOR, '.tag_wrap a')
            if not hashtag_elements:
                hashtag_elements = self.driver.find_elements(By.CSS_SELECTOR, '.post_tag_wrap a, .tag__tFC3j')
            
            hashtag_texts = [tag.text.strip() for tag in hashtag_elements if tag.text.strip()]
            
            # 해시태그 수 계산
            visible_hashtag_count = sum(1 for text in hashtag_texts if text.startswith('#'))
            additional_count = 0
            
            # +숫자 형식의 추가 해시태그 수 확인
            for text in hashtag_texts:
                if text.startswith('+'):
                    try:
                        additional_count = int(text[1:])
                        break
                    except ValueError:
                        continue
            
            total_hashtag_count = visible_hashtag_count + additional_count
            return total_hashtag_count, [tag for tag in hashtag_texts if tag.startswith('#')]
        except Exception as e:
            print(f"해시태그 추출 중 오류: {str(e)}")
            return 0, []
    
    def parse_images(self):
        """이미지 수 파싱"""
        try:
            images = self.driver.find_elements(By.CSS_SELECTOR, 'img[id^="img_"]')
            return len(images)
        except Exception as e:
            print(f"이미지 수 계산 중 오류: {str(e)}")
            return 0
    
    def parse_comments(self):
        """댓글 수 파싱"""
        try:
            comment_label = self.driver.find_element(By.XPATH, "//span[@class='sp ico'][contains(text(), '댓글')]")
            comment_count_element = comment_label.find_element(By.XPATH, "./following-sibling::em")
            comment_text = comment_count_element.text.strip()
            return int(''.join(filter(str.isdigit, comment_text)))
        except Exception:
            return 0
    
    def parse_likes(self):
        """공감 수 파싱"""
        try:
            like_elements = self.driver.find_elements(By.CSS_SELECTOR, '.like_count, .btn_like .num, .u_cnt._count')
            for element in like_elements:
                try:
                    count_text = element.text.strip()
                    return int(''.join(filter(str.isdigit, count_text)))
                except ValueError:
                    continue
            return 0
        except Exception:
            return 0
    
    def parse_stickers(self):
        """스티커 수 파싱"""
        try:
            stickers = self.driver.find_elements(By.CSS_SELECTOR, 'img.se-sticker-image, img.se-sticker-imgae, .se-sticker-image')
            return len(stickers)
        except Exception:
            return 0
    
    def parse_maps(self):
        """지도 정보 수 파싱"""
        try:
            maps = self.driver.find_elements(By.CSS_SELECTOR, 'a.se-map-info, .se-module-map')
            return len(maps)
        except Exception:
            return 0
    
    def parse_all(self):
        """모든 정보 파싱"""
        return {
            'Content': self.parse_content(),
            'PublishDate': self.parse_publish_date(),
            'HashtagCount': self.parse_hashtags()[0],
            'Hashtags': self.parse_hashtags()[1],
            'ImageCount': self.parse_images(),
            'StickerCount': self.parse_stickers(),
            'CommentCount': self.parse_comments(),
            'LikeCount': self.parse_likes(),
            'MapCount': self.parse_maps()
        } 