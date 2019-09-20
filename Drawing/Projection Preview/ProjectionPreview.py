from WebKit import WebView, NSURL
import vanilla
import tempfile
import os
from mojo.extensions import getExtensionDefault, setExtensionDefault, ExtensionBundle

from ZdogDraw import drawZdogGlyph


"""

To Do:
   Don't just read the data out of the lib and the glyph points, because it might be rotated.
   Work with a notification to call for the current glyph data?

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
                
        self.w = vanilla.Window((600, 350), minSize=(600,350), autosaveName="KernProof")
        self.w.bind("resize", self.windowResizedCallback)
        
    
        topHeight = 75
        self.w.refreshButton = vanilla.SquareButton((10, 10, 85, 25), "Refresh", callback=self.refreshPreviewCallback)
    
        x = 110
        self.w.zoomScale = vanilla.EditText((x, 10, 40, 25), "0.5")
        self.w.zoomLabel = vanilla.TextBox((x+50, 15, 50, 25), "Zoom", sizeStyle="small")
        self.w.strokeWidth = vanilla.EditText((x, 40, 40, 25), "70")
        self.w.doStrokeBox = vanilla.CheckBox((x+50, 40, 100, 25), "Stroke", sizeStyle="small", value=True)
        
        # Web view
        self.w.webView = WebView.alloc().initWithFrame_(((0, 0), (500, 500)))
        #self.w.webView.preferences().setUserStyleSheetEnabled_(True)
        #self.w.webView.preferences().setUserStyleSheetLocation_(NSURL.fileURLWithPath_(self.tempCSSPath))
        self.w.scroll = vanilla.ScrollView((0, topHeight, -0, -0), self.w.webView, hasHorizontalScroller=False, hasVerticalScroller=False)
    
        self.w.open()
        self.refreshPreviewCallback(None)
        
        
        
    def windowResizedCallback(self, sender):
        sv = self.w.scroll.getNSScrollView()
        self.w.webView.setFrame_(sv.frame())
    
    def refreshPreviewCallback(self, sender):
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
        r = drawZdogGlyph(self.glyph, pointData=self.pointData, stroke=stroke, doStroke=doStroke, zoom=self.w.zoomScale.get(), destPath=self.tempHTMLPath)

    # @@@ Copied from ProjectionViewControl.py
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
                    ident = pt.name#getIdentifier()
                    if ident:
                        if ident in libData:
                            self.pointData[ident] = dict(x=pt.x, y=pt.y, z=libData[ident])

ProjectionPreviewWindow()

