

HTMLTEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width" />

  <title>Path commands</title>

  <style>
    html { height: 100%; }

    body {
      min-height: 100%;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: sans-serif;
      text-align: center;
    }

    .illo {
      display: block;
      margin: 20px auto;
      background: #FFF;
      cursor: move;
    }
  </style>

</head>
<body>

<div class="container">
  <canvas class="illo" width="580" height="580"></canvas>
</div>

<script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>

<script type = "text/javascript">
 <!--

    // ----- variables ----- //

    var eggplant = '#636';
    var black = '#000'
    var red = '#f00';
    var strokeWidth = 20;

    // ----- model ----- //

    var illo = new Zdog.Illustration({
      element: '.illo',
      zoom: @@@ZOOM@@@,
      dragRotate: true,
    });

    // ----- drawing commands ----- //

@@@COMMANDS@@@

    // ----- animate ----- //

    function animate() {
      illo.updateRenderGraph();
      requestAnimationFrame( animate );
    }
    animate();

    //let viewRotation = new Zdog.Vector();
    //viewRotation.x = 3.14159
    //viewRotation.y = 0
    //viewRotation.z = 0
    //illo.rotate.set(viewRotation);
    
 //-->
</script>

</body>
</html>
"""



# Canvas size
CANVASWIDTH = 600
CANVASHEIGHT = 600


def makeUniqueName(length=None):
    if not length:
        length = 8
    name = ""
    for i in range(length):
        name += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return name


def getZ(pointData, point):
    # Get the z value for this point from the pointData
    ident = point.name#getIdentifier()
    if ident == None:
        allNames = self.pointData.keys()
        ident = makeUniqueName()
        pt.name = ident
    if ident in pointData:
        ptData = pointData[ident]
        return ptData.z
    else: return 0


def getLoc(pointData, point):
    # Get the z value for this point from the pointData
    ident = point.name
    if ident in pointData:
        ptData = pointData[ident]
        # Subtract the y from the height to flip the coordinates
        # Invert the "z" so that a positive value in my font data is negative depth
        return (ptData["x"], CANVASHEIGHT-ptData["y"], ptData["z"])
    else: return (0, 0, 0)
    


def drawZdogGlyph(g, pointData=None, offset=None, stroke=20, doStroke=True, zoom=0.5, destPath=None):
    
    """
    Draw a glyph to a Zdog JS file
    
    To Do:
        Optionally show handles and points
        Possibly also take a callback to reload the HTML?
    
    """
    
    js = ""
    prevPt = None
    
        
    
    if not g == None:
        
        if not len(g.contours) == 0:
        
            # Center the glyph if there's no offset given
            if offset == None:
                glyphWidth, glyphHeight = (g.box[2] - g.box[0], g.box[3] - g.box[1])
                #offset = (-width * 0.5, -height*0.5)
                offset = ( -(glyphWidth*0.5),  -(glyphHeight*0.5) )
                # offset = (0, 0)
            
            
            for c in g.contours:
        
                # Set the start point, either the first point if the contour is open, or the last point if the contour is closed
                if c.open:
                    prevPt = c.segments[0].points[0]
                else: prevPt = c.segments[-1].points[-1]
        
                # Draw the contours
                for sIdx, s in enumerate(c.segments):
            
                    # New shape for this segment
                    js += "\n\nnew Zdog.Shape({\n  addTo: illo,\n  path: ["
            
                    if len(s.points) == 1:
                        #pts = (prevPt.x, prevPt.y, getZ(pointData, prevPt), s.points[0].x, s.points[0].y, getZ(pointData, s.points[0]))
                        prevLoc = getLoc(pointData, prevPt)
                        ptLoc = getLoc(pointData, s.points[0])
                        pts = (prevLoc[0], prevLoc[1], prevLoc[2], ptLoc[0], ptLoc[1], ptLoc[2])
                        js += "\n    { x: %s, y: %s , z: %s },\n    { x: %s, y: %s , z: %s },\n  ]," % pts
                        prevPt = s.points[0]
            
                    else:
                        pts = []
                        for pt in s.points:
                            #pts += [pt.x, pt.y, getZ(pointData, pt)]
                            ptLoc = getLoc(pointData, pt)
                            pts += [ptLoc[0], ptLoc[1], ptLoc[2]]
                        prevLoc = getLoc(pointData, prevPt)
                        js += "\n    { x: %s, y: %s , z: %s }," % (prevLoc[0], prevLoc[1], prevLoc[2])
                        js += "\n    { bezier: [{ x:  %s, y: %s, z: %s}, { x:  %s, y:  %s, z: %s }, { x:  %s, y:  %s, z: %s },]},\n  ]," % tuple(pts)
                        prevPt = s.points[-1]
        
                    if not offset == (0, 0):
                        js += "\n  translate: { x: %s, y: %s }," % offset
                    js += "\n  closed: false,"
            
                    if s.selected:
                        color = "red"
                    else: color = "black"
                    js += "\n  color: %s," % color
                    if doStroke:
                        js += "\n  stroke: %s,\n" % stroke
                        js += "\n  fill: false,\n"
                        js += "\n});\n"
                    else:
                        js += "\n  stroke: false,\n"
                        js += "\n  fill: true,\n"
                        js += "\n});\n"
                        
    
    # Write the file, if a path was given
    if not destPath == None:
        fullHTML = HTMLTEMPLATE.replace("@@@COMMANDS@@@", js)
        fullHTML = fullHTML.replace("@@@ZOOM@@@", str(zoom))
        htmlFile = open(destPath, "w")
        htmlFile.write(fullHTML)
        htmlFile.close()
    
    return js



"""
g = CurrentGlyph()

canvasSize = (1000, 1000)
width, height = (g.box[2] - g.box[0], g.box[3] - g.box[1])
offset = (-width * 0.5, -height*0.5)
zdogGlyph(g, offset=offset)
"""
