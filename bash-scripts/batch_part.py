#!/bin/python

from __future__ import print_function
import sys
import os
import csv

def read_csv(filename):
    ret = [] 
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter = ';')

        for row in reader:
            row['conductor_dia'] = float(row['conductor_dia'])
            row['insulator_dia'] = float(row['insulator_dia'])
            row['conductor_strand_dia'] = float(row['conductor_strand_dia'])
            row['conductor_pitch'] = float(row['conductor_pitch'])
            row['preassure_tool'] = not bool(row['preassure_tool'])
            row['colors'] = row['colors'].split()

            ret.append(row)

    csvfile.close()

    return ret

def main():
#Handle arguments
    if len(sys.argv) < 3:
        print("Need exactly 2 arguments. CSV file and output dir", file=sys.stderr)
        return -1

    csvdata = read_csv(sys.argv[1])
    output_dir = sys.argv[2]
    if output_dir[-1] != '/':
        output_dir += '/'

    for part in csvdata:
        conductor_dia = float(part['conductor_dia'])
        conductor_material = part['conductor_material']
        conductor_strand_dia = float(part['conductor_strand_dia'])
        conductor_pitch = float(part['conductor_pitch'])
        preassure_tool = str(part['preassure_tool'])
        insulator_material = part['insulator_material']
        insulator_dia = float(part['insulator_dia'])

        blender_cmd = "/home/john/src/blender-2.77-linux-glibc211-x86_64/blender --background"
        for color in part['colors']:
            filename = part['name'] + "-" + color

            cmd = "%s ../blender-scenes/jonas_part.blend --python jonas_part.py -- %f %s %f %f %s %s \"%s\" %s %f"\
                %(blender_cmd, conductor_dia, conductor_material, conductor_strand_dia, insulator_dia, preassure_tool,
                    insulator_material, output_dir + filename, color, conductor_pitch)

            print(cmd)
            os.system(cmd)


if __name__ == '__main__':
    main()
