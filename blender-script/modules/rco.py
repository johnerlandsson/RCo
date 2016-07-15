## @package rco
# This package contains functions to create primitive mesh and curve objects.
# Dont add materials here

import bpy
import bmesh
import math

JUNK_LAYER = (False, False, False, False, False, False, False, False, False,
              False, False, False, False, False, False, False, False, False,
              False, True)


class InputError(Exception):
    def __init__(self, msg):
        super(InputError, self).__init__(msg)


## 
# @brief Throw this exception for general errors
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
        polyline.bezier_points[i].handle_left[0] = hh * math.cos((-dtheta * i) +
                                                                 htheta)
        polyline.bezier_points[i].handle_left[1] = hh * math.sin((-dtheta * i) +
                                                                 htheta)
        polyline.bezier_points[i].handle_right[0] = hh * math.cos((-dtheta * i)
                                                                  - htheta)
        polyline.bezier_points[i].handle_right[1] = hh * math.sin((-dtheta * i)
                                                                  - htheta)

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

# TODO replace this with some matrix operation
def rotate_point_xy(p, angle):
    r = math.sqrt(p[0]**2 + p[1]**2)
    theta = math.atan(p[1] / p[0])
    p[0] = r * math.sin(theta + angle)
    p[1] = r * math.cos(theta + angle)

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

## Calculate the length of a helix
# @param radius Radius of the helix
# @param pitch Number of revolutions per length unit of the helix
# @param length Axial length of the helix
# @return The length of the helix
def helical_length(radius, pitch, length):
    circ = 2.0 * radius * math.pi * length * pitch
    return math.sqrt(circ**2 + length**2)

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
#TODO make this work properly
    ppr = math.floor(3.7 * math.log(outer_radius) + 32.0)
    ppr += ppr % 8
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

    return obj

## 
# @brief Creates a shell tube with zero thickness
# 
# @param length Length of the tube
# @param radius Radius of the tube
# @param context Context in wich to create the tube
# 
# @return The tube object
def make_mesh_shell_tube(length, radius, context):
    ppr = 16
    dtheta = (2.0 * math.pi) / ppr
    bm = bmesh.new()
    obj = bpy.data.objects.new("ShellTube",
                               bpy.data.meshes.new("ShellTubeMesh"))
    context.scene.objects.link(obj)

    # Create vertecies
    for i in range(ppr):
        x = radius * math.sin(i * dtheta)
        y = radius * math.cos(i * dtheta)

        bm.verts.new((x, y, 0))
        bm.verts.new((x, y, length))

    bm.verts.ensure_lookup_table()
    # Create faces
    for i in range(0, (ppr * 2) - 3, 2):
        bm.faces.new((bm.verts[i], bm.verts[i + 1], bm.verts[i + 3],
                      bm.verts[i + 2]))

    # Create last face
    bm.faces.new((bm.verts[(ppr * 2) - 1], bm.verts[(ppr * 2) - 2], bm.verts[0],
                  bm.verts[1]))

    bm.to_mesh(obj.data)

    # Set smooth shading
    for f in obj.data.polygons:
        f.use_smooth = True

    # Calculate normals
    obj.data.update(1)

    return obj
