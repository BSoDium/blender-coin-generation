<!-- omit in toc -->
# Recoinize dataset generator

This file is a set of scripts which aim to generate a large dataset for
our IA based project *[Recoinize](https://github.com/photonsquid/Recoinize)*.

<!-- omit in toc -->
## Summary

- [Workflow](#workflow)
- [Installation](#installation)
- [Usage](#usage)
- [TODOs](#todos)

## Workflow

1. Download all different coins from the [ECB website](https://www.ecb.europa.eu/euro/coins/html/index.en.html).
2. Process all images in order crop the coin from the image.
3. Generate textures ready to be applied on a 3D model.
4. For each coin, render `x` new random *pictures* (random light, orientation, etc.)
5. Create an AI friendly dataset (`test`, `train`, `validation`)
6. Upload it to [Hugging Face](https://huggingface.co/datasets/photonsquid/coins-euro)

## Installation

It depends on the script you want to run, but for the entire workflow, you need:

- Blender (v 3.8)
- Python (v.3.10)
- Some python packages (cf. `requirement.txt`)

## Usage

```bash
python ./main.py
```

## TODOs

- [ ] Make a wiki explaining each script
- [ ] Finish this `README.md`
- [ ] Make a great refactoring, so it works!
- [ ] Make a nice CLI
