import pickle
import json
import os
import shutil
from selenium.webdriver.remote.webelement import WebElement


def save_data2pickle(data, save_path: str):
     # 해당 경로에 폴더가 없는 경우 폴더 생성
    if make_dir(os.path.dirname(save_path)):    
        with open(save_path, 'wb') as fp:
            pickle.dump(data, fp)
            return True
    else:
        return False


def load_pickle2data(path: str):
    with open(path, "rb") as fp:
        res = pickle.load(fp)
        return res


def jsonToDict(file_path: str):
    with open(file_path,"r") as fp:
        jsonfile = json.load(fp)
        return jsonfile


def dictToJson(dict_data: dict, file_name: str, saved_path: str = "./"):
    # 해당 경로에 폴더가 없는 경우 폴더 생성
    if make_dir(saved_path):
        # 파일 저장
        with open(f"{saved_path}/{file_name}", 'w') as f:
            json.dump(dict_data, f)
        return True
    else:
        return False


def isFileAvailable(file_path: str):
    return os.path.isfile(file_path)


def element2png(element: WebElement, file_path: str, file_name: str):
    if make_dir(file_path):
        # 필요한 라인만 추출하기
        with open(f'{file_path}/{file_name}', 'wb') as fp:
            res = element.screenshot_as_png
            fp.write(res)
            return True
    else:
        return False


def make_dir(path: str):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except OSError:
        return False


def remove_dir(path: str):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        return True
    except OSError:
        return False
