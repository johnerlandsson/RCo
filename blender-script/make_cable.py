import bpy
import math

WORK_LAYER = [False, True, False, False, False, False, False, 
              False, False, False, False, False, False, False, 
              False, False, False, False, False, False]
JUNK_LAYER = [False, False, True, False, False, False, False, 
              False, False, False, False, False, False, False, 
              False, False, False, False, False, False]

# make_line
# Returns a line segment
# p1: First point of line segment
# p2: Second point of line segment
def make_line(p1, p2):
    curveData = bpy.data.curves.new('Line', type = 'CURVE')
    curveData.dimensions = '3D'
    #curveData.resolution_u = 12
    
    objectData = bpy.data.objects.new("objLine", curveData)
    objectData.location = (0, 0, 0)
    objectData.data.use_fill_caps = True
    bpy.context.scene.objects.link(objectData)
    
    polyline = curveData.splines.new('POLY')
    polyline.points.add(2)
    polyline.points[0].co = (p1[0], p1[1], p1[2], 1)
    polyline.points[0].co = (p2[0], p2[1], p2[2], 1)
    
    return objectData
 
# about_eq
# Helper function to compare floating point values
def about_eq(a, b):
    if a + 0.0001 > b and a - 0.0001 < b:
        return True
    return False

# make_bezier_spiral
# Returns a bezier curve in the shape of a spiral
# length: Total length in Z-axis
# pitch: Number of revolutions per length unit
# radius: Radius of spiral
def make_bezier_spiral(length, pitch, radius):
    #Calculate limits
    n_points = int(length * pitch * 4.0)
    
    #Create a Bezier curve object
    curveData = bpy.data.curves.new('Spiral', type = 'CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 0
    curveData.use_fill_caps = True  
    polyline = curveData.splines.new('BEZIER')
    polyline.bezier_points.add(n_points)
    
    #Create points
    theta = 0.0
    for i in range(n_points + 1):
        z = length * (i / n_points)
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        polyline.bezier_points[i].co = (x, y, z)
        
        if about_eq(x, 0.0) and about_eq(y, radius):
            lhy = y
            rhy = y
            lhx = (radius / 2.0)
            rhx = -(radius / 2.0)
        if about_eq(x, 0.0) and about_eq(y, -radius):
            lhy = y
            rhy = y
            lhx = -(radius / 2.0)
            rhx = (radius / 2.0)
        if about_eq(x, radius) and about_eq(y, 0.0):
            lhx = x
            rhx = x
            lhy = -(radius / 2.0)
            rhy = (radius / 2.0)
        if about_eq(x, -radius) and about_eq(y, 0.0):
            lhx = x
            rhx = x
            lhy = (radius / 2.0)
            rhy = -(radius / 2.0)
               
               
        dhz = (length / n_points) / 4.0 
        lhz = z - dhz
        rhz = z + dhz
    
        polyline.bezier_points[i].handle_left = (lhx, lhy, lhz)
        polyline.bezier_points[i].handle_right = (rhx, rhy, rhz)
    
        polyline.bezier_points[i].handle_left_type = 'ALIGNED'
        polyline.bezier_points[i].handle_left_type = 'ALIGNED'
        
        print("%f, %f, %f" %(x, y, z))
        
        theta += (2.0 * math.pi) / 4.0

    #Add object to a scene
    return bpy.data.objects.new('Spiral', curveData)

def strand_positions(conductor_radius, strand_radius):
    ret = []

    while True:
        no = int(math.floor((2.0 * math.pi * conductor_radius) / (2.0 * strand_radius)))
        ps = []
        x0 = conductor_radius * math.cos( 0 * 2 * math.pi / no)
        y0 = conductor_radius * math.sin( 0 * 2 * math.pi / no)
        x1 = conductor_radius * math.cos( 1 * 2 * math.pi / no)
        y1 = conductor_radius * math.sin( 1 * 2 * math.pi / no)
        dist = math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

        if dist < 2.0 * strand_radius:
            no -= 1

        for i in range(0, no):
            x = conductor_radius * math.cos(i * 2 * math.pi / no)
            y = conductor_radius * math.sin(i * 2 * math.pi / no)
            ps.append((x, y))

        ret.append(ps)

        rc_next = conductor_radius - (2.0 * strand_radius)
        if rc_next < strand_radius:
            if conductor_radius > 2.0 * strand_radius:
                ret.append([(0, 0)])
            break
        else:
            conductor_radius = rc_next

    return ret

def make_solid_conductor(length, radius):
    line = make_line((0, 0, 0), (0, 0, length))
    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0), layers = JUNK_LAYER)
    circle = bpy.context.active_object
    circle.scale = (radius, radius, 0)
    
    line.data.bevel_object = circle
    line.data.use_fill_caps = True
    
     
    

def make_conductor(length, conductor_radius, strand_radius):
    if conductor_radius == strand_radius or strand_radius == None:
        return make_solid_conductor(length, conductor_radius)
    
    return make_stranded_conductor(length, conductor_radius, strand_radius)        
        
        
        
make_conductor(3.0, 0.00162 / 2.0, None)