from fractions import Fraction
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from ledsacamcontrol.camcalib import Calib
from ledsacamcontrol.camcontrol import get_shutter_speed_list
from ledsacamcontrol.processing import get_real_exp_time_from_file, get_channel_values_at_shutter_speed,\
    get_shutter_speed_from_file, get_channel_values_from_file
from sklearn.linear_model import LinearRegression

cm = 1 / 2.54

class CamColorCalib(Calib):
    def __init__(self, nchannels=3, shutter_speed='1/1000', local_images=False, label="RGB_LED", intercept=True):
        super().__init__(nchannels=nchannels, shutter_speed=shutter_speed, local_images=local_images)
        self.saturation_correction_matrix = None
        self.integral_correction_matrix = None
        self.shutter_speed_list = get_shutter_speed_list(local_images=self.local_images)
        self.input_params_df = None
        self.label = label
        self.intercept = intercept


    def _get_nearest_shutter_speed(self, value):
        nearest_shutter_speed = min(self.shutter_speed_list, key=lambda x: abs(Fraction(x) - value))
        return nearest_shutter_speed

    def _set_input_params_df(self):
        leds_list = list(range(len(self.search_areas)))
        iterables = [leds_list, ["integral", "saturation"], list(range(self.nchannels)), list(range(self.nchannels))]
        columns = pd.MultiIndex.from_product(iterables,
                                             names=["led_id", "parameter_type", "LED_channel", "camera_channel"])
        empty_index = np.empty(len(self.shutter_speed_list))
        empty_index[:] = np.nan
        self.input_params_df = pd.DataFrame(columns=columns, index=self.shutter_speed_list)
        self.input_params_df.sort_index(ascending=True, inplace=True)
        self.real_exp_time_lut = pd.Series(index=self.shutter_speed_list, name="real_exp_time", dtype=np.float64)

    def start_calibration(self, channel, nphotos=5):
        if self.input_params_df is None:
            self._set_input_params_df()
        file = f'calib_ch_{channel}_init.{self.datatype}'
        channel_saturation_list_all, _, _ = get_channel_values_at_shutter_speed(self.init_shutter_speed,
                                                                                self.search_areas, self.radius,
                                                                                file, self.local_images)
        max_saturation = np.amax(channel_saturation_list_all)
        if max_saturation > 0.1 and max_saturation < 0.9:
            saturation_lut = np.linspace(0.2, 0.8, nphotos)
            calc_shutter_speed_lut = saturation_lut / max_saturation * Fraction(self.init_shutter_speed)
            real_shutter_speed_lut = [self._get_nearest_shutter_speed(value) for value in calc_shutter_speed_lut]

            for i, shutter_speed in enumerate(real_shutter_speed_lut):
                file = f'cam_calib_ch_{channel}_{i}.{self.datatype}'
                channel_saturation_list_all, channel_integral_list_all, _ = get_channel_values_at_shutter_speed(
                    shutter_speed, self.search_areas, self.radius, file, self.local_images)
                shutter_speed = get_shutter_speed_from_file(file) # Overwrite for case of local images
                for led_id, (channel_saturation_list, channel_integral_list) in enumerate(
                        zip(channel_saturation_list_all, channel_integral_list_all)):
                    self.input_params_df.loc[shutter_speed, (led_id, 'saturation', channel)] = channel_saturation_list
                    self.input_params_df.loc[shutter_speed, (led_id, 'integral', channel)] = channel_integral_list
                real_exp_time = get_real_exp_time_from_file(file)
                self.real_exp_time_lut[shutter_speed] = float(real_exp_time)
        else:
            print(f"Initial Saturation is {max_saturation} but must be between 10% and 90%")


    def get_calibration_params(self, led_id, calib_param, channel):
        params_df = self.input_params_df[led_id, calib_param, channel].dropna(how='all')
        real_exp_time_list = np.array(self.real_exp_time_lut[params_df.index])
        calibration_params_list, intercept_list = self._get_fit_params(real_exp_time_list, params_df)
        params_df["real_exp_time"] = real_exp_time_list
        return params_df, calibration_params_list, intercept_list

    def _get_fit_params(self, real_exp_time_list, params):
        fit_params_list = []
        intercept_list = []
        for channel in params:
            rel_saturation_list = params[channel]
            model = LinearRegression(fit_intercept=self.intercept)
            model.fit(real_exp_time_list.reshape(-1, 1), rel_saturation_list)
            fit_param = model.coef_[0]
            intercept = model.intercept_
            fit_params_list.append(fit_param)
            intercept_list.append(intercept)
        return fit_params_list, intercept_list

    def get_color_correction_matrix(self, led_id, calib_param):
        corr = np.zeros((self.nchannels, self.nchannels))
        for channel in self.input_params_df[led_id, calib_param, 0]:
            params_df = self.input_params_df[led_id, calib_param, channel].dropna(how='all')
            real_exp_time_list = np.array(self.real_exp_time_lut[params_df.index])
            corr[:, channel], _ = self._get_fit_params(real_exp_time_list, params_df)
        corr_normed = (corr / corr.max(axis=1))
        return corr_normed

    def plot_calib_params(self, fig_width, channels=[0], led_id='all', save=False):
        nchannels = len(channels)

        fig = plt.figure(constrained_layout=True)
        gird = gridspec.GridSpec(ncols=2, nrows=nchannels, figure=fig)
        fig.set_size_inches(fig_width * cm, 0.5 * fig_width * nchannels * cm)

        for i, led_channel in enumerate(channels):

            integral_values, correction_params_integral, intercept_integral = self.get_calibration_params(led_id, "integral", led_channel)
            saturation_values, correction_params_saturation, intercept_saturation = self.get_calibration_params(led_id, "saturation", led_channel)
            ax1 = fig.add_subplot(gird[i, 0])
            ax2 = fig.add_subplot(gird[i, 1])
            for channel, color in zip(saturation_values, ['red', 'green', 'blue']):
                last_value = saturation_values['real_exp_time'][-1]
                ax1.scatter(saturation_values['real_exp_time'], saturation_values[channel], color=color)
                ax2.scatter(integral_values['real_exp_time'], integral_values[channel], color=color)
                # ax1.scatter(saturation_values.index, saturation_values[channel], color=color, alpha=0.5)
                # ax2.scatter(integral_values.index, integral_values[channel], color=color, alpha=0.5)
                x = np.linspace(0, last_value)
                y_integral = lambda x: intercept_integral[channel] + x * correction_params_integral[channel]
                y_saturation = lambda x: intercept_saturation[channel] + x * correction_params_saturation[channel]
                ax1.plot(x, y_saturation(x), color=color, label=f"Cam Ch {channel}")
                ax2.plot(x, y_integral(x), color=color, label=f"Cam Ch {channel}")
                if led_id == 'all':
                    ax1.errorbar(saturation_values['real_exp_time'], saturation_values[channel])
                ax2.ticklabel_format(scilimits=(0, 0), axis='y')
                ax1.grid(True)
                ax2.grid(True)
                ax1.set_xlim(-0.1 * last_value, 1.1 * last_value)
                ax2.set_xlim(-0.1 * last_value, 1.1 * last_value)
                ax1.set_xlabel("shutter speed [s]")
                ax2.set_xlabel("shutter speed [s]")
                ax1.set_ylabel("Max saturation [-]")
                ax2.set_ylabel("Integral value [-]")
                ax1.set_title(f"Saturation LED Ch {led_channel}")
                ax2.set_title(f"Integral LED Ch {led_channel}")

        fig.tight_layout()
        plt.legend(bbox_to_anchor=(-0.2, -0.2), loc='upper center', ncol=3)
        if save == True:
            plt.savefig(f"color_correction_ch_all_led_id_{led_id}.pdf", dpi=1000, bbox_inches='tight')

    def save_input_params(self):
        rt_input_params_df = self.input_params_df
        rt_input_params_df["real_exposure_time"] = self.real_exp_time_lut
        rt_input_params_df.to_csv(f"{self.label}_input_params.csv")

    def save_cc_matrix(self, led_id='all'):
        if led_id == 'all':
            led_ids_list = range(self.nleds)
        else:
            led_ids_list = [led_id]

        for led_id in led_ids_list:
            integral_corr_matrix = self.get_color_correction_matrix(led_id, 'integral')
            saturation_corr_matrix = self.get_color_correction_matrix(led_id, 'saturation')
            np.savetxt(f"{self.label}_{led_id}_integral_corr_norm.csv", integral_corr_matrix, delimiter=",")
            np.savetxt(f"{self.label}_{led_id}_saturation_corr_norm.csv", saturation_corr_matrix, delimiter=",")

    def plot_cc_matrix(self, fig_width, led_id=0, save=False):
        integral_corr_matrix = self.get_color_correction_matrix(led_id, 'integral')
        saturation_corr_matrix = self.get_color_correction_matrix(led_id, 'saturation')

        width = 0.3
        channels = np.arange(3)
        fig, axs = plt.subplots(ncols=2)
        fig.set_size_inches(fig_width * cm, 0.5 * fig_width * cm)

        for ax, corr_matrix in zip(axs, [saturation_corr_matrix, integral_corr_matrix]):
            ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
            ax.bar(channels - width, corr_matrix[:, 0], width, color='red', label="Channel 0")
            ax.bar(channels, corr_matrix[:, 1], width, color='green', label="Channel 1")
            ax.bar(channels + width, corr_matrix[:, 2], width, color='blue', label="Channel 2")
            ax.set_xticks([0, 1, 2])
            ax.set_xlabel("Channel")
        axs[0].set_ylabel("Dependencie")
        axs[0].set_title("Saturation ratio")
        axs[1].set_title("Integral ratio")
        plt.legend(bbox_to_anchor=(-0.2, -0.2), loc='upper center', ncol=3)
        if save == True:
            plt.savefig(f"color_correction_dep_{self.label}.pdf", dpi=1000, bbox_inches='tight')

