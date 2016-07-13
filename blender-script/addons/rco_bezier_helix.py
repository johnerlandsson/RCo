bl_info = {
        "name": "Bezier helix",
        "category": "RCo",
}

import bpy
import rco

bpy.types.Scene.RCO_bezier_helix_radius = bpy.props.FloatProperty(
        name = "Radius",
        description = "Radius of the helix",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 1.0,
        min = 0.0001,
        max = 100.0)

bpy.types.Scene.RCO_bezier_helix_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Length of the helix in Z-axis",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 1.5,
        min = 0.01,
        max = 1000)

bpy.types.Scene.RCO_bezier_helix_pitch = bpy.props.FloatProperty(
        name = "Pitch",
        description = "Number of revolutions per length unit",
        default = 4.0,
        min = 0.1,
        max = 50.0)

bpy.types.Scene.RCO_bezier_helix_clockwize = bpy.props.BoolProperty(
        name = "Clockwize",
        description = "Direction of the helix")


class BezierHelix(bpy.types.Operator):
    bl_idname = "rco.bezier_helix"
    bl_label = "Bezier helix"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        length = scene.RCO_bezier_helix_length
        radius = scene.RCO_bezier_helix_radius
        pitch = scene.RCO_bezier_helix_pitch
        clockwize = scene.RCO_bezier_helix_clockwize

        rco.make_bezier_helix(length, pitch, radius, clockwize, 2.0, context)

        return {'FINISHED'}

class BezierHelixUI(bpy.types.Panel):
    bl_label = "Bezier helix"
    bl_idname = "OBJECT_PT_rco_bezier_helix_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Create'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "RCO_bezier_helix_length")
        layout.prop(scene, "RCO_bezier_helix_radius")
        layout.prop(scene, "RCO_bezier_helix_pitch")
        layout.prop(scene, "RCO_bezier_helix_clockwize")
        layout.operator("rco.bezier_helix", text = "Make")

def register():
    bpy.utils.register_class(BezierHelix)
    bpy.utils.register_class(BezierHelixUI)

def unregister():
    bpy.utils.unregister_class(BezierHelix)
    bpy.utils.unregister_class(BezierHelixUI)

if __name__ == '__main__':
    register()
