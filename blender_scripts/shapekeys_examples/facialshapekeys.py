import bpy

""" Leave this comment block unchanged across edits.

Mouth open (ranges from 0 to 1): degree of mouth openness
Scrunch nose (range from 0 to 1): scrunching of the nose.
Pursed lips (range from 0 to 1): degree to which to corners of the mouth are close together.

Left side smile (range from -1 to 1): left corner of mouth moves up to form a smile. Negative values move the corner down, as if in a frown.
Right side smile (range from -1 to 1): right corner of mouth moves up to form a smile. Negative values move the corner down, as if in a frown.
Left eye close (range from -0.3 to 1): positive values narrows the left eye, negative values widens it.
Right eye close (range from -0.3 to 1): positive values narrows the right eye, negative values widens it.
Left raised eyebrow (range from 0 to 1): arches the left eyebrow, as in a skeptical look or angry.
Right raised eyebrow (range from 0 to 1): arches the right eyebrow, as in a skeptical look or angry.
Left lifted eyebrow (range from 0 to 1): Left raises the eyebrow, as in a surprised look.
Right lifted eyebrow (range from 0 to 1): Right raises the eyebrow, as in a surprised look.
Left furrow eyebrow (range from 0 to 1): furrows the left eyebrow, as in angry or concentrated.
Right furrow eyebrow (range from 0 to 1): furrows the right eyebrow, as in angry or concentrated.
Left eyebrow upward tilt (range from 0 to 1): tilts the left eyebrow outwards, as in a sad look.
Right eyebrow upward tilt (range from 0 to 1): tilts the right eyebrow outwards, as in a sad look.
Left eye outer corner lift (range from -1 to 1): positive values the outer corner of the right eye up, as in smiling with the eyes. negative values move the outer corner down, as in sad expression.S
Right eye outer corner lift (range from -1 to 1): positive values the outer corner of the right eye up, as in smiling with the eyes. negative values move the outer corner down, as in sad expression.
Left eye inner corner lift (range from 0 to 1): positive values move the inner corner up, useful  when the outer corner is down.
Right eye inner corner lift (range from 0 to 1): positive values move the inner corner up, useful  when the outer corner is down.
"""

bpy.data.shape_keys["Key"].key_blocks["Mouth open"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Pursed lips"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Scrunch nose"].value = 0

bpy.data.shape_keys["Key"].key_blocks["Left side smile"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Right side smile"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Left eye close"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Right eye close"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Left raised eyebrow"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Right raised eyebrow"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Left lifted eyebrow"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Right lifted eyebrow"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Left furrow eyebrow"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Right furrow eyebrow"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Left eyebrow upward tilt"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Right eyebrow upward tilt"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Left eye outer corner lift"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Right eye outer corner lift"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Left eye inner corner lift"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Right eye inner corner lift"].value = 0


