class PwmEstimate:
    def __init__(self, nchannels=3, shutter_speed='1/2000',
                 saturation_calibration_matrix_single=None,
                 integral_calibration_matrix_single=None,
                 saturation_calibration_matrix_all=None,
                 integral_calibration_matrix_all=None,
                 saturation_calibration_matrix_all_raw=None,
                 integral_calibration_matrix_all_raw=None,
                 saturation_correction_matrix=None,
                 integral_correction_matrix=None,
                 local_images=False):
        self.saturation_calibration_matrix_single = saturation_calibration_matrix_single
        self.integral_calibration_matrix_single = integral_calibration_matrix_single
        self.saturation_calibration_matrix_all = saturation_calibration_matrix_all
        self.integral_calibration_matrix_all = integral_calibration_matrix_all
        self.saturation_calibration_matrix_all_raw = saturation_calibration_matrix_all_raw
        self.integral_calibration_matrix_all_raw = integral_calibration_matrix_all_raw
        self.saturation_correction_matrix = saturation_correction_matrix
        self.integral_correction_matrix = integral_correction_matrix
        self.shutter_speed = shutter_speed
        self.nchannels = nchannels
        self.local_images = local_images

    def set_led_locations(self, search_areas, radius):
        self.search_areas = search_areas
        self.radius = radius

    def capture_image(self, filename="PWM_est", datatype='CR2'):
        channel_saturation_list, channel_integral_list, _ = get_channel_values_at_shutter_speed(self.shutter_speed,
                                                                                                self.search_areas,
                                                                                                self.radius, filename,
                                                                                                datatype,
                                                                                                local_image=self.local_images)
        self.channel_saturation_list = channel_saturation_list[0]  # Hardcoding for only one LED
        self.channel_integral_list = channel_integral_list[0]  # Hardcoding for only one LED

    def get_channel_values(self):
        return self.channel_saturation_list, self.channel_integral_list

    def get_estimated_pwm_levels(self, calib_param='integral', calibration='single', color_correction=False):
        if calib_param == 'integral':
            color_correction_matrix = self.integral_correction_matrix
            if calibration == 'single':
                calibration_params = self.integral_calibration_matrix_single
            elif calibration == 'all':
                calibration_params = self.integral_calibration_matrix_all
            elif calibration == 'all_raw':
                calibration_params = self.integral_calibration_matrix_all_raw
            channel_values_list = self.channel_integral_list
        elif calib_param == 'saturation':
            color_correction_matrix = self.saturation_correction_matrix
            if calibration == 'single':
                calibration_params = self.saturation_calibration_matrix_single
            elif calibration == 'all':
                calibration_params = self.saturation_calibration_matrix_all
            elif calibration == 'all_raw':
                calibration_params = self.saturation_calibration_matrix_all_raw
            channel_values_list = self.channel_saturation_list
        if color_correction == True:
            channel_values_list = solve(color_correction_matrix, channel_values_list)
        pwm_levels = []
        for channel, channel_value in enumerate(channel_values_list):
            pwm_levels.append(calibration_params[channel, 0] * channel_value + calibration_params[channel, 1])
        return pwm_levels
