"""
Takes in a single prompt (language and/or image)
"""

from pathlib import Path
import os
import argparse
import yaml
from loguru import logger

from openai import OpenAI
import urllib

from refinement_process import refinement
from tasksolver.keychain import KeyChain

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='BlenderAlchemy Arguments')
    parser.add_argument('--starter_blend', type=str, help='path to the base blender file.') # path to the .blend file
    parser.add_argument('--blender_base', type=str, help='blender base file path.')       # The path of blender-python script
    parser.add_argument('--blender_script', type=str, help='script to edit.')             # the script to be edited
    parser.add_argument('--config', type=str, help='path to yaml file.')
    args = parser.parse_args()

    with open(args.config) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # initialize the image generator client
    kc = KeyChain() 
    for el in config["credentials"]:
        if config["credentials"][el] is not None:
            kc.add_key(el, config["credentials"][el])
    client = OpenAI(api_key=kc["openai"])  


    
    output_dir = Path(config['output']['output_dir'])
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    dimensions = [[int(ell) for ell in el.strip().split("x")] for el in config["run_config"]["tree_dims"]]    
    variants = [el.strip() for el in config["run_config"]["variants"]]
    
    desc = config["input"]["text_prompt"]


    # if config["run_config"]["enable_visual_imagination"]:
    #     assert config["run_config"]["num_tries"] > 0, "number of starter images should be positive if imagination is on."
    #     download_paths = []
    #     for i in range(config["run_config"]["num_tries"]):     # The number of starer_images entered in cmd line
    #         response = client.images.generate(
    #             model="dall-e-3",
    #             prompt=f"Close-up photorealistic rendering of {desc}",
    #             size="1024x1024",
    #             quality="standard",
    #             n=1,
    #         )
    #         download_paths.append(response.data[0].url)

    #     for instance_idx, url in enumerate(download_paths):     # Saved the generated images based on description
    #         download_to = output_dir/f"target_instance{instance_idx}.png"
    #         urllib.request.urlretrieve(url, download_to)
    #         logger.info(f"Saved generated image to {download_to}.")

    for instance_idx in range(config["run_config"]["num_tries"]):
        for var in variants:
            for depth, breadth in dimensions:
                subfolder = f'{var}_d{depth}_b{breadth}'
                results_folder = output_dir/f"instance{instance_idx}"/subfolder

                 
                # down the hole we go.
                refinement(config, 
                           credentials=kc,
                           breadth=breadth, depth=depth,
                           blender_file=args.starter_blend,
                           blender_script=args.blender_base,
                           init_code=args.blender_script,
                           method_variation=var,
                           output_folder=results_folder)  
                            
                                
