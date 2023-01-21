# Preprocess

This is a simple script to preprocess [downloaded images](https://github.com/seba1204/coin-scraper).
We need to remove any background, center the coin, and make it square.

## Usage

You need to have openCV for python.

You can run :

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

## Settings

Iniside main.py, you have 4 settings :

- `INPUT_PATH`: path to the folder containing the images. All images inside will be processed.
- `OUTPUT_PATH`: path to the folder where the processed images will be saved.
- `EDGES_PATH`: path to the folder where the edges of the coins are saved. Need to have a `edges.json` file.
- `NB_OF_TESTS`: number of images to process. If you want to process all images, set it to -1. If it is `>0`, it will take random images from the folder.

Output images are saved as `.png` files with the same name as the input image.
