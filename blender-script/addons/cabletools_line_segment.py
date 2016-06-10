bl_info = {
        "name": "Line segment",
        "category": "Object",
}

import bpy
import cabletools as ct
import math

bpy.types.Scene.CT_line_segment_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Length of line segment in Z-axis",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 1.5,
        min = 0.1,
        max = 10.0)

class LineSegment(bpy.types.Operator):
    bl_idname = "ct.line_segment"
    bl_label = "Line segment"
    bl_options = {'REGISTER'}

    def execute(self, context):
        length = context.scene.CT_line_segment_length

        ct.make_line((0, 0, 0), (0, 0, length), math.floor(length * 10.0),
                context)

        return {'FINISHED'}

class LineSegmentUI(bpy.types.Panel):
    bl_label = "Line segment"
    bl_idname = "OBJECT_PT_ct_line_segment_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Create'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_line_segment_length")
        layout.operator("ct.line_segment", text = "Make")

def register():
    bpy.utils.register_class(LineSegment)
    bpy.utils.register_class(LineSegmentUI)

def unregister():
    bpy.utils.unregister_class(LineSegment)
    bpy.utils.unregister_class(LineSegmentUI)

if __name__ == '__main__':
    register()
