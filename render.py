# This script should be run from the Blender Python console

import bpy
import os
import random
import subprocess
import pathlib
import logging

# Get current working directory
dir = bpy.path.abspath("//").replace("\\", "/")
# Constants
INPUT_DIR = f"{dir}out/cropped"
OUTPUT_DIR = f"{dir}out/rendered"
VARIATIONS = 3

# Run the "isolate.py" script via subprocess if the input directory doesn't exist or is empty
if not os.path.exists(INPUT_DIR) or len(os.listdir(INPUT_DIR)) == 0:
    logging.info("No textures found, running isolate.py")
    subprocess.run(["python", f"{dir}isolate.py"])

# If the output directory doesn't exist, create it
if not os.path.exists(OUTPUT_DIR):
    pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Get the cylinder object
cylinder = bpy.data.objects["Coin"]

# Get the material of the cylinder
mat = cylinder.data.materials[0]

# Get the texture nodes
for node in mat.node_tree.nodes:
    if node.name == "img_texture":
        tex_node = node
    elif node.name == "bump_texture":
        bump_node = node

# Iterate through the textures in the input directory
for texture_file in os.listdir(INPUT_DIR):
    if texture_file.endswith(".png"):

        # Load the texture
        img = bpy.data.images.load(os.path.join(INPUT_DIR, texture_file))

        # Set the texture node's image to the loaded texture
        tex_node.image = img

        # Get the name of the texture
        name = os.path.splitext(texture_file)[0].strip(".texture")

        # Set the output file name
        bpy.context.scene.render.filepath = os.path.join(OUTPUT_DIR, name)

        # Generate random positions for the camera and light and randomize the light's color and intensity
        for i in range(VARIATIONS):
            # Set the camera's position around the coin
            bpy.data.objects["Camera"].location = (random.uniform(-2, 2), random.uniform(-2.5, -3), random.uniform(-2, 2))

            # Set the light's position around the coin
            bpy.data.objects["Light"].location = (random.uniform(-1.5, 1.5), random.uniform(-2, -3), random.uniform(-1.5, 1.5))

            # Set the light's color
            bpy.data.objects["Light"].data.color = (random.uniform(0.5, 1), random.uniform(0.5, 1), random.uniform(0.5, 1))

            # Set the light's intensity
            bpy.data.objects["Light"].data.energy = random.uniform(0.5, 1)

            # Render the image
            # bpy.ops.render.render(write_still=True)
        