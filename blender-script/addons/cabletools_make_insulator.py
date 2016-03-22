bl_info = {
        "name": "Make insulator",
        "category": "Object",
}

import bpy
import cabletools as ct

bpy.types.Scene.CT_make_insulator_outer_dia = bpy.props.FloatProperty(
        name = "Outer Diameter",
        description = "Total diameter of the insulator",
        default = 3.0,
        min = 1.0,
        max = 300.0)

bpy.types.Scene.CT_make_insulator_inner_dia = bpy.props.FloatProperty(
        name = "Inner Diameter",
        description = "Total diameter of the insulators hole",
        default = 1.62,
        min = 0.5,
        max = 250.0)

bpy.types.Scene.CT_make_insulator_length = bpy.props.FloatProperty(
        name = "Length (m)",
        description = "Length of the insulator",
        default = 1.5,
        min = 0.5,
        max = 10.0)

class MakeInsulator(bpy.types.Operator):
    bl_idname = "ct.make_insulator"
    bl_label = "Make insulator"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        outer_radius = scene.CT_make_insulator_outer_dia / 2000.0
        inner_radius = scene.CT_make_insulator_inner_dia / 2000.0
        length = scene.CT_make_insulator_length

        ct.make_insulator(outer_radius, inner_radius, length, 0.0, context)

        return {'FINISHED'}

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
        layout.operator("ct.make_insulator", text = "Make")

def register():
    bpy.utils.register_class(MakeInsulator)
    bpy.utils.register_class(MakeInsulatorUI)
def unregister():
    bpy.utils.unregister_class(MakeInsulator)
    bpy.utils.unregister_class(MakeInsulatorUI)

if __name__ == '__main__':
    register()
