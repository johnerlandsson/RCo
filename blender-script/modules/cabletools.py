## @package cabletools
# This package contains functions to create cable related objects in blender.

import bmesh
import bpy
import cablematerials as cm
import math

CONDUCTOR_MATERIALS = [('cu', 'CU', 'Standard copper'),
                       ('cu-t', 'CU-Tinned', 'Tinned copper'),
                       ('al', 'AL', 'Aluminium')]
INSULATOR_MATERIALS = [('pvc', 'PVC', 'PVC'), ('pe', 'PE', 'Polyethelene'),
                       ('pex', 'PEX', 'Cross linked polyethylene')]
LAP_MATERIALS = [('cu', 'CU', 'Standard copper'),
                 ('nylon', 'Nylon', 'Nylon felt lap')]

INSULATOR_COLORS = []
for k in cm.INSULATOR_COLORS:
    INSULATOR_COLORS.append((k, k, k))
for k in cm.STRIPE_TYPES:
    INSULATOR_COLORS.append((k, k, k))

JUNK_LAYER = (False, False, False, False, False, False, False, False, False,
              False, False, False, False, False, False, False, False, False,
              False, True)


class InputError(Exception):
    def __init__(self, msg):
        super(InputError, self).__init__(msg)


class Error(Exception):
    def __init__(self, msg):
        super(Error, self).__init__(msg)


## Create a deep linked copy of an object 
# @param obj Object to copy
# @param context context in which to create the copy
# @param with_children Also create copies of objects children
#
# @return A deep linked copy of the passed object
def deep_link_object(obj, context, with_children=False):
    ret = bpy.data.objects.new(obj.name, obj.data)
    context.scene.objects.link(ret)

    if with_children:
        for child in obj.children:
            child_clone = bpy.data.objects.new(child.name, child.data)
            child_clone.parent = ret
            context.scene.objects.link(child_clone)

    return ret


## Convenience function to join a list of objects
# @param objects List of objects to join
# @param context Context containing the objects
# @return The new object
def join_objects(objects, context):
    if len(objects) < 2:
        return

    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select = True
    context.scene.objects.active = objects[0]
    bpy.ops.object.join()

    return context.active_object


## Creates a circle object using bezier curve
# @param radius Circle radius
# @param context Context in which to create the circle
# @return The circle object
def make_bezier_circle(radius, context):
    if radius <= 0:
        raise InputError("Invalid radius")

    curveData = bpy.data.curves.new('CircleCurve', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 1
    curveData.render_resolution_u = 7
    curveData.use_fill_caps = False

    polyline = curveData.splines.new('BEZIER')
    polyline.use_cyclic_u = True
    polyline.bezier_points.add(3)

    dtheta = math.pi / 2.0
    handle_length = (4.0 / 3.0) * math.tan(math.pi / (2.0 * (
        (2.0 * math.pi) / dtheta))) * radius

    for i in range(4):
        polyline.bezier_points[i].co[0] = radius * math.cos(-dtheta * i)  #X
        polyline.bezier_points[i].co[1] = radius * math.sin(-dtheta * i)  #Y

        hh = math.sqrt(radius**2 + handle_length**2)
        htheta = math.acos(radius / hh)
        polyline.bezier_points[i].handle_left[0] = hh * math.cos((dtheta * i) -
                                                                 htheta)
        polyline.bezier_points[i].handle_left[1] = hh * math.sin((dtheta * i) -
                                                                 htheta)
        polyline.bezier_points[i].handle_right[0] = hh * math.cos((dtheta * i)
                                                                  + htheta)
        polyline.bezier_points[i].handle_right[1] = hh * math.sin((dtheta * i)
                                                                  + htheta)

    ret = bpy.data.objects.new('Circle', curveData)
    context.scene.objects.link(ret)
    context.scene.objects.active = ret

    return ret


## Creates a line object
# @param p1 First point of line segment
# @param p2 Second point of line segment
# @param scene Scene in which to add the line segment
# @return The line object
def make_line(p1, p2, n_subdiv, context):
    if n_subdiv <= 0:
        raise InputError("No subdivisions set")
    elif p1 == p2:
        raise InputError("No distance between points")

    scene = context.scene

    curveData = bpy.data.curves.new('Line', type='CURVE')
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


## Creates two joined circles
# @param outer_radius Radius of the outer circle
# @param inner_radius Radius of the inner circle
# @param context Context in which to create it
# @return The new object
def make_tube_section(outer_radius, inner_radius, context):
    if outer_radius <= 0.0:
        raise InputError("Invalid outer radius")
    elif inner_radius <= 0.0:
        raise InputError("Invalid inner radius")

    # Create circles
    outer_circle = make_bezier_circle(outer_radius, context)
    inner_circle = make_bezier_circle(inner_radius, context)

    # Join circles
    ret = join_objects([outer_circle, inner_circle], context)
    ret.name = "TubeSection"

    return ret


## Creates part of a tube section. To be used for striped insulators
# @param outer_radius Radius of the outer circle
# @param inner_radius Radius of the inner circle
# @param amount Amount of circumference to be used (0-1)
# @param mirror Mirror the slice in X and Y directions
# @return The new object
def make_tube_section_slice(outer_radius, inner_radius, amount, mirror,
                            context):
    curveData = bpy.data.curves.new('StripedTubeSection', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 1
    curveData.render_resolution_u = 2
    curveData.use_fill_caps = False

    polyline = curveData.splines.new('BEZIER')
    polyline.use_cyclic_u = True
    polyline.bezier_points.add(5)

    theta = 2.0 * math.pi * amount
    dtheta = theta / 2.0

    handle_length_l = (4.0 / 3.0) * math.tan(math.pi / (2.0 * (
        (2.0 * math.pi) / dtheta))) * outer_radius
    handle_radius_l = math.sqrt(outer_radius**2 + handle_length_l**2)
    handle_length_s = (4.0 / 3.0) * math.tan(math.pi / (2.0 * (
        (2.0 * math.pi) / dtheta))) * inner_radius
    handle_radius_s = math.sqrt(inner_radius**2 + handle_length_s**2)
    handle_theta = math.acos(outer_radius / handle_radius_l)

    polyline.bezier_points[0].co[0] = outer_radius * math.cos(dtheta)
    polyline.bezier_points[0].co[1] = outer_radius * math.sin(dtheta)
    polyline.bezier_points[0].handle_left = polyline.bezier_points[0].co
    polyline.bezier_points[0].handle_right[0] = handle_radius_l * math.cos(
        dtheta - handle_theta)
    polyline.bezier_points[0].handle_right[1] = handle_radius_l * math.sin(
        dtheta - handle_theta)

    polyline.bezier_points[1].co[0] = outer_radius * math.cos(0)
    polyline.bezier_points[1].co[1] = outer_radius * math.sin(0)
    polyline.bezier_points[1].handle_left[0] = handle_radius_l * math.cos(
        handle_theta)
    polyline.bezier_points[1].handle_left[1] = handle_radius_l * math.sin(
        handle_theta)
    polyline.bezier_points[1].handle_right[0] = handle_radius_l * math.cos(
        -handle_theta)
    polyline.bezier_points[1].handle_right[1] = handle_radius_l * math.sin(
        -handle_theta)

    polyline.bezier_points[2].co[0] = outer_radius * math.cos(-dtheta)
    polyline.bezier_points[2].co[1] = outer_radius * math.sin(-dtheta)
    polyline.bezier_points[2].handle_right = polyline.bezier_points[2].co
    polyline.bezier_points[2].handle_left[0] = handle_radius_l * math.cos(
        -dtheta + handle_theta)
    polyline.bezier_points[2].handle_left[1] = handle_radius_l * math.sin(
        -dtheta + handle_theta)

    polyline.bezier_points[3].co[0] = inner_radius * math.cos(-dtheta)
    polyline.bezier_points[3].co[1] = inner_radius * math.sin(-dtheta)
    polyline.bezier_points[3].handle_left = polyline.bezier_points[2].co
    polyline.bezier_points[3].handle_right[0] = handle_radius_s * math.cos(
        -dtheta + handle_theta)
    polyline.bezier_points[3].handle_right[1] = handle_radius_s * math.sin(
        -dtheta + handle_theta)

    polyline.bezier_points[4].co[0] = inner_radius * math.cos(0)
    polyline.bezier_points[4].co[1] = inner_radius * math.sin(0)
    polyline.bezier_points[4].handle_left[0] = handle_radius_s * math.cos(
        -handle_theta)
    polyline.bezier_points[4].handle_left[1] = handle_radius_s * math.sin(
        -handle_theta)
    polyline.bezier_points[4].handle_right[0] = handle_radius_s * math.cos(
        handle_theta)
    polyline.bezier_points[4].handle_right[1] = handle_radius_s * math.sin(
        handle_theta)

    polyline.bezier_points[5].co[0] = inner_radius * math.cos(dtheta)
    polyline.bezier_points[5].co[1] = inner_radius * math.sin(dtheta)
    polyline.bezier_points[5].handle_right = polyline.bezier_points[5].co
    polyline.bezier_points[5].handle_left[0] = handle_radius_s * math.cos(
        dtheta - handle_theta)
    polyline.bezier_points[5].handle_left[1] = handle_radius_s * math.sin(
        dtheta - handle_theta)

    if mirror:
        for p in polyline.bezier_points:
            p.co[0] *= -1
            p.handle_right[0] *= -1
            p.handle_left[0] *= -1

    ret = bpy.data.objects.new('StripedTubeSection', curveData)
    context.scene.objects.link(ret)
    context.scene.objects.active = ret

    return ret


# TODO replace this with some matrix operation
def rotate_point_xy(p, angle):
    r = math.sqrt(p[0]**2 + p[1]**2)
    theta = math.atan(p[1] / p[0])
    p[0] = r * math.sin(theta + angle)
    p[1] = r * math.cos(theta + angle)


## Creates two curve objects representing the cross section of a striped
# insulator.
# @param outer_radius Radius of outer circle
# @param inner_radius Radius of inner circle
# @param amount Percentage of circumference to be striped
# @param double_sided Split stripe into two slices
# @param context Context in which to create the curve
# @return The two parts of the tube section
def make_striped_tube_section(outer_radius, inner_radius, amount, double_sided,
                              context):
    if amount > 0.51 or amount < 0.1:
        raise InputError("Please select an amount between 0.1 and 0.51")
    elif outer_radius <= 0.0 or inner_radius <= 0.0:
        raise InputError("Invalid radius")

    if double_sided:
        first = make_tube_section_slice(outer_radius, inner_radius,
                                        (1.0 - amount) / 2.0, False, context)
        second = make_tube_section_slice(outer_radius, inner_radius,
                                         (1.0 - amount) / 2.0, True, context)
        base = join_objects([first, second], context)

        first = make_tube_section_slice(outer_radius, inner_radius,
                                        amount / 2.0, False, context)
        second = make_tube_section_slice(outer_radius, inner_radius,
                                         amount / 2.0, True, context)
        stripe = join_objects([first, second], context)
        theta = math.pi
    else:
        base = make_tube_section_slice(outer_radius, inner_radius,
                                       1.0 - amount, False, context)
        stripe = make_tube_section_slice(outer_radius, inner_radius, amount,
                                         False, context)
        theta = math.pi + (math.pi / 2)

    theta_offs = 0
    for spline in stripe.data.splines:
        for p in spline.bezier_points:
            rotate_point_xy(p.co, theta + theta_offs)
            rotate_point_xy(p.handle_left, theta + theta_offs)
            rotate_point_xy(p.handle_right, theta + theta_offs)

        theta_offs += math.pi

    base.name = "TubeSectionBase"
    stripe.name = "TubeSectionStripe"

    return base, stripe


## Creates a tube representing the insulator
# @param inner_radius The inner radius of plastic tube
# @param outer_radius The outer radius of plastic tube
# @param length Length of the part/cable in Z-axis
# @param peel_length How much of the conductor that is visible        
# @return The new object
def make_insulator(inner_radius, outer_radius, length, peel_length, material,
                   color_name, context):
    # Create guide curve
    line = make_line((0, 0, length), (0, 0, 0), 1, context)
    line.data.use_fill_caps = True
    line.data.bevel_factor_start = peel_length * (1.0 / length)
    line.name = "Insulator"
    line.data.twist_mode = 'Z_UP'
    context.scene.objects.active = line

    # Solid colour insulator
    if color_name in cm.INSULATOR_COLORS.keys():
        base_color = cm.INSULATOR_COLORS[color_name]
        profile = make_tube_section(outer_radius, inner_radius, context)
        line.data.bevel_object = profile
        line.active_material = cm.INSULATOR_MATERIALS[material](base_color)
    # Striped insulator
    elif color_name in cm.STRIPE_TYPES.keys():  #Striped insulator
        stripe_data = cm.STRIPE_TYPES[color_name]
        base_color = stripe_data[0]
        stripe_color = stripe_data[1]
        amount = stripe_data[2]
        double_sided = stripe_data[3]
        base_prof, stripe_prof = make_striped_tube_section(
            outer_radius, inner_radius, amount, double_sided, context)

        stripe_line = bpy.data.objects.new('Stripe', line.data.copy())
        context.scene.objects.link(stripe_line)
        stripe_prof.parent = stripe_line

        line.data.bevel_object = base_prof
        line.active_material = cm.INSULATOR_MATERIALS[material](base_color)
        base_prof.parent = line

        stripe_line.data.bevel_object = stripe_prof
        stripe_line.active_material = cm.INSULATOR_MATERIALS[material](
            stripe_color)
        stripe_line.parent = line
    else:
        raise InputError("\"%s\" is not a valid colour:" % color_name)

    return line


# TODO Find standard function for this
## Helper function to compare floating point values
# @param a A float variable
# @param b A float variable to compare with
# @return True if a and b are equal
def about_eq(a, b):
    if a + 0.000001 > b and a - 0.000001 < b:
        return True
    return False


## Returns a bezier curve in the shape of a spiral
# @param length Total length in Z-axis
# @param pitch Number of revolutions per length unit
# @param radius Radius of helix
# @param context context in wich to create the helix
# @return The new object
def make_bezier_helix(length, pitch, radius, clockwize, n_subdivisions,
                      context):
    #Calculate limits
    if about_eq(pitch, 0.0):
        return make_line((0, 0, 0), (0, 0, length), 200.0 * length, context)

    if about_eq(length, 0.0):
        raise InputError("Length is zero")
    elif n_subdivisions < 1:
        raise InputError("n_subdivisions is zero")

    points_per_rev = 4.0 * n_subdivisions
    n_points = math.floor(length * pitch * points_per_rev)

    #Create a Bezier curve object
    curveData = bpy.data.curves.new('HelixCurve', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 1
    curveData.render_resolution_u = 5
    curveData.use_fill_caps = True
    polyline = curveData.splines.new('BEZIER')
    polyline.bezier_points.add(n_points)

    dtheta = (2.0 * math.pi) / points_per_rev
    if clockwize:
        dtheta *= -1
    handle_length = (4.0 / 3.0) * math.tan(math.pi / (2.0 * (
        (2.0 * math.pi) / dtheta))) * radius
    handle_radius = math.sqrt(radius**2 + handle_length**2)
    htheta = math.acos(radius / handle_radius)

    dz = (length / (length * pitch * 2 * math.pi)) * htheta

    for i in range(n_points + 1):
        z = length - (length * (i / n_points))
        polyline.bezier_points[i].co[0] = radius * math.cos(dtheta * i)
        polyline.bezier_points[i].co[1] = radius * math.sin(dtheta * i)
        polyline.bezier_points[i].co[2] = z

        if clockwize:
            handle_b = polyline.bezier_points[i].handle_left
            handle_a = polyline.bezier_points[i].handle_right
            tmpdz = dz * -1.0
        else:
            handle_a = polyline.bezier_points[i].handle_left
            handle_b = polyline.bezier_points[i].handle_right
            tmpdz = dz

        handle_a[0] = handle_radius * math.cos((dtheta * i) - htheta)
        handle_a[1] = handle_radius * math.sin((dtheta * i) - htheta)
        handle_a[2] = z + tmpdz

        handle_b[0] = handle_radius * math.cos((dtheta * i) + htheta)
        handle_b[1] = handle_radius * math.sin((dtheta * i) + htheta)
        handle_b[2] = z - tmpdz

    ret = bpy.data.objects.new('Helix', curveData)
    context.scene.objects.link(ret)
    context.scene.objects.active = ret

    return ret


## Circle packing algorithm
# @param conductor_radius Radius of the larger circle
# @param strand_radius Radius of the smaller circle
# @return A list of tuples representing the points
def strand_positions(conductor_radius, strand_radius):
    rc = conductor_radius
    rs = strand_radius
    ret = []

    while True:
        no = int(math.floor((2.0 * math.pi * rc) / (2.0 * rs)))
        ps = []
        x0 = rc * math.cos(0 * 2 * math.pi / no)
        y0 = rc * math.sin(0 * 2 * math.pi / no)
        x1 = rc * math.cos(1 * 2 * math.pi / no)
        y1 = rc * math.sin(1 * 2 * math.pi / no)
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


## Creates a single conductor core in the scene
# @param length Total length of the conductor in Z-axis
# @param radius Radius of the conductor
# @return The new object
def make_solid_conductor(length, radius, context):
    circle = make_bezier_circle(radius, context)
    circle.layers = JUNK_LAYER

    line = make_line((0, 0, 0), (0, 0, length), math.floor(length * 200.0),
                     context)
    line.name = "Conductor"
    line.data.bevel_object = circle
    line.data.use_fill_caps = True

    circle.parent = line

    context.scene.objects.active = line

    return line


## Creates a set of stranded conductor wires
# Use convenience function make_conductor instead of calling this directly
# @param length Axial length of the conductor
# @param conductor_radius Radius of the entire conductor
# @param pitch Number of revolutions per length unit
# @param strand_radius Radius of individual strands in the conductor
# @param context Context in wich to create the conductor
# @return The conductor object
def make_stranded_conductor(length, conductor_radius, pitch, strand_radius,
                            context):
    #Create a list of points corresponding to the strand positions
    points = strand_positions(conductor_radius - strand_radius, strand_radius)

    #Create a circle to be used as a bevel object
    circle = make_bezier_circle(strand_radius, context)
    circle.layers = JUNK_LAYER

    #Create progress indicator
    wm = bpy.context.window_manager
    wm.progress_begin(0, len(points))
    progress = 0

    strands = []
    orig_obj = None

    # iterate over the points and calculate positions of conductor helices
    for row in points:
        r = math.sqrt(row[0][0]**2 + row[0][1]**2)
        dtheta = (2.0 * math.pi) / len(row)
        theta = 0.0

        for i in range(len(row)):
            # Use make_solid_conductor for centred strand
            if about_eq(r, 0.0):
                strands.append(make_solid_conductor(length, strand_radius,
                                                    context))
                continue

            if i == 0:
                if about_eq(pitch, 0.0):
                    path = make_line((r, 0, 0), (r, 0, length),
                                     math.floor(length * 200.0), context)
                else:
                    path = make_bezier_helix(length=length,
                                             pitch=pitch,
                                             radius=r,
                                             clockwize=True,
                                             n_subdivisions=1,
                                             context=context)

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


## Creates a parametric conductor and puts it in the scene
# @param length Total conductor length in Z-axis
# @param conductor_radius Total radius of the combined conductor
# @param strand_radius Diameter of each strand. 0.0 for solid conductor
# @param strand_pitch Number of revolutions per length unit
# @param context Context in which to create the conductor object
# @return The new object
def make_conductor(length, conductor_radius, strand_radius, strand_pitch,
                   material, context):
    # Solid conductor
    if conductor_radius == strand_radius or about_eq(strand_radius, 0.0):
        conductor = make_solid_conductor(length=length,
                                         radius=conductor_radius,
                                         context=context)
    # Stranded conductor
    else:
        conductor = make_stranded_conductor(length=length,
                                            conductor_radius=conductor_radius,
                                            pitch=strand_pitch,
                                            strand_radius=strand_radius,
                                            context=context)

    conductor.active_material = cm.CONDUCTOR_MATERIALS[material]()

    return conductor


# make_braid_strand
# Creates a helical strand with alternating radii to be used with make_braid
# function.
#
# @param length Axial length of helix
# @param radius Radius of strand position
# @param pitch Number of revolutions per length unit in helix
# @param points_per_rev Number of points on helix for each revolution
# @param strand_radius Radius of the strand
# @param clockwise Rotation direction of helix
# @param context Context in which to create the strand
# @return The new object
def make_braid_strand(length, radius, pitch, points_per_rev, strand_radius,
                      clockwize, context):
    # Calculate angle between each point
    dtheta = (2.0 * math.pi) / points_per_rev
    if not clockwize:
        dtheta *= -1

# Calculate total number of points
    n_points = math.floor(points_per_rev * pitch * length)

    # Calculate handle offsets
    handle_length = (4.0 / 3.0) * math.tan(math.pi / (2.0 * (
        (2.0 * math.pi) / dtheta))) * radius
    handle_radius = math.sqrt(radius**2 + handle_length**2)
    htheta = math.acos(radius / handle_radius)

    # Calculate z offset for handles
    dz = (length / (length * pitch * 2 * math.pi)) * htheta

    #Create a Bezier curve object
    curveData = bpy.data.curves.new('HelixCurve', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 1
    curveData.render_resolution_u = 3
    curveData.use_fill_caps = True
    polyline = curveData.splines.new('BEZIER')
    polyline.bezier_points.add(n_points)

    # Determine start offset of alternating point radius
    if clockwize:
        offs = 1
    else:
        offs = 5

    z = 0.0
    for i in range(n_points + 1):
        # Calculate z position of point
        z = length * (i / n_points)

        # Determine if point is to be pulled in or out
        if offs >= 0 and offs <= 2:
            dradius = strand_radius * 1.1
        elif offs >= 4 and offs <= 6:
            dradius = strand_radius * -1.1
        else:
            dradius = 0
        offs += 1
        if offs > 7:
            offs = 0

        # Calculate point position
        polyline.bezier_points[i].co[0] = (radius + dradius) * math.cos(
            dtheta * i)
        polyline.bezier_points[i].co[1] = (radius + dradius) * math.sin(
            dtheta * i)
        polyline.bezier_points[i].co[2] = z

        # Calculate handle positions
        if not clockwize:
            handle_b = polyline.bezier_points[i].handle_left
            handle_a = polyline.bezier_points[i].handle_right
            tmpdz = dz
        else:
            handle_a = polyline.bezier_points[i].handle_left
            handle_b = polyline.bezier_points[i].handle_right
            tmpdz = dz * -1.0

        handle_a[0] = (
            handle_radius + dradius) * math.cos((dtheta * i) - htheta)
        handle_a[1] = (
            handle_radius + dradius) * math.sin((dtheta * i) - htheta)
        handle_a[2] = z + tmpdz

        handle_b[0] = (
            handle_radius + dradius) * math.cos((dtheta * i) + htheta)
        handle_b[1] = (
            handle_radius + dradius) * math.sin((dtheta * i) + htheta)
        handle_b[2] = z - tmpdz

    # Create object
    ret = bpy.data.objects.new('Helix', curveData)
    context.scene.objects.link(ret)
    context.scene.objects.active = ret
    return ret


## Creates a pleated tube object
#
# @param length Axial length of braid
# @param radius Radius of strand positions
# @param bundle_size Number of strands in each bundle
# @param n_bundle_pairs Number of spinaches going in each direction
# @param pitch Number of revolutions per length unit
# @param strand_radius Radius of each individual strand
# @param material String describing the conductor material
# @param context Context in which to create the braid
# @return The new object
def make_braid(length, radius, bundle_size, n_bundle_pairs, pitch,
               strand_radius, material, context):
    # Calculate total number of bundles
    n_bundles = int(n_bundle_pairs * 2)

    #Create progress indicator
    wm = bpy.context.window_manager
    wm.progress_begin(0, n_bundles + bundle_size)

    # Create shared bevel object
    strand_profile = make_bezier_circle(strand_radius, context)

    # Calculate angles
    dtheta = (2.0 * math.pi) / n_bundles
    strand_dtheta = (2.0 * math.pi) / ((radius * math.pi) / strand_radius)

    # Create clockwise strand
    cw_strands = [make_braid_strand(length, radius, pitch, n_bundles * 4,
                                    strand_radius, True, context)]
    cw_strands[0].data.bevel_object = strand_profile
    # Create counter-clockwise strand
    ccw_strands = [make_braid_strand(length, radius, pitch, n_bundles * 4,
                                     strand_radius, False, context)]
    ccw_strands[0].rotation_euler = (0, 0, (dtheta / 2))
    ccw_strands[0].data.bevel_object = strand_profile

    progress = 0
    for i in range(1, n_bundles):
        cw_strands.append(deep_link_object(cw_strands[0], context))
        cw_strands[-1].rotation_euler = (0, 0, (i * dtheta))
        ccw_strands.append(deep_link_object(ccw_strands[0], context))
        ccw_strands[-1].rotation_euler = (0, 0, (i * dtheta) + (dtheta / 2))
        progress += 1
        wm.progress_update(progress)

    cw_strands += ccw_strands
    strands = [join_objects(cw_strands, context)]

    for i in range(bundle_size):
        strands.append(deep_link_object(strands[0], context))
        strands[-1].rotation_euler = (0, 0, strand_dtheta * i)
        progress += 1
        wm.progress_update(progress)

    ret = join_objects(strands, context)
    ret.name = "Braid"

    ret.active_material = cm.CONDUCTOR_MATERIALS[material]()

    wm.progress_end()

    return ret


## Calculate the length of a helix
# @param radius Radius of the helix
# @param pitch Number of revolutions per length unit of the helix
# @param length Axial length of the helix
# @return The length of the helix
def helical_length(radius, pitch, length):
    circ = 2.0 * radius * math.pi * length * pitch
    return math.sqrt(circ**2 + length**2)


## Adds a cylindrical feature to existing mesh
#
# @param length Axial length of the cylinder
# @param radius Radius of the cylinder
# @param mesh_data Bmesh object to create cylinder in
def make_mesh_straight_strand(length, radius, mesh_data):
    ppr = 8
    n_circles = math.floor(100 * length)
    dz = length / 10
    dtheta = (2.0 * math.pi) / ppr

    for i in range(n_circles + 1):
        for j in range(ppr):
            # Create vertices
            x = radius * math.sin(j * dtheta)
            y = radius * math.cos(j * dtheta)
            z = dz * i

            mesh_data.verts.new((x, y, z))
            mesh_data.verts.ensure_lookup_table()

            # Create side faces
            if j > 0 and i > 0:
                mesh_data.faces.new(
                    (mesh_data.verts[-1], mesh_data.verts[-ppr - 1],
                     mesh_data.verts[-ppr - 2], mesh_data.verts[-2]))
        # Create last side face
        if i > 0:
            mesh_data.faces.new((mesh_data.verts[-ppr], mesh_data.verts[-1],
                                 mesh_data.verts[-ppr - 1],
                                 mesh_data.verts[-(ppr * 2)]))

        # Create a surface on first and last circle
        if i == 0 or i == n_circles:
            cap_face = []
            for j in range(ppr):
                cap_face.append(mesh_data.verts[-j - 1])
            mesh_data.faces.new(cap_face)


## Adds a single twisted strand to an existing mesh
#
# @param length Axial length of the strand
# @param radius Radius of strand position
# @param pitch Revolutions per length unit
# @param strand_radius Radius of the strand
# @param mesh_data Bmesh object in which to create the strand
# @param start_angle Angle of strand position
def make_mesh_bunched_strand(length,
                             radius,
                             pitch,
                             strand_radius,
                             mesh_data,
                             start_angle=0.0):
    ppr = 8  # Points per revolution
    cpr = 10  # Circles per revolution
    n_circles = math.floor(cpr * length * pitch)
    dtheta_cp = (2.0 * math.pi) / ppr  # Angle between circle points
    theta_x = math.atan((
        (length / pitch) / 2) / radius)  # Angle to rotate circle along x-axis
    dtheta_z = ((2.0 * math.pi) /
                (pitch * cpr)) * 8  # Angle to rotate circle around origin

    dz = length / n_circles  # Z distance between circles

    for j in range(n_circles + 1):
        for i in range(ppr):
            # Calculate points on circle
            x = strand_radius * math.sin(i * dtheta_cp) + radius
            y = strand_radius * math.cos(i * dtheta_cp)
            z = (dz * j) + (y * math.cos(theta_x))

            # Rotate circle around origin
            pr = math.sqrt(x**2 + y**2)
            ptheta = math.atan(y / x)
            x = pr * math.sin(j * dtheta_z - ptheta - start_angle)
            y = pr * math.cos(j * dtheta_z - ptheta - start_angle)

            # Create vertices
            mesh_data.verts.new((x, y, z))
            mesh_data.verts.ensure_lookup_table()

            # Create side faces
            if j > 0 and i > 0:
                mesh_data.faces.new((mesh_data.verts[-2], mesh_data.verts[-1],
                                     mesh_data.verts[-ppr - 1],
                                     mesh_data.verts[-ppr - 2]))

        # Create final side face
        if j > 0:
            mesh_data.faces.new((mesh_data.verts[-ppr], mesh_data.verts[-1],
                                 mesh_data.verts[-ppr - 1],
                                 mesh_data.verts[-(ppr * 2)]))

            # Create cap face for first and last circle
        if j == 0 or j == n_circles:
            cap_face = []
            for i in range(ppr):
                cap_face.append(mesh_data.verts[-(i + 1)])
            mesh_data.faces.new(cap_face)


            ## Creates a mesh object representing a bunched set of strands
            # 
            # @param length Axial length of the conductor
            # @param radius Conductor radius
            # @param pitch Number of revolutions per length unit
            # @param strand_radius Radius of individual strands
            # @return The new object
def make_stranded_mesh_conductor(length, radius, pitch, strand_radius):
    bm = bmesh.new()
    obj = bpy.data.objects.new("Conductor",
                               bpy.data.meshes.new("ConductorMesh"))
    bpy.context.scene.objects.link(obj)

    rc = radius - strand_radius
    while True:
        no = math.floor((2.0 * math.pi * rc) / (2.0 * strand_radius))
        x0 = rc
        y0 = 0.0
        x1 = rc * math.cos(2 * math.pi / no)
        y1 = rc * math.sin(2 * math.pi / no)
        dist = math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

        if dist < 2.0 * strand_radius:
            no -= 1

        for i in range(no):
            theta = ((2.0 * math.pi) / no) * i
            make_mesh_bunched_strand(length, rc, pitch, strand_radius, bm,
                                     theta)

        rc_next = rc - (2.0 * strand_radius)
        if rc_next < strand_radius:
            if rc > 2.0 * strand_radius:
                make_mesh_straight_strand(length, strand_radius, bm)
            break
        else:
            rc = rc_next

    bm.to_mesh(obj.data)
    obj.data.update()
    for f in obj.data.polygons:
        f.use_smooth = True

    return obj


## Creates an object with a cylinder mesh
#
# @param length Axial length in Z-axis
# @param radius Radius of the conductor
# @return The new object
def make_solid_mesh_conductor(length, radius):
    bm = bmesh.new()
    obj = bpy.data.objects.new("Conductor",
                               bpy.data.meshes.new("ConductorMesh"))
    bpy.context.scene.objects.link(obj)

    make_mesh_straight_strand(length, radius, bm)

    bm.to_mesh(obj.data)

    # Calculate normals
    obj.data.update()
    # Set smooth shading
    for f in obj.data.polygons:
        f.use_smooth = True

    return obj


## Creates a parametric conductor and puts it in the scene
# @param length Total conductor axial length in Z-axis
# @param conductor_radius Total radius of the combined conductor
# @param strand_radius Diameter of each strand. 0.0 for solid conductor
# @param strand_pitch Number of revolutions per length unit
def make_mesh_conductor(length, conductor_radius, strand_radius, strand_pitch,
                        material):
    # Solid conductor
    if conductor_radius == strand_radius or about_eq(strand_radius, 0.0):
        conductor = make_solid_mesh_conductor(length=length,
                                              radius=conductor_radius)
    # Stranded conductor
    else:
        conductor = make_stranded_mesh_conductor(length=length,
                                                 radius=conductor_radius,
                                                 pitch=strand_pitch,
                                                 strand_radius=strand_radius)

    # Add modifiers
    es_mod = conductor.modifiers.new('EdgeSplit', type="EDGE_SPLIT")
    es_mod.split_angle = 1.22
    subsurf_mod = conductor.modifiers.new('SubSurf', type="SUBSURF")
    subsurf_mod.levels = 0
    subsurf_mod.render_levels = 2

    conductor.active_material = cm.CONDUCTOR_MATERIALS[material]()

    bpy.context.scene.objects.active = conductor

    return conductor


## Returns a circular array of conductors
#
# @param length Length of conductors in Z-axis
# @param pitch Pitch of the entire conductor array
# @param radius Radius of conductor array
# @param conductor_radius Radius of each individual conductor
# @param strand_pitch Pitch of the individual strands in each conductor
# @param material String describing the conductor material
# @param strand_radius Radius of individual strands
# @param clockwise Direction of array rotation
# @param n_conductors Number of conductors in array
# @param context Context in which to create the array
# @return The new object
def make_conductor_array(length, pitch, radius, conductor_radius, strand_pitch,
                         material, strand_radius, clockwize, n_conductors,
                         context):
    if n_conductors < 1:
        return None

    # Create guide curve for curve modifier
    guide_curve = make_bezier_helix(length, pitch, radius, clockwize, 1,
                                    context)

    # Create conductor
    conductor = make_mesh_conductor(
        helical_length(radius, pitch, length), conductor_radius, strand_radius,
        strand_pitch, material)

    #Apply edge split modifier
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")

    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="cond_circ_arr")
    # Create and apply curve modifier
    curve_mod = conductor.modifiers.new('cond_circ_arr', 'CURVE')
    curve_mod.object = guide_curve
    curve_mod.deform_axis = 'POS_Z'
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="cond_circ_arr")

    # Don't need the guide curve any more
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


## Creates a circular array of insulators
#
# @param length Axial length of the array
# @param pitch Number of revolutions per length unit
# @param radius Radius of the array
# @param outer_radius Outer radius of individual insulators
# @param inner_radius Inner radius of individual insulators
# @param material String representing the name of insulator material
# @param colours White space separated string of colour names
# @param clockwise Rotation direction of array helix
# @param peel_length How much of the insulator end to be removed
# @param context Context in which to create the array
# @return The new object
def make_insulator_array(length, pitch, radius, outer_radius, inner_radius,
                         material, colors, clockwize, peel_length, context):
    ret = None
    color_names = colors.split()

    dtheta = (2.0 * math.pi) / len(color_names)
    theta = 0.0

    for color_name in color_names:
        guide_curve = make_bezier_helix(length, pitch, radius, clockwize, 1,
                                        context)
        guide_curve.data.use_fill_caps = True
        guide_curve.data.twist_mode = 'Z_UP'
        helix_length = helical_length(radius, pitch, length)
        guide_curve.data.bevel_factor_start = peel_length * (1 / helix_length)

        # Solid coloured insulator
        if color_name in cm.INSULATOR_COLORS.keys():
            base_profile = make_tube_section(outer_radius, inner_radius,
                                             context)
            base_profile.layers = JUNK_LAYER
            base_profile.parent = guide_curve
            guide_curve.data.bevel_object = base_profile
            color = cm.INSULATOR_COLORS[color_name]
            guide_curve.active_material = cm.INSULATOR_MATERIALS[material](
                color)
        # Striped insulator
        elif color_name in cm.STRIPE_TYPES.keys():
            stripe_data = cm.STRIPE_TYPES[color_name]
            base_color = stripe_data[0]
            stripe_color = stripe_data[1]
            amount = stripe_data[2]
            double_sided = stripe_data[3]

            base_profile, stripe_profile = make_striped_tube_section(
                inner_radius, outer_radius, amount, double_sided, context)

            # Make a copy of the guide curve for our stripe
            stripe_curve = bpy.data.objects.new('StripeCurve',
                                                guide_curve.data.copy())
            context.scene.objects.link(stripe_curve)
            stripe_curve.parent = guide_curve

            stripe_profile.parent = stripe_curve
            base_profile.parent = guide_curve

            guide_curve.data.bevel_object = base_profile
            guide_curve.active_material = cm.INSULATOR_MATERIALS[material](
                base_color)
            stripe_curve.data.bevel_object = stripe_profile
            stripe_curve.active_material = cm.INSULATOR_MATERIALS[material](
                stripe_color)
        else:
            raise InputError("\"%s\" is not a valid colour name" % color[0])

        guide_curve.rotation_euler = (0, 0, theta)
        theta += dtheta

        if ret == None:
            ret = guide_curve
        else:
            guide_curve.parent = ret

    ret.name = "InsulatorArray"

    return ret


## Creates a circular array of conductors with insulators
#
# @param length Axial length of the array
# @param pitch Array pitch
# @param radius Array radius
# @param clockwise Rotation direction of the array
# @param ins_outer_radius Outer radius of the insulator
# @param ins_inner_radius Inner radius of the insulator
# @param ins_material String representing material of the insulator
# @param ins_colours A string of colours describing the insulator colours. White space separated
# @param ins_peel_length How much of the insulator is pulled back to reveal conductor
# @param cond_radius Radius of conductor
# @param cond_strand_pitch How many revolutions per length unit are the strands twisted
# @param cond_material String representing material of the conductor
# @param cond_strand_radius Radius of the individual conductor strands
# @param context Context in which to create the array
# @return The new object
def make_part_array(length, pitch, radius, clockwize, ins_outer_radius,
                    ins_inner_radius, ins_material, ins_colors,
                    ins_peel_length, cond_radius, cond_strand_pitch,
                    cond_material, cond_strand_radius, context):

    n_parts = len(ins_colors.split())

    cond_arr = make_conductor_array(
        length, pitch, radius, cond_radius, cond_strand_pitch, cond_material,
        cond_strand_radius, clockwize, n_parts, context)
    ins_arr = make_insulator_array(length, pitch, radius, ins_outer_radius,
                                   ins_inner_radius, ins_material, ins_colors,
                                   clockwize, ins_peel_length, context)

    cond_arr.parent = ins_arr

    ins_arr.name = "PartArray"

    return ins_arr


## Convenience function to create an insulated conductor
#
# @param length Length of the part in Z-axis
# @param ins_radius Outer radius of the insulator
# @param ins_colour String representing the insulator colour
# @param ins_material String representing the insulator material
# @param peel_length How much of the insulator to be pulled back to reveal conductor
# @param cond_radius Conductor radius
# @param cond_material Material of conductor
# @param strand_radius Radius of individual strands
# @param strand_pitch Revolutions per length unit in strand twisting
# @param context Context in which to create the part
# @return The new object
def make_part(length, ins_radius, ins_color, ins_material, peel_length,
              cond_radius, cond_material, strand_radius, strand_pitch,
              context):
    insulator = make_insulator(cond_radius, ins_radius, length, peel_length,
                               ins_material, ins_color, context)
    conductor = make_mesh_conductor(length, cond_radius, strand_radius,
                                    strand_pitch, cond_material)
    conductor.parent = insulator
    insulator.name = "Part"

    return insulator


## Creates a tubular mesh object
#
# @param outer_radius Outer radius of tube
# @param inner_radius Inner radius of tube
# @param length Length of the tube in Z-axis
# @param context Context in which to create the tube
# @return The new object
def make_mesh_tube(outer_radius, inner_radius, length, context):
    if inner_radius >= outer_radius:
        raise InputError("Inner radius too big")
    elif outer_radius <= 0.0:
        raise InputError("Outer radius too small")

    # Calculate points per revolution
    ppr = math.floor(3.7 * math.log(outer_radius) + 32.0)
    if ppr <= 0:
        ppr = 4

    verts = []
    faces = []

    dtheta = (2.0 * math.pi) / ppr
    for i in range(ppr):
        x = math.sin(i * dtheta)
        y = math.cos(i * dtheta)

        verts.append((x * outer_radius, y * outer_radius, 0))
        verts.append((x * outer_radius, y * outer_radius, length))
        verts.append((x * inner_radius, y * inner_radius, 0))
        verts.append((x * inner_radius, y * inner_radius, length))

        if i == 0:
            continue

        offs = i * 4

        # Create side faces
        faces.append((offs + 0, offs - 4, offs - 3, offs + 1))
        faces.append((offs + 2, offs - 2, offs - 1, offs + 3))

        # Create end faces
        faces.append((offs + 0, offs + 2, offs - 2, offs - 4))
        faces.append((offs + 1, offs + 3, offs - 1, offs - 3))

    faces.append((0, ppr * 4 - 4, ppr * 4 - 3, 1))
    faces.append((2, ppr * 4 - 2, ppr * 4 - 1, 3))
    faces.append((0, 2, ppr * 4 - 2, ppr * 4 - 4))
    faces.append((1, 3, ppr * 4 - 1, ppr * 4 - 3))

    mesh = bpy.data.meshes.new("Tube")
    obj = bpy.data.objects.new("Tube", mesh)
    context.scene.objects.link(obj)
    mesh.from_pydata(verts, [], faces)

    mesh.update(calc_edges=True)
    mesh.calc_normals()

    # Set smooth shading
    for p in mesh.polygons:
        p.use_smooth = True

    # Add modifiers
    obj.modifiers.new('EdgeSplit', type="EDGE_SPLIT")
    subsurf_mod = obj.modifiers.new('SubSurf', type="SUBSURF")
    subsurf_mod.levels = 1
    subsurf_mod.render_levels = 2
