#!/bin/python

import sys
import os

def main():
#Handle arguments
    argv = sys.argv

    conductor_dia = 1.62
    conductor_material = "cu"
    conductor_strand_dia = 0.52
    preassure_tool = "False"
    insulator_material = "pvc"
    insulator_dia = 3.0
    filename = "fk1.5.png"

    cmd = "blender --background ../blender_scenes/part_scene.blend --python\
    part_scene.py -- %f %s %f %f %s %s %s" %(conductor_dia, conductor_material,
            conductor_strand_dia, insulator_dia, preassure_tool,
            insulator_material, filename)

    os.system(cmd)


if __name__ == '__main__':
    main()
