from mojo.events import addObserver, removeObserver
from mojo.canvas import CanvasGroup
from mojo.UI import CurrentGlyphWindow
import vanilla
import math
import random
import copy
import tempfile
import os
from WebKit import WebView, NSURL
from ZdogDraw import drawZdogGlyph



"""
To Do:
    
    - Try to switch back to point IDs instead of names
    - Docs and notes in the code

"""


def makeUniqueName(length=None):
    if not length:
        length = 8
    name = ""
    for i in range(length):
        name += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return name

def getSetUniqueName(pt):
    if pt.name == None:
        pt.name = makeUniqueName()
    return pt.name
    
def interpolate(f, x0, x1):
    return x0 + (x1 - x0) * f




class ProjectionViewControl(object):
    
    def __init__(self):
        
        
        """
        @@@ ALMOST WORKING AGAIN
        Switch back to not checking for enable/disable, always leave it enabled
        
        """
        
        self.debug = True
        
        # Glyph and font data
        self.glyph = None
        self.LIBKEY = "com.andyclymer.zPosition"
        self.LIBKEYVIEW = "com.andyclymer.projectionViewOrientation"
        self.pointData = {} # dict of x,y,z for each pointID
        
        # HTML proof
        self.tempPath = tempfile.mkstemp()[1]
        self.tempHTMLPath = self.tempPath + ".html"
        
        # Helper attributes
        self.holdChanges = False
        self.currentView = "front"
        #self.enableProjection = False # Enable the buttons and save point data to the lib?
        
        # Window
        self.w = vanilla.Window((620, 750), "3D Projection View", autosaveName="ProjectionPreview")
        topHeight = 120
        self.w.controlGroup = vanilla.Box((10, 10, 100, 100))  
        self.w.controlGroup.buttonFront = vanilla.SquareButton((40, 5, 40, 40), "●", callback=self.rotateFront)
        self.w.controlGroup.buttonFront.enable(False)
        self.w.controlGroup.buttonSide = vanilla.SquareButton((5, 5, 30, 40), "◑", callback=self.rotateSide)
        self.w.controlGroup.buttonSide.enable(False)
        self.w.controlGroup.buttonTop = vanilla.SquareButton((40, 50, 40, 30), "◓", callback=self.rotateTop)
        self.w.controlGroup.buttonTop.enable(False)
        #self.w.controlGroup.enableBox = vanilla.CheckBox((13, -38, 25, 25), "", callback=self.enableDisableCallback)
        x = 130
        self.w.vRule = vanilla.VerticalLine((x-10, 10, 1, 120))
        self.w.refreshButton = vanilla.SquareButton((x, 10, 130, 25), "Refresh preview", callback=self.refreshPreviewCallback, sizeStyle="small")
        self.w.zoomScaleChoice = vanilla.PopUpButton((x, 39, 70, 25), ["50%", "75%", "100%", "150%"], sizeStyle="small", callback=self.refreshPreviewCallback)
        self.w.zoomScaleChoice.set(2)
        self.w.doStrokeBox = vanilla.CheckBox((x, 64, 100, 25), "Stroke", sizeStyle="small", value=False, callback=self.refreshPreviewCallback)
        self.w.strokeWidth = vanilla.EditText((x+60, 67, 40, 20), "90", sizeStyle="small")
        self.w.strokeWidth.enable(False)
        self.w.note = vanilla.TextBox((x, 95, -10, 25), "Note: 3D preview requires an internet connection for the Zdog library, http://www.zzz.dog/", sizeStyle="small")
        # Web view
        self.w.webView = WebView.alloc().initWithFrame_(((0, 0), (500, 500)))
        self.w.scroll = vanilla.ScrollView((10, topHeight, -10, -10), self.w.webView, hasHorizontalScroller=False, hasVerticalScroller=False)
        self.w.bind("close", self.windowClosed)
        self.w.open()
        self.updateButtons()
        self.refreshPreviewCallback(None)
        
        addObserver(self, "glyphWillChange", "viewWillChangeGlyph")
        addObserver(self, "glyphDidChange", "viewDidChangeGlyph")
        addObserver(self, "fontWillSave", "glyphWindowWillClose")
        addObserver(self, "fontWillSave", "fontWillSave")
        addObserver(self, "fontDidSave", "fontDidSave")
        addObserver(self, "mouseUp", "mouseUp")
        
            
    # Window Callbacks

    def windowClosed(self, sender):
        # 3D widget window closed, rotate back to the front
        self.rotate("front")
    
    # def enableDisableCallback(self, sender):
    #     if self.debug: print("enableDisableCallback", self.glyph, self.w.controlGroup.enableBox.get())
    #     # Enable/disable the projection view
    #     # When disabled, rotate back to the front and stop reading/writing lib data
    #     if self.glyph:
    #         self.enableProjection = self.w.controlGroup.enableBox.get()
    #         if self.enableProjection:
    #             self.libReadGlyph()
    #         self._updateXYZPointData() # Organize the point data
    #         if not self.enableProjection:
    #             self.libWriteGlyph()
    #         self.rotate("front")
    #         self.updateButtons()
    
    def updateButtons(self):
        # Enable/disable buttons to match the current state
        self.w.controlGroup.buttonFront.enable(True)
        self.w.controlGroup.buttonSide.enable(True)
        self.w.controlGroup.buttonTop.enable(True)
        #self.w.controlGroup.enableBox.set(self.enableProjection)
        #if self.enableProjection:
        if self.currentView == "front":
            self.w.controlGroup.buttonFront.enable(False)
        if self.currentView == "side":
            self.w.controlGroup.buttonSide.enable(False)
        if self.currentView == "top":
            self.w.controlGroup.buttonTop.enable(False)

    def refreshPreviewCallback(self, sender):
        # Redraw to JS file
        try:
            stroke = int(self.w.strokeWidth.get())
        except: stroke = 40
        doStroke = self.w.doStrokeBox.get()
        actualZoomSettings = [0.25, 0.33, 0.5, 1]
        zoomChoice = self.w.zoomScaleChoice.get()
        r = drawZdogGlyph(self.glyph, pointData=self.pointData, stroke=stroke, doStroke=doStroke, zoom=actualZoomSettings[zoomChoice], destPath=self.tempHTMLPath)
        # Update webView
        self.w.webView.setMainFrameURL_(self.tempHTMLPath)
        
    
    # Observer Callbacks
    
    def mouseUp(self, info):
        # Write to the lib when the mouse is unclicked
        if not self.glyph == None:
            #if self.enableProjection:
            self.holdChanges = True
            self.libWriteGlyph()
            self.holdChanges = False
    
    def fontWillSave(self, info):
        # Rotate back to the front
        # Write data to the font lib
        if not self.glyph == None:
            self.rotate("front")
            self.libWriteGlyph()
    
    def fontDidSave(self, info):
        # Rotate back to previous rotation after saving
        if not self.glyph == None:
            self.rotate(self.currentView)
    
    def glyphWillChange(self, info):
        if self.debug: print("glyphWillChange", info["glyph"])
        # If there was already a glyph, remove the observer, rotate to the front and save
        if not self.glyph == None:
            self._updateXYZPointData()
            self.rotate("front")
            self.libWriteGlyph()
        self.updateButtons()
    
    def glyphDidChange(self, info):
        if self.debug: print("glyphDidChange", info["glyph"])
        # Take care of the old glyph, if there was one
        if not self.glyph == None:
            self.glyph.removeObserver(self, "Glyph.Changed")
            self.glyph.removeObserver(self, "Glyph.LibChanged")
            self._updateXYZPointData()
            self.rotate("front")
            self.libWriteGlyph()
        self.glyph = None
        self.pointData = {}
        # Disable the projection view, until the new glyph enables it
        self.w.controlGroup.enableBox.set(0)
        #self.enableProjection = False
        # If there is a new glyph, get set up and read lib data
        if not self.glyph == info["glyph"]:
            self.glyph = info["glyph"]
            if not self.glyph == None:
                self.glyph.addObserver(self, "glyphDataChanged", "Glyph.Changed")
                self.glyph.addObserver(self, "glyphLibDataChanged", "Glyph.LibChanged")
                self.libReadGlyph()
                # If there is pointData, enable projection editing
                #if len(self.pointData.keys()) > 0:
                #    self.w.controlGroup.enableBox.set(1)
                #    self.enableProjection = True
        self.updateButtons()
    
    def glyphDataChanged(self, notification):
        if self.debug: print("glyphDataChanged, hold:", self.holdChanges)
        # Glyph data changed
        # If it was because of an undo, the self.currentView wouldn't match what's in the lib
        libCurrentView = None
        if self.LIBKEYVIEW in self.glyph.lib:
            libCurrentView = self.glyph.lib[self.LIBKEYVIEW]
        else: libCurrentView = "front"
        if not self.currentView == libCurrentView:
            self.currentView = libCurrentView
            self.updateButtons()
        # Update the self.pointData
        if not self.holdChanges:
            glyph = notification.object
            if glyph == self.glyph.naked():
                self._updateXYZPointData()

    def glyphLibDataChanged(self, info):
        if self.debug: print("glyphLibDataChanged")
        # Lib data changed, read it again
        if not self.holdChanges:
            self.libReadGlyph()
    

    # Helper functions
        
    def _cleanXYZPointData(self):
        # Before most operations, a check and a fix can be done on the pointData.
        # If multiple points share the same ID, assign new IDs and copy pointData entries for the new point IDs (happens when copying/pasting contours)
        if not self.glyph == None:
            allNames = []
            didChange = False
            for c in self.glyph.contours:
                for pt in c.points:
                    ident = getSetUniqueName(pt)
                    if not ident in allNames:
                        allNames.append(ident)
                    else:
                        if self.debug: print("Found a duplicate name!")
                        # Names are doubled up. Give the point a new name
                        pt.name = None
                        newIdent = getSetUniqueName(pt)
                        # Copy the old z location to this point and add a new entry in the pointData dict
                        if ident in self.pointData:
                            self.pointData[newIdent] = dict(x=pt.x, y=pt.y, z=self.pointData[ident]["z"])
                        didChange = True
            if didChange:
                self.libWriteGlyph()
                self.glyph.changed()
                
    def _updateXYZPointData(self):
        if self.debug: print("_updateXYZPointData (glyph drawing changed)")
        # The glyph drawing changed, clean up the 3D point data
        if not self.glyph == None:
            #if self.enableProjection:
            for c in self.glyph.contours:
                # Hold aside all point idents, to see if any are doubled up
                allNames = [pt.name for pt in c.points]
                for ptIdx, pt in enumerate(c.points):
                    ident = getSetUniqueName(pt)
                    # Fix dupliate point names, if this name is being iused in another point
                    # (This would happen if the same contour was pasted back into the glyph)
                    if allNames.count(ident) > 1:
                        oldIdent = ident
                        # Get a new ident for this point
                        pt.name = None
                        ident = getSetUniqueName(pt)
                        # Make a new entry in self.pointData with this new name and all the copied info
                        if ident in self.pointData:
                            self.pointData[ident] = self.pointData[oldIdent].copy()
                    if not ident in self.pointData:
                        # Make new point data for this point
                        # Copy the data on the hidden axis from the previous point
                        prevIdent = getSetUniqueName(c.points[ptIdx-1])
                        # Temporarily copy x,y,z, the non-hidden axes will be updated in just a sec
                        if prevIdent in self.pointData:
                            tempData = dict(
                                x=self.pointData[prevIdent]["x"],
                                y=self.pointData[prevIdent]["y"],
                                z=self.pointData[prevIdent]["z"])
                        else: tempData = dict(x=0, y=0, z=0)
                        self.pointData[ident] = tempData
                    # Set the point data, taking into account the current viewing angle
                    if self.currentView == "side":
                        locs = [self.pointData[ident]["x"], pt.y, pt.x]
                    elif self.currentView == "top":
                        locs = [pt.x, self.pointData[ident]["y"], pt.y]
                    else: # must be "front" in this case
                        locs = [pt.x, pt.y, self.pointData[ident]["z"]]
                    self.pointData[ident]["x"] = locs[0]
                    self.pointData[ident]["y"] = locs[1]
                    self.pointData[ident]["z"] = locs[2]
            # Remove point data for points that no longer exist
            toRemove = []
            allNames = []
            for c in self.glyph.contours:
                for pt in c.points:
                    allNames += [pt.name for pt in c.points]
            for ident in self.pointData.keys():
                if not ident in allNames:
                    toRemove.append(ident)
            for ident in toRemove:
                del(self.pointData[ident])
        self.updateButtons()
        
    
    def libReadGlyph(self):
        # The lib only holds the "z" position
        # Read the lib and organize it into a pointData dict that has (x, y, z)
        if self.debug: print("libReadGlyph", self.glyph)
        # Rotate to the front
        if not self.currentView == "front":
            self.rotate("front")
        # Reset the point data dictionary
        self.pointData = {}
        # Read the lib data
        if not self.glyph == None:
            if self.LIBKEY in self.glyph.lib:
                libData = self.glyph.lib[self.LIBKEY]
            else: libData = {}
            # If there is libData, enable the projection and keep procesing
            if len(libData.keys()):
                # Enable the projection, if it's not already enabled
                #self.w.controlGroup.enableBox.set(1)
                #self.enableProjection = True
                self.updateButtons()
                # Finish processing the data out of the lib
                for c in self.glyph.contours:
                    for pt in c.points:
                        ident = getSetUniqueName(pt)
                        if ident in libData:
                            zLoc = libData[ident]
                        else: zLoc = 0
                        self.pointData[ident] = dict(x=pt.x, y=pt.y, z=zLoc)
    
    def _dataCheck(self):
        # Make sure the point data looks valid
        # A rare bug causes the (x, y) data to be applied to the z when switching glyphs
        if len(self.glyph.contours) == 0:
            return True
        exactX = True
        exactY = True
        for ptId, loc in self.pointData.items():
            if not loc["x"] == loc["z"]:
                exactX = False
            if not loc["y"] == loc["z"]:
                exactY = False
        if exactX or exactY:
            #for ptId, loc in self.pointData.items():
            #    print(ptId, loc)
            return False
        else: return True
             
    def libWriteGlyph(self):
        if self.debug: print("libWriteGlyph", self.glyph)
        if self.debug:
            if self.LIBKEYVIEW in self.glyph.lib:
                glyphCurrentView = self.glyph.lib[self.LIBKEYVIEW]
            else: glyphCurrentView = "front"
            if not glyphCurrentView == self.currentView:
                # Don't write, because the lib thinks it should be in a different view
                print("VIEW PROBLEM when writing, glyph", glyphCurentView, "current", self.currentView)
        # Write the point data back to the glyph lib
        #if self.enableProjection:
        if not self.glyph == None:
            # Data check: make sure that all of the "z" data isn't exactly the same as the "x" or "y" data
            if not self._dataCheck():
                print("Problem with point data", self.glyph.name)
            else:
                libData = {}
                for ident, pointLoc in self.pointData.items():
                    libData[ident] = pointLoc["z"]
                # Remove the old lib key and only update it if there's data
                if self.LIBKEY in self.glyph.lib.keys():
                    del(self.glyph.lib[self.LIBKEY])
                #if self.LIBKEYVIEW in self.glyph.lib.keys():
                #    del(self.glyph.lib[self.LIBKEYVIEW])
                if len(libData.keys()):
                    self.glyph.lib[self.LIBKEY] = copy.deepcopy(libData)
    
    def rotate(self, viewDirection, isSaving=False):
        if self.debug: print("rotate", viewDirection, self.glyph)
        # Rotate the points in the glyph window
        #if self.enableProjection:
        self.glyph.prepareUndo("Rotate")
        # First, clean up the point data
        self._cleanXYZPointData()
        # Then, move the points around
        self.holdChanges = True
        if not self.glyph == None:
            if len(self.glyph.contours) > 0:
                for c in self.glyph.contours:
                    for pt in c.points:
                        ident = pt.name
                        if ident in self.pointData:
                            pointLoc = self.pointData[ident]
                            if viewDirection in [None, "front"]:
                                pt.x = pointLoc["x"]
                                pt.y = pointLoc["y"]
                            elif viewDirection == "side":
                                pt.x = pointLoc["z"]
                                pt.y = pointLoc["y"]
                            elif viewDirection == "top":
                                pt.x = pointLoc["x"]
                                pt.y = pointLoc["z"]
                self.glyph.changed()
            # Update the interface
            self.currentView = viewDirection
            self.updateButtons()
            # Update the lib. Remove the view direction from the lib once it's back to the front, 
            # otherwise hold the direction in the lib to help with undo
            if viewDirection == "front":
                if self.LIBKEYVIEW in self.glyph.lib.keys():
                    del(self.glyph.lib[self.LIBKEYVIEW])
            else: self.glyph.lib[self.LIBKEYVIEW] = viewDirection
            self.glyph.performUndo()
            self.holdChanges = False
            
    def rotateFront(self, sender):
        self.rotate("front")

    def rotateSide(self, sender):
        self.rotate("side")
    
    def rotateTop(self, sender):
        self.rotate("top")


ProjectionViewControl()