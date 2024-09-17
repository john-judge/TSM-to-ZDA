


class Progress:
    """ Reports the status and progress of the current operation. """

    def __init__(self, window):
        """ Initializes the progress dialog. """
        self.window = window
        self.message = "Status: Idle"
        self.current_value = 0  # out of 1000
        self.current_total = 1000

    def get_normalized_current_value(self):
        """ Normalizes the current value. """
        return int(self.current_value * 1000 / self.current_total)

    def increment_progress_value(self, value):
        """ Increments the progress value. """
        self.current_value += value
        self.window['progress_bar'].update(current_count=self.get_normalized_current_value())

    def set_current_total(self, value, unit='s'):
        """ Sets the current total. """
        print("Setting current total to", value)
        self.current_total = value
        self.update_status_message("Remaining: " + str(round(self.current_total - self.current_value, 1)) + " " + unit)

    def update_progress_bar(self, value):
        """ Updates the progress bar. """
        print("Updating progress bar to", value)
        self.current_value = value
        self.window['progress_bar'].update(current_count=self.get_normalized_current_value())

    def update_status_message(self, message):
        """ Updates the progress dialog. """
        self.window['status_text'].update(message)
        self.window.refresh()

    def complete(self):
        """ Completes the progress dialog, resets the progress bar and status message. """
        self.update_progress_bar(0)
        self.update_status_message("Status: Idle")

    