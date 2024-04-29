import pickle
import json
import os
from selenium.webdriver.remote.webelement import WebElement


def save_data2pickle(data, save_path: str):
    with open(save_path, 'wb') as fp:
        pickle.dump(data, fp)
        return True


def load_pickle2data(path: str):
    with open(path, "rb") as fp:
        res = pickle.load(fp)
        return res


def jsonToDict(file_name: str):
    jsonfile = json.loads(file_name)
    return jsonfile


def dictToJson(dict_data: dict, file_name: str, saved_path: str = "./"):
    # 해당 경로에 폴더가 없는 경우 폴더 생성
    try:
        if not os.path.exists(saved_path):
            os.makedirs(saved_path)
    except OSError:
        return False
    # 파일 저장
    with open(f"{saved_path}/{file_name}", 'w') as f:
        json.dump(dict_data, f)
    return True


def isFileAvailable(file_path: str):
    return os.path.isfile(file_path)


def element2png(element: WebElement):
    # 필요한 라인만 추출하기
    with open("./test.png", 'wb') as fp:
        res = element.screenshot_as_png
        fp.write(res)
