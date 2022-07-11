import os.path

import numpy as np
import random
from datetime import datetime
from fractions import Fraction
import rawpy
import exifread
from ledsacamcontrol.camcontrol import capture_image_at_shutter_speed


def get_channel_values_at_shutter_speed(shutter_speed, search_areas, radius, file, local_image):
    if local_image == False:
        capture_image_at_shutter_speed(shutter_speed, file)
    channel_saturation_list, channel_integral_list, channel_array_list, _, _ = get_channel_values_from_file(file, search_areas, radius)
    return channel_saturation_list, channel_integral_list, channel_array_list

def get_channel_values_from_array(channel_array, radius, x, y):
    colordepth = 14
    channel_range = 2 ** colordepth - 1
    cropped_channel_array = channel_array[x-radius:x+radius, y-radius:y+radius]
    channel_sat = cropped_channel_array.max()/channel_range
    channel_integral = np.sum(cropped_channel_array)
    channel_mean = np.mean(cropped_channel_array)
    channel_max = np.max(cropped_channel_array)
    return cropped_channel_array, channel_sat, channel_integral, channel_max, channel_mean

def get_channel_arrays_from_file(file, separate_channels = True):
    with rawpy.imread(file) as raw:
        colordepth = 14
        data = raw.raw_image_visible.copy()
        filter_array = raw.raw_colors_visible
        black_level = raw.black_level_per_channel[0]
        channel_range = 2 ** colordepth - 1
        white_level = channel_range # Todo: remove harcoding
        channel_array = data.astype(np.int16) - black_level
        channel_array = (channel_array * (channel_range / (white_level - black_level))).astype(np.int16)
        channel_array = np.clip(channel_array, 0, channel_range)
        if separate_channels == True:
            channel_0_array = np.where(filter_array == 0, channel_array, 0)
            channel_1_array = np.where((filter_array == 1) | (filter_array == 3), channel_array, 0)
            channel_2_array = np.where(filter_array == 2, channel_array, 0)
            return [channel_0_array, channel_1_array, channel_2_array]
        return channel_array

def get_channel_values_from_file(file, search_areas, radius):
    _, file_type = os.path.splitext(file)
    cropped_channel_array_list_all = []
    channel_sat_list_all = []
    channel_integral_list_all = []
    channel_max_list_all = []
    channel_mean_list_all = []

    if file_type in ['.csv', '.txt']:
        chanel_array = get_channel_arrays_from_file_txt(file)
        for led in search_areas:
            xi = led[1]
            yi = led[2]
            cropped_channel_array_list = []
            channel_sat_list = []
            channel_integral_list = []
            channel_max_list = []
            channel_mean_list = []
            cropped_channel_array, channel_sat, channel_integral, channel_max, channel_mean = get_channel_values_from_array(chanel_array, radius,
                                                                                                 xi, yi)
            cropped_channel_array_list.append(cropped_channel_array)
            channel_sat_list.append(channel_sat)
            channel_integral_list.append(channel_integral)
            channel_max_list.append(channel_max)
            channel_mean_list.append(channel_mean)
            cropped_channel_array_list_all.append(cropped_channel_array_list)
            channel_sat_list_all.append(channel_sat_list)
            channel_integral_list_all.append(channel_integral_list)
            channel_max_list_all.append(channel_max_list)
            channel_mean_list_all.append(channel_mean_list)
    else:
        chanel_array_list = get_channel_arrays_from_file(file)
        for led in search_areas:
            xi = led[1]
            yi = led[2]
            cropped_channel_array_list = []
            channel_sat_list = []
            channel_integral_list = []
            channel_max_list = []
            channel_mean_list = []
            for chanel_array in chanel_array_list:
                cropped_channel_array, channel_sat, channel_integral, channel_max, channel_mean = get_channel_values_from_array(chanel_array, radius,                                                                                  xi, yi)
                cropped_channel_array_list.append(cropped_channel_array)
                channel_sat_list.append(channel_sat)
                channel_integral_list.append(channel_integral)
                channel_max_list.append(channel_max)
                channel_mean_list.append(channel_mean)
            cropped_channel_array_list_all.append(cropped_channel_array_list)
            channel_sat_list_all.append(channel_sat_list)
            channel_integral_list_all.append(channel_integral_list)
            channel_max_list_all.append(channel_max_list)
            channel_mean_list_all.append(channel_mean_list)


    return channel_sat_list_all, channel_integral_list_all, channel_max_list_all, channel_mean_list_all, cropped_channel_array_list_all

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

def get_capture_date_time(file):
    capture_time = get_exif_entry(file, "DateTimeOriginal")
    #TODO: Remove fake time miliseconds
    return datetime.strptime(capture_time + f".{random.randint(0, 999)}", '%Y:%m:%d %H:%M:%S.%f')

def get_channel_arrays_from_file_txt(file):
    all_temperatures = []
    with open(file, 'r', encoding='WINDOWS 1252') as ir_file:
        read_data = False
        for line in ir_file:
            if 'Data' in line:
                read_data = True
                continue
            if read_data == True:
                line = line.replace(',', '.')
                line = line.replace(';', ' ')
                line_data = line.split()
                line_temperatures = list(map(float, line_data))
                if line_temperatures:
                    all_temperatures.append(line_temperatures)
        return np.array(all_temperatures)
