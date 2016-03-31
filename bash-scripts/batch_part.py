#!/bin/python

import sys
import os

def main():
#Handle arguments
    argv = sys.argv

    csv = []
    csv.append({'conductor_dia': 1.62, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.52, 
                'conductor_pitch': 0.0,
                'preassure_tool': False, 
                'insulator_material': 'pvc',
                'insulator_dia': 3.0,
                'name': 'fk1.5',
                'colors': ['red', 'green', 'blue', 'yellow']})

    csv.append({'conductor_dia': 1.62, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.52, 
                'conductor_pitch': 0.0,
                'preassure_tool': False, 
                'insulator_material': 'pe',
                'insulator_dia': 3.0,
                'name': 'fq1.5',
                'colors': ['red', 'green', 'blue', 'yellow']})

    csv.append({'conductor_dia': 2.05, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.66, 
                'conductor_pitch': 0.0,
                'preassure_tool': False, 
                'insulator_material': 'pvc',
                'insulator_dia': 3.6,
                'name': 'fk2.5',
                'colors': ['red', 'green', 'blue', 'yellow']})

    csv.append({'conductor_dia': 2.05, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.66, 
                'conductor_pitch': 0.0,
                'preassure_tool': False, 
                'insulator_material': 'pe',
                'insulator_dia': 3.6,
                'name': 'fq2.5',
                'colors': ['red', 'green', 'blue', 'yellow']})

    csv.append({'conductor_dia': 2.55, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.3, 
                'conductor_pitch': 1.0 / 0.045,
                'preassure_tool': False, 
                'insulator_material': 'pvc',
                'insulator_dia': 4.1,
                'name': 'rk4',
                'colors': ['red', 'green', 'blue', 'yellow']})

    csv.append({'conductor_dia': 2.55, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.3, 
                'conductor_pitch': 1.0 / 0.045,
                'preassure_tool': False, 
                'insulator_material': 'pe',
                'insulator_dia': 4.1,
                'name': 'rq4',
                'colors': ['red', 'green', 'blue', 'yellow']})

    csv.append({'conductor_dia': 3.15, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.3, 
                'conductor_pitch': 1.0 / 0.045,
                'preassure_tool': False, 
                'insulator_material': 'pvc',
                'insulator_dia': 4.7,
                'name': 'rk6',
                'colors': ['red', 'green', 'blue', 'yellow']})

    csv.append({'conductor_dia': 3.15, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.3, 
                'conductor_pitch': 1.0 / 0.045,
                'preassure_tool': False, 
                'insulator_material': 'pe',
                'insulator_dia': 4.7,
                'name': 'rq6',
                'colors': ['red', 'green', 'blue', 'yellow']})

    csv.append({'conductor_dia': 1.8, 
                'conductor_material': 'cu', 
                'conductor_strand_dia': 0.0, 
                'conductor_pitch': 0.0,
                'preassure_tool': False, 
                'insulator_material': 'pvc',
                'insulator_dia': 3.4,
                'name': 'ek2.5',
                'colors': ['red', 'green', 'blue', 'yellow']})

    for part in csv:
        conductor_dia = float(part['conductor_dia'])
        conductor_material = part['conductor_material']
        conductor_strand_dia = float(part['conductor_strand_dia'])
        conductor_pitch = float(part['conductor_pitch'])
        preassure_tool = str(part['preassure_tool'])
        insulator_material = part['insulator_material']
        insulator_dia = float(part['insulator_dia'])
        for color in part['colors']:
            filename = part['name'] + "-" + color + '.png'

            cmd = "blender --background ../blender_scenes/part_scene.blend --python part_scene.py -- %f %s %f %f %s %s %s %s %f"\
                %(conductor_dia, conductor_material, conductor_strand_dia, insulator_dia, preassure_tool,
                    insulator_material, filename, color, conductor_pitch)

            print(cmd)
            os.system(cmd)


if __name__ == '__main__':
    main()
