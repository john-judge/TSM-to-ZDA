class EventMapping:

    def __init__(self, gui):
        self.event_mapping = {
            '-github-': {
                'function': gui.launch_github_page,
                'args': {'kind': "technical"},
            },
            'Help': {
                'function': gui.launch_github_page,
                'args': {'kind': "user"},
            },
            '-psg-': {
                'function': gui.launch_github_page,
                'args': {'kind': "issue"},
            },
            '-timer-': {
                'function': gui.launch_little_dave_calendar,
                'args': {'kind': "issue"},
            },
            "Choose Save Directory": {
                'function': gui.choose_save_dir,
                'args': {},
            },
            'num_trials': {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_num_trials, 'max_val': 20},
            },
            'int_trials': {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_int_trials},
            },
            'num_records': {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_num_records, 'max_val': 20},
            },
            'int_records': {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_int_records},
            },
            "Increment Record": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.acqui_data.increment_record,
                         'call2': gui.update_tracking_num_fields}
            },
            "Decrement Record": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.acqui_data.decrement_record,
                         'call2': gui.update_tracking_num_fields}
            },
            "Increment Location": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.acqui_data.increment_location,
                         'call2': gui.update_tracking_num_fields}
            },
            "Decrement Location": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.acqui_data.decrement_location,
                         'call2': gui.update_tracking_num_fields}
            },
            "Increment Slice": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.acqui_data.increment_slice,
                         'call2': gui.update_tracking_num_fields}
            },
            "Decrement Slice": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.acqui_data.decrement_slice,
                         'call2': gui.update_tracking_num_fields}
            },
            "Increment File": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.acqui_data.increment_file,
                         'call3': gui.sync_gui_fields_from_meta}
            },
            "Decrement File": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.acqui_data.decrement_file,
                         'call3': gui.sync_gui_fields_from_meta}
            },
            "Location Number": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.set_location,
                         'call2': gui.update_tracking_num_fields}
            },
            "Record Number": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.set_record,
                         'call2': gui.update_tracking_num_fields}
            },
            "Slice Number": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.set_slice,
                         'call2': gui.update_tracking_num_fields}
            },
            "Save Preference": {
                'function': gui.save_preference,
                'args': {}
            },
            "Load Preference": {
                'function': gui.load_preference,
                'args': {}
            },
        }

    def get_event_mapping(self):
        return self.event_mapping