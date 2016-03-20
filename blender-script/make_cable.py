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
    
    objectData = bpy.data.objects.new("Line", curveData)
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
        #Calculate positions
        z = length * (i / n_points)
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        polyline.bezier_points[i].co = (x, y, z)
        
        #Calculate handle positions for each quadrant
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
        
        theta += (2.0 * math.pi) / 4.0

    return bpy.data.objects.new('Spiral', curveData)

# strand_positions
# Circle packing algorithm
# conductor_radius: Radius of the larger circle
# strand_radius: Radius of the smaller circle
# Returns: A list of tuples representing the points
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

# make_solid_conductor
# Creates a single conductor core in the scene
# length: Total length of the conductor in Z-axis
# radius: Radius of the conductor
def make_solid_conductor(length, radius):
    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0), layers = JUNK_LAYER)
    circle = bpy.context.active_object
    circle.scale = (radius, radius, 0)
    
    line = make_line((0, 0, 0), (0, 0, length))    
    line.data.bevel_object = circle
    line.data.use_fill_caps = True
    bpy.context.scene.objects.active = line
    line.select = True
    bpy.ops.object.convert(target='MESH')
    
    bpy.context.scene.objects.unlink(circle)
    
    return line

# make_stranded_conductor
# Creates a set of stranded conductor wires
# Use convenience function make_conductor instead of calling this directly
def make_stranded_conductor(length, conductor_radius, pitch, strand_radius):
    points = strand_positions(conductor_radius, strand_radius)
    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0), layers = JUNK_LAYER)
    circle = bpy.context.active_object
    circle.scale = (strand_radius, strand_radius, 0)
        
    for row in points:
        r = math.sqrt(row[0][0]**2 + row[0][1]**2)
        dtheta = (2.0 * math.pi) / len(row)
        theta = 0.0
        for i in range(len(row)):
            if about_eq(r, 0.0):
                make_solid_conductor(length, strand_radius)
                continue
            
            spiral = make_bezier_spiral(length, pitch, r)
            bpy.context.scene.objects.link(spiral)            
            spiral.rotation_euler = (0, 0, theta)
            spiral.data.bevel_object = circle
            spiral.data.use_fill_caps = True
            
            for obj in bpy.context.scene.objects:
                obj.select = False
                
            spiral.select = True
            bpy.context.scene.objects.active = spiral
            bpy.ops.object.convert(target='MESH')
            
            theta += dtheta
            
    bpy.context.scene.objects.unlink(circle)
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and (obj.name.startswith("Line") or obj.name.startswith("Spiral")):
            obj.select = True
        else:
            obj.select = False

    bpy.ops.object.join()
    bpy.context.scene.objects.active.name = "Conductor"

# make_conductor
# Creates a parametric conductor and puts it in the scene
def make_conductor(length, conductor_radius, strand_radius, strand_pitch):
    if conductor_radius == strand_radius or strand_radius == None:
        return make_solid_conductor(length, conductor_radius)
    
    return make_stranded_conductor(length, conductor_radius, strand_pitch, strand_radius)        

# make_insulator
# Creates a tube representing the insulator
# inner_radius: The inner radius of plastic tube
# outer_radius: The outer radius of plastic tube
# length: Length of the part/cable in Z-axis
# peel_length: How much of the conductor that is visible        
def make_insulator(inner_radius, outer_radius, length, peel_length):
    bpy.ops.object.select_all(action='DESELECT')
        
    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0), layers = JUNK_LAYER)
    inner_circle = outer_circle = bpy.context.scene.objects.active            
    inner_circle.scale = (inner_radius, inner_radius, 0)

    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0), layers = JUNK_LAYER)
    outer_circle = bpy.context.scene.objects.active
    outer_circle.scale = (outer_radius, outer_radius, 0)

    outer_circle.select = True
    inner_circle.select = True
    bpy.ops.object.join()
    
    insulator_circles = bpy.context.scene.objects.active
    
    line = make_line((0, 0, 0), (0, 0, length))
    line.data.bevel_object = insulator_circles
    line.data.use_fill_caps = True
    line.data.bevel_factor_start = peel_length
    line.name = "Insulator"
    
    bpy.context.scene.objects.active = line
    bpy.ops.object.select_all(action='DESELECT')
    line.select = True
    bpy.ops.object.convert(target='MESH')
    
    bpy.context.scene.objects.unlink(insulator_circles)
        
# make_part
# Creates a parametric part and puts it into the scene
def make_part(length = 1.0, conductor_radius = 1.0, insulator_radius = 2.0, insulator_peel_length = 0.01,
                conductor_strand_radius = None, conductor_strand_pitch = 1.0):
    make_conductor(length, conductor_radius, conductor_strand_radius, conductor_strand_pitch)
    conductor = bpy.context.scene.objects.active
    
    make_insulator(conductor_radius, insulator_radius, length, insulator_peel_length)
    insulator = bpy.context.scene.objects.active
    
    #Group insulator and conductor
    insulator.parent = conductor




make_part(1.0, 0.0015, 0.003, 0.01, 0.0005, 4.0)

