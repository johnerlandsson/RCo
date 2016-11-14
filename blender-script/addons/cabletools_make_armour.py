bl_info = {
        "name": "Make armour",
        "category": "RCo",
}

import bpy
import cabletools as ct

# Create properties
bpy.types.Scene.CT_make_armour_diameter = bpy.props.FloatProperty(
        name = "Diameter",
        description = "Total diameter of the armour",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.005,
        min = 0.0005,
        max = 0.3)

bpy.types.Scene.CT_make_armour_strand_dia = bpy.props.FloatProperty(
        name = "Strand Diameter",
        description = "Total diameter of the individual strands",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.0008,
        min = 0.0001,
        max = 0.01)

bpy.types.Scene.CT_make_armour_n_strands = bpy.props.IntProperty(
        name = "Number of strands",
        description = "Number of strands in armour",
        default = 10,
        min = 2,
        max = 500)

bpy.types.Scene.CT_make_armour_length = bpy.props.FloatProperty(
        name = "Length",
        description = "Length of the armour",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.25,
        min = 0.1,
        max = 10.0)

bpy.types.Scene.CT_make_armour_pitch = bpy.props.FloatProperty(
        name = "Pitch",
        description = "Axial length between revolutions",
        subtype = 'DISTANCE',
        unit = 'LENGTH',
        default = 0.28,
        min = 0.0,
        max = 1)

bpy.types.Scene.CT_make_armour_clockwize = bpy.props.BoolProperty(
        name = "Clockwize",
        description = "Direction of the pitch")

bpy.types.Scene.CT_make_armour_material = bpy.props.EnumProperty(
        items = ct.CONDUCTOR_MATERIALS,
        name = "Material")

# Operator class
class MakeArmour(bpy.types.Operator):
    bl_idname = "ct.make_armour"
    bl_label = "Make armour"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        length = scene.CT_make_armour_length
        material = scene.CT_make_armour_material
        armour_radius = scene.CT_make_armour_diameter / 2.0
        strand_radius = scene.CT_make_armour_strand_dia / 2.0
        strand_pitch = 1.0 / scene.CT_make_armour_pitch
        n_strands = scene.CT_make_armour_n_strands
        clockwize = scene.CT_make_armour_clockwize 

        ct.make_armour(length=length, 
                       radius=armour_radius, 
                       strand_radius=strand_radius,
                       n_strands=n_strands, 
                       pitch=strand_pitch, 
                       clockwize=clockwize,
                       material=material, 
                       context=context)

        return {'FINISHED'}

# Panel class
class MakeArmourUI(bpy.types.Panel):
    bl_label = "Make armour"
    bl_idname = "OBJECT_PT_ct_make_armour_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cable Tools'
    bl_translation_context = '*'
    bl_context = ''

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, "CT_make_armour_diameter")
        layout.prop(scene, "CT_make_armour_strand_dia")
        layout.prop(scene, "CT_make_armour_n_strands")
        layout.prop(scene, "CT_make_armour_length")
        layout.prop(scene, "CT_make_armour_material")
        layout.prop(scene, "CT_make_armour_pitch")
        layout.prop(scene, "CT_make_armour_clockwize")
        layout.operator("ct.make_armour", text = "Make")

def register():
    bpy.utils.register_class(MakeArmour)
    bpy.utils.register_class(MakeArmourUI)
def unregister():
    bpy.utils.unregister_class(MakeArmour)
    bpy.utils.unregister_class(MakeArmourUI)

if __name__ == '__main__':
    register()
