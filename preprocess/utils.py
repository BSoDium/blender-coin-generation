import sys

import cv2
import numpy as np


def first_filters(img):
    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply histogram equalization to improve contrast
    equalized = cv2.equalizeHist(gray)

    # apply gaussian blur
    blur = cv2.GaussianBlur(equalized, (5, 5), 0)

    # create a all black image
    # black = np.zeros((blur.shape[0], blur.shape[1]), np.uint8)

    # apply this black image to blur with opacity 0.2
    # greyed = cv2.addWeighted(blur, 0.2, black, 0.8, 0)

    return blur


def debug() -> bool:
    """Return if the debugger is currently active"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None


def show_image(img, name="image"):
    if debug():
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
