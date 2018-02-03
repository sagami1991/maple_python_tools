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
        print(loc)
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
        # Crops the image from the desktop
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
        return cv2.cvtColor(game_img, cv2.COLOR_BGR2GRAY)

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


# if __name__ == '__main__':
#     game = GameController()
#     game.active_game_window()
    # イージーシグナスへ移動
    # img = game.take_png_screenshot()
    # time.sleep(0.1)
    # center_point = game.get_match_point("Screenshot_152.png", img)
    # game.send_click(center_point)
    # time.sleep(0.1)
    # game.send_click(center_point)
    # time.sleep(0.1)
    # game.send_click(center_point)
    # time.sleep(0.1)
    # game.send_click([center_point[0] - 185, center_point[1]])
    # time.sleep(0.1)
    # game.send_click([center_point[0] - 25, center_point[1] + 265])
    # time.sleep(1)

    # グループ申請
    # game.send_key('7')
    # time.sleep(0.1)
    # group_ss = game.take_png_screenshot()
    # find_group_point = game.get_match_point("Screenshot_157.png", group_ss)
    # game.send_click(find_group_point)
    # group_list_ss = game.take_png_screenshot()
    # my_group_point = game.template_match("Screenshot_159.png", group_list_ss)
    # game.send_click([my_group_point[0]+160, my_group_point[1]])
    # time.sleep(0.1)
    # game.send_key(win32con.VK_RETURN)

    # screen = game.take_png_screenshot()
    # my_group_point = game.template_match("Screenshot_160.png", screen)


    # cv2.imshow("a", img)
    # cv2.waitKey()



