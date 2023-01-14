import os
import cv2
import numpy as np
import pathlib
import logging


def main(input_folder, output_folder):
    # Loop through all the images in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            # Load the image using OpenCV
            img = cv2.imread(os.path.join(input_folder, filename))

            # Add an alpha channel to the image
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

            # Boost the contrast
            hcimg = cv2.convertScaleAbs(img, alpha=1.5, beta=0)

            # Convert the image to grayscale
            gray = cv2.cvtColor(hcimg, cv2.COLOR_BGR2GRAY)

            # Apply a Gaussian blur to reduce noise
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            # Detect circles using the Hough Transform
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=150, param2=80, minRadius=0, maxRadius=0)

            # If no circles were found, skip this image
            if circles is None:
                logging.warning(f"No circles found in {filename}")
                continue

            # Choose the circles with the largest radius with no overlap
            coins = []
            for c in circles[0]:
                # Check if the circle overlaps with any of the circles we've already chosen
                if not any((c[0]-c[2] < c2[0]+c2[2] and c[0]+c[2] > c2[0]-c2[2] and c[1]-c[2] < c2[1]+c2[2] and c[1]+c[2] > c2[1]-c2[2]) for c2 in coins):
                    # If it doesn't overlap, add it to the list
                    coins.append(c)

            # Create the output folder if it doesn't exist
            pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

            # Iterate through the circles
            for c, i in zip(coins, range(len(coins))):
                
                # Get the center and radius of the circle
                x, y, r = c.astype(int)

                # Create a mask with the circle area (white circle on black background)
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

                # Save the texture
                cv2.imwrite(os.path.join(output_folder, f"{name}-{i}.texture.png"), texture)
                

if __name__ == "__main__":
    main("./raw", "./out/cropped")
