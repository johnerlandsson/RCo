bl_info = {
        "name": "Make part array",
        "category": "RCo",
        "description": "Cabletools: Create a circular array of parts"
}

import bpy
import cabletools as ct

# Create properties
bpy.types.Scene.CT_make_part_array_cond_diameter = bpy.props.FloatProperty(
        name = "Conductor diameter",
        description = "Total diameter of the conductor",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.0075,
        min = 0.0005,
        max = 0.02)

bpy.types.Scene.CT_make_part_array_cond_strand_dia = bpy.props.FloatProperty(
        name = "Strand Diameter",
        description = "Total diameter of the individual strands",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.0004,
        min = 0.0,
        max = 0.005)

bpy.types.Scene.CT_make_part_array_cond_pitch = bpy.props.FloatProperty(
        name = "Conductor pitch",
        description = "Axial distance between revolutions",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.045,
        min = 0.005,
        max = 1.0)

bpy.types.Scene.CT_make_part_array_cond_material = bpy.props.EnumProperty(
        items = ct.CONDUCTOR_MATERIALS,
        name = "Conductor material")

bpy.types.Scene.CT_make_part_array_ins_outer_dia = bpy.props.FloatProperty(
        name = "Insulator Diameter",
        description = "Total diameter of the insulator",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.0099,
        min = 0.0005,
        max = 0.03)

bpy.types.Scene.CT_make_part_array_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Axial length of array",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.25,
        min = 0.1,
        max = 1.0)

bpy.types.Scene.CT_make_part_array_ins_material = bpy.props.EnumProperty(
        items = ct.INSULATOR_MATERIALS,
        name = "Insulator material")

bpy.types.Scene.CT_make_part_array_clockwize = bpy.props.BoolProperty(
        name = "Clockwize",
        description = "Rotation direction of array")

bpy.types.Scene.CT_make_part_array_ins_peel_length = bpy.props.FloatProperty(
        name = "Peel length",
        description = "How much of the insulator is peeled off",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.01,
        min = 0.001,
        max = 0.1)

bpy.types.Scene.CT_make_part_array_colors = bpy.props.StringProperty(
        name = "Colors",
        description = "Whitespace separated list of insulator colors",
        default = "white brown black white brown black")

bpy.types.Scene.CT_make_part_array_radius = bpy.props.FloatProperty(
        name = "Radius",
        description = "Radius of the array",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.01,
        min = 0.0005,
        max = 0.1)

bpy.types.Scene.CT_make_part_array_pitch = bpy.props.FloatProperty(
        name = "Pitch",
        description = "Axial distans between array revolutions",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.25,
        min = 0.005,
        max = 2)

# Operator class
class MakePartArray(bpy.types.Operator):
    bl_idname = "ct.make_part_array"
    bl_label = "Make part array"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        
        # Array params
        length = scene.CT_make_part_array_length
        radius = scene.CT_make_part_array_radius
        pitch = 1.0 / scene.CT_make_part_array_pitch
        clockwize = scene.CT_make_part_array_clockwize

        # Insulator params
        outer_radius = scene.CT_make_part_array_ins_outer_dia / 2.0
        inner_radius = scene.CT_make_part_array_cond_diameter / 2.0
        insulator_material = scene.CT_make_part_array_ins_material
        insulator_colors = scene.CT_make_part_array_colors
        peel_length = scene.CT_make_part_array_ins_peel_length

        # Conductor params
        conductor_radius = inner_radius
        conductor_strand_radius = scene.CT_make_part_array_cond_strand_dia / 2.0
        conductor_material = scene.CT_make_part_array_cond_material
        conductor_pitch = 1.0 / scene.CT_make_part_array_cond_pitch

        # Create array
        ct.make_part_array(length = length,
                           pitch = pitch,
                           radius = radius,
                           clockwize = clockwize,
                           ins_outer_radius = outer_radius,
                           ins_inner_radius = inner_radius,
                           ins_material = insulator_material,
                           ins_colors = insulator_colors,
                           cond_radius = conductor_radius,
                           ins_peel_length = peel_length,
                           cond_strand_pitch = conductor_pitch,
                           cond_material = conductor_material,
                           cond_strand_radius = conductor_strand_radius,
                           context = context)

        return {'FINISHED'}

# Panel class
class MakePartArrayUI(bpy.types.Panel):
    bl_label = "Make part array"
    bl_idname = "OBJECT_PT_ct_make_part_array_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        layout.prop(scene, "CT_make_part_array_length")
        layout.prop(scene, "CT_make_part_array_radius")
        layout.prop(scene, "CT_make_part_array_pitch")
        layout.prop(scene, "CT_make_part_array_clockwize")

        layout.prop(scene, "CT_make_part_array_ins_outer_dia")
        layout.prop(scene, "CT_make_part_array_colors")
        layout.prop(scene, "CT_make_part_array_ins_material")
        layout.prop(scene, "CT_make_part_array_ins_peel_length")

        layout.prop(scene, "CT_make_part_array_cond_diameter")
        layout.prop(scene, "CT_make_part_array_cond_strand_dia")
        layout.prop(scene, "CT_make_part_array_cond_pitch")
        layout.prop(scene, "CT_make_part_array_cond_material")

        layout.operator("ct.make_part_array", text = "Make")

def register():
    bpy.utils.register_class(MakePartArray)
    bpy.utils.register_class(MakePartArrayUI)
def unregister():
    bpy.utils.unregister_class(MakePartArray)
    bpy.utils.unregister_class(MakePartArrayUI)

if __name__ == '__main__':
    register()
