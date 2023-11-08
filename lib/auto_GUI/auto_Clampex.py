import pyautogui as pa
import time
import os
from datetime import date

from lib.auto_GUI.auto_GUI_base import AutoGUIBase


class AutoClampex(AutoGUIBase):

    def __init__(self, data_dir="C:/Turbo-SM/SMDATA/John/",
                 pre_file="tsm50ms.pre",
                 use_today=True):
        self.clampex_trigger = "images/clampex_trigger.png"

        if not data_dir.endswith("/"):
            data_dir = data_dir + "/"

        self.data_dir = data_dir
        self.use_today = use_today

    def trigger(self):
        self.click_image(self.clampex_trigger)

    def trigger_periodically(self, n_triggers=10, sleep=5):
        for _ in range(n_triggers):
            self.click_clampex_image(self.clampex_trigger)
            time.sleep(sleep / 2)
            self.move_cursor_off()
            time.sleep(sleep / 2)

    def click_clampex_image(self, im):
        res = pa.locateOnScreen(im, confidence=0.9)
        if res is None:
            return False
        x, y = pa.center(res)

        pa.moveTo(x, y)
        pa.drag(1, 0, 0.5, button='left')


