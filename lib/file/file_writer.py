import ctypes
import os
import time

import numpy as np


# https://medium.com/@stephenscotttucker/interfacing-python-with-c-using-ctypes-classes-and-arrays-42534d562ce7


class FileWriter:

    def __init__(self, dll_path='./x64/Release/'):
        self.lib = None
        self.dll_enabled = True
        self.load_dll(dll_path=dll_path)
        self.define_c_types()
        self.controller = self.lib.createController()

    def __del__(self):
        if self.dll_enabled:
            try:
                self.lib.destroyController(self.controller)
            except AttributeError:
                pass

    def save_data_file(self, filename, images, num_trials, num_pts, int_pts, num_fp_pts, width, height,
                                    rliLow, rliHigh, rliMax, sliceNo, locNo, recNo, program, int_trials):
        print("write to file num_pts", num_pts)
        if self.dll_enabled:
            filename = filename.encode('utf-8')
            self.lib.saveDataFile(self.controller, filename, images.reshape(-1), num_trials, num_pts, int_pts, num_fp_pts, width,
                                  height, rliLow.reshape(-1), rliHigh.reshape(-1), rliMax.reshape(-1), sliceNo, locNo,
                                  recNo, program, int_trials)

    def define_c_types(self):
        if not self.dll_enabled:
            print("DLL not enabled.")
            return
        controller_handle = ctypes.POINTER(ctypes.c_char)
        c_ushort_array = np.ctypeslib.ndpointer(dtype=np.uint16, ndim=1)

        # c_float_array = np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS')

        # (unsigned short * images, int numTrials, int numPts, double intPts,
        # 	int num_fp_pts, int width,
        # 	int height, short * rliLow, short * rliHigh, short * rliMax,
        # 	short sliceNo, short locNo, short recNo, int program, int intTrials)

        self.lib.createController.argtypes = []  # argument types
        self.lib.createController.restype = controller_handle  # return type

        self.lib.destroyController.argtypes = [controller_handle]

        self.lib.saveDataFile.argtypes = [controller_handle, ctypes.c_char_p, c_ushort_array,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_double,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                            c_ushort_array, c_ushort_array, c_ushort_array,
                                            ctypes.c_short, ctypes.c_short, ctypes.c_short,
                                            ctypes.c_int, ctypes.c_int]

    def load_dll(self, dll_path='./x64/Release/', verbose=False):
        dll_path = os.path.abspath(dll_path)
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(os.getcwd())
            os.add_dll_directory(os.path.dirname(dll_path + os.path.sep + "PhotoLib.dll"))
            try:
                os.add_dll_directory(os.path.dirname(os.path.abspath('./PhotoLib/Include/EDT')))
                os.add_dll_directory(os.path.dirname(os.path.abspath('./PhotoLib/Include')))
                os.add_dll_directory(os.path.dirname(os.path.abspath('./PhotoLib')))
            except Exception as e:
                print("Not all DLL search paths added.")
            env_paths = os.environ['PATH'].split(';')
            for path in env_paths:
                try:
                    os.add_dll_directory(path)
                    if verbose:
                        print('added DLL dependency path:', path)
                except Exception as e:
                    if verbose:
                        print('Failed to add DLL dependency path:', path)
                        print(e)
            self.lib = ctypes.cdll.LoadLibrary(dll_path + os.path.sep + 'PhotoLib.dll')
        else:
            os.environ['PATH'] = os.path.dirname(dll_path + os.path.sep + "PhotoLib.dll") + ';' \
                                 + os.path.dirname(os.path.abspath('./PhotoLib/Include/EDT')) + ';' \
                                 + os.path.dirname(os.path.abspath('./PhotoLib/Include')) + ';' \
                                 + os.path.dirname(os.path.abspath('./PhotoLib')) + ';' \
                                 + os.environ['PATH']
            self.lib = ctypes.cdll.LoadLibrary(dll_path + 'PhotoLib.dll')
