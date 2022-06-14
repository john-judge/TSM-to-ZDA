

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

    def get_num_records(self):
        return self.num_records

    def get_int_trials(self):
        return self.int_trials

    def get_int_records(self):
        return self.int_records