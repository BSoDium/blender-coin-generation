# This script should be run from the Blender Python console

import bpy
import os
import random
import subprocess

# Constants
INPUT_DIR = "C:/Users/bsodium/Code/GitHub/blender-coin-generation/out/cropped"
OUTPUT_DIR = "C:/Users/bsodium/Code/GitHub/blender-coin-generation/out/rendered"
VARIATIONS = 3

# Run the "isolate.py" script via subprocess if the input directory doesn't exist or is empty
if not os.path.exists(INPUT_DIR) or len(os.listdir(INPUT_DIR)) == 0:
    subprocess.run(["python", "isolate.py", INPUT_DIR, OUTPUT_DIR])

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

        # Generate 10 random positions for the camera and light
        for i in range(VARIATIONS):
            # Set the camera's position around the coin, at a distance of 4 units approximately
            bpy.data.objects["Camera"].location = (random.uniform(-0.5, 0.5), random.uniform(-4, -5), random.uniform(-0.5, 0.5))

            # Set the light's position around the coin
            bpy.data.objects["Light"].location = (random.uniform(-1.5, 1.5), random.uniform(-2, -3), random.uniform(-1.5, 1.5))

            # Render the image
            # bpy.ops.render.render(write_still=True)
        