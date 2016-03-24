import bpy

def pvc_material(color):
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
    layer_weight.inputs['Blend'].default_value = 0.15

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0], mix_shader.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[1], diffuse.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[2], glossy.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[0], layer_weight.outputs[1])

    #set viewport color
    material.diffuse_color = color

    return material

def pex_material(color):
    material = bpy.data.materials.new('pex_material')
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
    layer_weight.inputs['Blend'].default_value = 0.15

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0], mix_shader.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[1], diffuse.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[2], glossy.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[0], layer_weight.outputs[1])

    #set viewport color
    material.diffuse_color = color

    return material

def pe_material(color):
    material = bpy.data.materials.new('pe_material')
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
    layer_weight.inputs['Blend'].default_value = 0.15

    # link nodes to material output
    material.node_tree.links.new(material_output.inputs[0], mix_shader.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[1], diffuse.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[2], glossy.outputs[0])
    material.node_tree.links.new(mix_shader.inputs[0], layer_weight.outputs[1])

    #set viewport color
    material.diffuse_color = color

    return material

INSULATOR_MATERIALS = {'pvc': pvc_material,
                       'pex': pex_material,
                       'pe': pe_material}
