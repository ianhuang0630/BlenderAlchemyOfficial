"""
Given a python file (indicated inthe commandline path), render the material output.
"""

import bpy
import random
import json
import os
import sys
from sys import platform


# def get_material_from_code(code_fpath):
#     assert os.path.exists(code_fpath)
#     import pdb; pdb.set_trace()
#     with open(code_fpath, "r") as f:
#         code = f.read()
#     exec(code)
#     return material 


if __name__ == "__main__":

    code_fpath = sys.argv[6]  # TODO: allow a folder to be given, each with a possible guess.
    rendering_fpath = sys.argv[7] # rendering


    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512

    with open(code_fpath, "r") as f:
        code = f.read()
    try:
        exec(code)
    except:
        raise ValueError
    
    # render, and save.
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = rendering_fpath
    bpy.ops.render.render(write_still=True)