

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
             'height': 320},
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
            crop_margin = int((w - h) / 2)
            camera_program_settings[i]['cropping'] = [
                crop_margin,
                w - crop_margin
            ]
        return camera_program_settings
