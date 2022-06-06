import os


class Automation:

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
        
