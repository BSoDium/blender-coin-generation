import cv2
import numpy as np
from compute_loss import compute_circle_loss
from constants import MAX_ITER
from utils import debug


def find_circle(img):

    # start with a big circle (radius = width of image, center = center of image)
    radius = int(img.shape[1] / 2) - 1
    center = (int(img.shape[1] / 2), int(img.shape[0] / 2))

    radiu_chgs = [0, -1, 1]
    x_cen_chgs = [0, 1, -1]
    y_cen_chgs = [0, 1, -1]

    nRc = len(radiu_chgs)
    nXc = len(x_cen_chgs)
    nYc = len(y_cen_chgs)

    number_of_changes = nRc * nXc * nYc

    index = 0

    old_white_in = []
    old_black_in = []
    old_white_out = []
    old_black_out = []
    old_loss = []

    counter = 0
    flag = 0

    while flag == 0:
        counter += 1

        white_in = np.zeros(number_of_changes)
        black_in = np.zeros(number_of_changes)
        white_out = np.zeros(number_of_changes)
        black_out = np.zeros(number_of_changes)

        i = 0

        for radiu_chg in radiu_chgs:
            for x_cen_chg in x_cen_chgs:
                for y_cen_chg in y_cen_chgs:
                    _rad = radiu_chg + radius
                    _x_cen = x_cen_chg + center[0]
                    _y_cen = y_cen_chg + center[1]

                    circle = (_x_cen, _y_cen, _rad)

                    (white_in[i], black_in[i], white_out[i],
                     black_out[i]) = compute_circle_loss(img, circle)

                    i += 1

        # find the index which maximizes the inside loss and minimizes the outside loss
        alpha = 1.1

        loss = abs(((
            (white_in) / (alpha * black_in) +
            (alpha * black_out) / (white_out)
        )))
        # normalize loss
        loss = loss / np.max(loss)

        options = np.array([{
            "loss": loss[i],
            "index": i,
            "radiu_chg": radiu_chgs[int((i-1) / (nXc * nYc))],
            "x_cen_chg": x_cen_chgs[int(((i-1) % (nXc * nYc)) / nYc)],
            "y_cen_chg": y_cen_chgs[int((i-1) % nYc)]
        } for i in range(1, number_of_changes)])

        # Remove the options which are not inside the image
        is_inside = np.array([(center[0] + option["x_cen_chg"] - (radius + option["radiu_chg"]) >= 0 and
                               center[0] + option["x_cen_chg"] + (radius + option["radiu_chg"]) < img.shape[1] and
                               center[1] + option["y_cen_chg"] - (radius + option["radiu_chg"]) >= 0 and
                               center[1] + option["y_cen_chg"] + (radius + option["radiu_chg"]) < img.shape[0]) for option in options])
        options = options[is_inside]
        losses_inside_circle = [option["loss"] for option in options]
        option_index = np.argmin(losses_inside_circle)

        old_white_in.append(white_in[options[option_index]["index"]])
        old_black_in.append(black_in[options[option_index]["index"]])
        old_white_out.append(white_out[options[option_index]["index"]])
        old_black_out.append(black_out[options[option_index]["index"]])
        old_loss.append(loss[options[option_index]["index"]])

        # print("changes: " + str(radiu_chg) + " " +
        #       str(x_cen_chg) + " " + str(y_cen_chg))
        # print("loss: " + str(loss[options[option_index]["index"]]))
        # print("chgt: " + str(options[option_index]["x_cen_chg"]) + " " +
        #       str(options[option_index]["y_cen_chg"]) + " " + str(options[option_index]["radiu_chg"]))

        # apply the changes
        radius += options[option_index]["radiu_chg"]
        center = (center[0] + options[option_index]["x_cen_chg"],
                  center[1] + options[option_index]["y_cen_chg"])

        # print("counter: " + str(counter) + " loss: " + str(losses[index]))

        show_image(img, black_in[index], white_in[index], black_out[index], white_out[index], loss[index], (center[0], center[1], radius, radius, 0),
                   old_loss, old_black_in, old_white_in, old_black_out, old_white_out)

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


def show_image(img, black_in,  white_in, black_out, white_out, loss, ellipse, old_loss, old_black_in, old_white_in, old_black_out, old_white_out):
    if debug():

        # set windows size to 500x500
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)  # Naming a window
        cv2.resizeWindow("image", 1000, 500)
        # change position of window to 0,0
        cv2.moveWindow("image", 0, 0)

        # convert image to color
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        black_in_f = "{0:.3f}".format(black_in)
        white_in_f = "{0:.3f}".format(white_in)
        black_out_f = "{0:.3f}".format(black_out)
        white_out_f = "{0:.3f}".format(white_out)

        loss_f = "{0:.3f}".format(loss)

        height, width, channels = img.shape

        txtHeight = 50

        center = (ellipse[0], ellipse[1])
        axis = (ellipse[2], ellipse[3])
        angle = ellipse[4]
        cv2.ellipse(img, center, axis, angle, 0, 360, (0, 255, 0), 2)

        # add padding to image
        img = cv2.copyMakeBorder(img, 0, 0, 0, 1200, cv2.BORDER_CONSTANT,
                                 value=[0, 0, 0])

        # add text to image
        # black in
        # white in
        # black out
        # white out
        # loss
        cv2.putText(img, "black in: " + black_in_f, (width, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)    # draw text
        cv2.putText(img, "white in: " + white_in_f, (width, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)    # draw text
        cv2.putText(img, "black out: " + black_out_f, (width, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)    # draw text
        cv2.putText(img, "white out: " + white_out_f, (width, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)    # draw text
        cv2.putText(img, "loss: " + loss_f, (width, 250),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)    # draw text

        # draw rectangle below text
        cv2.rectangle(img, (width, 300), (width + 1200, height),
                      (40, 40, 40), -1)

        # plot graph of losses over time inside the rectangle
        # losses goes from 0 to 1,
        # rectangle height is (height - 200)
        # map losses to rectangle height

        # there can be max 1000 losses, and the rectangle is 1200 pixels wide
        # so we need to plot 1 loss every 50 pixels

        for i in range(len(old_black_in)):
            l_loss = old_loss[i]
            l_loss = int(l_loss * (height - 500))

            x_1 = width + int(i) * 5
            x_2 = width + int((i + 1)) * 5

            # draw line from old_loss to new loss
            cv2.line(img, (x_1, height - 100 - l_loss),
                     (x_2, height - 100 - int(loss * (height - 500))), (255, 255, 0), 2)

        if (len(old_loss) > 1000):
            old_loss.pop(0)
            old_black_in.pop(0)
            old_white_in.pop(0)
            old_black_out.pop(0)
            old_white_out.pop(0)

        cv2.imshow('image', img)
        cv2.waitKey(1)
