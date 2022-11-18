import os.path
import pandas as pd
from ledsacamcontrol.camcalib import Calib
from ledsacamcontrol.processing import get_channel_values_from_file, get_capture_date_time

class TimeSeries(Calib):
    def __init__(self, nchannels=3, shutter_speed='1/1000', local_images=False, label="RGB_LED", intercept=True):
        super().__init__(nchannels=nchannels, shutter_speed=shutter_speed, local_images=local_images)
        self.img_series = None
        self.img_name_string = None

    def set_images_series(self, start, end, limit, skip=0):
        if end < start:
            self.img_series = list(range(start, limit + 1, skip))
            self.img_series.extend(list(range(1, end + 1, skip)))
        else:
            self.img_series = list(range(start, end + 1, 1 + skip))

    def set_img_name_string(self, img_name_string, img_dir='./'):
        self.img_name_string = os.path.join(img_dir, img_name_string)

    def write_channel_values_to_file(self, out_file):
        channel_saturation_list_all = []
        channel_integral_list_all = []
        channel_max_list_all = []
        channel_mean_list_all = []

        time_list = []
        print(f"Processing files")
        for i in self.img_series:
            print(i, end=" ")
            file = self.img_name_string.format(i)
            print(file)
            _, file_type = os.path.splitext(file)
            channel_saturation_list, channel_integral_list, channel_max_list, channel_mean_list, _ = get_channel_values_from_file(file, self.search_areas, self.radius)
            channel_saturation_list_all.append(pd.DataFrame(channel_saturation_list))
            channel_integral_list_all.append(pd.DataFrame(channel_integral_list))
            channel_max_list_all.append(pd.DataFrame(channel_max_list))
            channel_mean_list_all.append(pd.DataFrame(channel_mean_list))
            if file_type in ['.csv', '.txt']:
                time_list.append(file)
            else:
                time_list.append(get_capture_date_time(file))
        for channel_list, prefix in zip([channel_integral_list_all, channel_saturation_list_all, channel_max_list_all, channel_mean_list_all], ["integral", "saturation", "max", "mean"]):
            out_df = pd.concat(channel_list,  keys=time_list)
            out_df.index.names = ["Datetime", "LED_ID"]
            out_df.columns.names = ["Channel"]
            out_df = out_df.reset_index().pivot(index='Datetime', columns=['LED_ID'])
            out_df.to_csv(prefix + "_" + out_file + ".csv")