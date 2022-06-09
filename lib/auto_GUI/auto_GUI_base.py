import pyautogui as pa
import time


class AutoGUIBase:

    def __init__(self):
        pass

    @staticmethod
    def click_image(png, retry_attempts=10):
        res = None
        while res is None and retry_attempts > 0:
            res = pa.locateOnScreen(png, confidence=0.9)
            if res is None:
                print("target image not found, trying again", retry_attempts, "more times...")
                retry_attempts -= 1
            time.sleep(2)
        if retry_attempts < 1:
            return False
        x, y = pa.center(res)
        pa.click(x, y)
        return True

    def click_until_gone(self, png, retry_attempts=2):
        """ Keep clicking occurrences of the image until it is gone """
        while self.click_image(png, retry_attempts=retry_attempts):
            time.sleep(1)

    @staticmethod
    def pad_zeros(x, n=2):
        x = str(x)
        while len(x) < n:
            x = "0" + x
        return x