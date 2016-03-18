import bpy
import math

def rc_set_cursor_location(x=0.0, y=0.0, z=0.0):
    def areas_tuple():
        res = {}                                                               
        count = 0
        for area in bpy.context.screen.areas:                                  
            res[area.type] = count                                             
            count += 1
        return res  
    #print('-----new-----')
    areas = areas_tuple()
    view3d = bpy.context.screen.areas[areas['VIEW_3D']].spaces[0]
    view3d.pivot_point='CURSOR'
    view3d.cursor_location = (x, y, z)
    #print(areas)
    
def import_svg_profile(path="profile.svg"):
    #import svg
    #bpy.context.scene.cursor_location = (0.0, 0.0, 0.0) #(not working) set cursor to center before import
    rc_set_cursor_location() #set cursor to center before import
    bpy.ops.import_curve.svg(filepath=path) #import joined svg

def add_bezier_curve_profile():
    #make beizier circle
    bpy.ops.curve.primitive_bezier_circle_add(radius=0.1, view_align=False, enter_editmode=False, location=(0, 0, 0))

def make_spiral():
    coords = [(0,-1,0), (-1,-1,0), (-1,0,0), (-1,1,0), (0,1,0), (1,1,0), (1,0,0), (1,-1,0)]

    length=10 #lenght in z-led
    turns=2 # total number of turns
    curve_with_points = False

    numberOfCirclePoints = 8
    Radius = 1

    # create the Curve Datablock
    curveData = bpy.data.curves.new('myCurve', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 12
    startPoints = 0 #start points to set manually
    endPoints = 0 #end points to set manually

    print('----------new----------')
    #print (range(turns))
    #print ( len(coords) )
    #print (len(coords)*turns)

    # map coords to spline
    polyline = curveData.splines.new('NURBS')

    if curve_with_points:
        polyline.points.add(len(coords)*turns)
        for j in range(turns):
            for i, coord in enumerate(coords):
                x,y,z = coord
                #z = length * ((j+1)/turns) * ( (i+1)/len(coords) )
                multiply_z = (i+j*len(coords)) / ( (len(coords) * turns)-1 )
                z = length * multiply_z
                polyline.points[i+j*len(coords)].co = (x, y, z, 1)
                #print( str(i+j*len(coords)) )
                #print (z)
                #print ( (i)/(len(coords)-1) )
                #print ( multiply_z )
        #print( (len(coords) * turns)-1 )
    else:
        polyline.points.add(numberOfCirclePoints*turns)
        for j in range(turns):
            for i in range(0,numberOfCirclePoints):
                phi = math.pi * 2 * i / numberOfCirclePoints
                x = Radius * math.cos(phi)
                y = Radius * math.sin(phi)
                z = 0
                multiply_z = (i+j*numberOfCirclePoints) / ( (numberOfCirclePoints * turns) )
                z = length * multiply_z
                activePoint = i+j*numberOfCirclePoints
                if activePoint < startPoints or activePoint > (numberOfCirclePoints*turns) - endPoints: #make first and last points i middle
                    x = 0
                    y = 0
                polyline.points[activePoint].co = (x, y, z, 1)
                #print(i)
                #print (phi)
                #print(x,y,z)
                #print( round(x),round(y), z )
                #print (z)
        if startPoints > 0:#set start points manually
            polyline.points[0].co = (0.0, 0.0, 0.0, 1)
                
    # create Object
    curveOB = bpy.data.objects.new('myCurve', curveData)

    # attach to scene and validate context
    scn = bpy.context.scene
    scn.objects.link(curveOB)
    scn.objects.active = curveOB
    curveOB.select = True

    #attach profile curve to curve path
    #bpy.context.object.data.bevel_object = bpy.data.objects["BezierCircle"] #add profile object for curve
    bpy.context.object.data.bevel_object = bpy.data.objects["Curve"] #add profile object for curve
    bpy.context.object.data.use_fill_caps = True #create faces at ends of curve


import_svg_profile()
#add_bezier_curve_profile()
make_spiral()