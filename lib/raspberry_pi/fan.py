from lib.raspberry_pi.pi_base import RaspberryPi


class Fan(RaspberryPi):

    """ A fan object controlled during experiment
        turns on in between recording """
    
    def __init__(self) -> None:
        super().__init__()

    def turn_on(self, time_ms):
        self.run_command("python fan.py " + str(time_ms))