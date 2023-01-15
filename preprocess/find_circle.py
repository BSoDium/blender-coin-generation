import cv2
import numpy as np
from compute_loss import compute_circle_loss
from constants import MAX_ITER
from utils import debug


def find_circle(img):

    # start with a big circle (radius = width of image, center = center of image)
    radius = int(img.shape[1] / 2)
    center = (int(img.shape[1] / 2), int(img.shape[0] / 2))

    _radius = radius
    _center = center

    radiu_chgs = [0, -1, -2, -3]
    x_cen_chgs = [0, 1, -1]
    y_cen_chgs = [0, 1, -1]

    nRc = len(radiu_chgs)
    nXc = len(x_cen_chgs)
    nYc = len(y_cen_chgs)

    number_of_changes = nRc * nXc * nYc

    index = 0

    old_losses = []

    counter = 0
    flag = 0

    while flag == 0:
        counter += 1

        losses = np.zeros(number_of_changes)
        i = 0

        for radiu_chg in radiu_chgs:
            for x_cen_chg in x_cen_chgs:
                for y_cen_chg in y_cen_chgs:
                    _rad = radiu_chg + radius
                    _x_cen = x_cen_chg + center[0]
                    _y_cen = y_cen_chg + center[1]

                    circle = (_x_cen, _y_cen, _rad)

                    losses[i] = compute_circle_loss(img, circle, old_losses)

                    i += 1

        # find the index which maximizes the inside loss and minimizes the outside loss
        index = np.argmin(losses)

        old_losses.append(losses[index])

        # get the changes
        radiu_chg = radiu_chgs[int((index-1) / (nXc * nYc))]
        x_cen_chg = x_cen_chgs[int(((index-1) % (nXc * nYc)) / nYc)]
        y_cen_chg = y_cen_chgs[int((index-1) % nYc)]

        # print("changes: " + str(radiu_chg) + " " +
        #       str(x_cen_chg) + " " + str(y_cen_chg))

        # apply the changes
        _radius += radiu_chg
        _center = (center[0] + x_cen_chg, center[1] + y_cen_chg)

        # if new_circle is inside the image, not keep it
        is_new_circle_inside = (_center[0] - _radius > 0 and
                                _center[0] + _radius < img.shape[1] and
                                _center[1] - _radius > 0 and
                                _center[1] + _radius < img.shape[0])
        if is_new_circle_inside:
            radius = _radius
            center = _center

        # print("counter: " + str(counter) + " loss: " + str(losses[index]))

        show_image(img, losses[index], (center[0],
                   center[1], radius, radius, 0), old_losses)

    return (center, radius)


def get_flag(count, old_lossses):
    # if the loss is stable, then we are done
    if count > 5:
        diff = compute_diff(old_lossses)
        if diff < 0.1:
            return 1
    if count > MAX_ITER:
        return 2

    return 0


def compute_diff(o_old_losses):
    # compute the difference between the last 5 losses
    old_losses = o_old_losses[-5:]
    diff = 0
    for i in range(len(old_losses) - 1):
        diff += abs(old_losses[i] - old_losses[i+1])

    return diff / 5


def show_image(img, current_losse, ellipse, old_losses):
    if debug():

        # set windows size to 500x500
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)  # Naming a window
        cv2.resizeWindow("image", 1000, 500)
        # change position of window to 0,0
        cv2.moveWindow("image", 0, 0)

        # convert image to color
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        loss_f = "{0:.3f}".format(current_losse)

        height, width, channels = img.shape

        txtHeight = 50

        center = (ellipse[0], ellipse[1])
        axis = (ellipse[2], ellipse[3])
        angle = ellipse[4]
        cv2.ellipse(img, center, axis, angle, 0, 360, (0, 255, 0), 2)

        # add padding to image
        img = cv2.copyMakeBorder(img, 0, 0, 0, 1200, cv2.BORDER_CONSTANT,
                                 value=[0, 0, 0])
        cv2.putText(img, "loss: " + str(loss_f), (width + 10,  txtHeight),
                    cv2.FONT_HERSHEY_SIMPLEX, 2,  (0, 255, 0), 4)

        # draw rectangle below text
        cv2.rectangle(img, (width, 200), (width + 1200, height),
                      (40, 40, 40), -1)

        # plot graph of losses over time inside the rectangle
        # losses goes from 0 to 1,
        # rectangle height is (height - 200)
        # map losses to rectangle height

        # there can be max 1000 losses, and the rectangle is 1200 pixels wide
        # so we need to plot 1 loss every 50 pixels

        for i in range(len(old_losses)):
            i_loss = old_losses[i]
            i_loss = int(i_loss * (height - 200))

            x_1 = width + int(i)
            x_2 = width + int((i + 1))

            cv2.line(img, (x_1, height - i_loss),
                     (x_2, height - i_loss), (0, 255, 0), 1)
        if len(old_losses) > 10000:
            old_losses.pop(0)

        cv2.imshow('image', img)
        cv2.waitKey(1)
