import sys
import bpy
import cabletools as ct
import cablematerials as cm
import math

def printUsage():
    print("Usage: blender --background --python batch_part.py --[CONDUCTOR DIA]\
            [CONDUCTOR MATERIAL] [CONDUCTOR STRAND DIA] [INSULATOR DIA]\
            [INSULATOR PREASSURE TOOL] [INSULATOR MATERIAL] [FILENAME]")

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

    print("%f %s %f %f %f %s %s" %(conductor_r, conductor_material,
        conductor_strand_r, insulator_r, insulator_inner_r, insulator_material,
        filename))

#Setup blender variables
    context = bpy.context
    scene = context.scene
    guideCurve = scene.objects["GuideCurve"]

#Create part
    tubeSection = ct.make_tube_section(insulator_r, insulator_inner_r, context)
    guideCurve.data.bevel_object = tubeSection
    guideCurve.location = (0, 0, insulator_r)
    guideCurve.active_material = cm.INSULATOR_MATERIALS[insulator_material]((0.056, 0.593, 0.01))
    
    if conductor_r == conductor_strand_r or ct.about_eq(conductor_strand_r, 0.0):
        conductor = ct.make_solid_conductor(0.02, conductor_r, context)
    else:
        conductor = ct.make_stranded_conductor(0.02, conductor_r, 1.0 / 0.045,
                conductor_strand_r, context)

    conductor.rotation_euler = (0, math.pi / 2.0, 0)
    conductor.location = (0.22, 0, insulator_r)
    conductor.active_material = cm.CONDUCTOR_MATERIALS[conductor_material]()

#Render image
    bpy.data.scenes["Scene"].render.filepath = "./" + filename
    bpy.ops.render.render(write_still = True)


if __name__ == '__main__':
    main()
