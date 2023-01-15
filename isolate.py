import os
import cv2
import numpy as np
import pathlib
import logging
import json
from texture import Texture

DIR = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")


def export(image, circle, filepath, edge=None):
    # Get the center and radius of the circle
    x, y, r = circle.astype(int)

    # Create a mask with the circle area
    mask = np.zeros(image.shape[:2], np.uint8)
    cv2.circle(mask, (x, y), r, 255, -1, 8, 0)

    # Set the pixels outside the circle to transparent on a copy of the original image, then crop the image to the circle
    img2 = image.copy()
    img2[mask == 0] = (0, 0, 0, 0)
    crop = img2[y-r:y+r, x-r:x+r]
    texture = Texture(crop, edge=edge)

    # Apply a Gradient from original color to black on the edges of the circle
    gradient = lambda distance, min, max: (distance - min) / (max - min) if distance > min else 0
    for i in range(2*r):
        for j in range(2*r):
            d = np.sqrt((i - r)**2 + (j - r)**2)
            if d > r:
                continue
            g = gradient(d, 0.8*r, r)
            crop[i, j] = crop[i, j] * (1 - g)
    # Apply a linear gradient from original color to black on the edges of the edge texture
    w, h = edge.shape[:2]
    for i in range(w):
        for j in range(h):
            d = abs(i - w / 2)
            g = gradient(d, 0.8*(w / 2), w / 2)
            edge[i, j] = edge[i, j] * (1 - g)
    
    dmap = Texture(crop, edge=edge)

    filepath_no_ext = os.path.splitext(filepath)[0]

    texture.export(f"{filepath_no_ext}.texture.png")
    dmap.export(f"{filepath_no_ext}.dmap.png")


def main(input_folder, output_folder, edges_path):
    # Load edge texture json
    with open(edges_path, "r") as f:
        edges = json.load(f)

    # Loop through all the images in the input folder
    for filename in os.listdir(input_folder):
        # If the filename follows the format {countryCode}_{value}_{particularity (optional)}.{extension} value being a keyof edges.json
        # Example: "be_2euro_2008.jpg" should load the "2euro" edge texture
        edge = None
        metadata = filename.split(".")[0].split("_")
        value = metadata[1] if len(metadata) >= 2 else None
        if value and value in edges.keys():
            # Load the corresponding edge texture
            edge = cv2.imread(f"res/edges/{edges[value]}")
            # Add an alpha channel to the image
            edge = cv2.cvtColor(edge, cv2.COLOR_BGR2BGRA)

        # Load the image using OpenCV
        img = cv2.imread(os.path.join(input_folder, filename))

        # Add a padding around the image and inpaint the edges
        padding = 40
        img = cv2.copyMakeBorder(
            img, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
        mask = np.zeros(img.shape[:2], np.uint8)
        mask[:padding, :] = 255
        mask[-padding:, :] = 255
        mask[:, :padding] = 255
        mask[:, -padding:] = 255
        img = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

        # Add an alpha channel to the image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply histogram equalization to improve contrast
        gray = cv2.equalizeHist(gray)

        # Apply a Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Detect circles using the Hough Transform
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 45, param1=75, param2=80)

        # If no circles were found, skip this image
        if circles is None:
            logging.warning(f"No circles found in {filename}")
            continue

        # Out of all overlapping circles, only keep the biggest ones that don't overlap and are fully inside the image
        coins = []
        for c in circles[0]:
            # Check if the circle overlaps with any of the circles we've already chosen
            if not any((c[0]-c[2] < c2[0]+c2[2] and c[0]+c[2] > c2[0]-c2[2] and c[1]-c[2] < c2[1]+c2[2] and c[1]+c[2] > c2[1]-c2[2]) for c2 in coins) and (c[0]-c[2] > 0 and c[0]+c[2] < img.shape[1] and c[1]-c[2] > 0 and c[1]+c[2] < img.shape[0]):
                # If it doesn't overlap, add it to the list
                coins.append(c)

        # Draw the detected circles on the image
        gray2 = gray.copy()
        if coins is not None:
            for c in coins:
                x, y, r = c.astype(int)
                cv2.circle(gray2, (x, y), r, (255, 255, 255), 2, cv2.LINE_AA)

        # Create the output folder if it doesn't exist
        pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

        # Get the filename without the extension
        filename_no_ext = os.path.splitext(filename)[0]

        # Iterate through the circles
        for c, i in zip(coins, range(len(coins))):
            export(img, c, os.path.join(output_folder, f"{filename_no_ext}-{i}.png"), edge)


if __name__ == "__main__":
    main(f"{DIR}/raw", f"{DIR}/out/cropped", f"{DIR}/res/edges/edges.json")
