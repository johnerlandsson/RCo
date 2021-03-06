bl_info = {
        "name": "Make insulator",
        "category": "RCo",
}

import bpy
import cabletools as ct

# Create properties
bpy.types.Scene.CT_make_insulator_outer_dia = bpy.props.FloatProperty(
        name = "Outer Diameter",
        description = "Total diameter of the insulator",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.035,
        min = 0.001,
        max = 0.3)

bpy.types.Scene.CT_make_insulator_inner_dia = bpy.props.FloatProperty(
        name = "Inner Diameter",
        description = "Total diameter of the insulators hole",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.03,
        min = 0.0005,
        max = 0.25)

bpy.types.Scene.CT_make_insulator_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Length of the insulator",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.23,
        min = 0.1,
        max = 10.0)

bpy.types.Scene.CT_make_insulator_material = bpy.props.EnumProperty(
        items = ct.INSULATOR_MATERIALS,
        name = "Material")

bpy.types.Scene.CT_make_insulator_color_name = bpy.props.EnumProperty(
        items = ct.INSULATOR_COLORS,
        name = 'Color name')

# Operator class
class MakeInsulator(bpy.types.Operator):
    bl_idname = "ct.make_insulator"
    bl_label = "Make insulator"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        outer_radius = scene.CT_make_insulator_outer_dia / 2.0
        inner_radius = scene.CT_make_insulator_inner_dia / 2.0
        length = scene.CT_make_insulator_length
        material = scene.CT_make_insulator_material
        color_name = scene.CT_make_insulator_color_name

        ct.make_insulator(inner_radius, outer_radius, length, 0.0, material,
                color_name, context)

        return {'FINISHED'}

# Panel class
class MakeInsulatorUI(bpy.types.Panel):
    bl_label = "Make insulator"
    bl_idname = "OBJECT_PT_ct_make_insulator_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_make_insulator_outer_dia")
        layout.prop(scene, "CT_make_insulator_inner_dia")
        layout.prop(scene, "CT_make_insulator_length")
        layout.prop(scene, "CT_make_insulator_color_name")
        layout.prop(scene, "CT_make_insulator_material")
        layout.operator("ct.make_insulator", text = "Make")

def register():
    bpy.utils.register_class(MakeInsulator)
    bpy.utils.register_class(MakeInsulatorUI)
def unregister():
    bpy.utils.unregister_class(MakeInsulator)
    bpy.utils.unregister_class(MakeInsulatorUI)

if __name__ == '__main__':
    register()
