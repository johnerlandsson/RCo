import bpy

def insulator_material(color, blend_value):
    #Change to cycles render engine
    if bpy.context.scene.render.engine != 'CYCLES':
        bpy.context.scene.render.engine = 'CYCLES'

    material = bpy.data.materials.new('pvc_material')
    material.use_nodes = True
    
    diff_bsdf = material.node_tree.nodes.get('Diffuse BSDF')
    if not diff_bsdf == None:
        material.node_tree.nodes.remove(diff_bsdf)

    material_output = material.node_tree.nodes.get('Material Output')

    #add nodes
    diffuse = material.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = (color[0], color[1], color[2], 1.0)
    glossy = material.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    mix_shader = material.node_tree.nodes.new('ShaderNodeMixShader')
    layer_weight = material.node_tree.nodes.new('ShaderNodeLayerWeight')
    layer_weight.inputs['Blend'].default_value = blend_value

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0], mix_shader.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[1], diffuse.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[2], glossy.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[0], layer_weight.outputs[1])

    #set viewport color
    material.diffuse_color = color

    return material

def pvc_insulator_material(color):
    return insulator_material(color, 0.15)

def pex_insulator_material(color):
    return insulator_material(color, 0.15)

def pe_insulator_material(color):
    return insulator_material(color, 0.15)

def conductor_material(color, name):
    #Change to cycles render engine
    if bpy.context.scene.render.engine != 'CYCLES':
        bpy.context.scene.render.engine = 'CYCLES'

    # Check if material exists
    name = 'conductor_' + name + '_material'

    material = bpy.data.materials.get(name)
    if material != None:
        return material

    # Create material
    material = bpy.data.materials.new(name)

    # activate use nodes for material
    material.use_nodes = True

   # Remove default
    diff_bsdf = material.node_tree.nodes.get('Diffuse BSDF')
    if not diff_bsdf == None:
        material.node_tree.nodes.remove(diff_bsdf)
        print("Diffuse BSDF is none type")

    material_output = material.node_tree.nodes.get('Material Output')
    
    #add nodes and edit values
    mix_shader = material.node_tree.nodes.new('ShaderNodeMixShader')
    glossy1 = material.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    glossy1.inputs['Roughness'].default_value = 0.05
    glossy1.name = 'Glossy BSDF 1'
    glossy1.label = 'Glossy BSDF 1' 
    glossy2 = material.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    glossy2.inputs['Roughness'].default_value = 0.01
    glossy2.name = 'Glossy BSDF 2'
    glossy2.label = 'Glossy BSDF 2'
    layer_weight = material.node_tree.nodes.new('ShaderNodeLayerWeight')
    layer_weight.inputs['Blend'].default_value = 0.7
    mix_rgb = material.node_tree.nodes.new('ShaderNodeMixRGB')
    mix_rgb.inputs['Color1'].default_value = color
    mix_rgb.inputs['Color2'].default_value = [0.693576, 0.590995, 0.575779, 1.000000] #color kind of white
    mix_rgb.inputs['Fac'].default_value = 0.2

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0], mix_shader.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[0], layer_weight.outputs[1])
    material.node_tree.links.new(mix_shader.inputs[1], glossy1.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[2], glossy2.outputs[0])
    material.node_tree.links.new(glossy1.inputs[0], mix_rgb.outputs[0])
    material.node_tree.links.new(glossy2.inputs[0], mix_rgb.outputs[0])
    
    
    #set viewport color
    material.diffuse_color = color[0:3] #remove alpha color channel
    
    # return material
    return material

def copper_conductor_material():
    return conductor_material((0.603114, 0.093013, 0.000000, 1.000000),
    'copper')

def tinned_copper_conductor_material():
    return conductor_material((0.800000, 0.800000, 0.800000, 1.000000),
    'tinned_copper')

def aluminium_conductor_material():
    return conductor_material((0.800000, 0.800000, 0.800000, 1.000000),
    'aluminium')

INSULATOR_MATERIALS = {'pvc': pvc_insulator_material,
                       'pex': pex_insulator_material,
                       'pe': pe_insulator_material}

CONDUCTOR_MATERIALS = {'cu': copper_conductor_material,
                       'cu-t': tinned_copper_conductor_material,
                       'al': aluminium_conductor_material}

INSULATOR_COLORS = {'red': (0.549, 0.002, 0.009),
                    'green': (0.013, 0.549, 0.025),
                    'blue': (0.013, 0.07, 0.549),
                    'yellow': (0.532, 0.549, 0.004)}
