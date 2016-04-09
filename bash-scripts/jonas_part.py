import sys
import bpy
import cabletools as ct
import cablematerials as cm
import math

def printUsage():
    print("Usage: blender --background --python batch_part.py --[CONDUCTOR DIA]\
            [CONDUCTOR MATERIAL] [CONDUCTOR STRAND DIA] [INSULATOR DIA]\
            [INSULATOR PREASSURE TOOL] [INSULATOR MATERIAL] [FILENAME] [COLOR]")

def main():
#Handle arguments
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]

    conductor_r = float(argv[0]) / 2000.0
    conductor_material = argv[1]
    conductor_strand_r = float(argv[2]) / 2000.0
    insulator_r = float(argv[3]) / 2000.0

    preassure_tool = bool(argv[4])
    insulator_inner_r = conductor_r
    if preassure_tool:
        insulator_inner_r -= conductor_strand_r

    insulator_material = argv[5]

    filename = argv[6]

    color = cm.INSULATOR_COLORS[argv[7]]

    conductor_pitch = float(argv[8])

#Setup blender variables
    context = bpy.context
    scene = context.scene

#Create conductor
    if conductor_r == conductor_strand_r or ct.about_eq(conductor_strand_r, 0.0):
        conductor = ct.make_solid_conductor(0.53, conductor_r, context)
    else:
        conductor = ct.make_stranded_conductor(0.53, conductor_r,
                conductor_pitch, conductor_strand_r, context)
    conductor.rotation_euler = (0, math.pi / 2.0, 0)
    conductor.active_material = cm.CONDUCTOR_MATERIALS[conductor_material]()

#Create insulator
    insulator = ct.make_insulator(inner_radius = insulator_inner_r,
                                  outer_radius = insulator_r,
                                  length = 0.52,
                                  peel_length = 0.01,
                                  material = insulator_material,
                                  color = color,
                                  context = context)
    insulator.rotation_euler = (0, math.pi / 2.0, 0)


#Render image
    bpy.data.scenes["Scene"].camera = scene.objects["CamTop"]
    bpy.data.scenes["Scene"].render.filepath = "./" + filename + "_top.png"
    bpy.ops.render.render(write_still = True)

    bpy.data.scenes["Scene"].camera = scene.objects["CamBottom"]
    bpy.data.scenes["Scene"].render.filepath = "./" + filename + "_bottom.png"
    bpy.ops.render.render(write_still = True)

if __name__ == '__main__':
    main()
