import math
import os
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, RuleDescriptor
from fontParts.world import OpenFont, NewFont
from defcon import Font

from euclid import *
# Packaged with the Outliner extension
from outlineFitterPen import OutlineFitterPen, MathPoint



AXISINFO = {
    "HROT": dict(name="Horizontal Rotation", minimum=-45, maximum=45, default=0),
    "VROT": dict(name="Vertical Rotation", minimum=-45, maximum=45, default=0),
    "DPTH": dict(name="Depth", minimum=-100, maximum=100, default=100),
    "SLEN": dict(name="Shadow Length", minimum=0, maximum=100, default=100),
    "SANG": dict(name="Shadow Angle", minimum=-45, maximum=45, default=45)}
AXISORDER = ["HROT", "VROT", "DPTH", "SLEN", "SANG"]



def getIdent(pt, pointData={}):
    # Get the point name, and set a name if one doesn't exist
    ident = pt.name
    if ident == None:
        ident = makeUniqueName()
        pt.name = ident
    return ident


def makeUniqueName(length=None):
    if not length:
        length = 8
    name = ""
    for i in range(length):
        name += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return name





ZPOSITIONLIBKEY = "com.andyclymer.zPosition"
def readGlyphPointData(glyph):
    """
    Read the pointData out of the glyph lib
    """
    # Read the zPosition data out of the glyph lib, but retain a dictionary of x,y,z in pointData for easy rotation
    pointData = {}
    # Read the lib data
    if not glyph == None:
        if ZPOSITIONLIBKEY in glyph.lib:
            libData = glyph.lib[ZPOSITIONLIBKEY]
        else: libData = {}
        # Read data out of the lib
        for c in glyph.contours:
            for pt in c.points:
                # bring in the "z" location if it was in the lib (only for points that still exist)
                ident = getIdent(pt)
                if ident in libData:
                    zLoc = libData[ident]
                else: zLoc = 0
                pointData[ident] = zLoc#dict(x=pt.x, y=pt.y, z=zLoc)
    return pointData


def forceSmooth(bPt):
    """
    Force a bPoint to be smooth by moving its bcps into alignment
    """
    # Convert to mathPoints
    anchorPt = MathPoint(bPt.anchor)
    bcpIn = MathPoint(bPt.bcpIn)
    bcpInPt = anchorPt + bcpIn
    bcpOut = MathPoint(bPt.bcpOut)
    bcpOutPt = anchorPt + bcpOut
    # Get some BCP info
    distIn = anchorPt.distance(bcpInPt)
    angleIn = anchorPt.angle(bcpInPt, add=0)
    distOut = anchorPt.distance(bcpOutPt)
    angleOut = bcpOutPt.angle(anchorPt, add=0)
    # Average the angle
    if not None in [angleOut, angleIn, distOut, distIn]:
        avgAngle = ((distIn * angleIn) + (distOut * angleOut)) / (distIn + distOut)
        # Move the BCPs
        newIn = MathPoint(math.cos(avgAngle), math.sin(avgAngle)) * distIn
        newOut = MathPoint(math.cos(avgAngle), math.sin(avgAngle)) * distOut
        bPt.bcpIn = (newIn.x, newIn.y)
        bPt.bcpOut = (-newOut.x, -newOut.y) 


def testPointAlignent(bPt, pointData, angleError=0.1):
    """
    Test to see if a bPoint and its previous neighbor have BCPs that are in alignment
    """
    c = bPt.contour
    idx = bPt.index
    if c.open and idx in [0, 1]:
        # First point on an open contour, no problem here
        return False
    else:
        prevBPt = c.bPoints[idx-1]
        if [0, 0] in [prevBPt.bcpOut, prevBPt.bcpIn]:
            # There are no handles, no problem here
            return False
        else:
            # Make MathPoints
            prevAnchor = MathPoint(prevBPt.anchor)
            thisBcpOut = MathPoint(prevBPt.bcpOut)
            prevBCP = prevAnchor + thisBcpOut
            thisAnchor = MathPoint(bPt.anchor)
            thisBcpIn = MathPoint(bPt.bcpIn)
            thisBCP = thisAnchor + thisBcpIn
            # Find angles
            thisAngle = thisBCP.angle(thisAnchor)
            if not thisAngle: thisAngle = 0
            prevAngle = prevBCP.angle(prevAnchor)
            if not prevAngle: prevAngle = 0
            # If the angles are already within error range
            if abs(thisAngle - prevAngle) < angleError:
                # Test all combinations of bcps and anchors
                avg = (thisAngle + prevAngle) * 0.5
                testAngles = [
                    thisBCP.angle(prevAnchor),
                    thisBCP.angle(prevBCP),
                    prevBCP.angle(thisAnchor),
                    thisAnchor.angle(prevAnchor)]
                # If any of these are over the error amount, they don't overlap
                for testAngle in testAngles:
                    if abs(thisAngle - prevAngle) > angleError:
                        return False
                # All test angles were under the limit
                # Find which point is further back, that's the one that will move
                prevIdent = getIdent(bPt._point)
                thisIdent = getIdent(prevBPt._point)
                if pointData[thisIdent] < pointData[prevIdent]:
                    return bPt, thisAngle
                else: return prevBPt, thisAngle
    return False
    


def fixPointAlignment(g, pointData):
    # Find any overlapping points that need to move
    # Build new glyphs in the master font with nudged points
    # Return info about the change so that it cna prepare rules
    overlappingPts = {}
    for cIdx, c in enumerate(g.contours):
        for bPtIdx, bPt in enumerate(c.bPoints):
            result = testPointAlignent(bPt, pointData)
            if not result == False:
                bPtToMove, angle = result
                ident = getIdent(bPtToMove._point)
                angle = math.degrees(angle)
                if angle in [360, 180]:
                    if not "h" in overlappingPts:
                        overlappingPts["h"] = []
                    overlappingPts["h"].append(ident)
                elif angle in [270, 90]:
                    if not "v" in overlappingPts:
                        overlappingPts["v"] = []
                    overlappingPts["v"].append(ident)
                else:
                    if not "hv" in overlappingPts:
                        overlappingPts["hv"] = []
                    overlappingPts["hv"].append(ident)
    # "n", "w", and "nw" are the defaults when making glyphs
    categories = []
    idents = []
    for category in overlappingPts.keys():
        categories.append(category)
        for i in overlappingPts[category]:
            if not i in idents:
                idents.append(i)
    extensions = []
    # @@@ For now, build all of the options if one is needed
    if len(categories):
        extensions += [(".ne", (4, -4)), (".sw", (-4, 4)), (".se", (4, 4)), (None, (-4, -4))] # Normal glyph is "nw" # flipped the sign on the y axis
    # if "hv" in categories or "h" and "v" in categories:
    #     extensions += [(".ne", (2, 2)), (".sw", (-2, -2)), (".se", (2, -2)), (None, (-2, 2))]
    # if "h" in categories:
    #     extensions += [(".e", (2, 0)), (None, (-2, 0))]
    # if "v" in categories:
    #     extensions += [(".s", (0, -2)), (None, (0, 2))]
    # Make new glyphs
    newGlyphs = []
    font = g.font
    for extension, offset in extensions:
        if extension:
            newGlyphName = g.name + extension
            font.newGlyph(newGlyphName)
            ng = font[newGlyphName]
            ng.clear()
            ng.appendGlyph(g)
            ng.width = g.width
            ng.lib[ZPOSITIONLIBKEY] = pointData.copy()
            newGlyphs.append(ng)
        else:
            # No extension, this is just hte base glyph that needs to move
            ng = g
        # Move points
        for c in ng.contours:
            for bPt in c.bPoints:
                thisIdent = getIdent(bPt._point)
                if thisIdent in idents:
                    bPt.moveBy(offset)
        ng.changed()
    # Done
    return newGlyphs
                        



""" Glyph Transformations """
    

def rotateGlyph(g, sourceInfo, pointData, angle=45, aLoc=None):# valueX=0, valueY=0, zDepthFactor=1):
    # Turn the 1, 0, -1 into actual angles
    valueX = AXISINFO["VROT"][sourceInfo["VROT"]]
    valueY = AXISINFO["HROT"][sourceInfo["HROT"]]#sourceInfo["HROT"] * angle
    
    # Rotation axis
    axisVectorX = Vector3(1, 0, 0)
    axisVectorY = Vector3(0, 1, 0)
    
    # Location in the glph for the rotation to happen
    aLoc = (g.width * 0.5, 
            g.font.info.xHeight * 0.5,
            0)
            
    for c in g.contours:
        for pt in c.points:
            
            # Fetch the point data
            ident = pt.name#getIdentifier()
            if ident == None:
                allNames = pointData.keys()
                ident = makeUniqueName()
                pt.name = ident
            
            #v = pointData[ident].copy()
            #v = Vector3(pointData[ident]["x"], pointData[ident]["y"], pointData[ident]["z"])
            v = Vector3(pt.x, pt.y, pointData[ident])
        
            # Invert the "z" position
            #v.z = -v.z
            #v.z = v.z * 0.5
            # Translate
            m = Matrix4.new_translate(-aLoc[0], -aLoc[1], -aLoc[2])
            v = m.transform(v)
            # Rotate X
            m = m.new_rotate_axis(math.radians(valueX), axisVectorX)
            v = m.transform(v)
            # Rotate Y
            m = m.new_rotate_axis(math.radians(valueY), axisVectorY)
            v = m.transform(v)
            # Translate
            m = Matrix4.new_translate(aLoc[0], aLoc[1], aLoc[2])
            v = m.transform(v)
            
            # Move the point
            pt.x = v[0]
            pt.y = v[1]
            pt.z = v[2]
            
        c.changed()
        
    # Transform the margins
    # Rotate a point from (0, 0) and use the x offset for both margins
    v = Vector3(0, 0, 0)
    m = Matrix4.new_translate(-aLoc[0], -aLoc[1], -aLoc[2])
    v = m.transform(v)
    # Rotate
    m = m.new_rotate_axis(math.radians(valueY), axisVectorY)
    v = m.transform(v)
    # Translate
    m = Matrix4.new_translate(aLoc[0], aLoc[1], aLoc[2])
    v = m.transform(v)
    # The "y" value is the LSB and RSB offset
    g.leftMargin -= v[0]
    g.rightMargin -= v[0]



def flattenShadow(g, pointData, shadowDirection="right", shadowLengthFactor=1):
    """
    Apply the "z" depth to the "x" and "y" axis to flatten out a shadow
    shadowDirection = "left", "right", "center"
    shadowLengthFactor = multiplier on top of the "z" depth for the length of the shadow
    """
    # Flatten out the "Z" axis as a shadow
    #print(shadowAngle)
    for c in g.contours:
        for p in c.points:
            x = p.x
            y = p.y
            if p.name in pointData:
                z = pointData[p.name]
                if shadowDirection == "left":
                    x -= z * shadowLengthFactor
                    y -= z * shadowLengthFactor
                elif shadowDirection == "right":
                    x += z * shadowLengthFactor
                    y -= z * shadowLengthFactor
                else: # straight down
                    y -= z * shadowLengthFactor
                p.x = x
                p.y = y
                pointData[p.name] = 0#dict(x=x, y=y, z=0)
    return pointData


def outlineGlyph(g, offsetAmount, contrast=0, contrastAngle=0):
    """
    Outline a glyph
    """
    # Copy to background
    gl = g.getLayer("background")
    gl.appendGlyph(g)
    # Outline
    pen = OutlineFitterPen(None, offsetAmount, connection="Round", cap="Round", closeOpenPaths=True, alwaysConnect=True, contrast=contrast, contrastAngle=contrastAngle) 
    g.draw(pen)
    g.clear()
    pen.drawSettings(drawOriginal=False, drawInner=True, drawOuter=True)
    pen.drawPoints(g.getPointPen())




def buildDesignSpace(
        masterPath=None, 
        destPath=None, 
        glyphNames=[],
        compositionType="rotate", 
        outlineAmount=None, 
        forceSmooth=False,
        overlappingCurveFix=False,
        familyName=None,
        styleName=None):
    
    # Set up masters
    basePath, masterFileName = os.path.split(masterPath)
    if destPath == None:
        destPath = os.path.join(basePath, "Rotated")
    # Make new folders for the destPath
    if not os.path.exists(destPath):
        os.makedirs(destPath)
    
    # DesignSpace Document
    designSpace = DesignSpaceDocument()
    designSpaceDocFilename = os.path.splitext(masterFileName)[0] + ".designspace"
    designSpaceDocPath = os.path.join(destPath, designSpaceDocFilename)
    
    """ Source combinations and axis tags """
    
    # Collect axis tags and source info, based on the layout type
    sourceCombinations = []
    axisTags = []

    if compositionType == "rotate and depth":
        # Rotation, and "z" changes depth
        for valueHROT in ["minimum", "default", "maximum"]:
            for valueVROT in ["minimum", "default", "maximum"]:
                for valueDPTH in ["minimum", "default"]:
                    sourceCombinations.append(dict(HROT=valueHROT, VROT=valueVROT, DPTH=valueDPTH))
    elif compositionType == "rotate and shadow":
        # Rotation, and shadow length and angle
        for valueHROT in ["minimum", "default", "maximum"]:
            for valueVROT in ["minimum", "default", "maximum"]:
                for valueSLEN in ["minimum", "default"]:
                    for valueSANG in ["minimum", "maximum"]:
                        sourceCombinations.append(dict(HROT=valueHROT, VROT=valueVROT, SLEN=valueSLEN, SANG=valueSANG))
    else: # Normal rotation
        for valueHROT in ["minimum", "default", "maximum"]:
            for valueVROT in ["minimum", "default", "maximum"]:
                sourceCombinations.append(dict(HROT=valueHROT, VROT=valueVROT))
                
    # AxisDescriptors
    for tag in sourceCombinations[0].keys():
        a = AxisDescriptor()
        a.minimum = AXISINFO[tag]["minimum"]
        a.maximum = AXISINFO[tag]["maximum"]
        a.default = AXISINFO[tag]["default"]
        a.name = AXISINFO[tag]["name"]
        a.tag = tag
        a.labelNames[u'en'] = AXISINFO[tag]["name"]
        designSpace.addAxis(a)
        
    
    """ Make the source UFOs and SourceDescriptors """
        
    masterFont = OpenFont(path=masterPath, showInterface=False)
    #masterFont = Font(masterPath)
        
    for sourceInfo in sourceCombinations:
        # Build a filename
        fileNamePieces = []
        for tag in AXISORDER:
            if tag in sourceInfo:
                comboName = sourceInfo[tag]
                if comboName == "minimum":
                    comboName = tag + "n"
                elif comboName == "maximum":
                    comboName = tag + "x"
                else: comboName = tag + "d"
                fileNamePieces.append(comboName)
        tagName = "_".join(fileNamePieces)
        fileName = "Source-%s.ufo" % tagName
        sourceUfoPath = os.path.join(destPath, fileName)
        sourceInfo["fileName"] = fileName
        if not os.path.exists(sourceUfoPath):
            sourceFont = NewFont(showInterface=False)
            sourceFont.save(sourceUfoPath)
            sourceFont.info.familyName = familyName
            sourceFont.info.styleName = styleName
            sourceFont.save()
            sourceFont.close()
    

    """ Process Glyphs """
    
    # Collect all of the point data out of the lib
    glyphPointData = {}
    for gName in glyphNames:
        if gName in masterFont:
            g = masterFont[gName]
            pointData = readGlyphPointData(g)
            glyphPointData[gName] = pointData
        
    # A container for glyph names that need to follow a directional rule
    # After all glyph processing, these will be turned into RuleDescriptors
    # north and west are the defaults
    ruleConditionCategories = {
        #"n": [],
        "s": [],
        "e": [],
        #"w": [],
        "ne": [],
        #"nw": [],
        "se": [],
        "sw": []}
    
    # Build new glyphs to get ready for the glyph swapping rules (only if we're outlining)
    if overlappingCurveFix:
        glyphNames = list(glyphPointData.keys())
        for gName in glyphNames:
            g = masterFont[gName]
            pointData = glyphPointData[gName].copy()
            # Make adjustments and copies of the glyph to fix overlaps
            # Hold aside the new glyph names in the ruleConditionCategories containers
            # ruleConditionGlyphs are tuples of (glyphObj, category)
            # The actual glyph object "gDest" may also be changed, but not returned
            # and the new glyph will have all of the proper point data in its lib
            ruleConditionGlyphs = fixPointAlignment(g, pointData)
            for ruleGlyph in ruleConditionGlyphs:
                # Copy the point data to the dict
                glyphPointData[ruleGlyph.name] = glyphPointData[gName].copy()
                # Organize these new glyphs into their categories
                extensions = ruleConditionCategories.keys() # ["s", "e", "ne", "se", "sw"]
                for extension in ruleConditionCategories.keys():
                    if ruleGlyph.name.endswith("." + extension):
                        ruleConditionCategories[extension].append((gName, ruleGlyph.name))
    # @@@
    #print(ruleConditionCategories)

    # Process each UFO source, one at a time
    for sourceInfo in sourceCombinations:
        sourceUfoPath = os.path.join(destPath, sourceInfo["fileName"])
        sourceFont = OpenFont(path=sourceUfoPath, showInterface=False)
        #sourceFont = Font(sourceUfoPath)
        
        for gName in glyphPointData:
            pointData = glyphPointData[gName].copy()
            
            if "DPTH" in sourceInfo:
                if sourceInfo["DPTH"] == "minimum":
                    for ident in pointData:
                        pointData[ident] = -pointData[ident]
        
            # Get the glyph started
            g = masterFont[gName]
            if not gName in sourceFont:
                sourceFont.newGlyph(gName)
            gDest = sourceFont[gName]
            gDest.clear()
            gDest.appendGlyph(g)
            gDest.width = g.width
        
            # Extend the shadow
            if "SANG" in sourceInfo.keys():
                if sourceInfo["SANG"] == "minimum":
                    shadowDirection = "left"
                else: shadowDirection = "right"
                if sourceInfo["SLEN"] == "minimum":
                    shadowLengthFactor = 0
                else: shadowLengthFactor = 1
                #pointData = flattenShadow(gDest, pointData, shadowDirection, shadowLengthFactor * 2)
                pointData = flattenShadow(gDest, pointData, shadowDirection, shadowLengthFactor)
        
            # Rotate the glyph
            rotateGlyph(gDest, sourceInfo, pointData, angle=45)
        
            # Outline the glyph
            if outlineAmount:
                # @@@ Commenting out for now, doesn't look good
                # # Add contrast if it's the shadow
                # contrast = 0
                # contrastAngle = 0
                # if "SANG" in sourceInfo.keys():
                #     if not sourceInfo["SLEN"] == "minimum":
                #         contrast = outlineAmount * 2
                #         if sourceInfo["SANG"] == "minimum":
                #             contrastAngle = -45
                #         elif sourceInfo["SANG"] == "minimum":
                #             contrastAngle = 45
                # Outline
                outlineGlyph(gDest, outlineAmount)
                # @@@ and use contrast if its' a shaodw
        
            # Update
            gDest.changed()
        
        # @@@ After outlining, move overlapping points back
        # @@@ Might be difficult because now they've also rotated?
        # @@@ This way I can move the points even futher before outlining, which would result in better outlines
        
        # Done, save
        sourceFont.changed()
        sourceFont.save()


    """ Source Descriptors """

    for sourceInfo in sourceCombinations:
        sourceUfoPath = os.path.join(destPath, sourceInfo["fileName"])
        # Make a source description
        s = SourceDescriptor()
        s.path = sourceUfoPath
        s.name = os.path.splitext(sourceInfo["fileName"])[0]
        #s.font = defcon.Font(s.name)
        s.copyLib = True
        s.copyInfo = True
        s.copyFeatures = True
        s.familyName = masterFont.info.familyName
        s.styleName = s.name
        loc = {}
        for tag, value in sourceInfo.items():
            if not tag in ["fileName"]: # @@@ A little sloppy to do this
                if tag in AXISINFO:
                    axisName = AXISINFO[tag]["name"]
                    loc[axisName] = AXISINFO[tag][value]
                    # if value == "n":
                    #     loc[axisName] = AXISINFO[tag]["minimum"]
                    # elif value == "x":
                    #     loc[axisName] = AXISINFO[tag]["maximum"]
                    # else: # default
                    #     loc[axisName] = AXISINFO[tag]["default"]
        s.location = loc
        designSpace.addSource(s)
    
    
    """ Rule Descriptors """
    
    # Make the RuleDescriptors based on the ruleConditionCategories data
    HROTNAME = AXISINFO["HROT"]["name"]
    VROTNAME = AXISINFO["VROT"]["name"]
    for categoryName, ruleGlyphPairs in ruleConditionCategories.items():
        if len(ruleGlyphPairs):
            rd = RuleDescriptor()
            rd.name = categoryName
            conditions = []
            if categoryName == "n":
                conditions = [dict(name=VROTNAME, minimum=0, maximum=45)]
            elif categoryName == "s":
                conditions = [dict(name=VROTNAME, minimum=-45, maximum=0)]
            elif categoryName == "e":
                conditions = [dict(name=HROTNAME, minimum=0, maximum=45)]
            elif categoryName == "w":
                conditions = [dict(name=HROTNAME, minimum=-45, maximum=0)]
            elif categoryName == "ne":
                conditions = [dict(name=VROTNAME, minimum=0, maximum=45), dict(name=HROTNAME, minimum=0, maximum=45)]
            elif categoryName == "nw":
                conditions = [dict(name=VROTNAME, minimum=0, maximum=45), dict(name=HROTNAME, minimum=-45, maximum=0)]
            elif categoryName == "se":
                conditions = [dict(name=VROTNAME, minimum=-45, maximum=0), dict(name=HROTNAME, minimum=0, maximum=45)]
            elif categoryName == "sw":
                conditions = [dict(name=VROTNAME, minimum=-45, maximum=0), dict(name=HROTNAME, minimum=-45, maximum=0)]
            rd.conditionSets.append(conditions)
            for pair in ruleGlyphPairs:
                rd.subs.append(pair)
            designSpace.addRule(rd)
    
    
    
    # @@@ Ready to
    # @@@ - Build the font


    designSpace.write(designSpaceDocPath)
    
    
    

