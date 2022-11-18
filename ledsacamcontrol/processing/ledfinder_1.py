import numpy as np

def find_search_areas_1(image, window_radius, skip, threshold_factor):
    ### Temp
    width, height = image.shape
    image[:, 0:int(height/3)] = 0
    image[:, int(2/3*height):] = 0
    ### Temp
    print('finding led search areas')
    led_mask = generate_mask_of_led_areas(image, threshold_factor)
    search_areas_list = find_pos_of_max_col_val_per_area(image, led_mask, skip, window_radius)
    print("\nfound {} leds".format(len(search_areas_list)))
    search_areas_array = np.array(search_areas_list)

    return search_areas_array

def generate_mask_of_led_areas(image, threshold_factor):
    im_mean = np.mean(image)
    im_max = np.max(image)
    th = threshold_factor * (im_max - im_mean)
    print("mean pixel value:", im_mean)
    print("max pixel value:", im_max)
    print("Saturation:", im_max/ 2**14) #Todo: Remove hardcoding
    im_set = np.zeros_like(image)
    im_set[image > th] = 1
    return im_set

def find_pos_of_max_col_val_per_area(image, led_mask, skip, window_radius):

    search_areas_list = []
    led_id = 0
    for ix in range(window_radius, image.shape[0] - window_radius, skip):
        for iy in range(window_radius, image.shape[1] - window_radius, skip):
            if led_mask[ix, iy] != 0:
                max_x, max_y = find_led_pos(image, ix, iy, window_radius)
                search_areas_list.append([led_id, max_x, max_y])
                led_id += 1
                remove_led_from_mask(led_mask, ix, iy, window_radius)

                print('.', end='', flush=True)
    return search_areas_list

def find_led_pos(image, ix, iy, radius):
    s = np.index_exp[ix - radius:ix + radius, iy - radius:iy + radius]
    res = np.unravel_index(np.argmax(image[s]), image[s].shape)
    max_x = ix - radius + res[0]
    max_y = iy - radius + res[1]
#     max_x = ix -s_radius-5
#     max_y = iy -s_radius*2
    return max_x, max_y

def remove_led_from_mask(im_set, ix, iy, window_radius):
    im_set[ix - window_radius:ix + window_radius, iy - window_radius:iy + window_radius] = 0

