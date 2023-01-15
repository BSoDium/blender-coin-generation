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

    # coount number of white pixels of img2 inside the circle (mask == 0)
    nb_in_white = np.count_nonzero(img2[mask == 0] == 255)

    # count number of black pixels outside the mask (mask == 255)
    nb_out_black = np.count_nonzero(img2[mask == 255] == 0)

    nb_total_pixels = height * width

    alpha = 0.5
    beta = 1-alpha

    loss = abs(((
        alpha * (nb_in_white / nb_total_pixels) -
        beta * (nb_out_black / nb_total_pixels)
    )) / 2)

    return (loss)


def print_loss(loss):
    if debug():
        print("Loss: " + str(loss))
