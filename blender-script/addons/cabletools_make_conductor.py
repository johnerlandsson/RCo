bl_info = {
        "name": "Make conductor",
        "category": "RCo",
}

import bpy
import cabletools as ct

# Create properties
bpy.types.Scene.CT_make_conductor_diameter = bpy.props.FloatProperty(
        name = "Diameter",
        description = "Total diameter of the conductor",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.00162,
        min = 0.0005,
        max = 0.3)

bpy.types.Scene.CT_make_conductor_strand_dia = bpy.props.FloatProperty(
        name = "Strand Diameter",
        description = "Total diameter of the individual strands",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.00052,
        min = 0.0001,
        max = 0.01)

bpy.types.Scene.CT_make_conductor_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Length of the conductor",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 1.5,
        min = 0.2,
        max = 10.0)

bpy.types.Scene.CT_make_conductor_pitch = bpy.props.FloatProperty(
        name = "Pitch",
        description = "Axial length between revolutions",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.045,
        min = 0.0,
        max = 0.5)

bpy.types.Scene.CT_make_conductor_material = bpy.props.EnumProperty(
        items = ct.CONDUCTOR_MATERIALS,
        name = "Material")

# Operator class
class MakeConductor(bpy.types.Operator):
    bl_idname = "ct.make_conductor"
    bl_label = "Make conductor"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        length = scene.CT_make_conductor_length
        material = scene.CT_make_conductor_material
        conductor_radius = scene.CT_make_conductor_diameter / 2.0
        strand_radius = scene.CT_make_conductor_strand_dia / 2.0
        strand_pitch = 1.0 / scene.CT_make_conductor_pitch

        ct.make_conductor(length, conductor_radius, strand_radius,
                strand_pitch, material, context)

        return {'FINISHED'}

# Panel class
class MakeConductorUI(bpy.types.Panel):
    bl_label = "Make conductor"
    bl_idname = "OBJECT_PT_ct_make_conductor_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_make_conductor_diameter")
        layout.prop(scene, "CT_make_conductor_strand_dia")
        layout.prop(scene, "CT_make_conductor_length")
        layout.prop(scene, "CT_make_conductor_material")
        layout.prop(scene, "CT_make_conductor_pitch")
        layout.operator("ct.make_conductor", text = "Make")

def register():
    bpy.utils.register_class(MakeConductor)
    bpy.utils.register_class(MakeConductorUI)
def unregister():
    bpy.utils.unregister_class(MakeConductor)
    bpy.utils.unregister_class(MakeConductorUI)

if __name__ == '__main__':
    register()
