#!/usr/bin/python
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import time
import game_controller
import cv2
import win32con
import os
import numpy as np

class MainWindow(QFrame):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setFixedSize(200, 50)
        self.setWindowTitle("Maple auto HS 2pc")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        button = QPushButton("シグナスへ行く", self)
        button.clicked.connect(MainWindow.go_to_cygnus)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(button)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)

    @staticmethod
    def go_to_cygnus():
        game = game_controller.GameController()
        # イージーシグナスへ移動
        game.active_game_window()
        time.sleep(0.1)
        game.send_key('T')
        time.sleep(0.3)
        img = game.take_png_screenshot()
        center_point = game.template_match("Screenshot_152.png", img)
        if center_point is None:
            return
        game.send_click(center_point)
        time.sleep(0.1)
        game.send_click(center_point)
        time.sleep(0.1)
        game.send_click(center_point)
        time.sleep(0.1)
        game.send_click([center_point[0] - 185, center_point[1]])
        time.sleep(0.1)
        game.send_click([center_point[0] - 25, center_point[1] + 265])
        time.sleep(3)

        # グループ申請
        game.send_key('7')
        time.sleep(0.1)
        group_ss = game.take_png_screenshot()
        find_group_point = game.template_match("Screenshot_157.png", group_ss)
        if find_group_point is None:
            return
        game.send_click(find_group_point)
        time.sleep(0.2)
        group_list_ss = game.take_png_screenshot()
        my_group_point = game.template_match("Screenshot_159.png", group_list_ss)
        if my_group_point is None:
            return
        game.send_click([my_group_point[0]+160, my_group_point[1]])
        time.sleep(0.3)
        game.send_key(win32con.VK_RETURN)

    @staticmethod
    def start_watch_for_virtual():
        while True:
            game = game_controller.GameController()
            screen = game.take_png_screenshot()
            point = game.template_match("group_invite.png", screen)
            if point is None:
                time.sleep(3)
                continue
            game.send_click(point)
            time.sleep(0.3)
            game.send_key('U')
            time.sleep(2)
            game.send_key('7')
            time.sleep(1)

            screen = game.take_png_screenshot()
            point = game.template_match("group_list_main_character_name.png", screen)
            if point is None:
                continue
            game.send_click(point, True)
            time.sleep(0.3)

            screen = game.take_png_screenshot()
            point = game.template_match("group_expulsion.png", screen)
            if point is None:
                continue
            game.send_click(point)
            time.sleep(0.3)
            game.send_key('7')
            time.sleep(5)


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'main':
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    # elif len(sys.argv) >= 2 and sys.argv[1] == 'test':
        # img = cv2.imread(os.path.join("tmp", "Screenshot_165.png") ,cv2.IMREAD_COLOR)
        # lower_green = np.array([0, 255, 0])
        # upper_green = np.array([0, 255, 0])
        #
        # # 指定した色に基づいたマスク画像の生成
        # img_mask = cv2.inRange(img, lower_green, upper_green)
        # img_mask = cv2.resize(img_mask, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        # cv2.imshow("",img_mask)
        # cv2.waitKey()
        # str = game_controller.GameController.img_to_string(img_mask, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzゆかり[]>-")
        # print(str)
    else:
        MainWindow.start_watch_for_virtual()

