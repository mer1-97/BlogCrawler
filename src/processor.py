import pandas as pd
import multiprocessing
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm
from src.logger import program_logger

class BlogProcessor:
    def __init__(self, crawler):
        self.crawler = crawler

    def process_blog_item(self, item):
        """멀티프로세싱을 위한 블로그 아이템 처리 함수"""
        blog_url = item['link']
        result = self.crawler.get_blog_info(blog_url)
        
        if result:
            result['Title'] = item['title'].replace('<b>', '').replace('</b>', '')
            result['APIPostDate'] = item['postdate']
            return result
        return None

    def process_items(self, blog_items):
        """블로그 아이템들을 병렬로 처리"""
        total_items = len(blog_items)
        program_logger.info(f"총 {total_items}개의 블로그 게시글을 찾았습니다.")
        
        # CPU 코어 수에 따라 프로세스 수 결정 (최대 4개)
        num_processes = min(4, multiprocessing.cpu_count())
        program_logger.info(f"{num_processes}개의 프로세스로 크롤링을 시작합니다...")
        
        # 멀티프로세싱으로 크롤링 실행
        results = []
        with Pool(num_processes) as pool:
            process_func = partial(self.process_blog_item)
            for result in tqdm(
                pool.imap_unordered(process_func, blog_items),
                total=total_items,
                desc="크롤링 진행률",
                unit="건"
            ):
                if result:
                    results.append(result)
        
        return results

    def save_results(self, results):
        """결과를 CSV 파일로 저장"""
        if results:
            df = pd.DataFrame(results)
            filename = "results.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            program_logger.info(f"최종 결과가 저장되었습니다: {filename} (총 {len(results)}개)")
            return filename
        else:
            program_logger.warning("저장할 결과가 없습니다.")
            return None 