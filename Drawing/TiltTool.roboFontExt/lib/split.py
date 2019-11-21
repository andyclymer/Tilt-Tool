

# The start of new code for getting the third value when splitting a curve
# 2019_11_19

def _getNeighborCurveIdents(point):
    # Get the idents for the four points that are neighbors to an on-Curve,
    # they would have made up the curve that was there before it was split
    if not point.type in ["curve", "line"]:
        return []
    else:
        prevOnCurveIdent = None
        prevBcpIdent = None
        nextBcpIdent = None
        nextOnCurveIdent = None
        points = point.contour.points
        idx = points.index(point)
        for i in range(3):
            prevIdx = idx - i - 1
            pt = points[prevIdx]
            if pt.type in ["curve", "line"]:
                prevOnCurveIdent = getSetUniqueName(pt)
            else: prevBcpIdent = getSetUniqueName(pt)
        for i in range(3):
            nextIdx = idx + i + 1
            if nextIdx > len(points)-1:
                nextIdx = len(points) - nextIdx
            pt = points[nextIdx]
            if pt.type in ["curve", "line"]:
                nextOnCurveIdent = getSetUniqueName(pt)
            else: nextBcpIdent = getSetUniqueName(pt)
        # Leave out the bcps if they weren't found (it's a line)
        if None in [prevBcpIdent, nextBcpIdent]:
            idents = [prevOnCurveIdent, nextOnCurveIdent]
        else: idents = [prevOnCurveIdent, prevBcpIdent, nextBcpIdent, nextOnCurveIdent]
        return idents
    
    


def _splitFindThirdValue(point):
    # A curve was just split and point was added
    # find the third x,y,z value by fetching the point data for its neighbors, reconstrucing a curve using the other axis, and splitting again
    # Start with the neighboring curve idents
    curveIdents = _getNeighborCurveIdents(point)
    if not None in curveIdents:
        curveData = [pointData.get(ident, None) for ident in curveIdents]
        if not None in inData:
            # Split the two curves that isn't shown in the current view
            # Keep the result that only ends up with two curves
            curveZY = []
            curveXZ = []
            curveXY = []
            for d in curveData:
                curveZY.append((d["z"], d["y"]))
                curveXZ.append((d["x"], d["z"]))
                curveXY.append((d["x"], d["y"]))
            if currentView == "front": # XY
                split1 = splitCubic(*curveZY, point.x, isHorizontal=False)
                split2 = splitCubic(*curveXZ, point.y, isHorizontal=True)
            elif currentView == "side": # ZY
                split1 = splitCubic(*curveXY, point.x, isHorizontal=False)
                split2 = splitCubic(*curveXZ, point.y, isHorizontal=True)
            else: # Bottom XZ
                split1 = splitCubic(*curveXY, point.x, isHorizontal=False)
                split2 = splitCubic(*curveZY, point.x, isHorizontal=True)

# Format the curve using one axis that's not visible and anotehr axis (x)
# then split along the z at that xc location

    
    print(nextOnCurve)
    
g = CurrentGlyph()

for c in g.contours:
    for p in c.points:
        if p.selected:
            _getNeighborOnCurves(p)