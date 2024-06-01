from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import image_process as ip
import file_manage as conv
from tqdm import tqdm


current_timestamp = datetime.now().timestamp()


class Crawler:
    '''
    크롤링을 주된 업무로 갖는 클래스 
    '''
    class __DriverOptionConfig:
        '''
        웹드라이버에 대한 옵션을 설정하는 클래스
        '''

        def __init__(self):
            self.user_agent = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36"
            self.ignito = "--incognito"
            self.head_less = "--headless=new"
            self.profile_dir = "--profile-directory=Default"
            self.no_sandbox = "--no-sandbox"

    class __CustomPathConfig:
        '''
        파일 저장&로드 경로에 대한 옵션을 설정하는 클래스
        '''

        def __init__(self):
            self.session_file_path = "./data/boj_login_cookies.pkl"
            self.tmp_image_forder_path = "./tmp"
            self.solved_ac_json_path = "./data/solved_ac_data.json"
            self.user_data_path = "./data/user_data.pkl"

    # 클래스 내부 변수

    test_start: int
    test_end: int
    custom_path_config = __CustomPathConfig()
    __driver: webdriver.Chrome
    user_id: str
    user_name: str
    # end

    def __init__(self):
        '''크롤러 생성자'''
        pass

    def __save_user_data(self) -> bool:
        """초기에 입력된 사용자의 정보를 저장하는 메소드"""
        user_data = {
            "user_name": self.user_name,
            "user_id": self.user_id,
        }
        return conv.save_data2pickle(user_data, self.custom_path_config.user_data_path)

    def __load_user_data(self) -> bool:
        """사용자의 정보를 불러오는 메소드"""
        data = conv.load_pickle2data(self.custom_path_config.user_data_path)
        if (data != None):
            self.user_id = data["user_id"]
            self.user_name = data["user_name"]
            return True
        else:
            self.user_name = input("사용자의 이름을 알려주세요: ")
            self.user_id = input("사용자의 백준 아이디를 입력해주세요 : ")
            return self.__save_user_data()

    def __reset_driver(self) -> webdriver.Chrome:
        '''웹드라이버를 초기화하는 메소드 '''
        option_config = self.__DriverOptionConfig()
        chrome_options = Options()
        chrome_options.add_argument(option_config.user_agent)
        if conv.isFileAvailable(self.custom_path_config.session_file_path):
            chrome_options.add_argument(option_config.head_less)
        chrome_options.add_argument(option_config.ignito)
        chrome_options.add_argument(option_config.no_sandbox)
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    # 한번 로그인 하면 해당 세션 정보를 저장하여 사용하기
    def __login(self):
        "로그인"
        # 내부에서 사용할 변수들
        login_url = "https://www.acmicpc.net/login"
        home_url = "https://www.acmicpc.net/"
        
        
        with tqdm(desc="백준 로그인 진행", total= 100,leave=False) as pbar:
            if not conv.isFileAvailable(self.custom_path_config. session_file_path):
                # id 박스
                id_box_query = '//input[@name="login_user_id"]'  
                # 자동로그인 체크박스
                auto_check_query = '//input[@name="auto_login" and @type = "checkbox"]'
                # 최대 대기 시간
                wait_seconds = 10

                
                self.__driver.get(url=login_url)
                # 자동 로그인 체크 박스 요소가 등장할 때까지 최대 10초 기다리기
                WebDriverWait(self.__driver, wait_seconds).until(
                    EC.presence_of_element_located((By.XPATH, auto_check_query)))

                self.__driver.find_element(
                    by=By.XPATH, value=auto_check_query).click()  # 로그인 상태 유지
                self.__driver.find_element(
                    by=By.XPATH, value=id_box_query).send_keys(self.user_id)

                pbar.update(30)
                
                while (True):
                    if (self.__driver.current_url == home_url):
                        # 쿠키를 로컬 파일로 저장하기
                        pbar.update(30)
                        if (conv.save_data2pickle(self.__driver.get_cookies(), save_path=self.custom_path_config.session_file_path)):
                            pbar.update(40)
                            break
            else:
                self.__driver.get(home_url)
                pbar.update(30)
                cookies = conv.load_pickle2data(
                    self.custom_path_config.session_file_path)
                for cookie in cookies:
                    self.__driver.add_cookie(cookie)
                pbar.update(30)
                self.__driver.get(home_url)
                time.sleep(1)
                pbar.update(40)
                

    def __get_data_for_result(self) -> dict:
        '''사용자가 진행한 solved ac 클래스 문제 및 업솔빙 정보를 가져오는 메소드'''
        url = "https://www.acmicpc.net/status"

        # 관련된 쿼리들
        find_user_id_query = '//input[@name="user_id"]'
        find_correct_query = '//select[@name="result_id"]/option[text()="맞았습니다!!"]'
        find_submit_btn_query = '//button[@class="btn btn-primary btn-sm margin-left-3 form-control"]'
        find_score_board_query = '//table[@class="table table-striped table-bordered"]/tbody'
        find_user_solved_query = f'{find_score_board_query}/tr[./td[9]/a[number(@data-timestamp)>={self.test_start} and number(@data-timestamp)<={self.test_end}]]'

        # 최대 대기 시간
        wait_seconds = 10

        # 처리된 결과물
        res = dict()

        with tqdm(desc="클래스 및 업솔빙 문제 해결 정보 가져오기", total=100,leave=False) as pbar:
            self.__driver.get(url)
            WebDriverWait(self.__driver, wait_seconds).until(
                EC.presence_of_element_located((By.XPATH, find_user_id_query)))
            self.__driver.find_element(
                by=By.XPATH, value=find_user_id_query).send_keys(self.user_id)  # 사용자 아이디 검색
            self.__driver.find_element(
                by=By.XPATH, value=find_correct_query).click()  # 맞은 값만 찾기
            self.__driver.find_element(
                by=By.XPATH, value=find_submit_btn_query).click()  # 검색하기

            pbar.update(50)

            while True:
                continue_flag = False
                WebDriverWait(self.__driver, wait_seconds).until(
                    EC.presence_of_element_located((By.XPATH, find_score_board_query)))
                results = self.__driver.find_elements(
                    By.XPATH, find_user_solved_query)
                if len(results) == 0:
                    break

                for idx, val in enumerate(results):
                    problem_num = val.find_element(By.XPATH, './td[3]/a').text
                    if problem_num not in res:
                        file_name = f"{problem_num}.png"
                        if conv.element2png(element=val, file_path=self.custom_path_config.tmp_image_forder_path, file_name=f"{problem_num}.png"):
                            res[problem_num] = self.custom_path_config.tmp_image_forder_path + \
                                f"/{file_name}"
                    if idx == len(results)-1:
                        time_stamp = val.find_element(
                            By.XPATH, './td[./a[@data-timestamp]]/a').get_attribute("data-timestamp")
                        if self.test_start <= int(time_stamp) <= self.test_end:
                            continue_flag = True

                if not continue_flag:
                    break

                else:
                    next_button_query = '//div[@class = "text-center"]/a[@id="next_page"]'
                    next_btn = self.__driver.find_element(
                        By.XPATH, next_button_query).get_attribute("href")
                    if next_btn != None:
                        self.__driver.get(next_btn)
                    else:
                        break

            pbar.update(50)
            return res

    def __crawl_solved_ac(self):
        '''solved.ac에서 클래스별 문제 정보를 가져온 후 파일화 하는 메소드'''
        url = "https://solved.ac/class/"
        target = {"update_date": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), "value": {}}
        with tqdm(range(1, 6), desc="solved_ac 클래스 정보 가져오기",leave=False) as pbar:
            for i in pbar:
                self.__driver .get(f'{url}{i}')
                problem_num_xpath = '//a[@class="css-q9j30p"]'
                res = self.__driver .find_elements(
                    by=By.XPATH, value=problem_num_xpath)[::2]
                result = list(map(lambda x: x.text, res))
                target["value"][f"class {i}"] = result
        json_path = self.custom_path_config.solved_ac_json_path.split("/")
        conv.dictToJson(
            dict_data=target, file_name=f"{json_path[2]}", saved_path=f"./{json_path[1]}")

    def __collect_problems(self):
        url = "https://www.acmicpc.net/group/practice/19564"
        wait_seconds = 20

        latest_test_link = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[1]/a' 
        start_test = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[2]/span'
        end_test = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[3]/span'

        # 가장 최근에 종료된 테스트로 이동하기
        with tqdm(desc="최근에 종료된 시험에 대한 정보 가져오기", total=100,leave=False) as pbar:
            self.__driver.get(url)
            WebDriverWait(self.__driver, wait_seconds).until(EC.presence_of_element_located((By.XPATH, latest_test_link)))
            link = self.__driver.find_element(by=By.XPATH, value=latest_test_link).get_property("href")

            # 75분 이후의 기간부터 문제 풀이 값을 검색한다.
            self.test_start = int(self.__driver.find_element(by=By.XPATH, value=start_test).get_attribute("data-timestamp")) + 4501
            self.test_end = int(self.__driver.find_element(
                by=By.XPATH, value=end_test).get_attribute("data-timestamp"))

            pbar.update(30)  # 진행률 30퍼 증가

            # 시험 문제 목록 가져오기
            self.__driver.get(link)
            problem_data_query = '//table[@class="table table-bordered"]/thead/tr/th'
            WebDriverWait(self.__driver, wait_seconds).until(EC.presence_of_element_located((By.XPATH,  problem_data_query))) #해당하는 요소가 등장할 때까지 웹페이지 로딩을 기다림.
            problems = self.__driver.find_elements(by=By.XPATH, value=problem_data_query)[2:-1] #시험 문제의 수가 변경되는 경우를 인식하기 위해 수정. 
            problems = list(map(lambda x: x.find_elements(By.XPATH, "./child::a")[0].get_property("href").split("/")[-1], problems))

            pbar.update(30)  # 진행률 30퍼 증가

            # 시험 중에 풀지 못한 문제 목록으로 필터링하기
            user_name_th_query = f'//table[@class="table table-bordered"]/tbody/tr[./th/a[contains(text(),"{self.user_id}")]]/td'
            user_th = list(map(lambda x: x.text.split(
                "/")[-1].strip(), self.__driver.find_elements(by=By.XPATH, value=user_name_th_query)[:6]))

            pbar.update(30)  # 진행률 30퍼 증가
            # 결과값
            res = []
            for check in zip(problems, user_th):
                if (check[1] == "--"):
                    continue
                elif int(check[1]) > 75:
                    res.append(check[0])
            pbar.update(10)  # 진행률 10퍼 증가 (종료)
            return res

    def __match_image2cat(self, solved_problems: dict, upsolved_data: list):
        solved_ac = conv.jsonToDict(
            self.custom_path_config.solved_ac_json_path)
        res = {"upsolved": [], "solved_ac": {}}
        pbar = tqdm(solved_problems.items(), "결과 이미지로 합성하기",leave=False)
        for k, v in pbar:
            if k in upsolved_data:
                res["upsolved"].append(v)  # 이미지 경로 저장
            else:
                for cls in solved_ac["value"].keys():
                    if k in solved_ac["value"][cls]:
                        if not cls in res["solved_ac"]:
                            res["solved_ac"][cls] = [v]
                        else:
                            res["solved_ac"][cls].append(v)
                        break
        return res

    def __destroy(self):
        '''클래스가 종료될 때, 정리가 필요한 데이터들을 정리하는 메소드'''
        self.__driver.close()
        conv.remove_dir(self.custom_path_config.tmp_image_forder_path)

    # 시작점 -> 이곳에 진행할 메소드를 정리해두면 된다.
    def start_crawl(self):
        pbar = tqdm(desc="전체 진행률", total=100)
        
        if self.__load_user_data():
            self.__driver = self.__reset_driver()
            self.__login()
        else:
            print("사용자 정보 저장에 오류가 발생했습니다. ")
        
        pbar.update(10)  # 진행률 10퍼 증가
        
        if not conv.isFileAvailable(self.custom_path_config.solved_ac_json_path):
            self.__crawl_solved_ac()
        pbar.update(10)  # 진행률 10퍼 증가
        upsolved = self.__collect_problems()
        
        pbar.update(20)  # 진행률 20퍼 증가

        solved_problems = self.__get_data_for_result()
        pbar.update(20)  # 진행률 20퍼 증가

        res = self.__match_image2cat(
            upsolved_data=upsolved,
              solved_problems=solved_problems)  # 분류된 데이터들

        pbar.update(40)  # 진행률 40퍼 증가
        pbar.close()
        file_path = ip.make_collage(date=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), user_name=self.user_name, data=res)

        print(f"이미지 경로 : {file_path}")

        self.__destroy()
