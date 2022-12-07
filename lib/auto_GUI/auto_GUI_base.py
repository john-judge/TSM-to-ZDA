import pyautogui as pa
import time
import os
from datetime import date


class AutoGUIBase:

    def __init__(self):
        pass

    @staticmethod
    def click_image(png, retry_attempts=10, sleep=2, clicks=1):
        res = None
        while res is None and retry_attempts > 0:
            res = pa.locateOnScreen(png, confidence=0.9)
            if res is None:
                retry_attempts -= 1
            time.sleep(sleep)
        if retry_attempts < 1:
            return False
        x, y = pa.center(res)
        pa.click(x, y, clicks=clicks)
        return True

    def click_nth_image(self, png, n, retry_attempts=10, sleep=2, clicks=1):
        if n is None:
            return True
        locations = None
        while locations is None and retry_attempts > 0:
            locations = self.get_image_locations(png)
            retry_attempts -= 1
        i = 0
        for loc in locations:
            if i == n:
                x, y = pa.center(loc)
                pa.click(x, y, clicks=clicks)
                break
            i += 1
        if i < n:
            return False
        time.sleep(sleep)
        return True

    @staticmethod
    def get_image_locations(png):
        return pa.locateAllOnScreen(png,
                                    confidence=0.9,
                                    grayscale=False)

    def click_until_gone(self, png, retry_attempts=2):
        """ Keep clicking occurrences of the image until it is gone """
        while self.click_image(png, retry_attempts=retry_attempts):
            time.sleep(1)

    def make_new_folder_today(self):
        """ With a file explorer open, create new file and name it MM-DD-YY"""
        # pa.hotkey('ctrl', 'shift', 'n')  # make new folder
        # time.sleep(0.5)
        today = date.today().strftime("%m-%d-%y")
        self.type_string(today)
        time.sleep(0.5)
        pa.press(['enter', 'enter'])

    def os_make_new_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    @staticmethod
    def type_string(s):
        pa.press([c for c in s])

    @staticmethod
    def pad_zeros(x, n=2):
        x = str(x)
        while len(x) < n:
            x = "0" + x
        return x

    @staticmethod
    def key_delete_all():
        pa.hotkey('ctrl', 'a')
        time.sleep(1)
        pa.press(['backspace'])

    @staticmethod
    def move_cursor_off():
        pa.moveTo(50, 50)
