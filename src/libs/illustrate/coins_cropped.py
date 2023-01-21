from os import listdir
from os.path import join


def crop():
    INPUT_FOLDER = "./raw/"
    OUTPUT_FOLDER = "./out/cropped/"
    NUMBER_OF_COUNTRIES = 5

    # each image is named like this: <country-name>_<coin-value>_<edition>.jpg

    # generate a dict  with the following format:
    # {
    #   <country-name>: {
    #       <coin-value>: <image-name>,
    #       <coin-value>: <image-name>,
    #       ...
    #   },
    #   <country-name>: {
    #       <coin-value>: <image-name>,
    #       <coin-value>: <image-name>,
    #       ...
    #   },
    #   ...
    # }

    # get all images (.png, .jpg, .jpeg, .bmp, .gif)
    images = [f for f in listdir(INPUT_FOLDER) if is_image(f)]

    selected_images = {}

    current_nb_of_countries = 0
    for image in images:
        # get image name
        image_name = image.split("_")
        country = image_name[0]
        value = image_name[1]

        full_path = join(INPUT_FOLDER, image)

        if country not in selected_images:
            if current_nb_of_countries >= NUMBER_OF_COUNTRIES:
                continue
            selected_images[country] = {}
            current_nb_of_countries += 1

        if value not in selected_images[country]:
            selected_images[country][value] = full_path


if __name__ == '__main__':
    crop()
