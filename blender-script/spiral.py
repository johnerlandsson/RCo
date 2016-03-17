import bpy
import math

#Parameters
length = 2.0                #Z length of spiral
pitch = 2.0                 #Number of revolutions per length unit
radius = 1.0                #Radius of spiral
points_per_revolution = 8   #Number of points for every revolution of the spiral

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
    z = length * (theta / max_theta)
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    
    polyline.points[i].co = (x, y, z, 1)
    
    theta += (2.0 * math.pi) / points_per_revolution

#Add object to a scene
curveObject = bpy.data.objects.new('Spiral', curveData)
scn = bpy.context.scene
scn.objects.link(curveObject)
scn.objects.active = curveObject
curveObject.select = True