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

    test_start: int
    test_end: int
    custom_path_config = __CustomPathConfig()


    def __init__(self, user_boj_id, user_name):
        '''크롤러 생성자'''
        self.__session_data_path = "./data/boj_login_cookies.pkl"
        self.__base_url = "https://www.acmicpc.net/"  # 기본 시작 url 필요한 경우
        self.__driver = self.__reset_driver()
        self.user_id = user_boj_id
        self.user_name = user_name
        self.__login()


    def __reset_driver(self) -> webdriver.Chrome:
        '''웹드라이버를 초기화하는 메소드 '''
        option_config = self.__DriverOptionConfig()
        chrome_options = Options()
        chrome_options.add_argument(option_config.user_agent)
        if conv.isFileAvailable(self.__session_data_path):
            chrome_options.add_argument(option_config.head_less)
        chrome_options.add_argument(option_config.ignito)
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
                    if (conv.save_data2pickle(self.__driver.get_cookies(), save_path=self.custom_path_config.session_file_path)):
                        break
        else:
            self.__driver.get("https://www.acmicpc.net/")
            cookies = conv.load_pickle2data(self.__session_data_path)
            for cookie in cookies:
                self.__driver.add_cookie(cookie)
            self.__driver.get("https://www.acmicpc.net/")
            time.sleep(1)

    def __get_data_for_result(self) -> dict:
        '''연습문제 중 업솔빙에 대한 데이터를 가져오는 메소드'''
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
        # 주어진 조건에 맞는 데이터만 가져오기
        # 1. 특정 기간 내에 푼 문제인지
        # 2. 업솔빙인지 아니면 클래스 문제를 풀은 것인지
        tr_query = f'//table[@class="table table-striped table-bordered"]/tbody/tr[./td[9]/a[number(@data-timestamp)>={self.test_start} and number(@data-timestamp)<={self.test_end}]]'
        tr_available_check = '//table[@class="table table-striped table-bordered"]/tbody'
        res = dict()

        while True:
            continue_flag = False
            WebDriverWait(self.__driver, 5).until(
                EC.presence_of_element_located((By.XPATH, tr_available_check)))
            results = self.__driver.find_elements(By.XPATH, tr_query)
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

        return res

    def __crawl_solved_ac(self):
        '''solved.ac에서 클래스별 문제 정보를 가져온 후 파일화 하는 메소드'''
        url = "https://solved.ac/class/"
        target = {"update_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"value":{}}

        for i in range(1, 6):
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
        self.__driver.get(url)
        # 가장 최근에 종료된 테스트로 이동하기
        last_test_link = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[1]/a'
        start_test = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[2]/span'
        end_test = '//table[@class = "table table-bordered table-striped"]/tbody/tr[2]/td[3]/span'
        WebDriverWait(self.__driver, 5).until(
            EC.presence_of_element_located((By.XPATH, last_test_link)))
        link = self.__driver.find_element(
            by=By.XPATH, value=last_test_link).get_property("href")

        # 75분 이후의 기간부터 문제 풀이 값을 검색한다.
        self.test_start = int(self.__driver.find_element(
            by=By.XPATH, value=start_test).get_attribute("data-timestamp")) + 4501
        self.test_end = int(self.__driver.find_element(
            by=By.XPATH, value=end_test).get_attribute("data-timestamp"))

        # 시험 문제 목록 가져오기
        self.__driver.get(link)
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
        return res

    def __match_image2cat(self, solved_problems: dict, upsolved_data: list):
        solved_ac = conv.jsonToDict(
            self.custom_path_config.solved_ac_json_path)
        res = {"upsolved": [], "solved_ac": {}}
        for k,v in solved_problems.items():
            if k in upsolved_data:
                res["upsolved"].append(v) #이미지 경로 저장 
            else:
                for cls in solved_ac["value"].keys():
                    if k in  solved_ac["value"][cls]:
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
    
    def __make_result_image(self):
        '''결과 이미지를 출력한 후, 경로를 반환하는 메소드'''
        upsolved =  self.__collect_problems()
        solved_problems = self.__get_data_for_result()
        res = self.__match_image2cat(upsolved_data=upsolved,solved_problems=solved_problems) #분류된 데이터들 
        file_path = ip.make_collage(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user_name=self.user_name,data=res)
        return file_path

    # 시작점 -> 이곳에 진행할 메소드를 정리해두면 된다.
    def start_crawl(self):
        if not conv.isFileAvailable(self.custom_path_config.solved_ac_json_path):
            self.__crawl_solved_ac()
        
        path = self.__make_result_image()
        
        print(path)
        self.__destroy()