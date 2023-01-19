import cv2
import os
import numpy as np
import glob

# this script will create a big image with some coins in it
# it is for illustration purposes only

# list of countries
countries = [
    "at",
    "be",
    "ad",
    "fi",
    "it",
    "es",
    "de",
    "gr",
]

# list of coin values
values = [
    "2euro",
    "1euro",
    "50cents",
    "20cents",
    "10cents",
    "5cents",
    "2cents",
    "1cent"
]

PATH = "raw"
OUTPUT_PATH = "out"


x = 100
nb_countries = len(countries)
nb_values = len(values)

width = x * nb_values
height = x * nb_countries

# create empty image of dimension (x, x)
main_image = np.zeros((width, height, 3), np.uint8) * 255

# for each country
for country in countries:
    for value in values:
        # image path is PATH/<country>_<value>*.jpg where * is can be any character, or empty
        # so we use glob to get all the files that match the pattern
        image_path = os.path.join(PATH, f"{country}_{value}*.jpg")
        # get all the files that match the pattern
        files = glob.glob(image_path)
        # if there are no files, skip
        if len(files) == 0:
            print(f"no files for {country}_{value}")
            continue
        # get file with the shortest len
        file = min(files, key=len)
        # open image
        image = cv2.imread(file)
        # resize image
        image = cv2.resize(image, (x, x))
        # paste image in main image at the right position
        i = countries.index(country)
        j = values.index(value)
        main_image[i * x:(i + 1) * x, j * x:(j + 1) * x] = image

# save image
cv2.imwrite(OUTPUT_PATH + "/main_image.jpg", main_image)
