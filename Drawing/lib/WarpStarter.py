import math
import random
import copy
from fontTools.misc.bezierTools import splitCubicAtT, splitCubic
import vanilla
from fontTools.pens.basePen import BasePen




def getOpposite(angle, adjacent):
    # Get the opposite side of a triangle if we have the angle and the adjacent length
    if not angle == 0:
        opposite = math.tan(math.radians(angle)) * adjacent
        return opposite
    else: return 0
    
def getAngle(pt0, pt1):
    return 90 - math.degrees(math.atan2(pt0[1]-pt1[1], pt1[0]-pt0[0]))
    
def interpolate(f, x0, x1):
    return x0 + (x1 - x0) * f
    
def interpolatePoints(f, p0, p1, roundValue=False):
    x = interpolate(f, p0[0], p1[0])
    y = interpolate(f, p0[1], p1[1])
    if roundValue:
        return (int(round(x)), int(round(y)))
    else: return (x, y)

def splitWithAngle(curve, y):
    # Split a curve at location y and return the location and angle
    r = splitCubic(*curve, y, isHorizontal=True)
    if len(r) == 2:
        splitLoc = r[0][-1]
        a = getAngle(r[0][-1], r[1][1]) # handle to handle
    else:
        # The y location is either exatly on the end of the curve, or off the curve
        # Return the angle and location either at the top or bottom
        if y >= curve[0][1]:
            splitLoc = curve[0]
            a = getAngle(curve[0], curve[1])
        else:
            splitLoc = curve[-1]
            a = getAngle(curve[-2], curve[-1])
    return splitLoc, a
    
def makeUniqueName(length=None):
    if not length:
        length = 8
    name = ""
    for i in range(length):
        name += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return name

def absoluteBCP(anchor, bcp):
    return (anchor.x - bcp.x, anchor.y - bcp.y)

    

        
def warpGlyph(g, angle=-40, floatingDist=120):
    LIBKEY = "com.andyclymer.zPosition"

    if len(g.contours):

        # Get point bounds (not the glyph bounds of the shape, but bounds of the handles too)
        boundTop = g.bounds[3]
        boundBot = g.bounds[1]
        for c in g.contours:
            for pt in c.points:
                if pt.y > boundTop:
                    boundTop = pt.y
                if pt.y < boundBot:
                    boundBot = pt.y
    
        # Find handle locations at 33.3 / 66.7 between these bounds
        p0 = [0, boundTop]
        p3 = [0, boundBot]
        p1y = interpolate(0.3333, boundTop, boundBot)
        p1x = getOpposite(angle, boundTop-p1y)
        p1 = [p1x, p1y]
        p2y = interpolate(0.6667, boundTop, boundBot)
        p2x = getOpposite(angle, p2y-boundBot)
        p2 = [p2x, p2y]
    
        if False: # Draw the curve
            pen = g.getPen()
            pen.moveTo(p0)
            pen.curveTo(p1, p2, p3)
            pen.endPath()
            g.changed()
    
        # Shift this curve so that it's balanced at the floatingDist
        midPt = splitCubicAtT(p0, p1, p2, p3, 0.5)[0][-1][0]
        floatShift = int(round((-midPt*0.5) + floatingDist))
        p0[0] += floatShift
        p1[0] += floatShift
        p2[0] += floatShift
        p3[0] += floatShift
        warpCurve = [p0, p1, p2, p3]
    
        # For each bpoint in the contour, find where it would it the curve
        # Move bPoint anchors to match the angle of that point on the curve. 
        # Keep the "y" location of all points (including handles) as they move
    
        libData = {}
    
        for c in g.contours:
        
            # Take care of the first moveTo
            pt = c.points[0]
            splitLoc, angle = splitWithAngle(warpCurve, pt.y)
            anchorZ = splitLoc[0]
            if pt.name == None:
                pt.name = makeUniqueName()
            libData[pt.name] = int(round(anchorZ))
            prevOnCurve = pt
                
            for s in c.segments:
                if len(s.points) == 3:
                    # Split at the prevOnCurve to move this bcpOut
                    bcpOut = absoluteBCP(prevOnCurve, s.points[0])
                    splitLoc, angle = splitWithAngle(warpCurve, prevOnCurve.y)
                    bcpOutZ = getOpposite(angle, bcpOut[1]) + libData[prevOnCurve.name]
                    # Split at the new on curve and move the bcpIn
                    bcpIn = absoluteBCP(s.points[-1], s.points[1])
                    splitLoc, angle = splitWithAngle(warpCurve, s.points[-1].y)
                    anchorZ = splitLoc[0]
                    bcpInZ = getOpposite(angle, bcpIn[1]) + anchorZ
                
                    # Three points now have three "z" values
                    # bcpOutZ, bcpInZ, anchorZ
                    zLocs = [bcpOutZ, bcpInZ, anchorZ]
                    for ptIdx, pt in enumerate(s.points):
                        if pt.name == None:
                            pt.name = makeUniqueName()
                        libData[pt.name] = int(round(zLocs[ptIdx]))
                else:
                    pt = s.points[0]
                    splitLoc, angle = splitWithAngle(warpCurve, pt.y)
                    anchorZ = splitLoc[0]
                    if pt.name == None:
                        pt.name = makeUniqueName()
                    libData[pt.name] = int(round(anchorZ))
                # Hold the previous onCurve for the next segment
                prevOnCurve = s.points[-1]
                        
        if LIBKEY in g.lib.keys():
            g.lib[LIBKEY].clear()
        g.lib[LIBKEY] = copy.deepcopy(libData)




class CurvePen(BasePen):
    
    def __init__(self, glyph):
        BasePen.__init__(self, glyph)
        
        self.glyph = RGlyph()
        self.pen = self.glyph.getPen()
        self.firstPt = None
        self.prevPt = None
        
    def _moveTo(self, pt):
        self.pen.moveTo(pt)
        self.firstPt = pt
        self.prevPt = pt

    def _lineTo(self, pt):
        bcpOutPt = interpolatePoints(0.33, self.prevPt, pt, roundValue=True)
        bcpInPt = interpolatePoints(0.67, self.prevPt, pt, roundValue=True)
        self.pen.curveTo(bcpOutPt, bcpInPt, pt)
        self.prevPt = pt

    def _curveToOne(self, pt1, pt2, pt3):
        self.pen.curveTo(pt1, pt2, pt3)
        self.prevPt = pt3

    def _closePath(self):
        pt = self.firstPt
        bcpOutPt = interpolatePoints(0.33, self.prevPt, pt, roundValue=True)
        bcpInPt = interpolatePoints(0.67, self.prevPt, pt, roundValue=True)
        self.pen.curveTo(bcpOutPt, bcpInPt, pt)
        self.pen.closePath()
        self.prevPt = None

    def _endPath(self):
        self.pen.endPath()
        self.prevPt = None
        
        

class WarpWindow:
    
    def __init__(self):
        self.w = vanilla.FloatingWindow((140, 110), "Warp Starter")
        self.w.curveButton = vanilla.SquareButton((10, 10, -10, 25), "Curve Segments", sizeStyle="small", callback=self.doCurve)
        self.w.warpButton = vanilla.SquareButton((10, 45, -10, 25), "AutoWarp", sizeStyle="small", callback=self.doWarp)
        self.w.warpAngle = vanilla.EditText((10, 75, 58, 25), "-45")
        self.w.floatDist = vanilla.EditText((72, 75, 58, 25), "120")
        self.w.open()
    
    def doCurve(self, sender):
        g = CurrentGlyph()
        g.prepareUndo("Curve Segments")
        if not g == None:
            pen = CurvePen(g)
            g.draw(pen)
            resultGlyph = pen.glyph
            g.clearContours()
            g.appendGlyph(resultGlyph)
        g.performUndo()
    
    def doWarp(self, sender):
        try:
            g = CurrentGlyph()
            g.prepareUndo("Warp Glyph")
            angle = self.w.warpAngle.get()
            angle = float(angle)
            floatingDist = self.w.floatDist.get()
            floatingDist = int(floatingDist)
            g = CurrentGlyph()
            warpGlyph(g, angle, floatingDist)
            g.performUndo()
        except: print("Couldn't warp! Bad values? No glyph?")
            

WarpWindow()