bl_info = {
    "name": "Creates a central filler",
    "category": "RCo",
}

import bpy
import cabletools as ct

# Create properties

bpy.types.Scene.CT_make_central_filler_diameter = bpy.props.FloatProperty(
    name="Diameter",
    description="Outer diameter of the filler",
    default=0.006,
    subtype='DISTANCE',
    unit='LENGTH',
    min=0.002,
    max=0.3)

bpy.types.Scene.CT_make_central_filler_length = bpy.props.FloatProperty(
    name="Length",
    description="Length of the filler",
    default=0.27,
    subtype='DISTANCE',
    unit='LENGTH',
    min=0.01,
    max=2.0)

bpy.types.Scene.CT_make_central_filler_material = bpy.props.EnumProperty(
        items = ct.INSULATOR_MATERIALS,
        name = "Material")


class MakeCentralFiller(bpy.types.Operator):
    bl_idname = "ct.make_central_filler"
    bl_label = "Make central filler"
    bl_options = {'REGISTER'}

    def execute(self, context):
        radius = context.scene.CT_make_central_filler_diameter / 2
        length = context.scene.CT_make_central_filler_length
        material = context.scene.CT_make_central_filler_material

        ct.make_central_filler(length, radius, 0.001, material, context)

        return {'FINISHED'}

class MakeCentralFillerUI(bpy.types.Panel):
    bl_label = "Make central filler"
    bl_idname = "OBJECT_PT_ct_make_central_filler_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_make_central_filler_length")
        layout.prop(scene, "CT_make_central_filler_diameter")
        layout.prop(scene, "CT_make_central_filler_material")
        layout.operator("ct.make_central_filler", text="Make")

def register():
    bpy.utils.register_class(MakeCentralFiller)
    bpy.utils.register_class(MakeCentralFillerUI)

def unregister():
    bpy.utils.unregister_class(MakeCentralFiller)
    bpy.utils.unregister_class(MakeCentralFillerUI)


if __name__ == '__main__':
    register()
