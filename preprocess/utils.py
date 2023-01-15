import sys

import cv2
import numpy as np


def first_filters(img):

    d = True   # debug (show images)

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # show_image(gray, d, "gray")

    # create an image filled by 255 2x bigger than the original
    img_shape = gray.shape
    img2 = np.ones((img_shape[0] * 2, img_shape[1]
                   * 2), np.uint8) * 255

    # copy img in img2 in a centred position
    x = int(img_shape[0] / 2)
    y = int(img_shape[1] / 2)
    img2[x:x + img_shape[0], y:y + img_shape[1]] = gray
    # show_image(img2, d, "img2")

    # Apply histogram equalization to improve contrast
    equalized = cv2.equalizeHist(img2)
    # show_image(equalized, d, "equalized")

    blur = cv2.GaussianBlur(equalized, (5, 5), 2)

    # Apply a threshold to remove the background
    ret, thresh = cv2.threshold(
        blur, 255, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # show_image(thresh, d, "thresh")

    # apply threshold to remove the background
    img2[thresh == 255] = 0

    # get min_x, min_y, max_x, max_y of the threshold
    min_x = np.min(np.where(thresh == 0)[0])
    min_y = np.min(np.where(thresh == 0)[1])
    max_x = np.max(np.where(thresh == 0)[0])
    max_y = np.max(np.where(thresh == 0)[1])

    # convert back to color
    img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

    # draw an ellipse inside the rectangle
    center_x = int((min_y + max_y) / 2)
    center_y = int((min_x + max_x) / 2)
    major_axis = int((max_y - min_y) / 2)
    minor_axis = int((max_x - min_x) / 2)
    angle = 0
    cv2.ellipse(img2, (center_x, center_y),
                (major_axis, minor_axis), angle, 0, 360, (0, 0, 255), 2)

    show_image(img2, d, "rectangle")

    # apply gaussian blur
    # blur = cv2.GaussianBlur(thresh, (5, 5), 0)
    # show_image(blur, d, "blur")

    # create a all black image
    # black = np.zeros((blur.shape[0], blur.shape[1]), np.uint8)

    # apply this black image to blur with opacity 0.2
    # greyed = cv2.addWeighted(blur, 0.2, black, 0.8, 0)
    # show_image(greyed, d, "greyed")

    return thresh


def debug() -> bool:
    """Return if the debugger is currently active"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None


def show_image(img, debug, name="image"):
    if debug:
        # set windows size to 500x500
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)  # Naming a window
        cv2.moveWindow(name, 0, 0)
        cv2.resizeWindow(name, 1920, 1080)
        cv2.imshow(name, img)
        cv2.waitKey(0)
