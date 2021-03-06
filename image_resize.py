import sys
import os
import subprocess
import math
import shutil

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

# compute maximum zoom level
full_filename, tile_size = sys.argv[1:]
filename, extension = os.path.splitext(full_filename)
file_size = subprocess.check_output('identify -format "%wx%h" ' + full_filename)
sizex, sizey = map(int, file_size.split('x'))
max_zoom_level = math.ceil(math.log(max(sizex, sizey) / int(tile_size), 2))
output_dir = filename + "_tiles"
create_dir(output_dir)

i = int(max_zoom_level)
prev_filename = full_filename
for zoom_level in range(i, -1, -1):
    filename_for_zoom_level = "{0}_{1}{2}".format(filename, zoom_level, extension)
    dir_name_for_zoom_level = os.path.join(output_dir, str(zoom_level))
    create_dir(dir_name_for_zoom_level)
    # if we are at max zoom level, there is no need to resize
    if zoom_level == i:
        shutil.copy(prev_filename, filename_for_zoom_level)
    # otherwise, resize image to half
    if not os.path.exists(filename_for_zoom_level):
        subprocess.call(['convert', '-resize', '50%', prev_filename, filename_for_zoom_level], shell=True)
    # tile the image
    tile_args = ['convert', '-limit', 'map', '4GiB', '-limit', 'memory', '2GiB',
        filename_for_zoom_level,
        '-crop', '{0}x{0}'.format(tile_size),
        '-set', 'filename:tile',
        '%[fx:page.x/{0}]_%[fx:page.y/{0}]'.format(tile_size),
        '+repage', '+adjoin',
        '{0}\\tile-%[filename:tile].png'.format(dir_name_for_zoom_level)]
    subprocess.call(tile_args, shell=True)
    prev_filename = filename_for_zoom_level
