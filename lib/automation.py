import os
import time
import threading


class FileDetector:
    """ Automatically detect and convert files in directory """
    def __init__(self, directory=None, file_type='.tsm'):
        self.directory = directory
        if self.directory is None:
            self.directory = os.getcwd()
        self.file_list = []
        self.file_type = file_type
        self.unprocessed_files = []

        self.stop_flag = False

    def update_file_list(self):
        files = os.listdir(self.directory)
        for f in files:
            if f[-4:] == self.file_type:
                self.file_list.append(f)

    def detect_files_background(self):
        while not self.stop_flag:
            time.sleep(5)
            self.detect_files()

    def detect_files(self):
        old_files = [x for x in self.file_list]
        self.update_file_list()
        for f in self.file_list:
            if f not in old_files:
                self.handle_new_file(f)

    def start_file_detection_loop(self):
        self.stop_flag = False
        self.unprocessed_files = []
        self.file_list = []
        threading.Thread(target=self.detect_files_background,
                         args=(),
                         daemon=True).start()

    def stop_file_detection_loop(self):
        self.stop_flag = True

    def handle_new_file(self, filename):
        self.unprocessed_files.append(filename)

    def get_unprocessed_file_list(self):
        self.unprocessed_files.sort()
        ls = [self.directory + "/" + x for x in self.unprocessed_files]
        self.unprocessed_files = []  # mark files processed
        return ls


class AutoLauncher:
    """ Automatically open relevant programs and folders """
    def __init__(self, desktop='./Shortcuts/',
                 photoZ_shortcut="PhotoZ-TSM-compatible.exe - Shortcut.lnk",
                 turboSM_shortcut='Turbo-SM64-NI.lnk',
                 turboSMDATA='SMDATA - Shortcut.lnk',
                 pulser_shortcut='Prizmatix Pulser.url',
                 recycle_bin='Recycle Bin.lnk',
                 tsm_to_zda_files='TSM-to-ZDA.lnk'):
        # defaults are for new rig
        if desktop[0] == '.':
            desktop = os.getcwd() + desktop[1:]
        self.desktop = desktop
        self.photoZ_shortcut = photoZ_shortcut  
        self.turboSM_shortcut = turboSM_shortcut 
        self.turboSMDATA = turboSMDATA
        self.pulser_shortcut = pulser_shortcut
        self.recycle_bin = recycle_bin
        self.tsm_to_zda_files = tsm_to_zda_files

    def launch_photoZ(self):
        try:
            os.startfile(self.desktop + self.photoZ_shortcut)
        except Exception as e:
            print(e)
            print("Could not start PhotoZ. Continuing under assumption that"
                  " you launched it manually previously.")

    def launch_turboSM(self):
        os.startfile(self.desktop + self.turboSM_shortcut)

    def launch_folder(self, folder):
        try:
            os.startfile(folder)
            return True
        except FileNotFoundError as e:
            print(e)
            return False

    def launch_turboSMDATA(self):
        os.startfile(self.desktop + self.turboSMDATA)
    
    def launch_turboSMDATA(self):
        os.startfile(self.desktop + self.turboSMDATA)
        
    def launch_pulser(self):
        os.startfile(self.desktop + self.pulser_shortcut)
        
    def launch_recycle(self):
        os.startfile(self.desktop + self.recycle_bin)
        
    def launch_tsm_to_zda_files(self):
        os.startfile(self.desktop + self.tsm_to_zda_files)
        
    def launch_pulser(self):
        os.startfile(self.desktop + self.pulser_shortcut)
        
    def launch_all(self):
        self.launch_photoZ()
        self.launch_turboSM()
        self.launch_turboSMDATA()
        self.launch_pulser()
        self.launch_tsm_to_zda_files()
        self.launch_recycle()
        
