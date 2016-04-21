import bpy
import cabletools as ct

bl_info = {
        "name": "Striped tube section",
        "category": "Object",
}

bpy.types.Scene.CT_striped_tube_section_outer_dia = bpy.props.FloatProperty(
        name = "Outer diameter",
        description = "Diameter of outer circle",
        default = 1.5,
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        min = 0.1,
        max = 100.0)

bpy.types.Scene.CT_striped_tube_section_inner_dia = bpy.props.FloatProperty(
        name = "Inner diameter",
        description = "Diameter of inner circle",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 1.0,
        min = 0.1,
        max = 100.0)

bpy.types.Scene.CT_striped_tube_section_amount = bpy.props.FloatProperty(
        name = "Amount",
        description = "Amount of circomference to be striped",
        subtype = 'PERCENTAGE',
        unit = 'NONE',
        default = 40.0,
        min = 1.0,
        max = 50.0)

bpy.types.Scene.CT_striped_tube_section_double_sided = bpy.props.BoolProperty(
        name = "Double sided",
        description = "Stripe on one side or both?",
        default = False)


class StripedTubeSection(bpy.types.Operator):
    bl_idname = "ct.striped_tube_section"
    bl_label = "Striped tube section"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        outer_radius = scene.CT_striped_tube_section_outer_dia / 2.0
        inner_radius = scene.CT_striped_tube_section_inner_dia / 2.0
        amount = scene.CT_striped_tube_section_amount * 0.01
        double_sided = scene.CT_striped_tube_section_double_sided

        ct.make_striped_tube_section(outer_radius, inner_radius, amount,
                double_sided, context)

        return {'FINISHED'}

class StripedTubeSectionUI(bpy.types.Panel):
    bl_label = "Striped tube section"
    bl_idname = "OBJECT_PT_ct_striped_tube_section_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Create'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_striped_tube_section_outer_dia")
        layout.prop(scene, "CT_striped_tube_section_inner_dia")
        layout.prop(scene, "CT_striped_tube_section_amount")
        layout.prop(scene, "CT_striped_tube_section_double_sided")
        layout.operator("ct.striped_tube_section", text = "Make")

def register():
    bpy.utils.register_class(StripedTubeSection)
    bpy.utils.register_class(StripedTubeSectionUI)

def unregister():
    bpy.utils.unregister_class(StripedTubeSection)
    bpy.utils.unregister_class(StripedTubeSectionUI)

if __name__ == '__main__':
    register()
