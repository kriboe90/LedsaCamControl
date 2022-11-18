class PwmColorCalib():
    def __init__(self, nchannels=3, shutter_speed='1/2000', saturation_correction_matrix=None,
                 integral_correction_matrix=None, local_images=False):
        self.local_images = local_images
        self.shutter_speed = shutter_speed
        self.nchannels = nchannels
        self.saturation_correction_matrix = saturation_correction_matrix
        self.integral_correction_matrix = integral_correction_matrix
        self._set_input_params_df()

    def set_led_locations(self, search_areas, radius):
        self.search_areas = search_areas
        self.radius = radius

    def _set_input_params_df(self):
        iterables = [["integral", "saturation", "rgb_pwm_levels"], [*range(self.nchannels), "all", "all_raw"],
                     [*range(self.nchannels)]]
        columns = pd.MultiIndex.from_product(iterables, names=["parameter_type", "LED_channel", "camera_channel"])
        self.input_params_df = pd.DataFrame(columns=columns)

    def get_max_saturation(self):
        channel_saturation_list, _, _ = get_channel_values_at_shutter_speed(self.shutter_speed, self.search_areas,
                                                                            self.radius, local_image=self.local_images)
        max_saturation = max(channel_saturation_list[0])  # Hardcoding for only one LED
        return max_saturation

    def add_calibration_params(self, rgb_levels, channel='all'):
        filename = "calib_" + "_".join(str(level) for level in rgb_levels)
        channel_saturation_list, channel_integral_list, _ = get_channel_values_at_shutter_speed(self.shutter_speed,
                                                                                                self.search_areas,
                                                                                                self.radius,
                                                                                                filename=filename,
                                                                                                datatype='CR2',
                                                                                                local_image=self.local_images)
        channel_saturation_list = channel_saturation_list[0]  # Hardcoding for only one LED
        channel_integral_list = channel_integral_list[0]  # Hardcoding for only one LED
        index = len(self.input_params_df)
        if channel == 'all':
            self.input_params_df.loc[
                index, ('integral', 'all_raw')] = channel_integral_list  # Hardcoding for only one LED
            self.input_params_df.loc[
                index, ('saturation', 'all_raw')] = channel_saturation_list  # Hardcoding for only one LED
            self.input_params_df.loc[index, ('rgb_pwm_levels', 'all_raw')] = rgb_levels

            channel_integral_list = solve(self.integral_correction_matrix,
                                          channel_integral_list)  # Hardcoding for only one LED
            channel_saturation_list = solve(self.saturation_correction_matrix,
                                            channel_saturation_list)  # Hardcoding for only one LED

        self.input_params_df.loc[index, ('integral', channel)] = channel_integral_list  # Hardcoding for only one LED
        self.input_params_df.loc[
            index, ('saturation', channel)] = channel_saturation_list  # Hardcoding for only one LED
        self.input_params_df.loc[index, ('rgb_pwm_levels', channel)] = rgb_levels

    def get_pwm_calibration_matrix(self, calib_param, calibration='single'):
        pwm_calibration_array = []
        for channel in range(self.nchannels):
            if calibration == 'single':
                led_channel = channel
            elif calibration == 'all':
                led_channel = 'all'
            elif calibration == 'all_raw':
                led_channel = 'all_raw'
            channel_values = self.input_params_df.loc[:, (calib_param, led_channel, channel)].dropna().to_numpy()
            pwm_levels = self.input_params_df.loc[:, ('rgb_pwm_levels', led_channel, channel)].dropna().to_numpy()
            print(channel_values, pwm_levels)
            fit_params = self._get_fit_params(pwm_levels, channel_values)
            pwm_calibration_array.append(fit_params)
        return pwm_calibration_array

    # def get_calibration_params(self, calib_param, channel, calib_channel):
    #     if calib_param == 'integral':
    #         channel_values = self.integral_params
    #     elif calib_param == 'saturation':
    #         channel_values = self.saturation_params
    #     if calib_channel == 'all':
    #         calib_channel = -1
    #     self.pwm_params_array = np.array([np.array(xi) for xi in self.pwm_params])
    #     self.channel_values_array = np.array([np.array(xi) for xi in channel_values])
    #     calibration_params_list = self._get_fit_params(self.pwm_params_array[calib_channel][:, channel], self.channel_values_array[calib_channel][:, channel])
    #     return calibration_params_list

    def _get_fit_params(self, pwm_levels, channel_values):
        model = LinearRegression(fit_intercept=True)
        model.fit(channel_values.reshape(-1, 1), pwm_levels)
        return model.coef_[0], model.intercept_

    def find_leds(self, channel, radius, skip, threshold_factor, plot=True):
        self.radius = radius
        filename = 'find_leds_pwm_calib'
        file = f'{filename}.CR2'
        if not self.local_images:
            if os.path.exists(file):
                os.remove(file)
            capture_image_at_shutter_speed(self.init_shutter_speed, file)
        channel_arrays_list = get_channel_arrays_from_file(file)
        channel_array = channel_arrays_list[channel]
        search_areas = find_search_areas(channel_array, window_radius=radius, skip=skip,
                                         threshold_factor=threshold_factor)
        print(search_areas)
        self.search_areas = search_areas

        if plot == True:
            fig, ax = plt.subplots(figsize=(4, 36))
            x_min = search_areas[0][1] - 5 * radius
            x_max = search_areas[-1][1] + 5 * radius
            y_min = search_areas[0][2] - 5 * radius
            y_max = search_areas[-1][2] + 5 * radius

            plt.imshow(channel_array, cmap='gray_r')
            for led in search_areas:
                ax.scatter(led[2], led[1], s=100)
                circle = plt.Circle((led[2], led[1]), radius=radius, color='red', fill=False)
                ax.add_patch(circle)
            ax.set_ylim(x_min, x_max)
            ax.set_xlim(y_min, y_max)