import bpy
import math
import numpy as np


# a set of helper functions that you can use
# 1) get bounding boxes
# 2) get locations 
# 3) calculate xyz coordinate using xyz coordinate/bounding box of another object.
# 4) get distance + direction along one axis between bounding box of 1 object and bounding box of another
# 3) move up/down/sidetoside (delta x,y,z)
# 4) rotate degrees around z

def get_bounding_box(object):
    """
    Get the bounding box for the object
    Returns a dict with keys:
        "minpoint" for the minimum xyz point as numpy array
        "maxpoint" for the minimum xyz point as numpy array
    """
    vertices = np.array([(object.matrix_world @ v.co).to_tuple() for v in object.data.vertices])
    # vertices = np.array([v.co.to_tuple() for v in object.data.vertices])
    min_point = np.min(vertices, axis=0)
    max_point = np.max(vertices, axis=0)
    return {"minpoint": min_point, 
            "maxpoint": max_point}
        
def get_bounding_box_center(object):
    bounding_box = get_bounding_box(object)
    return 0.5*bounding_box["minpoint"] + 0.5*bounding_box["maxpoint"]

def get_bounding_box_top(object):
    """
    Get the bounding box for the top of the object
    Returns a dict with keys:
        "minpoint" for the minimum xyz point as numpy array
        "maxpoint" for the minimum xyz point as numpy array
    """
    bounding_box = get_bounding_box(object)
    bounding_box["minpoint"][2] = bounding_box["maxpoint"][2]
    return bounding_box

def get_bounding_box_top_center(object):
    """ Get the coordinate for the center of the bounding box of the top of the object.
    Returns: a 3D numpy array.
    """
    bounding_box = get_bounding_box_top(object)
    return 0.5*bounding_box["minpoint"] + 0.5*bounding_box["maxpoint"]

# functions to talk about the top/bottom/left/right/front/back

def bottom_of(obj):
    """ Get the bottom of an object in a 3D vector
    """
    min_point = get_bounding_box(obj)["minpoint"]
    z_coordinate = min_point[2]
    return np.array([0, 0, z_coordinate])

def top_of(obj):
    """ Get the top of an object in a 3D vector
    """
    max_point = get_bounding_box(obj)["maxpoint"]
    z_coordinate = max_point[2]
    return np.array([0, 0, z_coordinate])

def left_of(obj, otherleft=False):
    """
    get_bounding_box(obj)
    """
    # left on the screen corresponds to positive x axis
    
    if otherleft:
        left_x = get_bounding_box(obj)["minpoint"][0]
    else:
        left_x = get_bounding_box(obj)["maxpoint"][0]
    return np.array([left_x, 0, 0])

def right_of(obj, otherright=False):
    """
    """
    return left_of(obj, otherleft= not otherright)

def front_of_closer_to_camera(obj):
    """ Returns a 3D vector with the y component set to y coordinate closest to camera
    the camera view goes from positive y (closer to camera) to negative y
    """
    return np.array([0, get_bounding_box(obj)["maxpoint"][1], 0])

def back_of_further_from_camera(obj):
    """ Returns a 3D vector with the y component set to y coordinate furthest from camera
    the camera view goes from positive y (closer to camera) to negative y
    """
    return np.array([0, get_bounding_box(obj)["minpoint"][1], 0])

def move_to_side(obj1, obj2, distance, side,  move_along_one_axis=True): 
    """ Move obj1 such that it is `distance` away from the `side` side of obj2 
    Args:
        obj1: object being moved
        obj2: reference object
        distance: obj1 should be moved until it is `distance` units away from obj2
        side: "left", "right", "top", "bottom", "front", "back". These are sides of obj2 that obj1 moves in reference to.
    Returns:
        obj1
    """
    if not move_along_one_axis:
        obj1 = move_to(obj1, get_bounding_box_center(obj2))
        
    if side == "left":
        diff = vector_diff(right_of(obj1), left_of(obj2), offset=distance)
    elif side == "right":
        diff = vector_diff(left_of(obj1), right_of(obj2), offset=distance)
    elif side == "top":
        diff = vector_diff(bottom_of(obj1), top_of(obj2), offset=distance)
    elif side == "bottom":
        diff = vector_diff(top_of(obj1), bottom_of(obj2), offset=distance)
    elif side == "front":
        diff = vector_diff(back_of_further_from_camera(obj1), front_of_closer_to_camera(obj2), offset=distance)
    elif side == "back":
        diff = vector_diff(front_of_closer_to_camera(obj1), back_of_further_from_camera(obj2), offset=distance)
    move_by(obj1, diff) 
    return obj1

def move_until_dist_away(obj1, obj2, distance, 
                        axis="z"):
    """ Move an object to some distance from another object along some axis
    Args:
        obj1: object being moved
        obj2: reference object
        distance: obj1 should be moved until it is `distance` units away from obj2
        axis: the axis along which the distance is measured.
    Returns:
        obj1
    """
    assert axis in ("x", "y", "z")
    indexof = {"x":0,  "y":1,  "z": 2}
    obj1_box = get_bounding_box(obj1)
    obj2_box = get_bounding_box(obj2)

    diff1 = obj2_box["maxpoint"] - obj1_box["minpoint"]
    diff2 = obj2_box["minpoint"] - obj1_box["maxpoint"] 
    dist1 = diff1[indexof[axis]]
    dist2 = diff2[indexof[axis]]
    
    if abs(dist1) > abs(dist2):
        dist = dist2
    else:
        dist = dist1
    diff = np.array([0 if axis!="x" else dist,
                     0 if axis!="y" else dist,
                     0 if axis!="z" else dist])

    norm = np.linalg.norm(diff)
    if norm > 0:
        normed_diff = diff/norm
    else:
        normed_diff = diff
    diff = diff - distance*normed_diff
    
    move_by(obj1, diff)
    return obj1    
    
def vector_diff(from_vec, to_vec, offset=0):
    """
    Get the vector going from one point (from_vec) to another (to_vec)
    that goes up until it's `offset` units away from the `to_vec` point.
    """
    # offset is the number of units along 
    diff = to_vec - from_vec 
    norm = np.linalg.norm(diff)
    if norm > 0:
        normed_diff = diff/norm
    else:
        normed_diff = diff
    return diff - offset*normed_diff

def move_to(obj, location):
    """ Set the object location.
    """
    obj.location = location
    bpy.context.view_layer.update()
    return obj
    
def move_by(obj, vector):
    """ Shift the object location by a 3D vector
    """
    obj.location[0] += vector[0]
    obj.location[1] += vector[1]
    obj.location[2] += vector[2]
    bpy.context.view_layer.update()
    return obj

def rotate_by(obj, angle_degrees, axis="z"):
    """ Rotate the object by `angle_degree` degrees, along the axis specified.
    """
    rotation_additive = [0 if axis!="x" else angle_degrees,
                         0 if axis!="y" else angle_degrees, 
                         0 if axis!="z" else angle_degrees]
                             
    obj.rotation_euler[0] = obj.rotation_euler[0] + math.radians(rotation_additive[0])
    obj.rotation_euler[1] = obj.rotation_euler[1] + math.radians(rotation_additive[1])
    obj.rotation_euler[2] = obj.rotation_euler[2] + math.radians(rotation_additive[2])
    bpy.context.view_layer.update()
    return obj

def random_perturb(dx, dy, dz):
    """ Generate a 3D vector from a 3D gaussian 
    that has dx, dy, dz variance along the
    x, y, z axes, respectively.
    
    Useful for adding natural variation to translations and rotations
    of objects.
    """
    return np.random.normal(np.zeros(3), np.array([dx, dy, dz]))


# these are anchor objects -- objects that shouldn't be moved.
floor = bpy.data.objects["Floor"]
wall = bpy.data.objects["BackWall"]
windowwall = bpy.data.objects["WindowWall"]

# These are movable objects. 
sofa = bpy.data.objects["Sofa"]
carpet = bpy.data.objects["Carpet"]
table  = bpy.data.objects["Table"]
painting = bpy.data.objects["Painting"]
book1 = bpy.data.objects["Book1"]
book2 = bpy.data.objects["Book2"]
book3 = bpy.data.objects["Book3"]
book4 = bpy.data.objects["Book4"]
book5 = bpy.data.objects["Book5"]
plant1 = bpy.data.objects["Plant1"]
speaker = bpy.data.objects["Speaker"]
candle1 = bpy.data.objects["Candle1"]
candle2 = bpy.data.objects["Candle2"]
pampas_decor = bpy.data.objects["PampasDecor"]


# Code that creates the sstarter scene.
carpet = move_to_side(carpet, floor, 0.01, "top", move_along_one_axis=True)
carpet = move_to_side(carpet, windowwall, 0.3, "right",  move_along_one_axis=True)
carpet = move_to_side(carpet, wall, 0.3, "front", move_along_one_axis=True)

sofa = move_to_side(sofa, floor, 0.02, "top", move_along_one_axis=True)
sofa = move_to_side(sofa, wall, 0.35 , "front", move_along_one_axis=True)
sofa = move_to_side(sofa, windowwall, 0.35, "right", move_along_one_axis=True)

# this moves the table first to the corner of the sofa bounding box
table = move_to_side(table, carpet, 0.01, "top", move_along_one_axis=True)
table = move_to_side(table, sofa, 0.1, "front", move_along_one_axis=True)
table = move_to_side(table, sofa, 0.1, "right", move_along_one_axis=True)
# then, it moves the table inwards and to the left, to fit directly in front of the L-shaped couch.
# moving positive x values to move it to the left
# move negative y values to mvoe it inwards.
table = move_by(table, np.array([1.25, -0.25, 0])) # you can tweak this

# now we put the books on the table
book1 = move_by(move_to_side(book1, table, 0.01, "top", move_along_one_axis=False), # we want it to place the book at the center of the table first, so False. 
                random_perturb(dx=0.1, dy=0.1, dz=0))
book2 = move_to_side(book2, book1, 0.01, "top", move_along_one_axis=False) # place book2 on top of book 1, with the other 2 coordinates set to the bounding box center of book 1.
book2 = rotate_by(book2, 
                  random_perturb(dx=0, dy=0, dz=90)[2], # the last component of a random vector for the z rotation
                  axis="z") # the rotation is around the z axis
book3 = move_to_side(book3, book2, 0.01, "top", move_along_one_axis=False)

# Use the above code to reason about how to call the helper functions to make changes to the scene.
# Add your lines here 1
# add your lines here 2
# add your lines here 3...


