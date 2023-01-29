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
VARIATIONS = 2

# Run the "isolate.py" script via subprocess if the input directory doesn't exist or is empty
if not os.path.exists(INPUT_DIR) or len(os.listdir(INPUT_DIR)) == 0:
    logging.info("No textures found, running isolate.py")
    subprocess.run(["python", f"{dir}isolate.py"])

# If the output directory doesn't exist, create it
if not os.path.exists(OUTPUT_DIR):
    pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Get the coin object
coin = bpy.data.objects["Coin"]

# Get all materials
coin_face_mat = bpy.data.materials["Coin_face"]
coin_side_mat = bpy.data.materials["Coin_side"]
plane_concrete_mat = bpy.data.materials["Concrete"]
world_mat = bpy.data.worlds["World"]

# Get the texture nodes of the materials
for node in coin_face_mat.node_tree.nodes:
    match node.name:
        case "face_img_texture":
            face_tex_node = node
        case "face_bump_texture":
            face_bump_node = node
        case "rustiness":
            rustiness_node = node
        case "roughness":
            roughness_node = node

for node in coin_side_mat.node_tree.nodes:
    if node.name == "side_img_texture":
        side_tex_node = node
    elif node.name == "side_bump_texture":
        side_bump_node = node

for node in plane_concrete_mat.node_tree.nodes:
    if node.name == "texture_mapping":
        mapping_node = node

for node in world_mat.node_tree.nodes:
    match node.name:
        case "r_weight":
            r_weight_node = node
        case "g_weight":
            g_weight_node = node
        case "b_weight":
            b_weight_node = node

# List and group files in the input directory
files = os.listdir(INPUT_DIR)
textures = [file for file in files if file.endswith(".texture.png")]
dmaps = [file for file in files if file.endswith(".dmap.png")]

# Iterate through the textures in the input directory
for texture, dmap in zip(textures, dmaps):
    # Load the texture
    texture_image = bpy.data.images.load(os.path.join(INPUT_DIR, texture))
    dmap_image = bpy.data.images.load(os.path.join(INPUT_DIR, dmap))

    # Set the texture nodes image to the loaded texture
    face_tex_node.image = texture_image
    face_bump_node.image = dmap_image
    side_tex_node.image = texture_image
    side_bump_node.image = dmap_image

    # Get the name of the texture
    name = os.path.splitext(os.path.splitext(texture)[0])[0]

    # Set the output file name
    bpy.context.scene.render.filepath = os.path.join(OUTPUT_DIR, name)

    # Generate random positions for the camera and light and randomize the light's color and intensity
    for i in range(VARIATIONS):
        # Set the camera's position around the coin
        bpy.data.objects["Camera"].location = (
            random.uniform(-2, 2), random.uniform(-2.5, -3), random.uniform(-2, 2))

        # Set the coin's rotation around the y-axis
        coin.rotation_euler = (coin.rotation_euler[0], random.uniform(0, 6.28), coin.rotation_euler[2])

        # Set the light's color
        (
            r_weight_node.outputs[0].default_value,
            g_weight_node.outputs[0].default_value,
            b_weight_node.outputs[0].default_value
        ) = (
            random.uniform(0.6, 1),
            random.uniform(0.6, 1),
            random.uniform(0.6, 1)
        )

        # Randomize the plane's texture position (edit the mapping node's location)
        mapping_node.inputs[1].default_value = (
            random.uniform(-5, 5), random.uniform(-5, 5), 0)

        # Randomize the coin's age (0 = new, 1 = old) using a normal distribution
        age = min(abs(random.normalvariate(0, 0.2)), 1)

        # Randomize the rustiness of the coin using the age
        rustiness_node.outputs[0].default_value = min(0.6 + age * 0.7, 0.9)

        # Randomize the roughness of the coin using the age
        roughness_node.outputs[0].default_value = min(0.4 + age * 0.5, 0.8)

        continue

        # Render the image
        bpy.context.scene.render.filepath = os.path.join(
            OUTPUT_DIR, f"{name}_{i}")
        bpy.ops.render.render(write_still=True)

        # Set render engine to Workbench
        bpy.context.scene.render.engine = "BLENDER_WORKBENCH"

        # Hide background plane
        bpy.data.objects["Plane"].hide_render = True

        # Render the image
        bpy.context.scene.render.filepath = os.path.join(
            OUTPUT_DIR, f"{name}_{i}_mask")
        bpy.ops.render.render(write_still=True)

        # Set render engine to Cycles
        bpy.context.scene.render.engine = "CYCLES"

        # Show background plane
        bpy.data.objects["Plane"].hide_render = False
