import numpy as np
import cv2
from scipy.spatial import distance
from numpy.linalg import norm

def find_search_areas_2(gs_image: np.ndarray, radius: int, max_n_leds: int, percentile, ignore_edge_leds):
    """
    Finds LEDs on grayscale image by a maximum pixel search.
    """
    # Edges of the image can be ignored by setting to zero values
    if ignore_edge_leds == True:
        stancer = np.zeros(gs_image.shape)
        stancer[2 * radius:- 2 * radius, 2 * radius:- 2 * radius] = 1
        gs_image = gs_image * stancer

    # Local maximum values and surrounding areas in gs_image are set to zeroes until max_n_leds is reached
    # or maximum values falls below defined threshold
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gs_image)
    threshold = np.percentile(gs_image, percentile)
    search_areas_list = []
    max_val_list = []
    print("Threshold pixel value:", threshold)
    print("Searching LEDs")
    led_id = 0
    while maxVal > threshold and len(search_areas_list) < max_n_leds:
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gs_image)
        if maxVal > threshold:
            gs_image[maxLoc[1] - radius: maxLoc[1] + radius, maxLoc[0] - radius: maxLoc[0] + radius] = 0
            search_areas_list.append([led_id, maxLoc[1], maxLoc[0]])
            max_val_list.append(maxVal)
            print('.', end='', flush=True)
        led_id +=1
    print('\n')
    print(f"Found {len(search_areas_list)} LEDS!")
    print("Max values of last three LEDs:", *max_val_list[-3:])
    search_areas_array = np.array(search_areas_list)

    return search_areas_array


# def _find_closest_node(node: tuple, nodes_dict: dict) -> 'to be defined':
#     node = np.array(node)
#     nodes = np.array(list(nodes_dict.values()))
#     keys = np.array(list(nodes_dict.keys()))
#     distance_array = distance.cdist([node], nodes)
#     closest_index = distance_array.argmin()
#     dist = distance_array[0][closest_index]
#     return nodes[closest_index], keys[closest_index], dist
#
#
# def plot_leds(image, search_areas_dict, led_line_dict, radius, crop=False):
#     fig, ax = plt.subplots()
#     plt.imshow(image, cmap='Greys')
#     color_cycle = ax._get_lines.prop_cycler
#     patches = []
#     for led_line, led_id_list in led_line_dict.items():
#         color = next(color_cycle)['color']
#         for led_id in led_id_list:
#             led_loc = search_areas_dict[led_id]
#             circle = plt.Circle(led_loc, radius, facecolor='none', edgecolor=color, linewidth=0.1, alpha=0.5)
#             ax.add_patch(circle)
#             ax.text(led_loc[0], led_loc[1], led_id, font=font, color=color)
#         patches.append(circle)
#     plt.legend(patches, list(range(len(patches))))
#
#     if crop == True:
#         loc_array = np.array(list(search_areas_dict.values()))
#         min_x = loc_array[:, 0].min() - 3 * radius
#         max_x = loc_array[:, 0].max() + 3 * radius
#         max_y = loc_array[:, 1].min() - 3 * radius
#         min_y = loc_array[:, 1].max() + 3 * radius
#         plt.xlim(min_x, max_x)
#         plt.ylim(min_y, max_y)
#
#     if len(led_line_dict) > 1:
#         suf = 'lines'
#     else:
#         suf = 'search_areas'
#     plt.savefig(f'led_{suf}.pdf')
#
# def reorder_leds(search_areas_dict: dict, all_led_lines_dict: dict):
#     """
#     Reorder LEDs
#     """
#     search_areas_dict = search_areas_dict.copy()
#     all_led_lines_dict = all_led_lines_dict.copy()
#     last_led_id = 0
#     all_led_lines_dict_sorted = {}
#     for key, value in all_led_lines_dict.items():
#         n_leds_in_line = len(value)
#         led_id_list = list(range(last_led_id, n_leds_in_line + last_led_id))
#         all_led_lines_dict_sorted[key] = led_id_list
#         last_led_id = last_led_id + n_leds_in_line
#
#     led_ids = []
#     led_ids_sorted = []
#
#     for led_id in all_led_lines_dict.values():
#         led_ids.extend(led_id)
#     for led_id in all_led_lines_dict_sorted.values():
#         led_ids_sorted.extend(led_id)
#
#     search_areas_dict_sorted = {}
#     for led_id_old, led_id_new in zip(led_ids, led_ids_sorted):
#         search_areas_dict_sorted[led_id_new] = search_areas_dict[led_id_old]
#     print("LEDs have been reordered!\n")
#     return search_areas_dict_sorted, all_led_lines_dict_sorted
#
#
# def assign_leds_to_lines(search_areas_dict: dict, all_ref_led_id_list: list, max_n_neighbours=5,
#                          distance_weighting_factor=0.99) -> dict:
#     """
#     Assigns led_ids to led_arrays by means of defined reference led_ids.
#      Reference led_ids are defined as a list of lists in `all_ref_led_id_list`
#     """
#     search_areas_dict = search_areas_dict.copy()
#     all_led_lines_dict = {}
#     for led_line_id, ref_led_id_list in enumerate(all_ref_led_id_list):
#         led_line_list = []
#         ref_led_id_iter = iter(ref_led_id_list)
#         led_id = next(ref_led_id_iter)
#         ref_led_id = next(ref_led_id_iter)
#         led_loc = search_areas_dict[led_id]
#         ref_led_loc = search_areas_dict[ref_led_id]
#
#         while len(search_areas_dict) > 0:
#             del search_areas_dict[led_id]
#             search_areas_dict_temp = search_areas_dict.copy()
#             led_line_list.append(led_id)
#             neighbours_led_id_list = []
#             neighbours_dist_list = []
#
#             n_neighbours = min(max_n_neighbours, len(search_areas_dict))
#
#             # Compute distances from current led to nearest neighbour leds
#             for i in range(n_neighbours):
#                 neighbour_led_loc, neighbour_led_id, dist_neighbour = _find_closest_node(led_loc,
#                                                                                          search_areas_dict_temp)
#                 del search_areas_dict_temp[neighbour_led_id]
#                 neighbours_led_id_list.append(neighbour_led_id)
#                 neighbours_dist_list.append(dist_neighbour)
#             total_dist_dict = {}
#
#             # Compute total distance from current led to neighbour leds and from neighbour led to ref led
#             # Distance from neighbour led to ref led is weighted less to prefer leds closer to current led
#             for neighbour_led_id, dist_neighbour in zip(neighbours_led_id_list, neighbours_dist_list):
#                 neighbour_led_loc = search_areas_dict[neighbour_led_id]
#                 dist_ref = np.linalg.norm(np.array(ref_led_loc) - np.array(neighbour_led_loc))
#                 dist_total = distance_weighting_factor * dist_ref + dist_neighbour
#                 total_dist_dict[neighbour_led_id] = dist_total
#             led_id = min(total_dist_dict, key=total_dist_dict.get)
#             led_loc = search_areas_dict[led_id]
#
#             # If last led_id of led_line is reached go to next one
#             if led_id == ref_led_id_list[-1]:
#                 led_line_list.append(led_id)
#                 del search_areas_dict[led_id]
#                 break
#             elif led_id == ref_led_id:
#                 ref_led_id = next(ref_led_id_iter)
#                 ref_led_loc = search_areas_dict[ref_led_id]
#
#         all_led_lines_dict[led_line_id] = led_line_list
#     print(f"Number of not matched LEDs: {len(search_areas_dict)}")
#     print("LED IDs:")
#     for led_id in search_areas_dict:
#         print(led_id, end=" ")
#     print("\n")
#     return all_led_lines_dict
#
# def generate_line_indices_files(led_line_dict: dict, filename_extension=''):
#     for line, led_ids_list in led_line_dict.items():
#         filename = os.path.join('analysis',f'line_indices_{line:03}.csv')
#         out_file = open(filename, 'w')
#         for iled in led_ids_list:
#             out_file.write('{}\n'.format(iled))
#         print(f"{filename} written!")
#         out_file.close()
#
# def write_search_areas_to_file(search_areas_dict):
#     """
#     finds all LEDs in a single image file and defines the search areas, in
#     which future LEDs will be searched
#     """
#     search_areas = []
#     for led_id, search_area in search_areas_dict.items():
#         search_areas.append([led_id, search_area[0], search_area[1]])
#
#     np.savetxt('led_search_areas.csv', search_areas, delimiter=',',
#                header='LED id, pixel position x, pixel position y', fmt='%d')
#
#
#
# radius = 10
# # percentile = 99.92
# percentile = 99.9
#
# # max_n_leds = 1500
# max_n_leds = 2000
# n_neighbours = 3
#
# file = '/Users/kristianboerger/working_files/ledsa_test_images/led_finder/220323_V002_canon_1_1361.CR2'
# # all_ref_led_id_list = [[240, 193], [1350, 1278], [826, 814], [734, 1151], [504, 738], [987, 1139], [1557, 1414],
# #                        [326, 651], [434, 273, 222], [1572, 1475], [993, 937]]  # 220323_V002_canon_1_1361.CR2
# # all_ref_led_id_list = [
# #     [75, 509],
# #     [380, 568],
# #     [606, 619],
# #     [171, 549],
# #     [698, 682],
# #     [813, 1080],
# #     [910, 1114],
# #     [763, 1117]
# # ]
#
# all_ref_led_id_list = [
#     [293, 184],
#     [32, 292],
#     [651, 580],
#     [98, 590],
#     [824, 812],
#     [182, 589],
#     [983, 955]
# ]
#
# # file = '/Volumes/N-1/22_04_27/V005/canon_1/220427_V005_canon_1_1.CR2'
# # os.chdir('/Users/kristianboerger/working_files/ledsa/LEDSA_vs_DOM/V005/canon_1')
# # file = '/Users/kristianboerger/Desktop/experimente/canon_1/IMG_9509.CR2'
# # file = '/Users/kristianboerger/working_files/ledsa/image_data/V001/Cam_01/181127_v001_cam01_46.CR2'
# gs_image = get_channel_arrays_from_file(file, separate_channels=False)
# search_areas_dict = find_search_areas_2(gs_image, radius, max_n_leds, percentile=percentile)
# led_line_dict = {0: range(len(search_areas_dict))}
# plot_leds(gs_image, search_areas_dict, led_line_dict, radius, crop=True)
#
# led_line_dict = assign_leds_to_lines(search_areas_dict, all_ref_led_id_list, max_n_neighbours=n_neighbours)
# search_areas_dict, led_line_dict = reorder_leds(search_areas_dict, led_line_dict)
# plot_leds(gs_image, search_areas_dict, led_line_dict, radius, crop=True)
# generate_line_indices_files(led_line_dict)
# write_search_areas_to_file(search_areas_dict)
