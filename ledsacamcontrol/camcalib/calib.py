import matplotlib.pyplot as plt
import numpy as np
from ledsacamcontrol.camcontrol import capture_image_at_shutter_speed
from ledsacamcontrol.processing import find_search_areas, find_search_areas_advanced, find_search_areas_advanced_2, get_channel_arrays_from_file, get_channel_arrays_from_file_txt
class Calib():
    def __init__(self, nchannels=3, shutter_speed='1/1000', local_images=False):
        self.local_images = local_images
        self.init_shutter_speed = shutter_speed
        self.nchannels = nchannels
        self.search_areas = None
        self.radius = None
        self.nleds = None
        self.datatype = 'CR2'

    def find_leds(self, channel, radius, skip, threshold_factor, filename = 'find_leds'):
        self.radius = radius
        file = f'{filename}.{self.datatype}'
        if not self.local_images:
            capture_image_at_shutter_speed(self.init_shutter_speed, file)
        if self.datatype in ['txt', 'csv']:
            channel_array = get_channel_arrays_from_file_txt(file)
        else:
            if channel == 'all':
                channel_array = get_channel_arrays_from_file(file, separate_channels=False)
            else:
                channel_arrays_list = get_channel_arrays_from_file(file)
                channel_array = channel_arrays_list[channel]
        self.init_image = channel_array
        search_areas = find_search_areas(channel_array, window_radius=radius, skip=skip,
                                         threshold_factor=threshold_factor)
        self.search_areas = search_areas
        self.nleds = len(search_areas)


    def find_leds_advanced(self,channel, radius, exclude_width, exclude_height, n_leds, n_strips, strip_width, filename = 'find_leds', reorder=True, z_pixel_offset=None, border_width = None):
        self.radius = radius
        file = f'{filename}.{self.datatype}'
        if not self.local_images:
            capture_image_at_shutter_speed(self.init_shutter_speed, file)
        if self.datatype in ['txt', 'csv']:
            channel_array = get_channel_arrays_from_file_txt(file)
        else:
            if channel == 'all':
                channel_array = get_channel_arrays_from_file(file, separate_channels=False)
            else:
                channel_arrays_list = get_channel_arrays_from_file(file)
                channel_array = channel_arrays_list[channel]
        self.init_image = channel_array
        search_areas = find_search_areas_advanced(channel_array, window_radius=radius, exclude_width=exclude_width, exclude_height= exclude_height, n_leds=n_leds, n_strips=n_strips, strip_width=strip_width, reorder=reorder, z_pixel_offset=z_pixel_offset, border_width=border_width)
        self.search_areas = search_areas
        self.nleds =n_leds
        if filename:
            np.savetxt(f'{filename}.csv', self.search_areas, delimiter=',',
                       header='LED id, pixel position x, pixel position y', fmt='%d')
            print(f"{filename}.csv saved!")

    def find_leds_advanced_2(self, radius, max_n_leds=None, percentile=99.9, filename='find_leds', z_pixel_offset=None):
        self.radius = radius
        file = f'{filename}.{self.datatype}'
        if not self.local_images:
            capture_image_at_shutter_speed(self.init_shutter_speed, file)
        if self.datatype in ['txt', 'csv']:
            channel_array = get_channel_arrays_from_file_txt(file)
        else:
            channel_array = get_channel_arrays_from_file(file, separate_channels=False)

        self.init_image = channel_array
        search_areas = find_search_areas_advanced_2(channel_array, window_radius=radius, max_n_leds=max_n_leds, percentile=percentile, z_pixel_offset=z_pixel_offset)
        self.search_areas = search_areas
        if filename:
            np.savetxt(f'{filename}.csv', self.search_areas, delimiter=',',
                       header='LED id, pixel position x, pixel position y', fmt='%d')
            print(f"{filename}.csv saved!")

    def plot_ref_image(self):
        plt.imshow(self.init_image)

    def plot_leds(self, filename=None, crop_image=True):
        # fig, ax = plt.subplots(figsize=(4, 36)) # TODO: remove hardcoding of figsize
        fig, ax = plt.subplots() # TODO: remove hardcoding of figsize
        x_min = max(self.search_areas[:, 1]) + 50
        x_max = min(self.search_areas[:, 1]) - 50
        y_min = min(self.search_areas[:, 2]) - 50
        y_max = max(self.search_areas[:, 2]) + 50

        plt.imshow(self.init_image, cmap='gray_r')
        for i, led in enumerate(self.search_areas):
            color = np.random.rand(3,)
            circle = plt.Circle((led[2], led[1]), radius=self.radius, color=color, fill=False, linewidth=0.1)
            ax.add_patch(circle)
            ax.annotate(i, xy=(led[2]+30, led[1]), color=color, alpha=0.7)
        if crop_image == True:
            ax.set_ylim(x_min, x_max)
            ax.set_xlim(y_min, y_max)
        if filename:
            # plt.savefig(f"find_leds_{filename}.png")
            plt.savefig(f"find_leds_{filename}.pdf")


    def plot_single_led(self, image, led_id, channel, max_channel_value=None):
        if self.datatype in ['txt', 'csv']:
            channel_array = get_channel_arrays_from_file_txt(image)
        else:
            channel_arrays_list = get_channel_arrays_from_file(image)
            channel_array = channel_arrays_list[channel]
        plt.imshow(channel_array, vmax=max_channel_value)
        x_min = self.search_areas[led_id][1] - self.radius
        x_max = self.search_areas[led_id][1] + self.radius
        y_min = self.search_areas[led_id][2] - self.radius
        y_max = self.search_areas[led_id][2] + self.radius
        plt.xlim(y_min, y_max)
        plt.ylim(x_min, x_max)
        plt.title(f"Channel: {channel}, LED ID: {led_id}, Sum: {channel_array[x_min:x_max, y_min:y_max].sum()}, Max: {channel_array[x_min:x_max, y_min:y_max].max()}")







