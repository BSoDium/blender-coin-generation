import cv2
import numpy as np
from utils import debug


def compute_circle_loss(img, circle):

    x_center = circle[0]
    y_center = circle[1]
    radius = circle[2]

    return compute_loss_ellipse(img, (x_center, y_center, radius, radius, 0))


def compute_loss_ellipse(img, ellipse):

    center = (ellipse[0], ellipse[1])
    axis = (ellipse[2], ellipse[3])
    radius = ellipse[4]

    # shape of img
    height, width = img.shape

    # create a mask with the ellipse area
    mask = np.zeros(img.shape[:2], np.uint8)
    cv2.ellipse(mask, center, axis, radius, 0, 360, 255, -1)

    # revert the mask
    mask = cv2.bitwise_not(mask)

    # remove this mean to each pixel color (outside the circle)
    img2 = img.copy()

    nb_total_pixels = height * width

    # number of pixels inside the circle
    nb_in = np.count_nonzero(mask == 0)

    # number of pixels outside the circle
    nb_out = np.count_nonzero(mask == 255)

    # coount number of white pixels of img2 inside the circle (mask == 0)
    nb_in_white = np.count_nonzero(img2[mask == 0] == 255) / nb_total_pixels

    # count number of black pixels inside the circle (mask == 0)
    nb_in_black = np.count_nonzero(img2[mask == 0] == 0) / nb_total_pixels

    # count number of white pixels outside the circle (mask == 255)
    nb_out_white = np.count_nonzero(img2[mask == 255] == 255) / nb_total_pixels

    # count number of black pixels outside the circle (mask == 255)
    nb_out_black = np.count_nonzero(img2[mask == 255] == 0) / nb_total_pixels

    return (nb_in_white, nb_in_black, nb_out_white, nb_out_black)


def print_loss(loss):
    if debug():
        print("Loss: " + str(loss))
