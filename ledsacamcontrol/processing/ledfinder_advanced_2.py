import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.patches as mpatches
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import rawpy
import cv2
from scipy.spatial import distance
from numpy.linalg import norm

font = {'family' : 'monospace',
        'weight' : 'ultralight',
        'size'   : 1}

def find_search_areas_advanced_2(gs_image, window_radius, max_n_leds, percentile, z_pixel_offset):
    size_x, size_y = gs_image.shape

    border_width = window_radius
    empty_image = np.zeros_like(gs_image)
    empty_image[border_width: size_x - border_width, border_width: size_y - border_width] = gs_image[
                                                                                            border_width: size_x - border_width,
                                                                                            border_width: size_y - border_width]
    image = empty_image
    # plt.imshow(image)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(image)

    mean = np.mean(image)
    quantile = np.percentile(image, percentile)
    search_areas_list = []
    max_val_list = []
    print("Mean", mean)
    print("Quantile", quantile)
    print("Searching LEDs")
    led_id = 0
    while maxVal > quantile and len(search_areas_list) < max_n_leds:
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(image)
        # print(minVal, maxVal, minLoc, maxLoc)
        image[maxLoc[1] - window_radius: maxLoc[1] + window_radius, maxLoc[0] - window_radius: maxLoc[0] + window_radius] = 0
        search_areas_list.append([led_id, maxLoc[1], maxLoc[0]])
        max_val_list.append(maxVal)
        print('.', end='', flush=True)
        led_id += 1
    search_areas = np.array(search_areas_list)
    print('\n')
    print(f"Found {len(search_areas_list)} LEDS!")
    print(f"Max value of last LED is {maxVal}")
    if z_pixel_offset is not None:
        search_areas[:,1] += z_pixel_offset

    return search_areas



