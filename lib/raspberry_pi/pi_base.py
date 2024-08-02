#import spur
#from lib.raspberry_pi.ssh_password import *

class RaspberryPi:
    """ Base class supporting Raspberry Pi devices """

    def __init__(self) -> None:
        self.shell = self.connect_pi()

    def connect_pi(self):
        shell = None 
        '''spur.SshShell(hostname="raspberrypi", 
                              username=RASPBERRY_PI_SSH_USERNAME, 
                              password=RASPBERRY_PI_SSH_PASSWORD)'''
        return shell
    
    def run_command(self, command):
        command = command.split(" ")
        result = self.shell.run(command)
        return result.output 
