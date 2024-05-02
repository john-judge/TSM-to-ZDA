from lib.raspberry_pi.pi_base import RaspberryPi


class Fan(RaspberryPi):

    """ A fan object controlled during experiment
        turns on in between recording """
    
    def __init__(self) -> None:
        super().__init__()
        self.fan_status_on = False

    def turn_on(self, time_ms):
        self.run_command("python fan.py " + str(time_ms))
        self.fan_status_on = False

    def manual_on(self):
        self.run_command("python fan.py 0")
        self.fan_status_on = True

    def manual_off(self):
        self.run_command("python fan.py -1")
        self.fan_status_on = False

    def is_fan_on(self):
        return self.fan_status_on

    def toggle_power(self):
        if self.is_fan_on():
            self.manual_off()
            self.fan_status_on = False
        else:
            self.manual_on()
            self.fan_status_on = True
