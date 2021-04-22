import numpy as np
from fractions import Fraction
import rawpy
import exifread
from ledsacamcontrol.camcontrol import capture_image_at_shutter_speed


def get_channel_values_at_shutter_speed(shutter_speed, search_areas, radius, file, local_image):
    if local_image == False:
        capture_image_at_shutter_speed(shutter_speed, file)
    channel_saturation_list, channel_integral_list, channel_array_list = get_channel_values_from_file(file, search_areas, radius)
    return channel_saturation_list, channel_integral_list, channel_array_list

def get_channel_values_from_array(channel_array, radius, x, y):
    colordepth = 14
    channel_range = 2 ** colordepth - 1

    cropped_channel_array = channel_array[x-radius:x+radius, y-radius:y+radius]
    channel_sat = cropped_channel_array.max()/channel_range
    channel_integral = np.sum(cropped_channel_array)
    return cropped_channel_array, channel_sat, channel_integral

def get_channel_arrays_from_file(file):
    with rawpy.imread(file) as raw:
        colordepth = 14
        data = raw.raw_image_visible.copy()
        filter_array = raw.raw_colors_visible
        black_level = min(raw.black_level_per_channel[0], data.min())
        channel_range = 2 ** colordepth - 1
        white_level = channel_range # Todo: remove harcoding
        channel_array = data - black_level
        channel_array = (channel_array * (channel_range / (white_level - black_level))).astype(np.int16)
        channel_array = np.clip(channel_array, 0, channel_range)
        channel_0_array = np.where(filter_array == 0, channel_array, 0)
        channel_1_array = np.where((filter_array == 1) | (filter_array == 3), channel_array, 0)
        channel_2_array = np.where(filter_array == 2, channel_array, 0)
        return [channel_0_array, channel_1_array, channel_2_array]

def get_channel_values_from_file(file, search_areas, radius):
    chanel_array_list = get_channel_arrays_from_file(file)
    cropped_channel_array_list_all = []
    channel_sat_list_all = []
    channel_integral_list_all = []
    for led in search_areas:
        xi = led[1]
        yi = led[2]
        cropped_channel_array_list = []
        channel_sat_list = []
        channel_integral_list = []
        for chanel_array in chanel_array_list:
            cropped_channel_array, channel_sat, channel_integral = get_channel_values_from_array(chanel_array, radius,
                                                                                                 xi, yi)
            cropped_channel_array_list.append(cropped_channel_array)
            channel_sat_list.append(channel_sat)
            channel_integral_list.append(channel_integral)
        cropped_channel_array_list_all.append(cropped_channel_array_list)
        channel_sat_list_all.append(channel_sat_list)
        channel_integral_list_all.append(channel_integral_list)

    return channel_sat_list_all, channel_integral_list_all, cropped_channel_array_list_all

def get_exif_entry(filename, tag):
    with open(filename, 'rb') as f:
        exif = exifread.process_file(f, details=False, stop_tag=tag)
        if f"EXIF {tag}" not in exif:
            raise ValueError("No EXIF entry")
        exif_entry = exif[f"EXIF {tag}"]
    return str(exif_entry)

def get_real_exp_time_from_file(file):
    apex_time_value = Fraction(get_exif_entry(file, "ShutterSpeedValue"))
    real_exp_time = 1 / 2 ** apex_time_value
    return real_exp_time

def get_shutter_speed_from_file(file):
    return Fraction(get_exif_entry(file, "ExposureTime"))
