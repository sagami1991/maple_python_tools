import win32api
import win32gui
import win32con
import win32api
import win32ui
from ctypes import windll
import time
import numpy as np
import cv2
from sklearn.cluster import KMeans
import os
from matplotlib import pyplot
from PIL import ImageGrab
import subprocess

class GameController:
    _window_handle = 0
    _debug = False

    def __init__(self, debug=False):
        self._debug = debug
        self._window_handle = win32gui.FindWindow("MapleStoryClass", "MapleStory")

    def active_game_window(self):
        win32gui.SetForegroundWindow(self._window_handle)

    def get_match_point(self, image_name, screen_shot) -> [int, int]:
        train_img = cv2.imread(os.path.join("images", image_name), 0)
        query_img = screen_shot
        sift = cv2.xfeatures2d.SIFT_create()
        key_point1, descriptors1 = sift.detectAndCompute(train_img, None)
        key_point2, descriptors2 = sift.detectAndCompute(query_img, None)
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors1, descriptors2, k=2)
        good_matches = []
        cluster = []
        for m, n in matches:
            (x, y) = key_point2[m.trainIdx].pt
            if m.distance < 0.75 * n.distance:
                good_matches.append([m])
                cluster.append([int(x), int(y)])
        # 特徴点が少ない場合は失敗
        if len(cluster) <= 3:
            print("特徴点が少なすぎる")
            img3 = cv2.drawMatchesKnn(train_img, key_point1, query_img, key_point2, good_matches, None, flags=2)
            pyplot.imshow(img3)
            pyplot.show()
            return None
        k_means = KMeans(n_clusters=1, random_state=0).fit(cluster)
        center_point = k_means.cluster_centers_[0]
        return [int(center_point[0]), int(center_point[1])]

    def template_match(self, image_name, screen_shot) -> [int, int]:
        train_img = cv2.imread(os.path.join("images", image_name), 0)
        w, h = train_img.shape[::-1]
        result = cv2.matchTemplate(screen_shot, train_img, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= 0.8)
        if len(loc[0]) is 0:
            print("マッチしませんでした。" + image_name)
            return None
        x = loc[1][0]
        y = loc[0][0]
        # cv2.rectangle(screen_shot, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # cv2.imshow("result.png", screen_shot)
        # cv2.waitKey()
        return [int(x + 1 / 2 * w), int(y + 1 / 2 * h)]

    def take_png_screenshot(self):
        if not self._window_handle:
            raise Exception("ウインドウが存在しない")
        self.active_game_window()
        # Crops the image from the desktop
        w, h = win32gui.GetClientRect(self._window_handle)[2:]
        x, y = win32gui.ClientToScreen(self._window_handle, (0, 0))

        img = ImageGrab.grab((x, y, x + w, y + h))
        img = cv2.cvtColor(np.asarray(img), cv2.COLOR_BGR2GRAY)
        return img

    # ウインドウを最前面にしなくてもスクショがとれるが、環境によりできない場合もある
    def take_png_screenshot_for_win10(self, isColor=False):
        if not self._window_handle:
            raise Exception("ウインドウが存在しない")
        left, top, right, bottom = win32gui.GetWindowRect(self._window_handle)
        width = right - left
        height = bottom - top
        hwnd_dc = win32gui.GetWindowDC(self._window_handle)
        # Get a bitmap
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bit_map = win32ui.CreateBitmap()
        save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bit_map)
        result = windll.user32.PrintWindow(self._window_handle, save_dc.GetSafeHdc(), 1)
        if result != 1:
            raise Exception("スクショに失敗")
        bmp_info = save_bit_map.GetInfo()
        bmp_raw = save_bit_map.GetBitmapBits(False)
        game_img = np.array(bmp_raw, np.uint8).reshape(bmp_info['bmHeight'], bmp_info['bmWidth'], 4)
        # Clean Up
        win32gui.DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self._window_handle, hwnd_dc)
        if isColor:
            return cv2.cvtColor(game_img, cv2.COLOR_BGR2RGB)
        else:
            gray_scale_img = cv2.cvtColor(game_img, cv2.COLOR_BGR2GRAY)
            return gray_scale_img

    def send_key(self, key):
        if type(key) is str:
            key = ord(key)
        win32api.PostMessage(self._window_handle, 0x0100, key, win32api.MapVirtualKey(key, 0) << 16)

    def send_click(self, point, is_right_click=False):
        x, y = win32gui.ClientToScreen(self._window_handle, (point[0], point[1]))
        win32api.SetCursorPos([x, y])
        if is_right_click:
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    @staticmethod
    def img_to_string(img, char_set=None):
        cv2.imwrite("tmp\\ocr.png", img)
        command = "bin\\tess\\tesseract.exe --tessdata-dir bin\\tess\\tessdata tmp\\ocr.png tmp\\ocr "
        if char_set is not None:
            command += "-c tessedit_char_whitelist=" + char_set + " "
        command += "-psm 7 "
        command += "> nul 2>&1"
        CREATE_NO_WINDOW = 0x08000000
        subprocess.call(command, shell=True, creationflags=CREATE_NO_WINDOW)
        # Get the largest line in txt
        with open("tmp\\ocr.txt") as f:
            content = f.read().splitlines()
        output_line = ""
        for line in content:
            line = line.strip()
            if len(line) > len(output_line):
                output_line = line
        return output_line

