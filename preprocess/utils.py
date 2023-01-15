import sys

import cv2
import numpy as np


def first_filters(img):

    d = False   # debug (show images)

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    show_image(gray, d, "gray")

    # create an image filled by 255 2x bigger than the original
    img_shape = gray.shape
    img2 = np.ones((img_shape[0] * 2, img_shape[1]
                   * 2), np.uint8) * 255

    # copy img in img2 in a random position (but not too close to the borders)
    x = np.random.randint(0, img_shape[0] / 2)
    y = np.random.randint(0, img_shape[1] / 2)
    img2[x:x + img_shape[0], y:y + img_shape[1]] = gray
    show_image(img2, d, "img2")

    # Apply histogram equalization to improve contrast
    equalized = cv2.equalizeHist(img2)
    show_image(equalized, d, "equalized")

    # Apply a threshold to remove the background
    ret, thresh = cv2.threshold(
        equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    show_image(thresh, d, "thresh")

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
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
