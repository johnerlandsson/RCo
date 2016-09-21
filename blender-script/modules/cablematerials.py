## @package cablematerials
# This package contains material stuff for cabletools
import bpy
import os


## 
# @brief Append material node group from blendfile
# 
# @param folder_path Path to folder containing the blendfile
# @param filename Filename
# @param obj_name Name of the nodegroup in file
def append_nodegroup(
        folder_path=os.path.dirname(__file__) + "/../../blender-materials/",
        filename="cabletools.blend",
        obj_name="plastic_pvc"):
    obj_type = "NodeTree"
    # tip object_full_directory_path as str: "./materials.blend\\NodeTree\\"
    object_full_directory_path = folder_path + filename + "\\" + obj_type + "\\"

    bpy.ops.wm.append(
        directory=object_full_directory_path, filename=obj_name, link=False)


## 
# @brief General function to append an insulator material. Should not be called
# directly. Use convenience functions.
# 
# @param color Color of the material
# @param material_name Name of the material in cablematerials.blend
# @param material_node_group_name Name of the nodegroup in cablematerials.blend
# @param object_radius Radius of the object for texture scale
# 
# @return The material
def insulator_material(color, material_name, material_node_group_name,
                       object_radius):
    #Append material
    append_nodegroup(obj_name=material_node_group_name)

    #Change to cycles render engine
    if bpy.context.scene.render.engine != 'CYCLES':
        bpy.context.scene.render.engine = 'CYCLES'

    material = bpy.data.materials.new(material_name)
    material.use_nodes = True

    diff_bsdf = material.node_tree.nodes.get('Diffuse BSDF')
    if not diff_bsdf == None:
        material.node_tree.nodes.remove(diff_bsdf)

    material_output = material.node_tree.nodes.get('Material Output')

    #add nodes
    nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
    nodegroup.node_tree = bpy.data.node_groups[material_node_group_name]
    nodegroup.inputs['Color'].default_value = (color[0], color[1], color[2],
                                               1.0)
    #nodegroup.inputs['Blend'].default_value = blend_value #old value before nodegroups
    if 'object_radius' in nodegroup.inputs:
        nodegroup.inputs['object_radius'].default_value = object_radius

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0],
                                 nodegroup.outputs[0])

    return material


def pvc_insulator_material(color, object_radius=0.001):
    material = insulator_material(
        color=color,
        material_name='pvc_insulator_material',
        material_node_group_name='plastic_pvc',
        object_radius=object_radius)

    #set viewport color
    material.diffuse_color = color

    return material


def pe_insulator_material(color, object_radius=0.001):
    material = insulator_material(
        color=color,
        material_name='pe_insulator_material',
        material_node_group_name='plastic_pe',
        object_radius=object_radius)

    #set viewport color
    material.diffuse_color = color

    return material


def pur_insulator_material(color, object_radius=0.001):
    material = insulator_material(
        color=color,
        material_name='pur_insulator_material',
        material_node_group_name='plastic_pur',
        object_radius=object_radius)

    #set viewport color
    material.diffuse_color = color

    return material


def epd_insulator_material(color, object_radius=0.001):
    material = insulator_material(
        color=color,
        material_name='epd_insulator_material',
        material_node_group_name='plastic_epd',
        object_radius=object_radius)

    #set viewport color
    material.diffuse_color = color

    return material


def fill_insulator_material(color, object_radius=0.001):
    material = insulator_material(
        color=color,
        material_name='fill_insulator_material',
        material_node_group_name='plastic_fill',
        object_radius=object_radius)

    #set viewport color
    material.diffuse_color = color

    return material


def fill_rope_material(color, object_radius=0.001):
    material = insulator_material(
        color=color,
        material_name='fill_rope_material',
        material_node_group_name='plastic_fill_rope',
        object_radius=object_radius)

    #set viewport color
    material.diffuse_color = color

    return material


def conductor_material(material_name, material_node_group_name):
    #Append material
    append_nodegroup(obj_name=material_node_group_name)

    #Change to cycles render engine
    if bpy.context.scene.render.engine != 'CYCLES':
        bpy.context.scene.render.engine = 'CYCLES'

    material = bpy.data.materials.new(material_name)
    material.use_nodes = True

    diff_bsdf = material.node_tree.nodes.get('Diffuse BSDF')
    if not diff_bsdf == None:
        material.node_tree.nodes.remove(diff_bsdf)

    material_output = material.node_tree.nodes.get('Material Output')

    #add nodes
    nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
    nodegroup.node_tree = bpy.data.node_groups[material_node_group_name]
    #nodegroup.inputs['Color1'].default_value = (base_color[0], base_color[1], base_color[2], 1.0)
    #nodegroup.inputs['Color2'].default_value = (gloss_color[0],  gloss_color[1], gloss_color[2], 1.0)

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0],
                                 nodegroup.outputs[0])

    #set viewport color
    #material.diffuse_color = base_color

    return material


def copper_conductor_material():
    material = conductor_material('conductor_cu', 'metal_copper')
    material.diffuse_color = CONDUCTOR_COLORS['copper']
    return material


def tinned_copper_conductor_material():
    material = conductor_material('conductor_tin', 'metal_tin')
    material.diffuse_color = CONDUCTOR_COLORS['tin']
    return material


def aluminum_conductor_material():
    material = conductor_material('conductor_aluminum', 'metal_aluminum')
    material.diffuse_color = CONDUCTOR_COLORS['aluminum']
    return material


def iron_conductor_material():
    material = conductor_material('conductor_iron', 'metal_iron')
    material.diffuse_color = CONDUCTOR_COLORS['iron']
    return material


def lap_material(material_name, material_node_group_name, object_radius):
    #Append material
    append_nodegroup(obj_name=material_node_group_name)

    #Change to cycles render engine
    if bpy.context.scene.render.engine != 'CYCLES':
        bpy.context.scene.render.engine = 'CYCLES'

    material = bpy.data.materials.new(material_name)
    material.use_nodes = True

    diff_bsdf = material.node_tree.nodes.get('Diffuse BSDF')
    if not diff_bsdf == None:
        material.node_tree.nodes.remove(diff_bsdf)

    material_output = material.node_tree.nodes.get('Material Output')

    #add nodes
    nodegroup = material.node_tree.nodes.new('ShaderNodeGroup')
    nodegroup.node_tree = bpy.data.node_groups[material_node_group_name]
    #nodegroup.inputs['Blend'].default_value = blend_value #old value before nodegroups
    if 'object_radius' in nodegroup.inputs:
        nodegroup.inputs['object_radius'].default_value = object_radius

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0],
                                 nodegroup.outputs[0])

    return material


def nylon_lap_material(object_radius=0.001):
    material = lap_material(
        'lap_nylon', 'lap_nylon', object_radius=object_radius)
    material.diffuse_color = LAP_COLORS['nylon']
    return material


def chrome_lap_material(object_radius=0.001):
    material = lap_material(
        'lap_chrome', 'lap_chrome-2-sided', object_radius=object_radius)
    material.diffuse_color = LAP_COLORS['chrome']
    return material


def plastic_lap_material(object_radius=0.001):
    material = lap_material(
        'lap_plastic', 'lap_plastic', object_radius=object_radius)
    material.diffuse_color = LAP_COLORS['plastic']
    return material


INSULATOR_MATERIALS = {'pvc': pvc_insulator_material,
                       'pe': pe_insulator_material,
                       'pur': pur_insulator_material,
                       'epd': epd_insulator_material,
                       'fill': fill_insulator_material,
                       'fill_rope': fill_rope_material}

CONDUCTOR_MATERIALS = {'cu': copper_conductor_material,
                       'cu-t': tinned_copper_conductor_material,
                       'al': aluminum_conductor_material,
                       'fe': iron_conductor_material}

LAP_MATERIALS = {'nylon': nylon_lap_material,
                 'chrome': chrome_lap_material,
                 'plastic': plastic_lap_material}

INSULATOR_COLORS = {'red': (0.549, 0.002, 0.009),
                    'green': (0.013, 0.549, 0.025),
                    'blue': (0.013, 0.07, 0.549),
                    'beige': (0.638264, 0.533126, 0.387854),
                    'brown': (0.098, 0.02, 0.01),
                    'pink': (0.8, 0.084, 0.0332),
                    'black': (0.007, 0.007, 0.007),
                    'red': (0.246, 0.0, 0.005),
                    'white': (0.8, 0.8, 0.8),
                    'grey': (0.173, 0.173, 0.173),
                    'orange': (0.8, 0.136, 0.019),
                    'purple': (0.339, 0.044, 0.549),
                    'yellow': (0.532, 0.549, 0.004)}

CONDUCTOR_COLORS = {'copper': (0.603, 0.093, 0.0),
                    'tin': (0.603, 0.603, 0.603),
                    'aluminum': (0.666654, 0.590356, 0.748414),
                    'iron': (0.666654, 0.590356, 0.748414)}

LAP_COLORS = {'nylon': (0.6, 0.6, 0.6),
              'chrome': (0.603, 0.603, 0.603),
              'plastic': (0.8, 0.8, 0.8)}

STRIPE_TYPES = {
    'gr/ye':
    (INSULATOR_COLORS['green'], INSULATOR_COLORS['yellow'], 0.4, True),
    'd-black':
    (INSULATOR_COLORS['white'], INSULATOR_COLORS['black'], 0.5, False),
    'd-grey':
    (INSULATOR_COLORS['white'], INSULATOR_COLORS['grey'], 0.5, False),
    'd-red': (INSULATOR_COLORS['white'], INSULATOR_COLORS['red'], 0.5, False),
    'd-blue':
    (INSULATOR_COLORS['white'], INSULATOR_COLORS['blue'], 0.5, False),
    'd-brown':
    (INSULATOR_COLORS['white'], INSULATOR_COLORS['brown'], 0.5, False),
    'd-yellow':
    (INSULATOR_COLORS['white'], INSULATOR_COLORS['yellow'], 0.5, False),
    'd-green':
    (INSULATOR_COLORS['white'], INSULATOR_COLORS['green'], 0.5, False),
    'd-orange':
    (INSULATOR_COLORS['white'], INSULATOR_COLORS['orange'], 0.5, False),
    'd-pink':
    (INSULATOR_COLORS['white'], INSULATOR_COLORS['pink'], 0.5, False),
    'ye/red_50/50': (INSULATOR_COLORS['yellow'], INSULATOR_COLORS['red'], 0.5,
                     True),
    'gr/purp_90/10': (INSULATOR_COLORS['green'], INSULATOR_COLORS['purple'],
                      0.1, False)
}
