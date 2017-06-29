bl_info = {
        "name": "Make part",
        "category": "RCo",
        "description": "Cabletools: Create a single part"
}

import bpy
import cabletools as ct

# Create properties
bpy.types.Scene.CT_make_part_cond_diameter = bpy.props.FloatProperty(
        name = "Conductor diameter",
        description = "Total diameter of the conductor",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.0075,
        min = 0.001,
        max = 0.2)

bpy.types.Scene.CT_make_part_cond_strand_dia = bpy.props.FloatProperty(
        name = "Strand Diameter",
        description = "Total diameter of the individual strands",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.0004,
        min = 0.0,
        max = 0.005)

bpy.types.Scene.CT_make_part_cond_pitch = bpy.props.FloatProperty(
        name = "Conductor pitch",
        description = "Axial distance between revolutions",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.045,
        min = 0.005,
        max = 0.5)

bpy.types.Scene.CT_make_part_cond_material = bpy.props.EnumProperty(
        items = ct.CONDUCTOR_MATERIALS,
        name = "Conductor material")

bpy.types.Scene.CT_make_part_ins_outer_dia = bpy.props.FloatProperty(
        name = "Insulator Diameter",
        description = "Total diameter of the insulator",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.0099,
        min = 0.001,
        max = 0.03)

bpy.types.Scene.CT_make_part_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Axial length of the array",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.27,
        min = 0.2,
        max = 1.0)

bpy.types.Scene.CT_make_part_ins_material = bpy.props.EnumProperty(
        items = ct.INSULATOR_MATERIALS,
        name = "Insulator material")

bpy.types.Scene.CT_make_part_ins_color_name = bpy.props.EnumProperty(
        items = ct.INSULATOR_COLORS,
        name = 'Color name')

bpy.types.Scene.CT_make_part_ins_peel_length = bpy.props.FloatProperty(
        name = "Peel length",
        description = "How much of the insulator is peeled off",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.01,
        min = 0.001,
        max = 0.1)

# Operator class
class MakePart(bpy.types.Operator):
    bl_idname = "ct.make_part"
    bl_label = "Make part"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        
        length = scene.CT_make_part_length

        # Insulator params
        outer_radius = scene.CT_make_part_ins_outer_dia / 2.0
        inner_radius = scene.CT_make_part_cond_diameter / 2.0
        insulator_material = scene.CT_make_part_ins_material
        color_name = scene.CT_make_part_ins_color_name
        peel_length = scene.CT_make_part_ins_peel_length

        # Conductor params
        conductor_radius = inner_radius
        conductor_strand_radius = scene.CT_make_part_cond_strand_dia / 2.0
        conductor_material = scene.CT_make_part_cond_material
        conductor_pitch = 1.0 / scene.CT_make_part_cond_pitch

        # Create part
        ct.make_part(length, outer_radius, color_name, insulator_material,
                     peel_length, conductor_radius, conductor_material,
                     conductor_strand_radius, conductor_pitch, context)

        return {'FINISHED'}

# Panel class
class MakePartUI(bpy.types.Panel):
    bl_label = "Make part"
    bl_idname = "OBJECT_PT_ct_make_part_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        layout.prop(scene, "CT_make_part_length")

        layout.prop(scene, "CT_make_part_ins_outer_dia")
        layout.prop(scene, "CT_make_part_ins_color_name")
        layout.prop(scene, "CT_make_part_ins_material")
        layout.prop(scene, "CT_make_part_ins_peel_length")

        layout.prop(scene, "CT_make_part_cond_diameter")
        layout.prop(scene, "CT_make_part_cond_strand_dia")
        layout.prop(scene, "CT_make_part_cond_pitch")
        layout.prop(scene, "CT_make_part_cond_material")

        layout.operator("ct.make_part", text = "Make")

def register():
    bpy.utils.register_class(MakePart)
    bpy.utils.register_class(MakePartUI)
def unregister():
    bpy.utils.unregister_class(MakePart)
    bpy.utils.unregister_class(MakePartUI)

if __name__ == '__main__':
    register()
