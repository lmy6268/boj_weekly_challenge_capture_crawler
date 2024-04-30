import numpy as np
import cv2 as cv
from PIL import ImageFont, ImageDraw, Image 
from file_manage import make_dir
from os.path import dirname

def make_collage(date:str, user_name:str, data: dict):
    """ 결과 이미지를 합성하고, 출력된 이미지의 경로를 반환하는 메소드"""
    upsolved = data["upsolved"]
    class_solved = data["solved_ac"]
    res = []
    for i in upsolved:
        data = cv.imread(i)
        res.append(data)
    
    for i,v in enumerate([draw_text(f"캡쳐 일자 : {date}", res[0].shape),draw_text(f"이름 : {user_name}", res[0].shape),space(res[0].shape),draw_text("업솔빙", res[0].shape,type="bold")]):
        res.insert(i,v)
    for k in class_solved.keys():
        res.append(space(res[0].shape))
        res.append(draw_text(k, res[0].shape,type="bold"))
        for data in class_solved[k]:
            image = cv.imread(data)
            res.append(image)
    image_result = np.vstack(res)
    return make_image_file(date=date,image=image_result)


def draw_text(text: str, shape,font_size:int = 20,type:str = "light"):
    based_image = np.full(shape, 255, dtype=np.uint8)   
    text_pos = (10,0)
    font_color = (0,0,0)
    font_style = './font/MaruBuri-Light.ttf' if(type == "light") else './font/MaruBuri-Bold.ttf'
    font = ImageFont.truetype(font_style, font_size)
    based_image_pil = Image.fromarray(based_image)
    draw = ImageDraw.Draw(based_image_pil)
    draw.text(text_pos,text,font_color,font=font)
    return np.array(based_image_pil)

def space(shape):
    """빈공간을 만드는 메소드"""
    return np.full(shape,255,dtype=np.uint8)

def make_image_file(date:str,image:np.ndarray):
    """결과 이미지를 출력하고 경로를 반환하는 메소드 """
    path = f'./result/{date}.png'
    if(make_dir(dirname(path))):
        cv.imwrite(path,image)
        with open(path,'rb') as fp:
            Image.open(fp).show()
        return path 

    else:
        return None