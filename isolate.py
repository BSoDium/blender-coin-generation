import os
import cv2
import numpy as np
import pathlib
import logging
import json
import re

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

        # Add an alpha channel to the image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)


        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Boost the dominant color
        gray = cv2.equalizeHist(gray)

        # Apply a Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (15, 15), 0)

        # Add a padding of 40 pixels around the image
        gray = cv2.copyMakeBorder(gray, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
        img = cv2.copyMakeBorder(img, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))

        # Detect circles using the Hough Transform
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)

        # If no circles were found, skip this image
        if circles is None:
            logging.warning(f"No circles found in {filename}")
            continue

        # Out of all overlapping circles, only keep the biggest one that fully fits inside the image
        x, y, r = np.round(circles[0, :]).astype("int")[0]
        for (x2, y2, r2) in np.round(circles[0, :]).astype("int"):
            if r2 > r and x2-r2 >= 0 and y2-r2 >= 0 and x2+r2 < gray.shape[1] and y2+r2 < gray.shape[0]:
                x, y, r = x2, y2, r2

        # Draw the detected circles on the image
        gray2 = gray.copy()
        if circles is not None:
            for (xi, yi, ri) in np.round(circles[0, :]).astype("int"):
                cv2.circle(gray2, (xi, yi), ri, (0, 255, 0), 4)
                cv2.circle(gray2, (x, y), r, (255, 255, 255), 3)
                cv2.rectangle(gray2, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            # Display the image
            cv2.imshow("detected circles", gray2)
            cv2.waitKey(0)

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
        cv2.imwrite(os.path.join(output_folder, f"{name}.texture.png"), texture)
                

if __name__ == "__main__":
    main("./raw", "./out/cropped", "./res/edges/edges.json")
