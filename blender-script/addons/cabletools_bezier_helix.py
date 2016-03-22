bl_info = {
        "name": "Bezier helix",
        "category": "Object",
}

import bpy
import cabletools as ct

bpy.types.Scene.CT_bezier_helix_radius = bpy.props.FloatProperty(
        name = "Radius",
        description = "Radius of the helix",
        default = 1.0,
        min = 0.001,
        max = 100.0)

bpy.types.Scene.CT_bezier_helix_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Length of the helix in Z-axis",
        default = 1.5,
        min = 0.01,
        max = 100.0)

bpy.types.Scene.CT_bezier_helix_pitch = bpy.props.FloatProperty(
        name = "Pitch",
        description = "Number of revolutions per length unit",
        default = 4.0,
        min = 0.1,
        max = 50.0)

bpy.types.Scene.CT_bezier_helix_clockwize = bpy.props.BoolProperty(
        name = "Clockwize",
        description = "Direction of the helix")


class BezierHelix(bpy.types.Operator):
    bl_idname = "ct.bezier_helix"
    bl_label = "Bezier helix"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        length = scene.CT_bezier_helix_length
        radius = scene.CT_bezier_helix_radius
        pitch = scene.CT_bezier_helix_pitch
        clockwize = scene.CT_bezier_helix_clockwize

        ct.make_bezier_helix(length, pitch, radius, clockwize, context)

        return {'FINISHED'}

class BezierHelixUI(bpy.types.Panel):
    bl_label = "Bezier helix"
    bl_idname = "OBJECT_PT_ct_bezier_helix_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_bezier_helix_length")
        layout.prop(scene, "CT_bezier_helix_radius")
        layout.prop(scene, "CT_bezier_helix_pitch")
        layout.prop(scene, "CT_bezier_helix_clockwize")
        layout.operator("ct.bezier_helix", text = "Make")

def register():
    bpy.utils.register_class(BezierHelix)
    bpy.utils.register_class(BezierHelixUI)

def unregister():
    bpy.utils.unregister_class(BezierHelix)
    bpy.utils.unregister_class(BezierHelixUI)

if __name__ == '__main__':
    register()
