import cv2
import numpy as np
from utils import debug


def compute_circle_loss(img, circle, i_old_losses, o_old_losses):

    x_center = circle[0]
    y_center = circle[1]
    radius = circle[2]

    return compute_loss_ellipse(img, (x_center, y_center, radius, radius, 0), i_old_losses, o_old_losses)


def compute_loss_ellipse(img, ellipse, i_old_losses, o_old_losses):

    center = (ellipse[0], ellipse[1])
    axis = (ellipse[2], ellipse[3])
    radius = ellipse[4]

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

    show_image(img2, inside_mean, outside_mean,
               ellipse, i_old_losses, o_old_losses)

    return (inside_mean, outside_mean)


def print_loss(loss):
    if debug():
        print("Loss: " + str(loss))


def show_image(img, inside_mean, outside_mean, ellipse, i_old_losses, o_old_losses):
    if debug():
        i_old_losses.append(inside_mean)
        o_old_losses.append(outside_mean)

        # make window maximized
        cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)

        # convert image to color
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # add loss text to image
        # format loss to 3 decimals
        diff_mean = "{0:.3f}".format(inside_mean - outside_mean)
        inside_mean = "{0:.3f}".format(inside_mean)
        outside_mean = "{0:.3f}".format(outside_mean)

        height, width, channels = img.shape

        txtHeight = 50

        center = (ellipse[0], ellipse[1])
        axis = (ellipse[2], ellipse[3])
        angle = ellipse[4]
        cv2.ellipse(img, center, axis, angle, 0, 360, (0, 255, 0), 2)

        # add padding to image
        img = cv2.copyMakeBorder(img, 0, 0, 0, 500, cv2.BORDER_CONSTANT,
                                 value=[0, 0, 0])
        cv2.putText(img, "iLoss: " + str(inside_mean), (width + 10,  txtHeight),
                    cv2.FONT_HERSHEY_SIMPLEX, 2,  (0, 255, 0), 4)
        cv2.putText(img, "oLoss: " + str(outside_mean), (width + 10, 2 * txtHeight),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        cv2.putText(img, "dLoss: " + str(diff_mean), (width + 10,  3 * txtHeight),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (43, 57, 192), 4)

        # draw rectangle below text
        cv2.rectangle(img, (width, 4*txtHeight), (width + 500, height),
                      (40, 40, 40), -1)

        # plot graph of losses over time inside the rectangle
        # losses goes from 0 to 255,
        # rectangle height is (height - 4*txtHeight)
        # map losses to rectangle height

        # there can be max 1000 losses, and the rectangle is 500 pixels wide
        # so we need to plot 1 loss every 50 pixels

        for i in range(len(i_old_losses)):
            i_loss = i_old_losses[i]
            o_loss = o_old_losses[i]
            i_loss = int(i_loss * (height - 4 * txtHeight) / 255)
            o_loss = int(o_loss * (height - 4 * txtHeight) / 255)

            x_1 = width + int(i / 5)
            x_2 = width + int((i + 1) / 5)

            cv2.line(img, (x_1, height - i_loss),
                     (x_2, height - i_loss), (0, 255, 0), 1)
            cv2.line(img, (x_1, height - o_loss),
                     (x_2, height - o_loss), (0, 0, 255), 1)
        if len(i_old_losses) > 10000:
            i_old_losses.pop(0)
            o_old_losses.pop(0)

        cv2.imshow('image', img)
        cv2.waitKey(1)
