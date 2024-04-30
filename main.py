from crawler import Crawler

if __name__ == "__main__":
    user_name = input("사용자의 이름을 알려주세요: ")
    boj_id = input("사용자의 백준 아이디를 입력해주세요 : ")
    crawler = Crawler(user_boj_id=boj_id, user_name=user_name)  # 아이디와 비밀번호
    crawler.start_crawl()
