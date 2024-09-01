import bpy
import bpy
import mathutils
from numpy.random import uniform, normal, randint
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core.util.color import color_category
from infinigen.core import surface



def shader_thorns(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    texture_coordinate_1 = nw.new_node(Nodes.TextureCoord)
    
    mapping_1 = nw.new_node(Nodes.Mapping, input_kwargs={'Vector': texture_coordinate_1.outputs["UV"]})
    
    noise_texture_1 = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Vector': mapping_1, 'Scale': 401.1000})

    # the color of the thorn. 
    colorramp_2 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': noise_texture_1.outputs["Color"]})
    colorramp_2.color_ramp.elements[0].position = 0.0000
    colorramp_2.color_ramp.elements[0].color = [0.0388, 0.0002, 0.0000, 1.0000]
    colorramp_2.color_ramp.elements[1].position = 1.0000
    colorramp_2.color_ramp.elements[1].color = [0.1810, 0.0000, 0.0027, 1.0000]
    
    noise_texture_2 = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Scale': 22.4000})
    
    colorramp_3 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': noise_texture_2.outputs["Color"]})
    colorramp_3.color_ramp.elements[0].position = 0.1204
    colorramp_3.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    colorramp_3.color_ramp.elements[1].position = 1.0000
    colorramp_3.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    texture_coordinate = nw.new_node(Nodes.TextureCoord)
    
    mapping = nw.new_node(Nodes.Mapping, input_kwargs={'Vector': texture_coordinate.outputs["Generated"]})
    
    voronoi_texture = nw.new_node(Nodes.VoronoiTexture,
        input_kwargs={'Vector': mapping, 'Scale': 50.0000},
        attrs={'feature': 'DISTANCE_TO_EDGE'})
    
    colorramp_4 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': voronoi_texture.outputs["Distance"]})
    colorramp_4.color_ramp.elements[0].position = 0.0000
    colorramp_4.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    colorramp_4.color_ramp.elements[1].position = 0.0341
    colorramp_4.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    mix = nw.new_node(Nodes.Mix,
        input_kwargs={0: 0.8208, 6: colorramp_4.outputs["Color"], 7: colorramp_2.outputs["Color"]},
        attrs={'data_type': 'RGBA', 'blend_type': 'MULTIPLY'})
    
    bump_1 = nw.new_node('ShaderNodeBump', input_kwargs={'Strength': 0.6000, 'Height': mix.outputs[2]}, attrs={'invert': True})

    # the material properties of the thorn:
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': colorramp_2.outputs["Color"], 'Subsurface': 0.1000, 'Subsurface Color': colorramp_2.outputs["Color"], 'Roughness': colorramp_3.outputs["Color"], 'Normal': bump_1},
        attrs={'subsurface_method': 'BURLEY'})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': principled_bsdf}, attrs={'is_active_output': True})

def shader_stem(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    texture_coordinate_1 = nw.new_node(Nodes.TextureCoord)
    
    mapping_1 = nw.new_node(Nodes.Mapping, input_kwargs={'Vector': texture_coordinate_1.outputs["UV"]})
    
    noise_texture_1 = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Vector': mapping_1, 'Scale': 401.1000})
    
    colorramp_2 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': noise_texture_1.outputs["Color"]})
    colorramp_2.color_ramp.elements[0].position = 0.0000
    colorramp_2.color_ramp.elements[0].color = [0.0015, 0.0000, 0.0388, 1.0000]
    colorramp_2.color_ramp.elements[1].position = 1.0000
    colorramp_2.color_ramp.elements[1].color = [0.1770, 0.2738, 0.0283, 1.0000]
    
    noise_texture_2 = nw.new_node(Nodes.NoiseTexture, input_kwargs={'Scale': 22.4000})
    
    colorramp_3 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': noise_texture_2.outputs["Color"]})
    colorramp_3.color_ramp.elements[0].position = 0.1204
    colorramp_3.color_ramp.elements[0].color = [0.0000, 0.0000, 0.0000, 1.0000]
    colorramp_3.color_ramp.elements[1].position = 1.0000
    colorramp_3.color_ramp.elements[1].color = [1.0000, 1.0000, 1.0000, 1.0000]
    
    bump_1 = nw.new_node('ShaderNodeBump', input_kwargs={'Strength': 0.0922, 'Height': colorramp_2.outputs["Color"]})
    
    principled_bsdf = nw.new_node(Nodes.PrincipledBSDF,
        input_kwargs={'Base Color': colorramp_2.outputs["Color"], 'Subsurface': 0.1000, 'Subsurface Color': colorramp_2.outputs["Color"], 'Roughness': colorramp_3.outputs["Color"], 'Normal': bump_1},
        attrs={'subsurface_method': 'BURLEY'})
    
    translucent_bsdf = nw.new_node(Nodes.TranslucentBSDF, input_kwargs={'Color': colorramp_2.outputs["Color"], 'Normal': bump_1})
    
    mix_shader = nw.new_node(Nodes.MixShader,
        input_kwargs={'Fac': colorramp_2.outputs["Color"], 1: principled_bsdf, 2: translucent_bsdf})
    
    material_output = nw.new_node(Nodes.MaterialOutput, input_kwargs={'Surface': mix_shader}, attrs={'is_active_output': True})

def geometry_nodes(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler


    group_input = nw.new_node(Nodes.GroupInput,
        expose_input=[('NodeSocketGeometry', 'Geometry', None),
            ('NodeSocketFloatFactor', 'Start Leaves', 0.2167),
            ('NodeSocketFloatFactor', 'End Leaves', 0.8708),
            ('NodeSocketInt', 'Randomize Leaves', -22),
            ('NodeSocketFloat', 'Rose Bud Open (0)/ Closed (1)', 1)])
    
    set_position = nw.new_node(Nodes.SetPosition, input_kwargs={'Geometry': group_input.outputs["Geometry"]})
    
    spline_parameter = nw.new_node(Nodes.SplineParameter)
    
    colorramp = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': spline_parameter.outputs["Factor"]})
    colorramp.color_ramp.interpolation = "B_SPLINE"
    colorramp.color_ramp.elements[0].position = 0.0000
    colorramp.color_ramp.elements[0].color = [0.3330, 0.3330, 0.3330, 1.0000]
    colorramp.color_ramp.elements[1].position = 1.0000
    colorramp.color_ramp.elements[1].color = [0.0000, 0.0000, 0.0000, 1.0000]
    
    set_curve_radius = nw.new_node(Nodes.SetCurveRadius, input_kwargs={'Curve': set_position, 'Radius': colorramp.outputs["Color"]})
    
    curve_circle = nw.new_node(Nodes.CurveCircle, input_kwargs={'Radius': 0.0300})
    
    curve_to_mesh = nw.new_node(Nodes.CurveToMesh,
        input_kwargs={'Curve': set_curve_radius, 'Profile Curve': curve_circle.outputs["Curve"]})
    
    set_material = nw.new_node(Nodes.SetMaterial,
        input_kwargs={'Geometry': curve_to_mesh, 'Material': surface.shaderfunc_to_material(shader_stem)})

    # leaf count gives  the number of leaves.
    leaf_count = 23 
    resample_curve = nw.new_node(Nodes.ResampleCurve, input_kwargs={'Curve': set_position, 'Count': leaf_count}) 
    
    trim_curve = nw.new_node(Nodes.TrimCurve,
        input_kwargs={'Curve': resample_curve, 2: group_input.outputs["Start Leaves"], 3: group_input.outputs["End Leaves"]})
    
    object_info_3 = nw.new_node(Nodes.ObjectInfo, input_kwargs={'Object': bpy.data.objects['Leave 1'], 'As Instance': True})
    
    object_info_4 = nw.new_node(Nodes.ObjectInfo, input_kwargs={'Object': bpy.data.objects['Leave 2'], 'As Instance': True})
    
    object_info_5 = nw.new_node(Nodes.ObjectInfo, input_kwargs={'Object': bpy.data.objects['Leave 3'], 'As Instance': True})
    
    join_geometry_2 = nw.new_node(Nodes.JoinGeometry,
        input_kwargs={'Geometry': [object_info_3.outputs["Geometry"], object_info_4.outputs["Geometry"], object_info_5.outputs["Geometry"]]})
    
    random_value = nw.new_node(Nodes.RandomValue,
        input_kwargs={5: 1, 'Seed': group_input.outputs["Randomize Leaves"]},
        attrs={'data_type': 'INT'})
    
    curve_tangent = nw.new_node(Nodes.CurveTangent)
    
    align_euler_to_vector = nw.new_node(Nodes.AlignEulerToVector, input_kwargs={'Vector': curve_tangent}, attrs={'axis': 'Z'})
    
    spline_parameter_1 = nw.new_node(Nodes.SplineParameter)
    
    float_curve = nw.new_node(Nodes.FloatCurve, input_kwargs={'Value': spline_parameter_1.outputs["Factor"]})
    node_utils.assign_curve(float_curve.mapping.curves[0], [(0.0568, 0.4062), (0.3773, 0.8188), (1.0000, 0.7000)])
    
    instance_on_points = nw.new_node(Nodes.InstanceOnPoints,
        input_kwargs={'Points': trim_curve, 'Instance': join_geometry_2, 'Pick Instance': True, 'Instance Index': random_value.outputs[2], 'Rotation': align_euler_to_vector, 'Scale': float_curve})
    
    random_value_1 = nw.new_node(Nodes.RandomValue, input_kwargs={3: 0.4000})
    
    index = nw.new_node(Nodes.Index)
    
    multiply = nw.new_node(Nodes.Math, input_kwargs={0: index, 1: 2.3000}, attrs={'operation': 'MULTIPLY'})
    
    combine_xyz = nw.new_node(Nodes.CombineXYZ,
        input_kwargs={'X': random_value_1.outputs[1], 'Y': random_value_1.outputs[1], 'Z': multiply})
    
    rotate_instances = nw.new_node(Nodes.RotateInstances, input_kwargs={'Instances': instance_on_points, 'Rotation': combine_xyz})
    
    endpoint_selection = nw.new_node(Nodes.EndpointSelection, input_kwargs={'Start Size': 0})
    
    integer = nw.new_node(Nodes.Integer)  # rose petal density
    integer.integer = 7 
    
    mesh_line = nw.new_node(Nodes.MeshLine, input_kwargs={'Count': integer, 'Offset': (0.0000, 0.0000, 0.0000)})
    
    object_info = nw.new_node(Nodes.ObjectInfo, input_kwargs={'Object': bpy.data.objects['PEtal 1'], 'As Instance': True})
    
    object_info_1 = nw.new_node(Nodes.ObjectInfo, input_kwargs={'Object': bpy.data.objects['Petal 2'], 'As Instance': True})
    
    object_info_2 = nw.new_node(Nodes.ObjectInfo, input_kwargs={'Object': bpy.data.objects['Petal 3'], 'As Instance': True})
    
    join_geometry_1 = nw.new_node(Nodes.JoinGeometry,
        input_kwargs={'Geometry': [object_info.outputs["Geometry"], object_info_1.outputs["Geometry"], object_info_2.outputs["Geometry"]]})
    
    random_value_2 = nw.new_node(Nodes.RandomValue, input_kwargs={5: 1, 'Seed': -22}, attrs={'data_type': 'INT'})
    
    index_1 = nw.new_node(Nodes.Index)
    
    divide = nw.new_node(Nodes.Math, input_kwargs={0: index_1, 1: integer}, attrs={'operation': 'DIVIDE'})

    # key  of 3 and 4 map to to_min and to_maxes of the MapRange node,
    # when you increase the value at key 4, this makes the flower less flat, more realistic.
    map_range = nw.new_node(Nodes.MapRange, input_kwargs={'Value': divide, 3: 0.0, 4: 0.6000})
    
    add = nw.new_node(Nodes.Math, input_kwargs={0: map_range.outputs["Result"], 1: group_input.outputs["Rose Bud Open (0)/ Closed (1)"]})
    
    multiply_1 = nw.new_node(Nodes.Math, input_kwargs={0: index_1, 1: 2.3000}, attrs={'operation': 'MULTIPLY'})
    
    combine_xyz_1 = nw.new_node(Nodes.CombineXYZ, input_kwargs={'X': add, 'Z': multiply_1})
    
    float_curve_1 = nw.new_node(Nodes.FloatCurve, input_kwargs={'Factor': 0.8023, 'Value': divide})
    node_utils.assign_curve(float_curve_1.mapping.curves[0], [(0.0114, 0.0469), (0.4250, 0.7406), (0.6864, 0.0000)])
    
    multiply_2 = nw.new_node(Nodes.Math, input_kwargs={0: float_curve_1, 1: 1.4000}, attrs={'operation': 'MULTIPLY'})
    
    instance_on_points_1 = nw.new_node(Nodes.InstanceOnPoints,
        input_kwargs={'Points': mesh_line, 'Instance': join_geometry_1, 'Pick Instance': True, 'Instance Index': random_value_2.outputs[2], 'Rotation': combine_xyz_1, 'Scale': multiply_2})
    
    curve_tangent_1 = nw.new_node(Nodes.CurveTangent)
    
    align_euler_to_vector_1 = nw.new_node(Nodes.AlignEulerToVector, input_kwargs={'Vector': curve_tangent_1}, attrs={'axis': 'Z'})
    
    instance_on_points_2 = nw.new_node(Nodes.InstanceOnPoints,
        input_kwargs={'Points': resample_curve, 'Selection': endpoint_selection, 'Instance': instance_on_points_1, 'Rotation': align_euler_to_vector_1})
    
    resample_curve_1 = nw.new_node(Nodes.ResampleCurve, input_kwargs={'Curve': trim_curve, 'Count': 42})
    
    curve_line = nw.new_node(Nodes.CurveLine,
        input_kwargs={'End': (0.0000, 0.0000, 0.2000), 'Length': 0.0200},
        attrs={'mode': 'DIRECTION'})
    
    set_position_1 = nw.new_node(Nodes.SetPosition, input_kwargs={'Geometry': curve_line})
    
    spline_parameter_2 = nw.new_node(Nodes.SplineParameter)
    
    colorramp_1 = nw.new_node(Nodes.ColorRamp, input_kwargs={'Fac': spline_parameter_2.outputs["Factor"]})
    colorramp_1.color_ramp.interpolation = "EASE"
    colorramp_1.color_ramp.elements[0].position = 0.0000
    colorramp_1.color_ramp.elements[0].color = [0.3330, 0.3330, 0.3330, 1.0000]
    colorramp_1.color_ramp.elements[1].position = 1.0000
    colorramp_1.color_ramp.elements[1].color = [0.0000, 0.0000, 0.0000, 1.0000]
    
    set_curve_radius_1 = nw.new_node(Nodes.SetCurveRadius, input_kwargs={'Curve': set_position_1, 'Radius': colorramp_1.outputs["Color"]})
    
    curve_circle_1 = nw.new_node(Nodes.CurveCircle, input_kwargs={'Radius': 0.0100})
    
    curve_to_mesh_1 = nw.new_node(Nodes.CurveToMesh,
        input_kwargs={'Curve': set_curve_radius_1, 'Profile Curve': curve_circle_1.outputs["Curve"]})
    
    curve_tangent_2 = nw.new_node(Nodes.CurveTangent)
    
    align_euler_to_vector_2 = nw.new_node(Nodes.AlignEulerToVector, input_kwargs={'Vector': curve_tangent_2})
    
    spline_parameter_3 = nw.new_node(Nodes.SplineParameter)
    
    float_curve_2 = nw.new_node(Nodes.FloatCurve, input_kwargs={'Value': spline_parameter_3.outputs["Factor"]})
    node_utils.assign_curve(float_curve_2.mapping.curves[0], [(0.0568, 0.4062), (0.3886, 0.7719), (1.0000, 0.7000)])
    
    instance_on_points_3 = nw.new_node(Nodes.InstanceOnPoints,
        input_kwargs={'Points': resample_curve_1, 'Instance': curve_to_mesh_1, 'Rotation': align_euler_to_vector_2, 'Scale': float_curve_2})
    
    random_value_3 = nw.new_node(Nodes.RandomValue, input_kwargs={1: (0.2000, 4.6000, 4.6000)}, attrs={'data_type': 'FLOAT_VECTOR'})
    
    rotate_instances_1 = nw.new_node(Nodes.RotateInstances,
        input_kwargs={'Instances': instance_on_points_3, 'Rotation': random_value_3.outputs["Value"]})
    
    set_material_1 = nw.new_node(Nodes.SetMaterial,
        input_kwargs={'Geometry': rotate_instances_1, 'Material': surface.shaderfunc_to_material(shader_thorns)})
    
    join_geometry = nw.new_node(Nodes.JoinGeometry,
        input_kwargs={'Geometry': [set_material, rotate_instances, instance_on_points_2, set_material_1]})
    
    group_output = nw.new_node(Nodes.GroupOutput, input_kwargs={'Geometry': join_geometry}, attrs={'is_active_output': True})



def apply(obj, selection=None, **kwargs):
    surface.add_geomod(obj, geometry_nodes, selection=selection, attributes=[])
apply(bpy.context.active_object)