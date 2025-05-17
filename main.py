import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

def get_blog_content(blog_url):
    # 모바일 버전 URL로 변환 (더 간단한 HTML 구조)
    mobile_url = blog_url.replace('blog.naver.com', 'm.blog.naver.com')
    
    # User-Agent 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 페이지 요청
        response = requests.get(mobile_url, headers=headers)
        response.raise_for_status()
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 블로그 본문 찾기 (모바일 버전의 컨텐츠 영역)
        content = soup.select_one('div.se-main-container')
        
        if content:
            # 텍스트 추출 및 정리
            text_content = content.get_text('\n', strip=True)
            return text_content
        else:
            # 옛날 버전 블로그 형식 시도
            content = soup.select_one('#viewTypeSelector, .post-view')
            if content:
                text_content = content.get_text('\n', strip=True)
                return text_content
            return "블로그 본문을 찾을 수 없습니다."
            
    except Exception as e:
        return f"오류 발생: {str(e)}"

def save_to_csv(url, content, filename=None):
    # 현재 시간을 파일명에 포함
    if filename is None:
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blog_content_{current_time}.csv"
    
    # DataFrame 생성
    df = pd.DataFrame({
        'URL': [url],
        'Content': [content],
        'Crawling_Time': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    
    # CSV 파일로 저장
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    return filename

def main():
    blog_url = "https://blog.naver.com/khing311/223775190985"
    print("블로그 내용을 가져오는 중...")
    content = get_blog_content(blog_url)
    
    # CSV 파일로 저장
    filename = save_to_csv(blog_url, content)
    print(f"\n블로그 내용이 '{filename}' 파일로 저장되었습니다.")
    
    # 콘솔에도 내용 출력
    print("\n=== 블로그 내용 ===\n")
    print(content)

if __name__ == "__main__":
    main() 