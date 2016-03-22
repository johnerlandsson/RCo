import bpy
import math

# make_line
# Returns a line segment
# p1: First point of line segment
# p2: Second point of line segment
# scene: Scene in wich to add the line segment
def make_line(p1, p2, scene):
    curveData = bpy.data.curves.new('Line', type = 'CURVE')
    curveData.dimensions = '3D'
    
    objectData = bpy.data.objects.new("Line", curveData)
    objectData.location = (0, 0, 0)
    objectData.data.use_fill_caps = True
    scene.objects.link(objectData)
    
    polyline = curveData.splines.new('POLY')
    polyline.points.add(2)
    polyline.points[0].co = (p1[0], p1[1], p1[2], 1)
    polyline.points[0].co = (p2[0], p2[1], p2[2], 1)
    
    return objectData

# make_tube_section
# Creates two joined circles
# outer_radius: Radius of the outer circle
# inner_radius: Radius of the inner circle
# context: Context in wich to create it
def make_tube_section(outer_radius, inner_radius, context):
    #Create outer circle
    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0))
    outer_circle = context.active_object
    outer_circle.scale = (outer_radius, outer_radius, 0)
    #Create inner circle
    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0))
    inner_circle = context.active_object
    inner_circle.scale = (inner_radius, inner_radius, 0)

    #Join circles
    bpy.ops.object.select_all(action='DESELECT')
    inner_circle.select = True
    outer_circle.select = True
    bpy.ops.object.join()
    bpy.context.scene.objects.active.name = "TubeSection"

    return context.active_object

# make_insulator
# Creates a tube representing the insulator
# inner_radius: The inner radius of plastic tube
# outer_radius: The outer radius of plastic tube
# length: Length of the part/cable in Z-axis
# peel_length: How much of the conductor that is visible        
def make_insulator(inner_radius, outer_radius, length, peel_length, context):
    insulator_circles = make_tube_section(outer_radius, inner_radius, context) 

    line = make_line((0, 0, 0), (0, 0, length), context.scene)
    line.data.bevel_object = insulator_circles
    line.data.use_fill_caps = True
    line.data.bevel_factor_start = peel_length
    line.name = "Insulator"
    
    context.scene.objects.active = line
    bpy.ops.object.select_all(action='DESELECT')
    line.select = True
    bpy.ops.object.convert(target='MESH')
    
    context.scene.objects.unlink(insulator_circles)

    return line

# about_eq
# Helper function to compare floating point values
def about_eq(a, b):
    if a + 0.000001 > b and a - 0.000001 < b:
        return True
    return False

# make_bezier_helix
# Returns a bezier curve in the shape of a spiral
# length: Total length in Z-axis
# pitch: Number of revolutions per length unit
# radius: Radius of helix
# context: context in wich to create the helix
def make_bezier_helix(length, pitch, radius, context):
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

    helixObject = bpy.data.objects.new('Helix', curveData)
    context.scene.objects.link(helixObject)

    return helixObject
