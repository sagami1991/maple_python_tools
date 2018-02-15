from game_controller import GameController
import time

# 5秒毎にグループ申請監視→グループ申請許可→スキルかける→追放
if __name__ == '__main__':
    while True:
        game = GameController()
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
