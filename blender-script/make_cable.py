import bpy
import math

def make_circle(radius):
    n_points = 32
    curveData = bpy.data.curves.new('Circle', type = 'CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 12
    polyline = curveData.splines.new('NURBS')
    curveData.splines[0].use_cyclic_u = True
    polyline.points.add(n_points + 1)
    
    theta = 0.0
    for i in range(n_points + 1):
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        z = 0
        
        polyline.points[i].co = (x, y, z, 1)
        
        theta += (2.0 * math.pi) / n_points
        
    
    return bpy.data.objects.new('Circle', curveData)

def make_spiral(length, pitch, radius, start_angle = 0.0, points_per_revolution = 32):
    #Calculate limits
    max_theta = length * pitch * 2.0 * math.pi
    n_points = 2 + int(max_theta / ((2.0 * math.pi) / points_per_revolution))

    #Create a NURBS curve ovject
    curveData = bpy.data.curves.new('Spiral', type = 'CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 12
    polyline = curveData.splines.new('NURBS')
    polyline.points.add(n_points)

    #Create points
    theta = 0.0
    for i in range(n_points):
        z = length * (i / n_points)
        x = radius * math.cos(theta + start_angle)
        y = radius * math.sin(theta + start_angle)
        
        polyline.points[i].co = (x, y, z, 1)
        
        theta += (2.0 * math.pi) / points_per_revolution

    #Add object to a scene
    return bpy.data.objects.new('Spiral', curveData)

def rotation_normal_to_spiral(spiral):
    if len(spiral.data.splines[0].points) < 2:
        print("rotation_normal_to_spiral: Not enough points in spiral.")
        return None
    
    p1 = spiral.data.splines[0].points[0].co[0:3]
    p2 = spiral.data.splines[0].points[1].co[0:3]
    
    rx = 1/math.acos(p1[0] - p2[0])
    ry = 1/math.asin(p1[1] - p2[1])
    rz = 1/math.asin(p1[2] - p2[2])
    print("%f, %f, %f" %(p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2]))
    print("%f, %f, %f" %(rx, ry, rz))
    
    return (rx, ry, rz)

def draw_spiral_part(length, part_radius, pitch, pitch_radius, start_angle): 
    spiral = make_spiral(length, pitch, pitch_radius, start_angle)
    scn = bpy.context.scene
    scn.objects.link(spiral)
    scn.objects.active = spiral

    circle = make_circle(part_radius)
    scn.objects.link(circle)
    scn.objects.active = circle
    circle.rotation_mode = 'XYZ'
    print(type(circle))
    #circle.rotation_euler = rotation_normal_to_spiral(spiral)
    circle.location = (pitch_radius, 0, 0)

    spiral.data.bevel_object = circle

for i in range(6):
    theta = i * ((2.0 * math.pi) / 6)
    draw_spiral_part(3.0, 0.05, 0.5, 0.12, theta)

#print("%f, %f, %f" %(rot[0], rot[1], rot[2]))