from WebKit import WebView, NSURL
import vanilla
import tempfile
import os
from mojo.extensions import getExtensionDefault, setExtensionDefault, ExtensionBundle

from ZdogDraw import drawZdogGlyph


"""
ProjectionPreview
by Andy Clymer
"""

class ProjectionPreviewWindow:
    
    def __init__(self):
        
        self.debug = False
        
        # Glyph and font data
        self.glyph = None
        self.LIBKEY = "com.andyclymer.zPosition"
        self.pointData = {} # dict of x,y,z for each pointID
        
        self.tempPath = tempfile.mkstemp()[1]
        self.tempHTMLPath = self.tempPath + ".html"
                
        self.w = vanilla.Window((620, 740), "3D Projection Preview", autosaveName="ProjectionPreview")
        self.w.bind("resize", self.windowResizedCallback)
        
        topHeight = 65
        self.w.refreshButton = vanilla.SquareButton((10, 10, 130, 25), "Reload glyph data", callback=self.refreshPreviewCallback, sizeStyle="small")
    
        x = 150
        self.w.zoomScaleChoice = vanilla.PopUpButton((x, 10, 70, 25), ["50%", "75%", "100%", "150%"], sizeStyle="small", callback=self.refreshPreviewCallback)
        self.w.zoomScaleChoice.set(2)
        self.w.strokeWidth = vanilla.EditText((x+90, 10, 40, 25), "90")
        self.w.strokeWidth.enable(False)
        self.w.doStrokeBox = vanilla.CheckBox((x+140, 10, 100, 25), "Stroke", sizeStyle="small", value=False, callback=self.refreshPreviewCallback)
        
        self.w.note = vanilla.TextBox((10, 43, -10, 25), "Note: Requires an internet connection for the Zdog library to load, http://www.zzz.dog/", sizeStyle="small")
        
        # Web view
        self.w.webView = WebView.alloc().initWithFrame_(((0, 0), (500, 500)))
        self.w.scroll = vanilla.ScrollView((10, topHeight, -10, -10), self.w.webView, hasHorizontalScroller=False, hasVerticalScroller=False)
    
        self.w.open()
        self.refreshPreviewCallback(None)
        
    def windowResizedCallback(self, sender):
        sv = self.w.scroll.getNSScrollView()
        self.w.webView.setFrame_(sv.frame())
    
    def refreshPreviewCallback(self, sender):
        self.w.strokeWidth.enable(self.w.doStrokeBox.get())
        self.windowResizedCallback(None)
        self.glyph = CurrentGlyph()
        self.libReadGlyph()
        self.redrawJS(None)
        self.w.webView.setMainFrameURL_(self.tempHTMLPath)
    
    def redrawJS(self, sender):
        # Rotate back to the front, write new HTML, rotate back to the current view, realod the webview
        try:
            stroke = int(self.w.strokeWidth.get())
        except: stroke=40
        doStroke = self.w.doStrokeBox.get()
        actualZoomSettings = [0.25, 0.33, 0.5, 1]
        zoomChoice = self.w.zoomScaleChoice.get()
        r = drawZdogGlyph(self.glyph, pointData=self.pointData, stroke=stroke, doStroke=doStroke, zoom=actualZoomSettings[zoomChoice], destPath=self.tempHTMLPath)

    def libReadGlyph(self):
        if self.debug: print("libReadGlyph")
        # Read the zPosition data out of the glyph lib, but retain a dictionary of x,y,z in self.pointData for easy rotation
        self.pointData = {}
        # Read the lib data
        if not self.glyph == None:
            if self.LIBKEY in self.glyph.lib:
                libData = self.glyph.lib[self.LIBKEY]
            else: libData = {}
            # Read data out of the lib
            for c in self.glyph.contours:
                for pt in c.points:
                    # bring in the "z" location if it was in the lib (only for points that still exist)
                    ident = pt.name
                    if ident:
                        if ident in libData:
                            self.pointData[ident] = dict(x=pt.x, y=pt.y, z=libData[ident])

ProjectionPreviewWindow()

