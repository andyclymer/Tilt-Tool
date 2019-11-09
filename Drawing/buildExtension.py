from __future__ import absolute_import
from __future__ import print_function
import os
from mojo.extensions import ExtensionBundle


basePath = os.path.dirname(__file__)
extensionPath = os.path.join(basePath, "TiltTool.roboFontExt")
libPath = os.path.join(basePath, "lib")
htmlPath = os.path.join(basePath, "html")
resourcesPath = os.path.join(basePath, "resources")

B = ExtensionBundle()

B.name = "Tilt Tool"
B.version = "0.2"
B.developer = "Andy Clymer"
B.developerURL = 'http://www.andyclymer.com/'

B.mainScript = "ProjectionViewControl.py"
B.launchAtStartUp = False
B.addToMenu = [
    {
        'path' : 'ProjectionViewControl.py',
        'preferredName': 'Enable Projection View Control',
        'shortKey' : '',
    },
    {
        'path' : 'ProjectionPreview.py',
        'preferredName': 'Projection Preview...',
        'shortKey' : '',
    },
    {
        'path' : 'GlyphPreview.py',
        'preferredName': 'Glyph Preview...',
        'shortKey' : '',
    },
    {
        'path' : 'WarpStarter.py',
        'preferredName': 'Warp Starter...',
        'shortKey' : '',
    }]
    
B.requiresVersionMajor = '3'
B.requiresVersionMinor = '3'
B.infoDictionary["html"] = False

B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=False)

print("Done")