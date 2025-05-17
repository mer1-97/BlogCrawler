import pandas as pd
from datetime import datetime

def export_to_csv(results):
    """결과를 CSV 파일로 저장"""
    if not results:
        return None
        
    # 현재 시간을 파일명에 포함
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'blog_content_{timestamp}.csv'
    
    # DataFrame 생성
    df = pd.DataFrame(results)
    
    # 컬럼 순서 지정
    columns = ['URL', 'Content', 'PublishDate', 'HashtagCount',
              'ImageCount', 'StickerCount', 'CommentCount', 'LikeCount',
              'MapCount']
    
    # 크롤링 시간 추가
    df['Crawling_Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # CSV 파일로 저장
    df[columns + ['Crawling_Time']].to_csv(filename, index=False, encoding='utf-8-sig')
    return filename

def print_result(result):
    """결과 출력"""
    print("\n=== 분석 결과 ===")
    print(f"URL: {result['URL']}")
    print(f"작성일: {result['PublishDate']}")
    print(f"해시태그 수: {result['HashtagCount']}")
    print(f"이미지 수: {result['ImageCount']}")
    print(f"스티커 수: {result['StickerCount']}")
    print(f"댓글 수: {result['CommentCount']}")
    print(f"공감 수: {result['LikeCount']}")
    print(f"지도 정보 수: {result['MapCount']}")
    print(f"본문 길이: {len(result['Content'])} 글자")
    print("\n본문 미리보기:")
    print(result['Content'][:200] + "..." if len(result['Content']) > 200 else result['Content'])
    print("="*50) 