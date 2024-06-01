from crawler import Crawler
from file_manage import remove_dir

pycache = "__pycache__"

if __name__ == "__main__":
    Crawler().start_crawl()
    remove_dir(pycache) #가끔 캐시 파일이 생기는 경우가 있어, 추가

