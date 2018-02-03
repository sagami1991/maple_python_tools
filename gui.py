#!/usr/bin/python
import sys
from PyQt5.QtWidgets import *
import time
import game_controller

class MainWindow(QFrame):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setFixedSize(300, 200)
        self.setWindowTitle("Maple auto HS 2pc")
        button = QPushButton("仮想PC向け - 開始", self)
        button.clicked.connect(self.start_watch_for_virtual)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(button)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)

    def start_watch_for_virtual(self):
        while True:
            game = game_controller.GameController()
            screen = game.take_png_screenshot()
            point = game.template_match("group_invite.png", screen)
            if point is None:
                time.sleep(5)
                continue
            game.send_click(point)
            time.sleep(0.1)
            game.send_key('U')
            time.sleep(2)
            game.send_key('7')
            time.sleep(0.1)

            screen = game.take_png_screenshot()
            point = game.template_match("group_list_main_character_name.png", screen)
            game.send_click(point, True)
            time.sleep(0.1)

            screen = game.take_png_screenshot()
            point = game.template_match("group_expulsion.png", screen)
            game.send_click(point)
            time.sleep(5)






if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
