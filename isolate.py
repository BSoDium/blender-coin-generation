import os
import cv2
import numpy as np
import pathlib
import logging
import json
import re

DIR = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")


def main(input_folder, output_folder, edges_path):
    # Load edge texture json
    with open(edges_path, "r") as f:
        edges = json.load(f)

    # Loop through all the images in the input folder
    for filename in os.listdir(input_folder):
        # If the filename follows the format {countryCode}_{value}_{particularity (optional)}.{extension} value being a keyof edges.json
        edge = None
        m = re.search(r"(\w+)_(\w+)(?:_(\w+))?\.\w+", filename)
        value = m.group(2)
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

        # Iterate through the circles
        for c, i in zip(coins, range(len(coins))):

            # Get the center and radius of the circle
            x, y, r = c.astype(int)

            # Create a mask with the circle area
            mask = np.zeros(img.shape[:2], np.uint8)
            cv2.circle(mask, (x, y), r, 255, -1, 8, 0)

            # Set the pixels outside the circle to transparent on a copy of the original image
            img2 = img.copy()
            img2[mask == 0] = (0, 0, 0, 0)

            # Crop the image to the circle
            crop = img2[y-r:y+r, x-r:x+r]

            # Get the filename without the extension
            name = os.path.splitext(filename)[0]

            # Create a new image with the correct size for the texture
            texture = np.zeros((r*4, r*4, 4), np.uint8)

            # Copy the cropped image to the lower left corner of the texture
            texture[r*2:, :r*2] = crop

            # Calculate the average color of the cropped image
            avg_color = np.mean(crop, axis=(0, 1))

            # Fill a circle with the average color in the lower right corner of the texture
            cv2.circle(texture, (r*3, r*3), r, avg_color, -1, 8, 0)

            # If the edge texture was loaded, resize it and copy it to the upper half of the texture
            if edge is not None:
                texture[:r*2, :r*4] = cv2.resize(edge, (r*4, r*2))

            # Save the texture
            cv2.imwrite(os.path.join(output_folder,
                        f"{name}-{i}.texture.png"), texture)


if __name__ == "__main__":
    main(f"{DIR}/raw", f"{DIR}/out/cropped", f"{DIR}/res/edges/edges.json")
