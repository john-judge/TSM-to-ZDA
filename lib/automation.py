import os


class Automation:

    def __init__(self, photoZ_shortcut='C:/Users/jjudge3/Desktop/ImageJ - Shortcut.lnk',
                 turboSM_shortcut=''):
        self.photoZ_shortcut = photoZ_shortcut  # default is for new rig
        self.turboSM_shortcut = turboSM_shortcut  # default is for new rig

    def launch_photoZ(self):
        os.startfile(self.photoZ_shortcut)

    def launch_turboSM(self):
        os.startfile(self.turboSM_shortcut)
