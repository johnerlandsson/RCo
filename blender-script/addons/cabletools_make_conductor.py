bl_info = {
        "name": "Make conductor",
        "category": "Object",
}

import bpy
import cabletools as ct

# Create properties
bpy.types.Scene.CT_make_conductor_diameter = bpy.props.FloatProperty(
        name = "Diameter (mm)",
        description = "Total diameter of the conductor",
        default = 1.62,
        min = 1.0,
        max = 300.0)

bpy.types.Scene.CT_make_conductor_strand_dia = bpy.props.FloatProperty(
        name = "Strand Diameter (mm)",
        description = "Total diameter of the individual strands",
        default = 0.52,
        min = 0.0,
        max = 10.0)

bpy.types.Scene.CT_make_conductor_length = bpy.props.FloatProperty(
        name = "Length (m)",
        description = "Length of the conductor",
        default = 1.5,
        min = 0.2,
        max = 10.0)

bpy.types.Scene.CT_make_conductor_pitch = bpy.props.FloatProperty(
        name = "Pitch",
        description = "Number of revolutions per length unit",
        default = 8.0,
        min = 0.0,
        max = 20.0)

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
        conductor_radius = scene.CT_make_conductor_diameter / 2000.0
        strand_radius = scene.CT_make_conductor_strand_dia / 2000.0
        strand_pitch = scene.CT_make_conductor_pitch

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
