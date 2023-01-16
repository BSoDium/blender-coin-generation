import os
from os import listdir
from os.path import isfile, join

import cv2
import numpy as np
from utils import (convert_gif_to_jpg, crop_image, export, get_edge, get_edges,
                   get_ellipse_coords, get_extension, is_image, show_image)

INPUT_PATH = "./raw/"
OUTPUT_PATH = "./out/cropped/"
EDGES_PATH = "./res/edges/edges.json"
NB_OF_TESTS = -1  # -1 for all images, n > 0 for n random images


def main():

    # get all images (.png, .jpg, .jpeg, .bmp, .gif)
    images = [f for f in listdir(INPUT_PATH) if is_image(f)]

    nb_of_images_in_path = len(images)
    nb_of_images = NB_OF_TESTS > 0 and NB_OF_TESTS or nb_of_images_in_path

    edges = get_edges(EDGES_PATH)

    for i in range(nb_of_images):

        # get image name
        if NB_OF_TESTS > 0:
            # if we want to test, then we choose randomly
            image_name = images[np.random.randint(0, nb_of_images_in_path)]
        else:
            # else, read all images in the folder (in order)
            image_name = images[i]

        full_path = join(INPUT_PATH, image_name)

        # if it is an .gif, we convert it to .png
        if get_extension(image_name) == "gif":
            full_path = convert_gif_to_jpg(full_path)

        # read image
        img = cv2.imread(full_path)

        # get coin position and size from image
        coin = get_ellipse_coords(img)

        # crop image
        croped = crop_image(img, coin, -1)

        # show image
        # show_image(img, "output")

        # check if the output folder exists
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)

        # get the corresponding edge texture
        edge = get_edge(image_name, edges)

        # saved it as png with bump texture
        export(croped, image_name, OUTPUT_PATH, edge)

        print("Image {}/{} saved ({})".format(
              str(i + 1), str(nb_of_images), image_name))


if __name__ == "__main__":
    main()
