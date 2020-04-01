
# Remove the data from the lib
# Reset point names

f = CurrentFont()
for gn in f.selection:

    g = f[gn]
    for layerName in ["foreground", "outline", "background"]:
        gl = g.getLayer(layerName)
    
        if "com.andyclymer.zPosition" in gl.lib.keys():
            del(gl.lib["com.andyclymer.zPosition"])

        for c in gl.contours:
            for p in c.points:
                p.name = None