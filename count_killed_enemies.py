from game_controller import GameController
import cv2
import numpy as np
import logging
import time

def main():
    logger = get_logger()
    logger.info("取得開始")
    game = GameController()
    old = 0
    # 数字データ
    numbers = get_numbers_ndarray()
    while True:
        screen = game.take_png_screenshot_for_win10(True)
        screen = screen[90:90+40, -190:-1]  # だいたいスキルアイコンの下あたりにある想定でクロップ
        mask_image = cv2.inRange(screen, np.array([255, 34, 34]), np.array([255, 34, 34]))  # 赤色文字のみ抽出
        mask_image, contours, hierarchy = cv2.findContours(mask_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        rects = convert_contours_to_rects(contours)
        rects = remove_same_x_rect(rects)
        text = ""
        for [x, y, w, h] in rects:
            for i, number in enumerate(numbers):
                if np.allclose(mask_image[y:y+9, x:x+2], number):
                    text = text + str(i)
        if text != "":
            num = int(text)
            if old != 0:
                number_per_minute = num - old
                old = num
                logger.info("差分撃破数:{0}".format(number_per_minute))
            else:
                old = num
                logger.info("初回取得完了 数字:{0}".format(num))
        else:
            old = 0
            logger.info("撃破数取得エラー")
        time.sleep(60)


def get_logger():
    logger = logging.getLogger("")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger

# 輪郭抽出したものを座標データに変換する
def convert_contours_to_rects(contours):
    return list(map(lambda cnt:cv2.boundingRect(cnt), contours))

# 同じx座標を削除、高さ9未満のもを削除、x座標でソート
def remove_same_x_rect(rects):
    rects.sort(key=lambda x: x[0])
    new_rects = []
    rect_x = []
    for rect in rects:
        if rect[3] >= 9 and rect[0] not in rect_x:
            new_rects.append(rect)
            rect_x.append(rect[0])
    return new_rects


# 比較用数字画像の取得
def get_numbers_ndarray():
    numbers = np.empty((0, 9, 2), int)
    numbers_image = cv2.imread("./images/0-9.png", cv2.IMREAD_GRAYSCALE)
    numbers_image, contours, hierarchy = cv2.findContours(numbers_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    rects = convert_contours_to_rects(contours)
    rects = remove_same_x_rect(rects)
    for [x, y, w, h] in rects:
        number = numbers_image[y:y+9, x:x+2]
        numbers = np.append(numbers, [number], axis=0)
        # cv2.rectangle(numbers_image, (x, y), (x + w, y + h), (0, 0, 255), 1)
    return numbers


if __name__ == '__main__':
    main()
