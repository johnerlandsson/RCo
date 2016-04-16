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

JUNK_LAYER = (False, False, False, False, False, False, False, False, False, False,
              False, False, False, False, False, False, False, False, False, True)

BEZIER_CIRCLE_HANDLE_TO_RADIUS_RATIO = 0.55213

# deep_link_objects
# Returns a copy of the passed object. Data is linked
# object: Object to copy
# context: context in wich to create the copy
def deep_link_object(obj, context, with_children = False):
    ret = bpy.data.objects.new(obj.name, obj.data)
    context.scene.objects.link(ret)

    if with_children:
        for child in obj.children:
            child_clone = bpy.data.objects.new(child.name, child.data)
            child_clone.parent = ret
            context.scene.objects.link(child_clone)

    return ret

# join_objects
# Conveniencefunction to join a list of objects
# objects: List of objects to join
# context: Context containing the objects
def join_objects(objects, context):
    if len(objects) < 2:
        return
    
    bpy.ops.object.select_all(action = 'DESELECT')
    for o in objects:
        o.select = True
    context.scene.objects.active = objects[0]
    bpy.ops.object.join()
    
    return context.active_object

# make_circle
# Returns a bezier circle
# radius: Circle radius
# context: Context in wich to create the circle
def make_circle(radius, context):
    curveData = bpy.data.curves.new('CircleCurve', type = 'CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 1
    curveData.render_resolution_u = 20
    curveData.use_fill_caps = False

    polyline = curveData.splines.new('BEZIER')
    polyline.use_cyclic_u = True
    polyline.bezier_points.add(3)
    
    dtheta = math.pi / 2.0
    handle_length = (4.0/3.0) * math.tan(math.pi / (2.0 * ((2.0 * math.pi) / dtheta))) * radius
    
    for i in range(4):
        polyline.bezier_points[i].co[0] = radius * math.cos(dtheta * i) #X
        polyline.bezier_points[i].co[1] = radius * math.sin(dtheta * i) #Y
        
        hh = math.sqrt(radius**2 + handle_length**2)
        htheta = math.acos(radius / hh)
        polyline.bezier_points[i].handle_left[0] = hh * math.cos((dtheta * i) - htheta)
        polyline.bezier_points[i].handle_left[1] = hh * math.sin((dtheta * i) - htheta)
        polyline.bezier_points[i].handle_right[0] = hh * math.cos((dtheta * i) + htheta)
        polyline.bezier_points[i].handle_right[1] = hh * math.sin((dtheta * i) + htheta)
        
    ret = bpy.data.objects.new('Circle', curveData)
    context.scene.objects.link(ret)
    context.scene.objects.active = ret
    
    return ret

# make_line
# Returns a line segment
# p1: First point of line segment
# p2: Second point of line segment
# scene: Scene in wich to add the line segment
def make_line(p1, p2, n_subdiv, scene):
    # Make sure we are in object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    curveData = bpy.data.curves.new('Line', type = 'CURVE')
    curveData.dimensions = '3D'
    
    objectData = bpy.data.objects.new("Line", curveData)
    objectData.location = (0, 0, 0)
    objectData.data.use_fill_caps = True
    objectData.data.use_fill_deform = True
    objectData.data.fill_mode = 'FULL'
    objectData.data.render_resolution_u = 1
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
    
    return objectData

# make_tube_section
# Creates two joined circles
# outer_radius: Radius of the outer circle
# inner_radius: Radius of the inner circle
# context: Context in wich to create it
def make_tube_section(outer_radius, inner_radius, context):
    # Make sure we are in object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    # Create circles
    outer_circle = make_circle(outer_radius, context)
    inner_circle = make_circle(inner_radius, context)

    # Join circles
    ret = join_objects([outer_circle, inner_circle], context)
    ret.name = "TubeSection"

    return ret


# make_tube_section_slice
# Creates part of a tube section. To be used for striped insulators
# outer_radius: Radius of the outer circle
# inner_radius: Radius of the inner circle
# amount: Amount of circomference to be used (0-1)
# mirror: Mirror the slice in X and Y directions
def make_tube_section_slice(outer_radius, inner_radius, amount, mirror, context):
    curveData = bpy.data.curves.new('StripedTubeSection', type = 'CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 1
    curveData.render_resolution_u = 20
    curveData.use_fill_caps = False

    polyline = curveData.splines.new('BEZIER')
    polyline.use_cyclic_u = True
    polyline.bezier_points.add(5)
    
    theta = 2.0 * math.pi * amount
    dtheta = theta / 2.0
    
    handle_length_l = (4.0/3.0) * math.tan(math.pi / (2.0 * ((2.0 * math.pi) / dtheta))) * outer_radius
    handle_radius_l = math.sqrt(outer_radius**2 + handle_length_l**2)
    handle_length_s = (4.0/3.0) * math.tan(math.pi / (2.0 * ((2.0 * math.pi) / dtheta))) * inner_radius
    handle_radius_s = math.sqrt(inner_radius**2 + handle_length_s**2)
    handle_theta = math.acos(outer_radius / handle_radius_l)
            
    polyline.bezier_points[0].co[0] = outer_radius * math.cos(dtheta)
    polyline.bezier_points[0].co[1] = outer_radius * math.sin(dtheta)
    polyline.bezier_points[0].handle_left = polyline.bezier_points[0].co
    polyline.bezier_points[0].handle_right[0] = handle_radius_l * math.cos(dtheta - handle_theta)
    polyline.bezier_points[0].handle_right[1] = handle_radius_l * math.sin(dtheta - handle_theta)
    
    polyline.bezier_points[1].co[0] = outer_radius * math.cos(0)
    polyline.bezier_points[1].co[1] = outer_radius * math.sin(0)
    polyline.bezier_points[1].handle_left[0] = handle_radius_l * math.cos(handle_theta)
    polyline.bezier_points[1].handle_left[1] = handle_radius_l * math.sin(handle_theta)
    polyline.bezier_points[1].handle_right[0] = handle_radius_l * math.cos(-handle_theta)
    polyline.bezier_points[1].handle_right[1] = handle_radius_l * math.sin(-handle_theta)

    polyline.bezier_points[2].co[0] = outer_radius * math.cos(-dtheta)
    polyline.bezier_points[2].co[1] = outer_radius * math.sin(-dtheta)
    polyline.bezier_points[2].handle_right = polyline.bezier_points[2].co
    polyline.bezier_points[2].handle_left[0] = handle_radius_l * math.cos(-dtheta + handle_theta)
    polyline.bezier_points[2].handle_left[1] = handle_radius_l * math.sin(-dtheta + handle_theta)

    polyline.bezier_points[3].co[0] = inner_radius * math.cos(-dtheta)
    polyline.bezier_points[3].co[1] = inner_radius * math.sin(-dtheta)
    polyline.bezier_points[3].handle_left = polyline.bezier_points[2].co
    polyline.bezier_points[3].handle_right[0] = handle_radius_s * math.cos(-dtheta + handle_theta)
    polyline.bezier_points[3].handle_right[1] = handle_radius_s * math.sin(-dtheta + handle_theta)

    polyline.bezier_points[4].co[0] = inner_radius * math.cos(0)
    polyline.bezier_points[4].co[1] = inner_radius * math.sin(0)
    polyline.bezier_points[4].handle_left[0] = handle_radius_s * math.cos(-handle_theta)
    polyline.bezier_points[4].handle_left[1] = handle_radius_s * math.sin(-handle_theta)
    polyline.bezier_points[4].handle_right[0] = handle_radius_s * math.cos(handle_theta)
    polyline.bezier_points[4].handle_right[1] = handle_radius_s * math.sin(handle_theta)

    polyline.bezier_points[5].co[0] = inner_radius * math.cos(dtheta)
    polyline.bezier_points[5].co[1] = inner_radius * math.sin(dtheta)
    polyline.bezier_points[5].handle_right = polyline.bezier_points[5].co
    polyline.bezier_points[5].handle_left[0] = handle_radius_s * math.cos(dtheta - handle_theta)
    polyline.bezier_points[5].handle_left[1] = handle_radius_s * math.sin(dtheta - handle_theta) 
    
    if mirror:
        for p in polyline.bezier_points:
            p.co[0] *= -1
            p.co[1] *= -1
            p.handle_right[0] *= -1
            p.handle_left[0] *= -1   
            p.handle_right[1] *= -1
            p.handle_left[1] *= -1   

    ret = bpy.data.objects.new('StripedTubeSection', curveData)
    context.scene.objects.link(ret)
    context.scene.objects.active = ret
    
    return ret

# insulator_stripe_vg
# Creates a vertexgroup representing the slice(s) on an insulator to be colored
# differently from the base color
# object: Object to select vertices from
# amount: Percentage of circomference
# double_sided: Stripe on one side or both?
def insulator_stripe_vg(object, amount, double_sided = True):
    # Make sure we are working on a mesh object
    if object.type != 'MESH':
        return None
    
    # Make sure we are in edit mode
    if bpy.ops.mode != 'EDIT':
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    
    # Calculate max/min angle
    angle = 2.0 * math.pi * amount
    if double_sided:
        angle /= 2.0
        
    # Create new vertex group
    mesh = bmesh.from_edit_mesh(object.data)
    group = object.vertex_groups.new("Stripe")    
    
    # Add vertices to group
    group_items = []
    for v in mesh.verts:
        va = math.atan(v.co.x / v.co.y)
        if not double_sided and v.co.y < 0.0:
            continue
        if va < angle / 2.0 and va > -angle / 2.0:
            group_items.append(v.index)
    # Switch back to object mode
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)                            
    group.add(group_items, 1.0, 'ADD')
    
    return group            

# make_insulator
# Creates a tube representing the insulator
# inner_radius: The inner radius of plastic tube
# outer_radius: The outer radius of plastic tube
# length: Length of the part/cable in Z-axis
# peel_length: How much of the conductor that is visible        
def make_insulator(inner_radius, outer_radius, length, peel_length, material,
        color, context):
    # Make sure we are in object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    insulator_circles = make_tube_section(outer_radius, inner_radius, context) 

    line = make_line((0, 0, 0), (0, 0, length), math.floor(length * 200.0), context.scene)
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
    # Make sure we are in object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    #Calculate limits
    if about_eq(pitch, 0.0):
        return make_line((0, 0, 0), (0, 0, length), 200.0 * length,
                context.scene)

    if about_eq(length, 0.0):
        print("make_bezier_helix: length is zero")
        return None

    points_per_rev = 4.0 * n_subdivisions
    n_points = math.floor(length * pitch * points_per_rev)

    #Create a Bezier curve object
    curveData = bpy.data.curves.new('HelixCurve', type = 'CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 1
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
    # Make sure we are in object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    circle = make_circle(radius, context)
    circle.layers = JUNK_LAYER
    
    line = make_line((0, 0, 0), (0, 0, length), math.floor(length * 200.0), context.scene)
    line.name = "Conductor"
    line.data.bevel_object = circle
    line.data.use_fill_caps = True

    circle.parent = line
    
    context.scene.objects.active = line

    return line

# make_stranded_conductor
# Creates a set of stranded conductor wires
# Use convenience function make_conductor instead of calling this directly
def make_stranded_conductor(length, conductor_radius, pitch, strand_radius,
                            context):
    # Make sure we are in object mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

    #Create a list of points corresponding to the strand positions
    points = strand_positions(conductor_radius - strand_radius, strand_radius)

    #Create a circle to be used as a bevel object
    circle = make_circle(strand_radius, context)
    circle.layers = JUNK_LAYER

    #Create progress indicator
    wm = bpy.context.window_manager
    wm.progress_begin(0, len(points))
    progress = 0

    strands = []
    orig_obj = None
    
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
            
            if i == 0:
                if about_eq(pitch, 0.0):
                    path = make_line((r, 0, 0), (r, 0, length), math.floor(length *
                        200.0), context.scene)
                else:
                    path = make_bezier_helix(length = length, 
                                              pitch = pitch, 
                                              radius = r,
                                              clockwize = True,
                                              n_subdivisions = 1,
                                              context = context)

                # Add bevel object
                path.data.bevel_object = circle
                path.data.use_fill_caps = True
                path.data.use_fill_deform = True
                path.data.fill_mode = 'FULL'

                orig_obj = path
            else:
                path = bpy.data.objects.new(orig_obj.name, orig_obj.data)
                context.scene.objects.link(path)

            strands.append(path)
            path.rotation_euler = (0, 0, theta)
            
            # Update progress
            progress += 1
            wm.progress_update(progress)

            # Calculate next angle
            theta += dtheta
            
    # Join strands
    ret = join_objects(strands, context)
    ret.name = "Conductor"
    circle.parent = ret

    wm.progress_end()

    return ret

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

# make_braid_bundle
# Helper function to create a bundle of spiraling strands.
# Used by make_braid
#
# length: Length of spirals in Z-axis
# radius: Radius of spirals
# pitch: Number of revolutions per length unit
# strand_profile: Bevel object for the helixes
# strand_radius: Radius of individual strands
# bundle_size: Number of strands in each bundle
# clockwize: True if spirals turn clockwize
# context: Context in wich to create the bundle
def make_braid_bundle(length, radius, pitch, strand_profile, strand_radius, 
                        bundle_size, clockwize, context):
    # Calculate angle between strands
    dtheta = 2.0 * math.pi / ((radius * math.pi) / (1.6 * strand_radius))
 
    strands = []
    theta = 0.0
    for i in range(bundle_size):
        # Create helix
        if i == 0:
            helix = make_bezier_helix(length, pitch, radius, clockwize, 2, context)
            helix.data.bevel_object = strand_profile
            helix.data.use_fill_caps = True
            strands.append(helix)
        else:
            helix = deep_link_object(strands[0], context)
            strands.append(helix)
            
        helix.rotation_euler = (0, 0, theta)
        helix.name = "BraidStrand"
        
        strands.append(helix)
        
        theta += dtheta
            
    return join_objects(strands, context)
            
# make_braid
# Creates a cable braid. 
#
# length: Length of spirals in Z-axis
# radius: Radius of spirals
# pitch: Number of revolutions per length unit
# strand_radius: Radius of individual strands
# bundle_size: Number of strands in each bundle
# n_bundle_pairs: Number of clockwize and anticlockwize bundles
# material: Name of the material
# context: Context in wich to create the bundle
def make_braid(length, radius, pitch, strand_radius, bundle_size,
        n_bundle_pairs, material, context):
    # Calculate angle between bundles
    dtheta = 2.0 * math.pi / n_bundle_pairs
    
    wm = bpy.context.window_manager
    wm.progress_begin(0, n_bundle_pairs)
    
    # Create bundles
    theta = 0.0
    cw_bundles = []
    ccw_bundles = []
    strand_profile = make_circle(strand_radius, context)
    strand_profile.layers = JUNK_LAYER
    strand_profile.name = "StrandProfile"
    
    for i in range(n_bundle_pairs):
        # Keep track of first strands
        if i == 0:
            bundle_cw = make_braid_bundle(length, radius, pitch, strand_profile,
                    strand_radius, bundle_size, True, context)
            bundle_ccw = make_braid_bundle(length, radius, pitch, strand_profile,
                    strand_radius, bundle_size, False, context)
            bundle_ccw.rotation_euler = (0, 0, dtheta / 2.0)
        # Create copies of original strands
        else:
            bundle_cw = deep_link_object(cw_bundles[0], context, True)
            bundle_cw.rotation_euler = (0, 0, theta)
            cw_bundles.append(bundle_cw)
            
            bundle_ccw = deep_link_object(ccw_bundles[0], context, True)
            bundle_ccw.rotation_euler = (0, 0, theta + (dtheta / 2.0))
            ccw_bundles.append(bundle_ccw)
        
        cw_bundles.append(bundle_cw)
        ccw_bundles.append(bundle_ccw)
                
        theta += dtheta
        wm.progress_update(i)
    
    
    wm.progress_end()
    
    cw = join_objects(cw_bundles, context)
    ccw = join_objects(ccw_bundles, context)
    
    braid = join_objects([cw, ccw], context)
    braid.name = "Braid"
    #strand_profile.parent = braid
    strand_profile.hide = True
    braid.active_material = cm.CONDUCTOR_MATERIALS[material]()
    
    return braid

#################################################################################################
# The following functions has been lifted from Curve Tools by Zak
# Permission pending
# https://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Curve/Curve_Tools
#################################################################################################

#cubic bezier value
def cubic(p, t):
    return p[0]*(1.0-t)**3.0 + 3.0*p[1]*t*(1.0-t)**2.0 + 3.0*p[2]*(t**2.0)*(1.0-t) + p[3]*t**3.0

#gets a bezier segment's control points on global coordinates
def getbezpoints(spl, mt, seg=0):
    points = spl.bezier_points
    p0 = mt * points[seg].co
    p1 = mt * points[seg].handle_right
    p2 = mt * points[seg+1].handle_left
    p3 = mt * points[seg+1].co
    return p0, p1, p2, p3

#calculates a global parameter t along all control points
#t=0 begining of the curve
#t=1 ending of the curve

def calct(obj, t):

    spl=None
    mw = obj.matrix_world
    if obj.data.splines.active==None:
        if len(obj.data.splines)>0:
            spl=obj.data.splines[0]
    else:
        spl = obj.data.splines.active

    if spl==None:
        return False

    if spl.type=="BEZIER":
        points = spl.bezier_points
        nsegs = len(points)-1

        d = 1.0/nsegs
        seg = int(t/d)
        t1 = t/d - int(t/d)

        if t==1:
            seg-=1
            t1 = 1.0

        p = getbezpoints(spl,mw, seg)

        coord = cubic(p, t1)

        return coord

    elif spl.type=="NURBS":
        data = getnurbspoints(spl, mw)
        pts = data[0]
        ws = data[1]
        order = spl.order_u
        n = len(pts)
        ctype = spl.use_endpoint_u
        kv = knots(n, order, ctype)

        coord = C(t, order-1, pts, ws, kv)

        return coord

def arclength(obj):
    length = 0.0

    if obj.type=="CURVE":
        prec = 1000 #precision
        inc = 1/prec #increments

        for i in range(0, prec):
            ti = i*inc
            tf = (i+1)*inc
            a = calct(obj, ti)
            b = calct(obj, tf)
            r = (b-a).magnitude
            length+=r

    return length

#################################################################################################
# End Curve Tools functions
#################################################################################################

# make_conductor_array
# Returns a circular array of conductors
#
# length: Length of conductors in Z-axis
# pitch: Pitch of the entire conductor array
# radius: Radius of conductor array
# conductor_radius: Radius of each individual conductor
# strand_pitch: Pitch of the individual strands in each conductor
# material: String describing the conductor material
# strand_radius: Radius of individual strands
# clockwize: Direction of array rotation
# n_conductors: Number of conductors in array
# context: Context in wich to create the array
def make_conductor_array(length, pitch, radius, conductor_radius, 
                         strand_pitch, material, strand_radius, 
                         clockwize, n_conductors, context):
    if n_conductors < 1:
        return None

    # Create guide curve for curve modifier
    guide_curve = make_bezier_helix(length, pitch, radius, clockwize, 1, context)
    
    # Create conductor
    conductor = make_conductor(arclength(guide_curve), 
                               conductor_radius, 
                               strand_radius,
                               strand_pitch,
                               material,
                               context)
    # Create and apply curve modifier
    curve_mod = conductor.modifiers.new('cond_circ_arr', 'CURVE')
    curve_mod.object = guide_curve
    curve_mod.deform_axis = 'POS_Z'
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="cond_circ_arr")
    
    # Don't need the guide curve anymore
    context.scene.objects.unlink(guide_curve)

    conductors = [conductor]
    
    # Duplicate and rotate
    theta = dtheta = (2.0 * math.pi) / n_conductors    
    for i in range(0, n_conductors - 1):
        ob_new = deep_link_object(conductor, context)
        ob_new.rotation_euler = (0, 0, theta)
        conductors.append(ob_new)
        ob_new.parent = conductor

        theta += dtheta

    return conductor
    #return join_objects(conductors, context)
