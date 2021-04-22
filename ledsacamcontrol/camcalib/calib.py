import matplotlib.pyplot as plt

from ledsacamcontrol.camcontrol import capture_image_at_shutter_speed
from ledsacamcontrol.processing import find_search_areas, get_channel_arrays_from_file
class Calib():
    def __init__(self, nchannels=3, shutter_speed='1/1000', local_images=False):
        self.local_images = local_images
        self.init_shutter_speed = shutter_speed
        self.nchannels = nchannels
        self.search_areas = None
        self.radius = None
        self.nleds = None
        self.datatype = 'CR2'

    def find_leds(self, channel, radius, skip, threshold_factor):
        self.radius = radius
        filename = 'find_leds'
        file = f'{filename}.{self.datatype}'
        if not self.local_images:
            capture_image_at_shutter_speed(self.init_shutter_speed, file)
        channel_arrays_list = get_channel_arrays_from_file(file)
        channel_array = channel_arrays_list[channel]
        self.init_image = channel_array
        search_areas = find_search_areas(channel_array, window_radius=radius, skip=skip,
                                         threshold_factor=threshold_factor)
        self.search_areas = search_areas
        self.nleds = len(search_areas)

    def plot_leds(self):
        fig, ax = plt.subplots(figsize=(4, 36)) # TODO: remove hardcoding of figsize
        x_min = self.search_areas[0][1] - 5 * self.radius
        x_max = self.search_areas[-1][1] + 5 * self.radius
        y_min = self.search_areas[0][2] - 5 * self.radius
        y_max = self.search_areas[-1][2] + 5 * self.radius

        plt.imshow(self.init_image, cmap='gray_r')
        for led in self.search_areas:
            circle = plt.Circle((led[2], led[1]), radius=self.radius, color='red', fill=False)
            ax.add_patch(circle)
        ax.set_ylim(x_min, x_max)
        ax.set_xlim(y_min, y_max)
        plt.savefig("find_leds.png")


