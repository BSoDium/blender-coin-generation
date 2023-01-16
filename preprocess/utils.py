import sys

import cv2
import imageio
import numpy as np
from constant import IMAGE_EXTENSION


def get_ellipse_coords(img):

    d = True   # debug (show images)

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_shape = gray.shape

    # create an image filled by 255 2x bigger than the original
    img2 = np.ones((img_shape[0] * 2, img_shape[1]
                   * 2), np.uint8) * 255

    # copy img in img2 in a centred position
    x = int(img_shape[0] / 2)
    y = int(img_shape[1] / 2)
    img2[x:x + img_shape[0], y:y + img_shape[1]] = gray

    # Apply histogram equalization to improve contrast
    equalized = cv2.equalizeHist(img2)

    # Apply gaussian blur to remove noise
    blur = cv2.GaussianBlur(equalized, (5, 5), 2)

    # Apply a threshold to remove the background
    ret, thresh = cv2.threshold(
        blur, 255, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # get min_x, min_y, max_x, max_y of the threshold
    min_x = np.min(np.where(thresh == 0)[0])
    min_y = np.min(np.where(thresh == 0)[1])
    max_x = np.max(np.where(thresh == 0)[0])
    max_y = np.max(np.where(thresh == 0)[1])

    # get ellipse coords
    center_x = int((min_y + max_y) / 2)
    center_y = int((min_x + max_x) / 2)
    major_axis = int((max_y - min_y) / 2)
    minor_axis = int((max_x - min_x) / 2)
    angle = 0

    # transpose ellipse coords into the original image
    center_x -= y
    center_y -= x

    return ((center_x, center_y, major_axis, minor_axis, angle))


def crop_image(img, ellipse, size):
    """Crop the image to the ellipse, resize it to size*size, if size == -1, size will be the max of the input image"""
    center_x, center_y, major_axis, minor_axis, angle = ellipse

    # get image size
    if (size == -1):
        # if we want to crop the image to the ellipse
        # we need to resize it to the original size
        size = max(img.shape[0], img.shape[1])

    # get an ellipse mask
    mask = np.zeros(img.shape, np.uint8)
    mask = cv2.ellipse(mask, (center_x, center_y),
                       (major_axis, minor_axis), angle, 0, 360, (255, 255, 255), -1)
    # apply the mask to the image
    img = cv2.bitwise_and(img, mask)

    # remove the black borders by cropping the image arround the ellipse
    min_x = np.min(np.where(mask == 255)[0])
    min_y = np.min(np.where(mask == 255)[1])
    max_x = np.max(np.where(mask == 255)[0])
    max_y = np.max(np.where(mask == 255)[1])
    img = img[min_x:max_x, min_y:max_y]

    # resize the image to a square (it will stretch the image)
    img = cv2.resize(img, (size, size))

    # add alpha channel to remove background
    img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # remove background
    img[np.all(img == [0, 0, 0, 255], axis=2)] = [0, 0, 0, 0]

    return img


def debug() -> bool:
    """Return if the debugger is currently active"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None


def show_image(img, name="image"):
    if debug():
        # set windows size to 500x500
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)  # Naming a window
        cv2.moveWindow(name, 0, 0)
        cv2.resizeWindow(name, 1920, 1080)
        cv2.imshow(name, img)
        cv2.waitKey(0)


def is_image(file_name: str) -> bool:
    """Return if the file is an image"""
    return file_name.endswith(IMAGE_EXTENSION)


def get_extension(file_name: str) -> str:
    """Return the extension of the file"""
    return file_name.split(".")[-1]


def remove_extension(file_name: str) -> str:
    """Return the file name without the extension"""
    return ".".join(file_name.split(".")[:-1])


def convert_gif_to_jpg(file_name):
    """Convert a gif image to jpg"""
    # convet gif to jpg (opencv can't read gif, according to Copilot)

    # read the gif
    gif = imageio.mimread(file_name)
    # output folder
    output_path = file_name.replace(".gif", ".png")
    # get only the first frame
    imageio.imwrite(output_path, gif[0])

    return output_path
