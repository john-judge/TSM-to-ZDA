

class AcquiData:

    def __init__(self):

        self.location_no = 1
        self.slice_no = 1
        self.record_no = 1

        self.num_trials = 5
        self.int_trials = 10
        self.num_records = 1
        self.int_records = 15  # seconds

        self.num_skip_points = 100  # num points to discard from beginning of each trial
        self.num_flatten_points = 0  # num points on beginning to flatten
        self.init_delay = 0
        self.num_points = 500
        self.num_extra_points = 200

        # specialized recording settings
        # PPR
        self.is_paired_pulse_recording = False
        self.ppr_ipi_interval = [10, 141, 10]

    def get_num_points(self):
        return self.num_points

    def set_num_points(self, value):
        self.num_points = value

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

    def get_init_delay(self):
        return self.init_delay

    def set_init_delay(self, value):
        self.init_delay = value

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

    def set_num_extra_points(self, value):
        self.num_extra_points = value

    def get_num_extra_points(self):
        return self.num_extra_points

    def get_num_skip_points(self):
        return self.num_skip_points

    def set_num_skip_points(self, value):
        self.num_skip_points = value

    def get_num_flatten_points(self):
        return self.num_flatten_points

    def set_num_flatten_points(self, value):
        self.num_flatten_points = value

    def get_ppr_start(self):
        return self.ppr_ipi_interval[0]

    def get_ppr_end(self):
        return self.ppr_ipi_interval[1]

    def set_ppr_start(self, value):
        self.ppr_ipi_interval[0] = value

    def set_ppr_end(self, value):
        self.ppr_ipi_interval[1] = value

    def get_ppr_interval(self):
        return self.ppr_ipi_interval[2]

    def set_ppr_interval(self, value):
        self.ppr_ipi_interval[2] = value

