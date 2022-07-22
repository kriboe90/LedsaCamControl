import numpy as np
import rawpy
import time
import matplotlib.pyplot as plt
from skimage import measure
# import cv2
# def find_search_areas_advanced(image, window_radius, n_leds, exclude_radius, reorder=True):
#     print('finding led search areas')
#     radius = max(window_radius, exclude_radius)
#     search_areas = []
#     mask = np.zeros_like(image)
#     x_shape = image.shape[0]
#     y_shape = image.shape[1]
#     for i in range(n_leds):
#         max_pixel_position = np.where(image == image.max())
#         start_x = max(max_pixel_position[0][0] - exclude_radius, 0)
#         end_x = min(max_pixel_position[0][0] + exclude_radius, x_shape)
#         start_y = max(max_pixel_position[1][0] - exclude_radius, 0)
#         end_y = min(max_pixel_position[1][0] + exclude_radius, y_shape)
#         mask[start_x : end_x, start_y : end_y] =1
#         image = np.ma.masked_where(mask==1, image)
#         search_areas.append([i, max_pixel_position[0][0], max_pixel_position[1][0]])
#     search_areas = np.array(search_areas)
#     if reorder == True:
#         order = np.argsort(search_areas[:, 1])
#         search_areas = search_areas[order]
#         search_areas[:,0] = range(search_areas.shape[0])
#     return search_areas

# def find_search_areas_advanced(image, window_radius, n_leds, exclude_radius, reorder=True):
#     start = time.time()
#     print('finding led search areas')
#     radius = max(window_radius, exclude_radius)
#     search_areas = []
#     mask = np.zeros_like(image)
#     x_shape = image.shape[0]
#     y_shape = image.shape[1]
#     th = 2 * np.mean(image)
#     image_masked = np.ma.masked_where(image < th, image)
#     # image_masked = np.where(image<0.5*th, 1, 0)
#     # plt.imshow(image_masked)
#     # plt.colorbar()
#     # plt.show()
#     for i in range(n_leds):
#         image_masked = np.where(mask==0, image_masked, 0)
#         max_pixel_position = np.where(image == image.max())
#         max_pixel_x = max_pixel_position[0][0]
#         max_pixel_y = max_pixel_position[1][0]
#         start_x = max(max_pixel_x - exclude_radius, 0)
#         end_x = min(max_pixel_x + exclude_radius, x_shape)
#         start_y = max(max_pixel_y - exclude_radius, 0)
#         end_y = min(max_pixel_x + exclude_radius, y_shape)
#
#         mask[start_x : end_x, start_y : end_y] =1
#         search_areas.append([i, max_pixel_x, max_pixel_y])
#     search_areas = np.array(search_areas)
#     if reorder == True:
#         order = np.argsort(search_areas[:, 1])
#         search_areas = search_areas[order]
#         search_areas[:,0] = range(search_areas.shape[0])
#         print(time.time()-start)
#     return search_areas

def find_search_areas_advanced(image, window_radius, n_leds, exclude_width, exclude_height, n_strips, strip_width, reorder=True, z_pixel_offset = None, border_width = None):
    widht =  strip_width
    strip_area_start_list = []
    strip_area_list = []
    strip_area_mask = np.zeros_like(image)
    size_x, size_y = image.shape
    if border_width is not None:
        empty_image = np.zeros_like(image)
        empty_image[border_width: size_x-border_width, border_width: size_y-border_width] = image[border_width: size_x-border_width, border_width: size_y-border_width]
        image = empty_image
    image_masked = image
    print(f"{n_strips} strips")
    print(f"Shape: {image.shape}")

    for strip in range(n_strips):
        max_value = image_masked.max()
        max_pixel_position = np.where(image_masked == max_value)
        max_pixel_position_x = max_pixel_position[1][0]
        max_pixel_position_y = max_pixel_position[0][0]
        print(f"Max X: {max_pixel_position_x}, Max Y: {max_pixel_position_y}, Max Value: {max_value}")
        strip_area = image_masked[:, max_pixel_position_x-widht : max_pixel_position_x+widht]
        strip_area_mask[:, max_pixel_position_x-widht : max_pixel_position_x+widht] = 1
        image_masked = np.where(strip_area_mask==0, image_masked, 0)
        strip_area_x_start = max_pixel_position_x-widht
        strip_area_start_list.append(strip_area_x_start)
        strip_area_list.append(strip_area)
    strip_area_list = np.array(strip_area_list)
    strip_area_indices = np.argsort(strip_area_start_list)
    strip_area_start_list.sort()
    reduced_image = np.concatenate(strip_area_list[strip_area_indices], axis=1)

    print('finding led search areas')
    # radius = max(window_radius, exclude_radius)
    search_areas_local = []
    mask = np.zeros_like(reduced_image)
    x_shape = image.shape[0]
    y_shape = image.shape[1]
    image = reduced_image
    for i in range(n_leds):
        max_pixel_position = np.where(image == image.max())
        start_x = max(max_pixel_position[0][0] - exclude_height, 0)
        end_x = min(max_pixel_position[0][0] + exclude_height, x_shape)
        start_y = max(max_pixel_position[1][0] - exclude_width, 0)
        end_y = min(max_pixel_position[1][0] + exclude_width, y_shape)
        mask[start_x : end_x, start_y : end_y] =1
        image = np.ma.masked_where(mask==1, image)
        search_areas_local.append([i, max_pixel_position[0][0], max_pixel_position[1][0]])
        print('.', end='', flush=True)

    print('Calculating global coordinates ...\n')
    # plt.imshow(mask)
    # plt.show()
    real_x_list = []
    for led in search_areas_local:
        x = led[2]
        strip_id = int(x / (widht * 2))
        real_x = strip_area_start_list[strip_id] + x - strip_id * 2 * widht
        real_x_list.append(real_x)
    real_x_coordinates = np.atleast_2d(real_x_list).T
    search_areas_local = np.array(search_areas_local)[:, 0:2]


    # search_areas = np.array(search_areas)
    print(f"{n_leds} LEDs found!")
    search_areas_global = np.concatenate((search_areas_local, real_x_coordinates), axis=1)
    if reorder == True:
        order = np.argsort(search_areas_global[:, 1])
        search_areas = search_areas_global[order]
        search_areas[:,0] = range(search_areas_global.shape[0])
    else:
        search_areas = search_areas_global

    if z_pixel_offset is not None:
        search_areas[:,1] += z_pixel_offset
    return search_areas


