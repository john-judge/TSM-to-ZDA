import os
import time
import threading


class AutoFileConverter:
    """ Automatically detect and convert files in directory """
    def __init__(self, directory=None, file_types=('.tsm')):
        self.directory = directory
        if self.directory is None:
            self.directory = os.getcwd()
        self.file_list = []
        self.file_types = file_types
        self.update_file_list()
        self.unprocessed_files = []

        self.stop_flag = False

    def update_file_list(self):
        files = os.listdir(self.directory)
        for f in files:
            if any([f.endswith(x) for x in self.file_types]):
                self.file_list.append(f)

    def detect_files_background(self):
        while not self.stop_flag:
            time.sleep(5)
            old_files = self.file_list
            self.update_file_list()
            for f in self.file_list:
                if f not in old_files:
                    self.handle_new_file(f)
            self.process_files()

    def start_file_detection_loop(self):
        self.stop_flag = False
        threading.Thread(target=self.detect_files_background,
                         args=(),
                         daemon=True).start()

    def stop_file_detection_loop(self):
        self.stop_flag = True

    def handle_new_file(self, filename):
        print("New file detected:", filename)
        self.unprocessed_files.append(filename)

    def get_unprocessed_file_list(self):
        self.unprocessed_files.sort()
        return [self.directory + x for x in self.unprocessed_files]


class AutoLauncher:
    """ Automatically open relevant programs and folders """
    def __init__(self, desktop='C:/Users/RedShirtImaging/Desktop/Shortcuts/',
                 photoZ_shortcut="PhotoZ-TSM-compatible.exe - Shortcut.lnk",
                 turboSM_shortcut='Turbo-SM64-NI.lnk',
                 turboSMDATA='SMDATA - Shortcut.lnk',
                 pulser_shortcut='Prizmatix-Pulser Plus.lnk',
                 recycle_bin='Recycle Bin.lnk',
                 tsm_to_zda_files='TSM-to-ZDA.lnk'):
        # defaults are for new rig
        self.desktop = desktop
        self.photoZ_shortcut = photoZ_shortcut  
        self.turboSM_shortcut = turboSM_shortcut 
        self.turboSMDATA = turboSMDATA
        self.pulser_shortcut = pulser_shortcut
        self.recycle_bin = recycle_bin
        self.tsm_to_zda_files = tsm_to_zda_files

    def launch_photoZ(self):
        os.startfile(self.desktop + self.photoZ_shortcut)

    def launch_turboSM(self):
        os.startfile(self.desktop + self.turboSM_shortcut)
        
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
        
