

class CameraSettings:

    def __init__(self):
        self.camera_settings = self.load_camera_settings()

    def get_program_settings(self, program):
        return self.camera_settings[program]

    def load_camera_settings(self):
        # Map camera settings to analysis adjustments
        camera_program_settings = [
            {'interval_between_samples': 1 / 200 * 1000,
             'width': 2048,
             'height': 1024},
            {'interval_between_samples': 1 / 2000 * 1000,
             'width': 2048,
             'height': 100},
            {'interval_between_samples': 1 / 1000 * 1000,
             'width': 1024,
             'height': 320,
             'cropping': [512-160, 512+160]},  # want to keep middle 320px of width
            {'interval_between_samples': 1 / 2000 * 1000,
             'width': 1024,
             'height': 160},
            {'interval_between_samples': 1 / 2000 * 1000,
             'width': 512,
             'height': 160},
            {'interval_between_samples': 1 / 4000 * 1000,
             'width': 512,
             'height': 80},
            {'interval_between_samples': 1 / 5000 * 1000,
             'width': 256,
             'height': 60},
            {'interval_between_samples': 1 / 7500 * 1000,
             'width': 256,
             'height': 40},
        ]

        for i in range(len(camera_program_settings)):
            camera_program_settings[i]['camera_program'] = i
            w = camera_program_settings[i]['width']
            h = camera_program_settings[i]['height']
            # auto crop margin. Cropping is the width-range of pixels to keep
            if "cropping" not in camera_program_settings[i]:
                camera_program_settings[i]['cropping'] = [
                    int(w/2) - int(h/2),
                    int(w/2) + int(h/2)
                ]
        return camera_program_settings
