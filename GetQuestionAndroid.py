import asyncio
import configparser
import json
import os
import time
from typing import Dict, Optional

from EdgeGPT import Chatbot, ConversationStyle
from PIL import Image

from common import screenshot, ocr

# 读取配置文件
config = configparser.ConfigParser()
config.read('./config/configure.conf', encoding='utf-8')


def load_cookies(cookie_path: str) -> Optional[Dict]:
    """Load cookies from a file.

    This function loads cookies from a given file path, and returns the
    cookies as a dictionary if the file exists.

    Args:
        cookie_path (str): The path to the file containing cookies.

    Returns:
        Optional[Dict]: A dictionary containing cookies if the file exists, otherwise None.
    """
    if cookie_path is None or not os.path.exists(cookie_path):
        print(f"Cookie file {cookie_path} not found. Please check the path and try again.")
        return None

    with open(cookie_path, 'r') as f:
        cookies = json.load(f)
    return cookies


async def main():
    cookie_path = "bing_cookie.json"
    bingai_mode = "balanced"
    valid_modes = ["precise", "balanced", "creative"]
    if bingai_mode not in valid_modes:
        print(bingai_mode + " is not a valid mode. The valid modes are precise, balanced, or creative.")
    cookies = load_cookies(cookie_path)
    # if cookies:
    #     bot = Chatbot(cookie_path=cookie_path)
    # else:
    #     print("Failed to initialize Chatbot. Exiting.")
    # exit()
    proxy = "http://127.0.0.1:18055"
    bot = await Chatbot.create(cookie_path=cookie_path, proxy=proxy)
    while True:
        # 截图
        t = time.perf_counter()
        screenshot.check_screenshot()

        # end_time = time.clock()
        # print(end_time - t)

        img = Image.open("./screenshot.png")

        # 文字识别,可选 Tesseract 和 Baidu ,请在 config/configure.conf 中进行相应配置

        # ocr_img: 需要分别截取题目和选项区域，使用 Tesseract
        # ocr_img_tess： 题目和选项一起截，使用 Tesseract
        # ocr_img_baidu： 题目和选项一起截，使用 baidu ocr，需配置 key

        # question, choices = ocr.ocr_img(img, config)
        # question, choices = ocr.ocr_img_tess(img, config)
        print("请求百度OCR")
        question, choices = ocr.ocr_img_baidu(img, config)

        # question = question.replace("单选题", "")
        # question = question.replace("多选题", "")
        # question = question.replace("判断题", "")

        print(question)
        print(choices)

        print("请求BingAI中")
        ask = question + str(choices) + "请告诉我选哪个选项?"
        return_b = await bot.ask(prompt=ask, conversation_style=ConversationStyle.balanced,
                                 wss_link="wss://sydney.bing.com/sydney/ChatHub", )
        # print(return_b)
        bing_text = return_b.get("item").get('messages')[1]['text']
        print(bing_text)
        # end_time2 = time.perf_counter()
        # print(end_time2 - end_time)

        # 用不同方法输出结果，取消某个方法在前面加上#

        # # 打开浏览器方法搜索问题
        # methods.run_algorithm(0, question, choices)
        # # 将问题与选项一起搜索方法，并获取搜索到的结果数目
        # methods.run_algorithm(1, question, choices)
        # # 用选项在问题页面中计数出现词频方法
        # methods.run_algorithm(2, question, choices)

        # 多线程
        # m1 = Thread(methods.run_algorithm(0, question, choices))
        # m2 = Thread(methods.run_algorithm(1, question, choices))
        # m3 = Thread(methods.run_algorithm(2, question, choices))
        # # m1.start()
        # m2.start()
        # m3.start()

        end_time3 = time.perf_counter()
        print('用时: {0}'.format(end_time3 - t))

        go = input('输入回车继续运行,输入 n 回车结束运行: ')
        if go == 'n':
            break

        print('------------------------')
    await bot.close()


if __name__ == '__main__':
    asyncio.run(main())
