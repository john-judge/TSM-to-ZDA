import struct
import numpy as np


class ZDA_Writer:

    def __init__(self):
        pass

    @staticmethod
    def pack_binary_data(data, bytes_type):
        if bytes_type == 'c':
            data = bytes(str(data), "utf-8")
        elif bytes_type in ['H', 'i', 'f', 'q']:
            data = int(data)

        bytes_type = bytes("<" + bytes_type, "utf-8")
        return struct.pack(bytes_type, data)

    def write_zda_to_file(self, images, metadata, filename, rli):
        file = open(filename, 'wb')

        # data type sizes in bytes
        chSize = 'c'  # 1
        shSize = 'H'  # 2
        nSize = 'i'  # 4
        tSize = 'q'  # 8
        fSize = 'f'  # 4

        file.write(self.pack_binary_data(metadata['version'], chSize))
        file.write(self.pack_binary_data(metadata['slice_number'], shSize))
        file.write(self.pack_binary_data(metadata['location_number'], shSize))
        file.write(self.pack_binary_data(metadata['record_number'], shSize))
        file.write(self.pack_binary_data(metadata['camera_program'], nSize))

        file.write(self.pack_binary_data(metadata['number_of_trials'], chSize))
        file.write(self.pack_binary_data(metadata['interval_between_trials'], chSize))
        file.write(self.pack_binary_data(metadata['acquisition_gain'], shSize))
        file.write(self.pack_binary_data(metadata['points_per_trace'], nSize))
        file.write(self.pack_binary_data(metadata['time_RecControl'], tSize))

        file.write(self.pack_binary_data(metadata['reset_onset'], fSize))
        file.write(self.pack_binary_data(metadata['reset_duration'], fSize))
        file.write(self.pack_binary_data(metadata['shutter_onset'], fSize))
        file.write(self.pack_binary_data(metadata['shutter_duration'], fSize))

        file.write(self.pack_binary_data(metadata['stimulation1_onset'], fSize))
        file.write(self.pack_binary_data(metadata['stimulation1_duration'], fSize))
        file.write(self.pack_binary_data(metadata['stimulation2_onset'], fSize))
        file.write(self.pack_binary_data(metadata['stimulation2_duration'], fSize))

        file.write(self.pack_binary_data(metadata['acquisition_onset'], fSize))
        file.write(self.pack_binary_data(metadata['interval_between_samples'], fSize))
        file.write(self.pack_binary_data(metadata['raw_width'], nSize))
        file.write(self.pack_binary_data(metadata['raw_height'], nSize))

        num_diodes = metadata['raw_width'] * metadata['raw_height']

        file.seek(1024, 0)
        # RLI
        for rli_type in ['rli_low', 'rli_high', 'rli_max']:
            for i in range(num_diodes):
                file.write(self.pack_binary_data(rli[rli_type][i], shSize))

        for i in range(metadata['number_of_trials']):
            for jw in range(metadata['raw_width']):
                for jh in range(metadata['raw_height']):
                    for k in range(metadata['points_per_trace']):
                        file.write(self.pack_binary_data(images[i,k,jw,jh], shSize))

        file.close()
