import pickle
import os


class Pickler:
    """ For saving and loading objects to pickle files """

    def __init__(self, dir_base, date, save_pickle_index, restore_pickle, slice_target):
        self.dir_base = dir_base
        self.date = date
        self.save_pickle_index = save_pickle_index
        self.restore_pickle = restore_pickle
        self.slice_target = slice_target

    def get_pickle_filename(self, dir_base, date, i_run, i_slice):
        return dir_base + date + "/saved_run" + str(i_run) + "-" + str(i_slice) + ".pickle"

    def process_pickle(self, io_obj):
        self.save_pickle(io_obj)
        self.load_pickle(io_obj)

    def save_pickle(self, obj):
        if self.save_pickle_index is not None and self.restore_pickle is None:
            pickle_filename = self.get_pickle_filename(self.dir_base,
                                                       self.date,
                                                       self.save_pickle_index,
                                                       self.slice_target)
            while os.path.exists(pickle_filename) and self.save_pickle_index < 99:
                self.save_pickle_index += 1
                pickle_filename = self.get_pickle_filename(self.dir_base,
                                                           self.date,
                                                           self.save_pickle_index,
                                                           self.slice_target)
            with open(pickle_filename, 'wb') as f:
                pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
                print("Wrote:", pickle_filename)

    def load_pickle(self, obj):
        # restore pickled objects if resuming a run.
        if self.restore_pickle is not None:
            obj = None
            pickle_filename = self.get_pickle_filename(self.dir_base,
                                                       self.date,
                                                       self.save_pickle_index,
                                                       self.slice_target)
            if os.path.exists(pickle_filename):
                with open(pickle_filename, 'rb') as f:
                    obj = pickle.load(f)
            else:
                raise FileNotFoundError


class SimplePickler:

    def __init__(self, pickle_filename):
        self.pickle_filename = pickle_filename

    def save_pickle_simple(self, obj):
        with open(self.pickle_filename, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
            print("Wrote:", self.pickle_filename)

    def load_pickle_simple(self):
        if os.path.exists(self.pickle_filename):
            with open(self.pickle_filename, 'rb') as f:
                obj = pickle.load(f)
        else:
            raise FileNotFoundError
