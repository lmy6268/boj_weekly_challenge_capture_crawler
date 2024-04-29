from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_recaptcha_solver import RecaptchaSolver
from datetime import datetime
import time

import file_manage as conv


current_timestamp = datetime.now().timestamp()


class Crawler:
    # 크롬 옵션 관련 클래스
    class __DriverOptionConfig:
        def __init__(self):
            self.user_agent = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36"
            self.ignito = "--incognito"
            self.head_less = "--headless=new"
            self.profile_dir = "--profile-directory=Default"
            self.no_sandbox = "--no-sandbox"

    # 크롤러 생성자
    def __init__(self, user_boj_id, user_name):
        self.__session_data_path = "./data/boj_login_cookies.pkl"
        self.__base_url = "https://www.acmicpc.net/"  # 기본 시작 url 필요한 경우
        self.__driver = self.__reset_driver()
        self.user_id = user_boj_id
        self.user_name = user_name
        self.__login()

    def __reset_driver(self):
        option_config = self.__DriverOptionConfig()
        chrome_options = Options()
        chrome_options.add_argument(option_config.user_agent)
        if conv.isFileAvailable(self.__session_data_path):
            chrome_options.add_argument(option_config.head_less)
        # chrome_options.add_argument(option_config.ignito)
        chrome_options.add_argument(option_config.no_sandbox)
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    # 한번 로그인 하면 해당 세션 정보를 저장하여 사용하기
    def __login(self):
        if not conv.isFileAvailable(self.__session_data_path):
            url = "https://www.acmicpc.net/login"
            self.__driver.get(url=url)
            # 로그인
            id_box = "login_user_id"
            auto_check = "auto_login"
            self.__driver.find_element(
                by=By.XPATH, value=f'//input[@name="{auto_check}"]').click()  # 로그인 상태 유지
            self.__driver.find_element(
                by=By.XPATH, value=f'//input[@name="{id_box}"]').send_keys(self.user_id)

            while (True):
                if (self.__driver.current_url == "https://www.acmicpc.net/"):
                    if (conv.save_data2pickle(self.__driver.get_cookies(), save_path=self.__session_data_path)):
                        break
        else:
            self.__driver.get("https://www.acmicpc.net/")
            cookies = conv.load_pickle2data(self.__session_data_path)
            for cookie in cookies:
                self.__driver.add_cookie(cookie)
            self.__driver.get("https://www.acmicpc.net/")
            time.sleep(1)

    # 스크린 캡쳐 테스트
    def __screenTest(self):
        url = "https://www.acmicpc.net/status"
        submit_btn = "btn btn-primary btn-sm margin-left-3 form-control"
        table_name = "table table-striped table-bordered"
        find_keyword = "맞았습니다!!"

        self.__driver.get(url)
        self.__driver.find_element(
            by=By.XPATH, value='//input[@name="user_id"]').send_keys(self.user_id)  # 사용자 아이디 검색
        self.__driver.find_element(
            by=By.XPATH, value=f'//select[@name="result_id"]/option[text()="{find_keyword}"]').click()  # 맞은 값만 찾기
        self.__driver.find_element(
            by=By.XPATH, value=f'//button[@class="{submit_btn}"]').click()  # 검색하기
        time.sleep(1)
        # 주어진 조건에 맞는 데이터만 가져오기
        # 1. 특정 기간 내에 푼 문제인지
        # 2. 업솔빙인지 아니면 클래스 문제를 풀은 것인지

    # solved.ac 클래스 별 문제 정보 얻어오기

    def __crawl_solved_ac(self):
        url = "https://solved.ac/class/"
        target = {"update_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        for i in range(1, 6):
            self.__driver .get(f'{url}{i}')
            problem_num_xpath = '//a[@class="css-q9j30p"]'
            res = self.__driver .find_elements(
                by=By.XPATH, value=problem_num_xpath)[::2]
            result = list(map(lambda x: x.text, res))
            target[f"class {i}"] = result
        conv.dictToJson(dict_data=target,
                        file_name="solved_ac_data", saved_path="./data")

    def __collect_problems(self):
        url = "https://www.acmicpc.net/group/practice/19564"
        self.__driver.get(url)
        # 가장 최근에 종료된 테스트로 이동하기
        last_test_link = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[1]/a'
        start_test = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[2]/span'
        end_test = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[3]/span'
        WebDriverWait(self.__driver, 5).until(
            EC.presence_of_element_located((By.XPATH, last_test_link)))
        link = self.__driver.find_element(by=By.XPATH, value=last_test_link).get_property("href")
        start_stamp = int(self.__driver.find_element(by=By.XPATH,value=start_test).get_attribute("data-timestamp")) + 4501 # 75분 이후의 기간부터 문제 풀이 값을 검색한다. 
        end_stamp = int(self.__driver.find_element(by=By.XPATH,value=end_test).get_attribute("data-timestamp"))
        self.__driver.get(link)

        # 시험 문제 목록 가져오기
        problem_data_query = '//table[@class="table table-bordered"]/thead/tr/th'
        WebDriverWait(self.__driver, 5).until(
            EC.presence_of_element_located((By.XPATH,  problem_data_query)))
        problems = self.__driver.find_elements(
            by=By.XPATH, value=problem_data_query)[2:8]
        problems = list(map(lambda x: x.find_elements(
            By.XPATH, "./child::a")[0].get_property("href").split("/")[-1], problems))

        # 시험 중에 풀지 못한 문제 목록으로 필터링하기
        user_name_th_query = f'//table[@class="table table-bordered"]/tbody/tr[./th/a[contains(text(),"{self.user_id}")]]/td'
        user_th = list(map(lambda x: x.text.split(
            "/")[-1].strip(), self.__driver.find_elements(by=By.XPATH, value=user_name_th_query)[:6]))
        # 결과값
        res = []
        for check in zip(problems, user_th):
            if (check[1] == "--"):
                continue
            elif int(check[1]) > 75:
                res.append(check[0])

        return {"start_time" : start_stamp, "end_time" :end_stamp , "result":res }
    # 시작점 -> 이곳에 진행할 메소드를 정리해두면 된다.

    def start_crawl(self):
        upsolved = self.__collect_problems()
        print(upsolved)
