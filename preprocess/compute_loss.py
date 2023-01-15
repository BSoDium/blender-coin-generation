import cv2
import numpy as np
from utils import debug


def compute_circle_loss(img, circle, old_losses):

    x_center = circle[0]
    y_center = circle[1]
    radius = circle[2]

    return compute_loss_ellipse(img, (x_center, y_center, radius, radius, 0), old_losses)


def compute_loss_ellipse(img, ellipse, old_losses):

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

    # compute the mean of the pixels that are in the mask
    mean = np.mean(img[mask == 255])

    # remove this mean to each pixel color (outside the circle)
    img2 = img.copy()
    img2[mask == 255] = img2[mask == 255] - mean

    # compute mean of the pixels that are inside the circle
    inside_mean = np.mean(img2[mask == 0])

    # compute the mean of pixels that are outside the circle
    outside_mean = np.mean(img2[mask == 255])

    nb_of_out_pixels = np.count_nonzero(img2[mask == 255])

    # compute the loss
    # loss = (inside_mean / 255 - outside_mean / 255) / 2
    # loss = outside_mean / 255
    alpha = 0.6
    beta = 1-alpha

    loss = ((
        alpha * (outside_mean / 255) -
        beta * (nb_of_out_pixels / (height * width))
    )) / 2

    return (loss)


def print_loss(loss):
    if debug():
        print("Loss: " + str(loss))
