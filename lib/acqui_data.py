

class AcquiData:

    def __init__(self):

        self.location_no = 1
        self.slice_no = 1
        self.record_no = 1

        self.num_trials = 5
        self.int_trials = 10  # ms
        self.num_records = 1
        self.int_records = 15  # seconds

    def get_slice_no(self):
        return self.slice_no

    def get_location_no(self):
        return self.location_no

    def get_record_no(self):
        return self.record_no

    def get_num_trials(self):
        return self.num_trials

    def set_num_trials(self, value):
        self.num_trials = value

    def get_num_records(self):
        return self.num_records

    def set_num_records(self, value):
        self.num_records = value

    def get_int_trials(self):
        return self.int_trials

    def set_int_trials(self, value):
        self.int_trials = value

    def get_int_records(self):
        return self.int_records

    def set_int_records(self, value):
        self.int_records = value

    def decrement_slice(self):
        self.slice_no -= 1
        # reset location/record numbers
        self.record_no = 1
        self.location_no = 1

    def increment_slice(self):
        self.slice_no += 1
        # reset location/record numbers
        self.record_no = 1
        self.location_no = 1

    def decrement_location(self):
        self.location_no -= 1
        # reset record numbers
        self.record_no = 1

    def increment_location(self):
        self.location_no += 1
        # reset record numbers
        self.record_no = 1

    def decrement_record(self):
        self.record_no -= 1

    def increment_record(self):
        self.record_no += 1

