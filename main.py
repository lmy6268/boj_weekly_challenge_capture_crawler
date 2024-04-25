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


def crawl():
    today = datetime.now
    baseUrl = "https://www.acmicpc.net/"

    chrome_options = Options()
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36")
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))
    solver = RecaptchaSolver(driver=driver)
    screenTest(driver)


def screenTest(driver: webdriver.WPEWebKit):
    url = "https://www.acmicpc.net/status"
    submit_btn = "btn btn-primary btn-sm margin-left-3 form-control"
    table_name = "table table-striped table-bordered"
    find_keyword = "맞았습니다!!"
    
    driver.get(url)
    driver.find_element(by=By.XPATH,value='//input[@name="user_id"]').send_keys("lmy6268") #사용자 아이디 검색 
    driver.find_element(by=By.XPATH,value=f'//select[@name="result_id"]/option[text()="{find_keyword}"]').click() #맞은 값만 찾기 
    driver.find_element(by=By.XPATH,value=f'//button[@class="{submit_btn}"]').click() #검색하기 
    time.sleep(1)
    
    #필요한 라인만 추출하기 
    with open("./test.png",'wb') as fp:
        res= driver.find_elements(by=By.XPATH, value=f'//tr[//td[3]/a[text()="1463"]]')[1].screenshot_as_png
        fp.write(res)
    
    
    


def login(driver,userName="name",userPw ="password"):
    # 로그인
    id_box = "login_user_id"
    pw_box = "login_password"
    auto_check = "auto_login"
    login_btn = "btn-u pull-right"

    driver.find_element(
        by=By.XPATH, value=f'//input[@name="{id_box}"]').send_keys(userName)
    time.sleep(0.75)
    driver.find_element(
        by=By.XPATH, value=f'//input[@name="{pw_box}"]').send_keys(userPw)
    time.sleep(1)
    driver.find_element(
        by=By.XPATH, value=f'//input[@name="{auto_check}"]').click()  # 로그인 상태 유지
    time.sleep(0.5)
    driver.find_element(
        by=By.XPATH, value=f'//button[@class="{login_btn}"]').click()
    time.sleep(1)


crawl()
