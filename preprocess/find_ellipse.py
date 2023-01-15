import cv2
import numpy as np
from compute_loss import compute_loss_ellipse
from utils import debug


def find_ellipse(img, init_circle):
    # define ellipse
    center_x = init_circle[0][0]
    center_y = init_circle[0][1]
    major_axis = init_circle[1]
    minor_axis = init_circle[1]
    angle = 0

    # matrix of changes 3*3*8: major_axis, minor_axis, angle
    major_axis_changes = [0, 1, -1, -2]
    minor_axis_changes = [0, 1, -1, -2]
    angle_changes = [0, 1, -1, 2, -2, 3, -3, 4, -4]

    nJc = len(major_axis_changes)
    nIc = len(minor_axis_changes)
    nAc = len(angle_changes)

    # number of changes
    number_of_changes = nJc * nIc * nAc

    index = 0

    old_losses = []

    while index != 1:

        losses = np.zeros(number_of_changes)
        i = 0

        for major_axis_chg in major_axis_changes:
            for minor_axis_chg in minor_axis_changes:
                for angle_chg in angle_changes:
                    _major_axis = major_axis + major_axis_chg
                    _minor_axis = minor_axis + minor_axis_chg
                    _angle = angle + angle_chg

                    current_ellipse = (center_x, center_y,
                                       _major_axis, _minor_axis, _angle)

                    losses[i] = compute_loss_ellipse(
                        img, current_ellipse, old_losses)

                    # show_ellipse(img, current_ellipse)

                    i += 1

        # find the index which maximizes the inside loss and minimizes the outside loss
        index = np.argmin(losses)

        old_losses.append(losses[index])

        # get the changes
        idx = index - 1
        a = int(idx / (nIc * nAc))
        b = int((idx % (nIc * nAc)) / nAc)
        c = int(idx % nAc)
        major_axis_chg = major_axis_changes[a]
        minor_axis_chg = minor_axis_changes[b]
        angle_chg = angle_changes[c]

        # apply the changes
        major_axis += major_axis_chg
        minor_axis += minor_axis_chg
        angle = (angle + angle_chg) % 360

        return (center_x, center_y, major_axis, minor_axis, angle)


def show_ellipse(img, ellipse):
    if debug():
        center_x = ellipse[0]
        center_y = ellipse[1]
        major_axis = ellipse[2]
        minor_axis = ellipse[3]
        angle = ellipse[4]

        img2 = img.copy()
        img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

        cv2.ellipse(img2, (center_x, center_y),
                    (major_axis, minor_axis), angle, 0, 360, (0, 0, 255), 2)
        cv2.imshow('img', img2)
        cv2.waitKey(1)


def print_results(index):
    if debug():
        print("chosen index: {}".format(index))
