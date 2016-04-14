bl_info = {
        "name": "Make braid",
        "category": "Object",
}

import bpy
import cabletools as ct

# Create properties

bpy.types.Scene.CT_make_braid_diameter = bpy.props.FloatProperty(
        name = "Diameter (mm)",
        description = "Inner diameter of the braid",
        default = 50,
        min = 10.0,
        max = 300.0)

bpy.types.Scene.CT_make_braid_strand_dia = bpy.props.FloatProperty(
        name = "Strand Diameter (mm)",
        description = "Total diameter of the individual strands",
        default = 0.4,
        min = 0.05,
        max = 3.0)

bpy.types.Scene.CT_make_braid_length = bpy.props.FloatProperty(
        name = "Length (m)",
        description = "Length of the braid",
        default = 0.25,
        min = 0.2,
        max = 10.0)

bpy.types.Scene.CT_make_braid_pitch = bpy.props.FloatProperty(
        name = "Pitch",
        description = "Number of revolutions per length unit",
        default = 8.33,
        min = 1.0,
        max = 20.0)

bpy.types.Scene.CT_make_braid_bundle_size = bpy.props.IntProperty(
        name = "Bundle size",
        description = "Number of strands in each bundle",
        default = 8,
        min = 1,
        max = 15)

bpy.types.Scene.CT_make_braid_n_bundle_pairs = bpy.props.IntProperty(
        name = "Number of pairs",
        description = "Number of bundle pairs in braid",
        default = 12,
        min = 1,
        max = 20)

bpy.types.Scene.CT_make_braid_material = bpy.props.EnumProperty(
        items = ct.CONDUCTOR_MATERIALS,
        name = "Material")

# Operator class
class MakeBraid(bpy.types.Operator):
    bl_idname = "ct.make_braid"
    bl_label = "Make braid"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        length = scene.CT_make_braid_length
        material = scene.CT_make_braid_material
        strand_radius = scene.CT_make_braid_strand_dia / 2000.0
        braid_radius = (scene.CT_make_braid_diameter / 2000.0) + 2.0 * strand_radius
        strand_pitch = scene.CT_make_braid_pitch
        bundle_size = scene.CT_make_braid_bundle_size
        n_bundle_pairs = scene.CT_make_braid_n_bundle_pairs

        ct.make_braid(length, braid_radius, strand_pitch,
                strand_radius, bundle_size, n_bundle_pairs, material, context)

        return {'FINISHED'}

# Panel class
class MakeBraidUI(bpy.types.Panel):
    bl_label = "Make braid"
    bl_idname = "OBJECT_PT_ct_make_braid_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_make_braid_diameter")
        layout.prop(scene, "CT_make_braid_strand_dia")
        layout.prop(scene, "CT_make_braid_length")
        layout.prop(scene, "CT_make_braid_material")
        layout.prop(scene, "CT_make_braid_pitch")
        layout.prop(scene, "CT_make_braid_bundle_size")
        layout.prop(scene, "CT_make_braid_n_bundle_pairs")
        layout.operator("ct.make_braid", text = "Make")

def register():
    bpy.utils.register_class(MakeBraid)
    bpy.utils.register_class(MakeBraidUI)
def unregister():
    bpy.utils.unregister_class(MakeBraid)
    bpy.utils.unregister_class(MakeBraidUI)

if __name__ == '__main__':
    register()
