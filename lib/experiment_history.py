


class ExperimentHistory:

    def __init__(self):
        pass

    def load(self, date):

        slice_target = [1,2]
        rec_target = [i for i in range(0,13)]
        tbs_recording_no = 5
        if date == '07-15-22':
            rec_target = [i for i in range(0,17)]  # 7/15
            tbs_recording_no = 5
        if date == '07-22-22' and slice_target == 1:
            rec_target = [i for i in range(0,18)]  # 7/19
            tbs_recording_no = 4
        if date == '07-22-22' and slice_target == 2:
            rec_target = [i for i in range(0,16)]
            tbs_recording_no = 5
        if date == '07-26-22' and slice_target == 1:
            rec_target = [i for i in range(0,19)]
            tbs_recording_no = 6
        if date == '07-26-22' and slice_target == 2:
            rec_target = [i for i in range(0,16)]
            tbs_recording_no = 4
        if date == '08-01-22':
            slice_target = [1,2]
            rec_target = [i for i in range(11)]
            tbs_recording_no = 4
        if date == "11-30-21":
            rec_target = [2]
        if date == "08-19-22":
            slice_target = [1,2]
            rec_target = [i for i in range(1,13)]
        if date == "08-22-22":
            slice_target = [1,2,3,4]
            rec_target = [i for i in range(1,6)]
        if date == "09-01-22":
            slice_target = [i for i in range(5,8)]  # first 4: stim was 0
            rec_target = [i for i in range(0,7)]
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "06-21-22":
            slice_target = [1,2,3]
            rec_target = [i for i in range(1,10)]
            cre_line_type = 'ai35hVOS /PV-Cre'
        if date == "10-14-22":
            slice_target = [1,2,3,4]
            rec_target = [i for i in range(1,4)]
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "2022-10-14": # anna's old rig data of same animal
            slice_target = [1,2,3,4]
            rec_target = [i for i in range(1,4)]
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "10-21-22":
            slice_target = [1,2,3,4]
            rec_target = [i for i in range(1,22)]
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "2022-10-21": # anna's old rig data of same animal
            slice_target = [1,2,3,4,5,6]
            rec_target = [i for i in range(1,4)]
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "10-28-22":
            slice_target = [1,2,3]
            rec_target = [i for i in range(1,17)]
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "2022-10-28": # anna's old rig data of same animal
            slice_target = [1,2,3,4,5]
            rec_target = [i for i in range(1,5)]
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "11-04-22":
            slice_target = [1,3,4]
            rec_target = [i for i in range(1,21)]
            tbs_recording_no = 11
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "2022-11-04": # anna's old rig data of same animal
            slice_target = [1,2,3,4,5]
            rec_target = [i for i in range(1,4)]
            cre_line_type = 'kv2.1hVOS 3.0 / PV-Cre'
        if date == "11-09-22":
            slice_target = [1,2,3,4]
            rec_target = [i for i in range(4,21)]
            tbs_recording_no = 11
            cre_line_type = 'ai35hVOS / Scnn1a-tg3-Cre'
        if date == "11-16-22":
            slice_target = [1,2,3,4]
            rec_target = [i for i in range(1,21)]
            tbs_recording_no = 11
            cre_line_type = 'ai35hVOS / Scnn1a-tg3-Cre'
        if date == "11-23-22": # Kate's
            slice_target = [9]
            rec_target = [4]
            cre_line_type = 'ai35hVOS / PV-Cre'
        if date == "11-30-22":
            slice_target = [1,2,3]
            rec_target = [i for i in range(1,21)]
            tbs_recording_no = 11
            cre_line_type = 'ai35hVOS / Scnn1a-tg3-Cre'
        if date == "12-16-22":
            slice_target = [1,2]  # first slice is not LTP, and not worth
            rec_target = [i for i in range(1, 21)]
            tbs_recording_no = 11
            cre_line_type = 'ai35hVOS / Scnn1a-tg3-Cre'
        if date == "01-10-23":
            slice_target = [1,2,3]  # first slice is not LTP, and not worth
            rec_target = [i for i in range(1, 21)]
            tbs_recording_no = 11
            cre_line_type = 'ai35hVOS / Scnn1a-tg3-Cre'

        return slice_target, rec_target, tbs_recording_no, cre_line_type