import struct
import numpy as np

from lib.file.file_writer import FileWriter


class ZDA_Writer:

    def __init__(self):
        pass

    @staticmethod
    def pack_binary_data(data, bytes_type):
        if bytes_type == 'c':
            data = bytes(str(data), "utf-8")
        elif bytes_type in ['H', 'i', 'f', 'q']:
            data = int(data)

        endianness = "<" if bytes_type in ['i', 'f', 'q'] else ">"

        bytes_type = bytes(endianness + bytes_type, "utf-8")
        return struct.pack(bytes_type, data)

    @staticmethod
    def write_zda_to_file_c_interface(images, metadata, filename, rli, fp_array):
        fw = FileWriter()

        # images shape (trial, t, x, y) -> (trial, x, y, t)
        num_trials, num_pts, width, height = images.shape
        images = np.swapaxes(images, 1, 3)
        images = np.swapaxes(images, 1, 2)

        # add fp_array onto end of images array
        full_data = np.zeros(images.size + fp_array.size,
                             dtype=np.uint16).reshape(metadata['number_of_trials'], -1)
        img_size = int(images.size / metadata['number_of_trials'])
        print(fp_array.shape)
        for i in range(metadata['number_of_trials']):
            full_data[i, :img_size] = images[i, :, :, :].reshape(-1)
            full_data[i, img_size:] = fp_array[i, :, :].reshape(-1)

        fw.save_data_file(filename, full_data.reshape(-1),
                          num_trials,
                          num_pts,
                          metadata['interval_between_samples'],
                          metadata['num_fp_pts'],
                          width,
                          height,
                          rli['rli_low'],
                          rli['rli_high'],
                          rli['rli_max'],
                          metadata['slice_number'],
                          metadata['location_number'],
                          metadata['record_number'],
                          metadata['camera_program'],
                          metadata['interval_between_trials'])

        # def save_data_file(self, images, num_trials, num_pts, int_pts, num_fp_pts, width, height,
        # rliLow, rliHigh, rliMax, sliceNo, locNo, recNo, program, int_trials)

    def write_zda_to_file(self, images, metadata, filename, rli, fp_array):
        self.write_zda_to_file_c_interface(images, metadata, filename, rli, fp_array)
        '''
        try:
            self.write_zda_to_file_c_interface(images, metadata, filename, rli, fp_array)
        except Exception as e:
            print(e)
            # print("Writing ZDA directly instead.")
            # self.write_zda_to_file_directly(images, metadata, filename, rli, fp_array)
            '''

    def write_zda_to_file_directly(self, images, metadata, filename, rli, fp_array):
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
        
        num_fp_pts = 4
        num_diodes = metadata['raw_width'] * metadata['raw_height'] + num_fp_pts

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
                        
        print("wrote", metadata['points_per_trace'], "points for", metadata['raw_width'], "x", metadata['raw_height'] , "x", metadata['number_of_trials'],
              "px")

        print(fp_array.shape)
        for _ in range(metadata['number_of_trials']):

            for i in range(num_fp_pts):
                for k in range(metadata['points_per_trace']):
                    file.write(self.pack_binary_data(fp_array[k, i], shSize))

        file.close()
