import cv2
import numpy as np


def add_transparency_mask(img):
    # apply a linear transparent mask from top to bottom
    # the mask is a 1 channel image, so we need to convert it to 3 channels
    # the mask is used only on the alpha channel

    # get shape
    height, width, _ = img.shape

    # convert img to 4 channels if it is not already
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    h_2_1 = height // 2
    h_2_2 = height - h_2_1

    # create a linear mask
    mask = np.linspace(1, 0, h_2_1)
    # fill the top half of the mask with 1
    mask = np.concatenate((np.ones(h_2_2), mask))
    # duplicate it so it has the same shape as the main image (height * y, width * x)
    mask = np.repeat(mask, width)
    # reshape it to (height * y, width * x, 1)
    mask = mask.reshape((height, width, 1))

    # apply the mask to the alpha channel,
    img[:, :, 3] = img[:, :, 3] * mask[:, :, 0]

    return img


def show_image(img):
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
