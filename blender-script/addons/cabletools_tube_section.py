bl_info = {
        "name": "Tube section",
        "category": "Object",
}

import bpy
import rco

bpy.types.Scene.RCO_tube_section_outer_dia = bpy.props.FloatProperty(
        name = "Outer diameter",
        description = "Diameter of outer circle",
        default = 1.5,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        min = 0.1,
        max = 100.0)

bpy.types.Scene.RCO_tube_section_inner_dia = bpy.props.FloatProperty(
        name = "Inner diameter",
        description = "Diameter of inner circle",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 1.0,
        min = 0.1,
        max = 100.0)

class TubeSection(bpy.types.Operator):
    bl_idname = "rco.tube_section"
    bl_label = "Tube section"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        outer_radius = scene.RCO_tube_section_outer_dia / 2.0
        inner_radius = scene.RCO_tube_section_inner_dia / 2.0
        rco.make_tube_section(outer_radius, inner_radius, context)

        return {'FINISHED'}

class TubeSectionUI(bpy.types.Panel):
    bl_label = "Tube section"
    bl_idname = "OBJECT_PT_ct_tube_section_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Create'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "RCO_tube_section_outer_dia")
        layout.prop(scene, "RCO_tube_section_inner_dia")
        layout.operator("rco.tube_section", text = "Make")

def register():
    bpy.utils.register_class(TubeSection)
    bpy.utils.register_class(TubeSectionUI)

def unregister():
    bpy.utils.unregister_class(TubeSection)
    bpy.utils.unregister_class(TubeSectionUI)

if __name__ == '__main__':
    register()
