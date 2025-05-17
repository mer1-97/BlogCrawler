# Naver Blog Crawler

네이버 블로그 포스트 정보를 수집하는 크롤러입니다.

## 기능

- 블로그 포스트 본문 추출
- 해시태그 수 계산
- 이미지 수 계산
- 댓글 수 추출
- 공감 수 추출
- 스티커 수 계산
- 지도 정보 수 계산
- 결과를 CSV 파일로 저장

## 요구사항

- Python 3.x
- Chrome 브라우저
- 필요한 Python 패키지:
  - selenium
  - beautifulsoup4
  - pandas
  - webdriver_manager

## 설치 방법

1. 저장소 클론
```bash
git clone [your-repository-url]
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 사용 방법

1. `main.py` 파일의 `urls` 리스트에 분석하고 싶은 네이버 블로그 포스트 URL을 추가합니다.
2. 스크립트 실행:
```bash
python main.py
```

## 출력 결과

- 콘솔에 분석 결과가 출력됩니다.
- 결과는 `blog_content_YYYYMMDD_HHMMSS.csv` 형식의 CSV 파일로 저장됩니다. 