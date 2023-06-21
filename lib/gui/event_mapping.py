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
            "Choose Data Directory": {
                'function': gui.choose_data_dir,
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
            'Launch All': {
                'function': gui.controller.start_up,
                'args': {}
            },
            "Launch PhotoZ": {
                'function': gui.controller.start_up_PhotoZ,
                'args': {}
            },
            "Launch TurboSM": {
                'function': gui.controller.start_up_TurboSM,
                'args': {}
            },
            "Empty Recycle Bin": {
                'function': gui.controller.empty_recycle_bin,
                'args': {}
            },
            "View Data Folder": {
                'function': gui.controller.open_data_folder,
                'args': {}
            },
            'Convert Files Switch': {
                'function': gui.controller.set_convert_files_switch,
                'args': {}
            },
            'Record': {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.controller.record,
                         'call2': gui.update_tracking_num_fields}
            },
            'Detect and Convert': {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.controller.detect_and_convert,
                         'call2': gui.update_tracking_num_fields}
            },
            'Theta Burst Stim': {
                'function': gui.controller.deliver_tbs,
                'args': {}
            },
            "Today subdir": {
                'function': gui.controller.set_use_today_subdir,
                'args': {}
            },
            "New rig settings": {
                'function': gui.controller.set_new_rig_settings,
                'args': {}
            },
            'Auto Export Maps': {
                'function': gui.controller.auto_export_maps,
                'args': {}
            },
            'SNR map only': {
                'function': gui.controller.set_export_snr_only,
                'args': {}
            },
            "Second pulse only": {
                'function': gui.controller.set_export_second_pulse_snr_only,
                'args': {}
            },
            'Paired Pulse Export': {
                'function': gui.export_paired_pulse,
                'args': {}
            },
            "Export Map Prefix" : {
                'function': gui.controller.set_auto_export_maps_prefix,
                'args': {}
            },
            'Auto Trace Export': {
                'function': gui.controller.export_roi_traces,
                'args': {}
            },
            'Persistent ROIs' : {
                'function': gui.controller.set_export_persistent_roi_traces,
                'args': {}
            },
            'camera settings': {
                'function': gui.controller.set_camera_program,
                'args': {}
            },
            "Skip Points": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_num_skip_points},
            },
            "Shorten recording": {
                'function': gui.controller.set_shorten_recording,
                'args': {}
            },
            "Flatten Points": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_num_flatten_points},
            },
            "Initial Delay": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_init_delay},
            }
        }

    def get_event_mapping(self):
        return self.event_mapping
