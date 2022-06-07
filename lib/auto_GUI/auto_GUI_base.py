import pyautogui as pa


class AutoGUIBase:

    def __init__(self):
        pass

    @staticmethod
    def click_image(png):
        x, y = pa.center(pa.locateOnScreen(png, confidence=0.9))
        pa.click(x, y)

    @staticmethod
    def pad_zeros(x, n=2):
        x = str(x)
        while len(x) < n:
            x = "0" + x
        return x