bl_info = {
        "name": "Make lap",
        "category": "RCo",
}

import bpy
import cabletools as ct

# Create properties
bpy.types.Scene.CT_make_lap_diameter = bpy.props.FloatProperty(
        name = "Diameter",
        description = "Total diameter of the lap tube",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.00162,
        min = 0.005,
        max = 0.3)

bpy.types.Scene.CT_make_lap_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Length of the lap tube",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.25,
        min = 0.1,
        max = 10.0)

bpy.types.Scene.CT_make_lap_material = bpy.props.EnumProperty(
        items = ct.LAP_MATERIALS,
        name = "Material")

# Operator class
class MakeLap(bpy.types.Operator):
    bl_idname = "ct.make_lap"
    bl_label = "Make lap"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        length = scene.CT_make_lap_length
        material = scene.CT_make_lap_material
        radius = scene.CT_make_lap_diameter / 2.0

        ct.make_lap(length, radius, material, context)

        return {'FINISHED'}

# Panel class
class MakeLapUI(bpy.types.Panel):
    bl_label = "Make lap"
    bl_idname = "OBJECT_PT_ct_make_lap_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_make_lap_diameter")
        layout.prop(scene, "CT_make_lap_length")
        layout.prop(scene, "CT_make_lap_material")
        layout.operator("ct.make_lap", text = "Make")

def register():
    bpy.utils.register_class(MakeLap)
    bpy.utils.register_class(MakeLapUI)
def unregister():
    bpy.utils.unregister_class(MakeLap)
    bpy.utils.unregister_class(MakeLapUI)

if __name__ == '__main__':
    register()
