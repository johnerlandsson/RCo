#!/bin/python

import inkex
import math
import simplepath
import simplestyle

#Calculate positions of new circles given a difference in radius between the
#outer and inner circles, and the radius of the inner circle
def make_inner_circles(rc, rs):
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
            ps.append(Circle(x, y, rs))

        ret.append(ps)

        rc_next = rc - (2.0 * rs)
        if rc_next < rs:
            if rc > 2.0 * rs:
                ret.append([Circle(0, 0, rs)])
            break
        else:
            rc = rc_next

    return ret

#Returns true if referenced node is a path
def node_is_path(node):
    if node.tag[-4:] == 'path':
        return True

    return False

#Returns true if referenced node is a circle
def node_is_circle(node):
    if node.tag[-6:] == 'circle':
        return True

    return False

#Circle class
class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

class CircleFillEffect(inkex.Effect):
#Consructor
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('-d', '--diameter', action = 'store', 
                type = 'float', dest = 'diameter', default = 0.5, 
                help = 'Diameter of circles to fill with')
        self.OptionParser.add_option('-t', '--tinned', action = 'store', 
                type = 'inkbool', dest = 'tinned', default = False, 
                help = 'Tinned copper material')

#Determine if the selected object is a circle and return a Circle object
    def findCircle(self):
        node = self.selected[self.selected.keys()[0]]
        if node_is_path(node):
            path = simplepath.parsePath( node.get('d'))

            a_cnt = 0
            x = 0
            y = 0
            r = 0
            radi = []

            for p in path:
                if p[0] in ('a', 'A'):
                    a_cnt += 1
                    radi.append(p[1][0])
                elif p[0] in ('m', 'M'):
                    x = p[1][0]
                    y = p[1][1]
                elif p[0] == 'l':
                    return None

            if a_cnt != 4:
                return None

            r = min(radi)
            if r != max(radi):
                return None

            return Circle(x - r, y, r)

        elif node_is_circle:
            if node.get('r') == None:
                return None
            
            return Circle(float(node.get('cx')), float(node.get('cy')),
                    float(node.get('r')))

        return None 

#Draw the new circles
    def drawCircles(self, circles, trans_point = (0.0, 0.0)):
        parent = self.current_layer
        i = 0
        for layer in circles:
            for c in layer:
                x = trans_point[0] + c.x
                y = trans_point[1] + c.y

                if not self.options.tinned:
                    material = 'CU'
                    color = '#aa4400'
                else:
                    material = 'CU-T'
                    color = '#808080'

                style = {'stroke': 'none', 'fill': color}

                attribs = {'cx': str(x), 
                           'cy': str(y), 
                           'r': str(c.r),
                           inkex.addNS('label', 'inkscape'):"is%d" %i,
                           'material':material,
                           'style': simplestyle.formatStyle(style)}

                inkex.etree.SubElement(parent, inkex.addNS('circle', 'svg'),
                        attribs)
                i += 1

#Implementation of abstract method
    def effect(self):
        if len(self.selected) > 1:
            inkex.errormsg("Multiple objects not yet implemented.")
            return
        elif len(self.selected) <= 0:
            inkex.errormsg("No object selected.")
            return

        outer_circle = self.findCircle()

        if outer_circle == None:
            inkex.errormsg("Selected object is not a valid circle.")
            return

        inner_radius = self.unittouu("%fmm" %self.options.diameter) / 2.0
        inner_circles = []

        if outer_circle.r < inner_radius:
            inkex.errormsg("Selected circle is smaller than inner circle")
            return
        elif outer_circle.r < 2.0 * inner_radius:
            inner_circles.append([Circle(0, 0, r=inner_radius)])
        else:
            rc = outer_circle.r - inner_radius
            inner_circles = make_inner_circles(rc, inner_radius)

        self.drawCircles(inner_circles, (outer_circle.x, outer_circle.y))


effect = CircleFillEffect()
effect.affect()
