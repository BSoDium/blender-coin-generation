import os

import cv2
import numpy as np
from helpers import add_transparency_mask

# this script will create a big image with some coins in it
# it is for illustration purposes only

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = "assets"
OUTPUT_PATH = "out"

assets_path = os.path.join(ROOT, ASSETS_PATH)
output_path = os.path.join(ROOT, OUTPUT_PATH)

x = 8
y = 12

# open the mesh image with transparency
mesh = cv2.imread(assets_path + "/mesh.png", cv2.IMREAD_UNCHANGED)
# get shape
height, width, _ = mesh.shape
# resize it, keep aspect ratio, set width to 100
mesh = cv2.resize(mesh, (100, int(height * 100 / width)))
height, width, _ = mesh.shape
# create an empty image of size (height * y, width * x) with alpha channel
main_image = np.zeros((height * y, width * x, 4), np.uint8)

# for each country
for i in range(y):
    for j in range(x):
        # copy the mesh image to the main image with alpha channel
        main_image[i * height:(i + 1) * height, j *
                   width:(j + 1) * width] = mesh


# add a linear transparency mask
main_image = add_transparency_mask(main_image)

# save image with transparency
cv2.imwrite(output_path + "/mesh.png", main_image)
