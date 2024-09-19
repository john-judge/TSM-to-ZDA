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
            'Load Preference': {
                'function': gui.load_preference,
                'args': {}
            },
            'Launch All': {
                'function': gui.controller.start_up,
                'args': {},
                'stoppable': True
            },
            "+ Pulser": {
                'function': gui.controller.set_should_auto_launch_pulser,
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
            'Launch Pulser': {
                'function': gui.controller.start_up_Pulser,
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
                         'call2': gui.update_tracking_num_fields},
                'stoppable': True
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
            "Collect Points": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_num_points},
            },
            "Extra Points": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_num_extra_points},
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
            },
            "PPR Start": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_ppr_start},
            },
            "PPR End": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_ppr_end},
            },
            "PPR Interval": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_ppr_interval},
            },
            'Paired Pulse': {
                'function': gui.controller.set_paired_pulse,
                'args': {}
            },
            "Create Pulser IPI Settings": {
                'function': gui.controller.set_should_create_pulser_settings,
                'args': {}
            },
            "PPR Control": {
                'function': gui.controller.set_ppr_control,
                'args': {}
            },
            "ppr_alignment_settings": {
                'function': gui.controller.set_ppr_alignment_settings,
                'args': {}
            },
            "Fan": {
                'function': gui.controller.toggle_fan,
                'args': {}
            },
            "SS Start": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_steady_state_freq_start},
            },
            "SS End": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_steady_state_freq_end},
            },
            "SS Interval": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_steady_state_freq_interval},
            },
            "Steady State":  {
                'function': gui.controller.deliver_steady_state,
                'args': {}
            },
            "Amplitude Trace Export" : {
                'function': gui.controller.set_export_amplitude_traces,
                'args': {}
            },
            "SNR Trace Export" : {
                'function': gui.controller.set_export_snr_traces,
                'args': {}
            },
            "Latency Trace Export" : {
                'function': gui.controller.set_export_latency_traces,
                'args': {}
            },
            "Halfwidth Trace Export" : {
                'function': gui.controller.set_export_halfwidth_traces,
                'args': {}
            },
            "Trace Export" : {
                'function': gui.controller.set_export_traces,
                'args': {}
            },
            "Export Trace Prefix" : {
                'function': gui.controller.set_trace_export_prefix,
                'args': {}
            },
            'roi_export_options': {
                'function': gui.controller.set_roi_export_options,
                'args': {}
            },
            'electrode_export_options': {
                'function': gui.controller.set_electrode_export_options,
                'args': {}
            },
            "Electrode Export Keyword": {
                'function': gui.controller.set_electrode_export_keyword,
                'args': {}
            },
            'ROIs Export Keyword': {
                'function': gui.controller.set_roi_export_keyword,
                'args': {}
            },
            "SNR Map Export": {
                'function': gui.controller.set_export_snr_maps,
                'args': {}
            },
            "SD Export": {
                'function': gui.controller.set_export_sd_traces,
                'args': {}
            },
            "Microns per Pixel": {
                'function': gui.controller.set_microns_per_pixel,
                'args': {},
            },
            "Max Amp Map Export" : {
                'function': gui.controller.set_export_max_amp_maps,
                'args': {}
            },    
            'Start Export':
            {
                'function': gui.controller.start_export,
                'args': {},
                'stoppable': True
            },
            "IDs Zero-Padded":
            {
                'function': gui.controller.set_zero_pad_ids,
                'args': {}
            },
            "Regenerate Summary": {
                'function': gui.controller.regenerate_summary,
                'args': {},
                'stoppable': True
            },
            "MM Start Pt": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_mm_start_pt},
            },
            "MM End Pt": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_mm_end_pt},
            },
            "MM Frame Interval": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.acqui_data.set_mm_interval},
            },
            "Start Movie Creation": {
                'function': gui.controller.start_movie_creation,
                'args': {},
                'stoppable': True
            },
            "Export by trial": {
                'function': gui.controller.set_export_by_trial,
                'args': {}
            },
            'Num Export Trials': {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.controller.set_num_export_trials},
            },
            'Overwrite Frames': {
                'function': gui.controller.set_mm_overwrite_frames,
                'args': {}
            },
        }

    def get_event_mapping(self):
        return self.event_mapping
