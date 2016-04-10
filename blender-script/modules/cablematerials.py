import bpy
import os

# append material node group from file
# folder_path: folder path for blend file
# obj_name: Name of node group in file
def append_nodegroup(folder_path=os.path.dirname(__file__) + "/../../blender-materials/", 
                     filename = "cabletools.blend", 
                     obj_name = "plastic_pvc"):
    obj_type = "NodeTree"
    # tip object_full_directory_path as str: "./materials.blend\\NodeTree\\"
    object_full_directory_path = folder_path + filename + "\\" + obj_type + "\\"
    
    bpy.ops.wm.append(
        directory=object_full_directory_path, 
        filename=obj_name, link=False )

def insulator_material(color, blend_value, material_name, material_node_group_name):
    #Append material
    append_nodegroup(obj_name = material_node_group_name)

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
    nodegroup.inputs['Color'].default_value = (color[0], color[1], color[2], 1.0)
    #nodegroup.inputs['Blend'].default_value = blend_value

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0], nodegroup.outputs[0])
    

    #set viewport color
    material.diffuse_color = color

    return material

def pvc_insulator_material(color):
    return insulator_material(color = color, 
                              blend_value = 0.15,
                              material_name = 'pvc_insulator_material',
                              material_node_group_name = 'plastic_pvc')

def pe_insulator_material(color):
    return insulator_material(color = color, 
                              blend_value = 0.15,
                              material_name = 'pe_insulator_material',
                              material_node_group_name = 'plastic_pvc')

def conductor_material(base_color, gloss_color, material_name,
        material_node_group_name):
    #Append material
    append_nodegroup(obj_name = material_node_group_name)

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
    nodegroup.inputs['Color1'].default_value = (base_color[0], 
                                                base_color[1],
                                                base_color[2], 
                                                1.0)
    nodegroup.inputs['Color2'].default_value = (gloss_color[0], 
                                                gloss_color[1], 
                                                gloss_color[2], 
                                                1.0)

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0], nodegroup.outputs[0])
    

    #set viewport color
    material.diffuse_color = base_color

    return material

def copper_conductor_material():
    return conductor_material((0.603, 0.093, 0.0), 
                              (0.694, 591, 576), 
                              'conductor_cu',
                              'metal_copper')

def tinned_copper_conductor_material():
    return conductor_material((0.603, 0.603, 0.603), 
                              (0.694, 591, 576), 
                              'conductor_cu',
                              'metal_tin')


INSULATOR_MATERIALS = {'pvc': pvc_insulator_material,
                       'pe': pe_insulator_material}

CONDUCTOR_MATERIALS = {'cu': copper_conductor_material,
                       'cu-t': tinned_copper_conductor_material}
                       

INSULATOR_COLORS = {'red': (0.549, 0.002, 0.009),
                    'green': (0.013, 0.549, 0.025),
                    'blue': (0.013, 0.07, 0.549),
                    'yellow': (0.532, 0.549, 0.004)}
