import cv2
import numpy as np
from compute_loss import compute_circle_loss
from utils import debug


def find_circle(img):

    # start with a big circle (radius = width of image, center = center of image)
    radius = int(img.shape[1] / 2)
    center = (int(img.shape[1] / 2), int(img.shape[0] / 2))

    radiu_chgs = [0, -1]
    x_cen_chgs = [0, 1, -1]
    y_cen_chgs = [0, 1, -1]

    nRc = len(radiu_chgs)
    nXc = len(x_cen_chgs)
    nYc = len(y_cen_chgs)

    number_of_changes = nRc * nXc * nYc

    index = 0

    i_old_losses = []
    o_old_losses = []
    old_diff = []

    counter = 0

    while compute_diff(o_old_losses, old_diff) > 0.001 and index != 1 and counter < 100:
        counter += 1

        i_losses = np.zeros(number_of_changes)
        o_losses = np.zeros(number_of_changes)
        i = 0

        for radiu_chg in radiu_chgs:
            for x_cen_chg in x_cen_chgs:
                for y_cen_chg in y_cen_chgs:
                    _rad = radiu_chg + radius
                    _x_cen = x_cen_chg + center[0]
                    _y_cen = y_cen_chg + center[1]

                    circle = (_x_cen, _y_cen, _rad)

                    (i_losses[i], o_losses[i]
                     ) = compute_circle_loss(img, circle, i_old_losses, o_old_losses)

                    # show_circle(img, circle)

                    i += 1

        # find the index which maximizes the inside loss and minimizes the outside loss
        index = np.argmin(o_losses)

        i_old_losses.append(i_losses[index])
        o_old_losses.append(o_losses[index])

        # print("index: " + str(index))

        if (o_old_losses[-1] > o_old_losses[-2]):

            # get the changes
            radiu_chg = radiu_chgs[int((index-1) / (nXc * nYc))]
            x_cen_chg = x_cen_chgs[int(((index-1) % (nXc * nYc)) / nYc)]
            y_cen_chg = y_cen_chgs[int((index-1) % nYc)]

            # print("changes: " + str(radiu_chg) + " " +
            #       str(x_cen_chg) + " " + str(y_cen_chg))

            # apply the changes
            radius += radiu_chg
            center = (center[0] + x_cen_chg, center[1] + y_cen_chg)

    return (center, radius)


def compute_diff(o_old_losses, old_diff):
    nb = 5
    if len(o_old_losses) < nb:
        return nb

    # detect if the last losses is stable
    diff = 0
    for i in range(nb):
        diff += abs(o_old_losses[-i] - o_old_losses[-i-1])

    # if this difference is similar to the n previous differences, then we are stable
    if len(old_diff) < nb:
        old_diff.append(diff)
        return nb

    old_diff.append(diff)

    # compute diff between the last nb+1 differences and diff
    diff = 0
    for i in range(nb):
        diff += abs(old_diff[-i] - old_diff[-i-1])

    print("diff: " + str(diff))

    return diff


def show_circle(img, circle):
    if debug():
        center = (circle[0], circle[1])
        radius = circle[2]

        img2 = img.copy()
        img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

        cv2.circle(img2, center, radius, (0, 255, 0), 2)
        cv2.imshow('img', img2)
        cv2.waitKey(1)
