import bpy
import math
import cablematerials as cm

CONDUCTOR_MATERIALS = [('cu', 'CU', 'Standard copper'), 
                       ('cu-t', 'CU-Tinned', 'Tinned copper'), 
                       ('al', 'AL', 'Aluminium')]
INSULATOR_MATERIALS = [('pvc', 'PVC', 'PVC'), 
                       ('pe', 'PE', 'Polyethelene'), 
                       ('pex', 'PEX', 'Cross linked polyethelene')]
LAP_MATERIALS = [('cu', 'CU', 'Standard copper'), 
                 ('nylon', 'Nylon', 'Nylon filt lap')]

# make_line
# Returns a line segment
# p1: First point of line segment
# p2: Second point of line segment
# scene: Scene in wich to add the line segment
def make_line(p1, p2, n_subdiv, scene):
    curveData = bpy.data.curves.new('Line', type = 'CURVE')
    curveData.dimensions = '3D'
    
    objectData = bpy.data.objects.new("Line", curveData)
    objectData.location = (0, 0, 0)
    objectData.data.use_fill_caps = True
    objectData.data.use_fill_deform = True
    objectData.data.fill_mode = 'FULL'
    objectData.data.render_resolution_u = 0
    objectData.data.resolution_u = 20
    scene.objects.link(objectData)
    
    polyline = curveData.splines.new('POLY')
    if n_subdiv <= 2:
        polyline.points.add(2)
        polyline.points[0].co = (p1[0], p1[1], p1[2], 1)
        polyline.points[1].co = (p2[0], p2[1], p2[2], 1)
    else:
        polyline.points.add(n_subdiv - 1)
        x = p1[0]
        y = p1[1]
        z = p1[2]
        dx = (p2[0] - p1[0]) / (n_subdiv - 1)
        dy = (p2[1] - p1[1]) / (n_subdiv - 1)
        dz = (p2[2] - p1[2]) / (n_subdiv - 1)
        for i in range(n_subdiv):
            polyline.points[i].co = (x, y, z, 1.0)
            x += dx
            y += dy
            z += dz

    scene.objects.active = objectData
    #bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    #bpy.ops.curve.select_all(action='SELECT')
    #bpy.ops.curve.subdivide(number_cuts = n_subdiv)
    #bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    
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
def make_insulator(inner_radius, outer_radius, length, peel_length, material,
        color, context):
    insulator_circles = make_tube_section(outer_radius, inner_radius, context) 

    line = make_line((0, 0, 0), (0, 0, length), math.floor(length * 20.0), context.scene)
    line.data.bevel_object = insulator_circles
    line.data.use_fill_caps = True
    line.data.bevel_factor_start = peel_length
    line.name = "Insulator"
    
    context.scene.objects.active = line

    bpy.ops.object.select_all(action='DESELECT')
    line.select = True
    bpy.ops.object.convert(target='MESH')
    
    context.scene.objects.unlink(insulator_circles)

    #Create material
    line.active_material = cm.INSULATOR_MATERIALS[material](color)

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
def make_bezier_helix(length, pitch, radius, clockwize, n_subdivisions, context):
    #Calculate limits
    if about_eq(pitch, 0.0):
        return make_line((0, 0, 0), (0, 0, length), 20.0 * length,
                context.scene)

    if about_eq(length, 0.0):
        print("make_bezier_helix: length is zero")
        return None

    points_per_rev = 4.0 * n_subdivisions
    n_points = math.floor(length * pitch * points_per_rev)

    #Create a Bezier curve object
    curveData = bpy.data.curves.new('Spiral', type = 'CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 10
    curveData.render_resolution_u = 20
    curveData.use_fill_caps = True  
    polyline = curveData.splines.new('BEZIER')
    polyline.bezier_points.add(n_points)
    
    #Create points
    theta = 0.0
    for i in range(n_points + 1):
        z = length * (i / n_points)
        handle_hyp = math.sqrt(radius**2 + (radius / (points_per_rev / 2.0))**2)
        h_theta = math.acos(radius / handle_hyp)

        if clockwize:
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            lhx = handle_hyp * math.cos(theta - h_theta)
            rhx = handle_hyp * math.cos(theta + h_theta)
            lhy = handle_hyp * math.sin(theta - h_theta)
            rhy = handle_hyp * math.sin(theta + h_theta)
        else:
            x = radius * math.sin(theta)
            y = radius * math.cos(theta)
            lhx = handle_hyp * math.sin(theta - h_theta)
            rhx = handle_hyp * math.sin(theta + h_theta)
            lhy = handle_hyp * math.cos(theta - h_theta)
            rhy = handle_hyp * math.cos(theta + h_theta)

        polyline.bezier_points[i].co = (x, y, z)
        
        dhz = (length / n_points) / 4.0 
        lhz = z - dhz
        rhz = z + dhz
    
        polyline.bezier_points[i].handle_left = (lhx, lhy, lhz)
        polyline.bezier_points[i].handle_right = (rhx, rhy, rhz)
    
        polyline.bezier_points[i].handle_left_type = 'ALIGNED'
        polyline.bezier_points[i].handle_left_type = 'ALIGNED'
        
        theta += (2.0 * math.pi * pitch * length) / n_points

    helixObject = bpy.data.objects.new('Helix', curveData)
    context.scene.objects.link(helixObject)
    context.scene.objects.active = helixObject
    if not clockwize:
        helixObject.rotation_euler = (0, 0, math.pi * 1.5)

    return helixObject

# strand_positions
# Circle packing algorithm
# conductor_radius: Radius of the larger circle
# strand_radius: Radius of the smaller circle
# Returns: A list of tuples representing the points
def strand_positions(conductor_radius, strand_radius):
    rc = conductor_radius
    rs = strand_radius
    ret = []

    while True:
        no = int(math.floor((2.0 * math.pi * rc) / (2.0 * rs)))
        ps = []
        x0 = rc * math.cos( 0 * 2 * math.pi / no)
        y0 = rc * math.sin( 0 * 2 * math.pi / no)
        x1 = rc * math.cos( 1 * 2 * math.pi / no)
        y1 = rc * math.sin( 1 * 2 * math.pi / no)
        dist = math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

        if dist < 2.0 * rs:
            no -= 1

        for i in range(0, no):
            x = rc * math.cos(i * 2 * math.pi / no)
            y = rc * math.sin(i * 2 * math.pi / no)
            ps.append((x, y))

        ret.append(ps)

        rc_next = rc - (2.0 * rs)
        if rc_next < rs:
            if rc > 2.0 * rs:
                ret.append([(0, 0)])
            break
        else:
            rc = rc_next

    return ret


# make_solid_conductor
# Creates a single conductor core in the scene
# length: Total length of the conductor in Z-axis
# radius: Radius of the conductor
def make_solid_conductor(length, radius, context):
    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0))
    circle = context.active_object
    circle.scale = (radius, radius, 0)
    
    line = make_line((0, 0, 0), (0, 0, length), math.floor(length * 20.0), context.scene)
    line.name = "Conductor"
    line.data.bevel_object = circle
    line.data.use_fill_caps = True
    context.scene.objects.active = line
    line.select = True
    bpy.ops.object.convert(target='MESH')
    
    context.scene.objects.unlink(circle)
    
    return line

# make_stranded_conductor
# Creates a set of stranded conductor wires
# Use convenience function make_conductor instead of calling this directly
def make_stranded_conductor(length, conductor_radius, pitch, strand_radius,
                            context):
    #Create a list of points corresponding to the strand positions
    points = strand_positions(conductor_radius - strand_radius, strand_radius)

    #Create a circle to be used as a bevel object
    bpy.ops.curve.primitive_bezier_circle_add(location = (0, 0, 0))
    circle = context.active_object
    circle.scale = (strand_radius, strand_radius, 0)

    strands = []
    
    # iterate over the points and calculate positions of conductor helixes
    for row in points:
        r = math.sqrt(row[0][0]**2 + row[0][1]**2)
        dtheta = (2.0 * math.pi) / len(row)
        theta = 0.0

        for i in range(len(row)):
            # Use make_solid_conductor for centered strand
            if about_eq(r, 0.0):
                strands.append( make_solid_conductor(length, strand_radius,
                    context))
                continue
            
            if about_eq(pitch, 0.0):
                path = make_line((r, 0, 0), (r, 0, length), math.floor(length *
                    20.0), context.scene)
            else:
                path = make_bezier_helix(length = length, 
                                          pitch = pitch, 
                                          radius = r,
                                          clockwize = True,
                                          n_subdivisions = 1,
                                          context = context)

            path.rotation_euler = (0, 0, theta)

            # Add bevel object
            path.data.bevel_object = circle
            path.data.use_fill_caps = True
            path.data.use_fill_deform = True
            path.data.fill_mode = 'FULL'
            strands.append(path)
            
            # Convert beveled object to mesh
            bpy.ops.object.select_all(action='DESELECT')
                
            path.select = True
            context.scene.objects.active = path
            bpy.ops.object.convert(target='MESH')

            
            theta += dtheta
            
    # Join strands
    bpy.ops.object.select_all(action='DESELECT')
    for strand in strands:
        strand.select = True
    context.scene.objects.active = strands[0]

    bpy.ops.object.join()
    context.scene.objects.active.name = "Conductor"


    # Remove the circle that was used as a bevel object
    context.scene.objects.unlink(circle)

    return context.scene.objects.active

# make_conductor
# Creates a parametric conductor and puts it in the scene
# length: Total conductor length in Z-axis
# conductor_radius: Total radius of the combined conductor
# strand_radius: Diameter of each strand. 0.0 for solid conductor
# strand_pitch: Number of revolutions per length unit
# context: Context in wich to create the conductor object
def make_conductor(length, conductor_radius, strand_radius, 
        strand_pitch, material, context):
    # Solid conductor
    if conductor_radius == strand_radius or about_eq(strand_radius, 0.0):
        conductor = make_solid_conductor(length = length, radius = conductor_radius,
                                            context = context)
    # Stranded conductor
    else:
        conductor = make_stranded_conductor(length = length, 
                                   conductor_radius = conductor_radius, 
                                   pitch = strand_pitch, 
                                   strand_radius = strand_radius,
                                   context = context)

    conductor.active_material = cm.CONDUCTOR_MATERIALS[material]()

    return conductor
