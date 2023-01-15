import os

import cv2
import numpy as np
from find_circle import find_circle
from find_ellipse import find_ellipse
from utils import first_filters

# IMAGE_NAME = 'ad_2euro_com_2016.jpg'
IMAGE_NAME = 'va_20cents_2013.jpg'
PATH = "./raw/"
DEBUG = True


def main():

    # read image
    full_path = os.path.join(PATH, IMAGE_NAME)

    # get all images (.png, .jpg, .jpeg, .bmp, .gif)
    images = [f for f in os.listdir(PATH) if f.endswith(
        ('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

    number_of_images = len(images)

    nb_of_tests = 1

    images_name = [None] * nb_of_tests
    circles = np.zeros((nb_of_tests, 3), dtype=int)

    # for 10 random images in the folder
    for i in range(nb_of_tests):
        # get random image
        # image_name = images[np.random.randint(0, number_of_images)]
        image_name = IMAGE_NAME
        full_path = os.path.join(PATH, image_name)

        # read image

        img = cv2.imread(full_path)

        # apply first filters to get better results
        img_filtered = first_filters(img)

        # find circle radius and center
        circle = find_circle(img_filtered)

        circles[i] = [int(circle[0][0]), int(circle[0][1]), int(circle[1])]
        images_name[i] = image_name

        # find ellipse parameters
        ellipse = find_ellipse(img_filtered, circle)

        # show results
        # center = (ellipse[0], ellipse[1])
        # radius = (ellipse[2], ellipse[3])
        # angle = ellipse[4]

        # cv2.ellipse(img, center, radius, angle, 0, 360, (0, 255, 0), 2)
        # cv2.imshow('img', img)
        # cv2.waitKey(0)
    # plot each image with its circle in a same window
    for i in range(nb_of_tests):
        image_name = str(images_name[i])
        circle = circles[i]
        full_path = os.path.join(PATH, image_name)
        img = cv2.imread(full_path)
        cv2.circle(img, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
        cv2.imshow('img', img)
        cv2.waitKey(0)


if __name__ == "__main__":
    main()
