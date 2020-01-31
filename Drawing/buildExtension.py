from __future__ import absolute_import
from __future__ import print_function
import os
from mojo.extensions import ExtensionBundle


basePath = os.path.dirname(__file__)
extensionPath = os.path.join(basePath, "3DProjectionView.roboFontExt")
libPath = os.path.join(basePath, "lib")
htmlPath = os.path.join(basePath, "html")
resourcesPath = os.path.join(basePath, "resources")

B = ExtensionBundle()

B.name = "3D Projection View"
B.version = "0.7"
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
        'preferredName': 'DesignSpace Preview...',
        'shortKey' : '',
    }]
    
B.requiresVersionMajor = '3'
B.requiresVersionMinor = '3'
B.infoDictionary["html"] = True

B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=False)

print("Done")