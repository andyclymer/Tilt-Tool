from roboHUD import BaseRoboHUDControl, registerControlClass, RoboHUDController
from mojo.events import addObserver, removeObserver
import vanilla
import math
import random
import copy


def makeUniqueName(length=None):
    if not length:
        length = 8
    name = ""
    for i in range(length):
        name += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return name



class ProjectionViewControl(BaseRoboHUDControl):
    
    """
    - glyph lib stores the "z" location under each point name
    - self.pointData holds a dict of "x,y,z" for each point name
    """

    name = "Projection View"
    size = (95, 95)
    dimWhenInactive = False

    def start(self):
        super(ProjectionViewControl, self).start()
        
        self.debug = True
        
        # Glyph and font data
        self.glyph = None
        self.LIBKEY = "com.andyclymer.zPosition"
        self.LIBKEYVIEW = "com.andyclymer.projectionViewOrientation"
        self.pointData = {} # dict of x,y,z for each pointID
        
        # Helper attributes
        self.holdChanges = False
        self.currentView = "front"
        self.enableProjection = False # Enable the buttons and save point data to the lib?
        
        # Window controls
        self.view.controlGroup = vanilla.Box((0, 0, 100, 100))
        self.view.controlGroup.buttonFront = vanilla.SquareButton((40, 5, 40, 40), "●", callback=self.rotateFront)
        self.view.controlGroup.buttonFront.enable(False)
        self.view.controlGroup.buttonSide = vanilla.SquareButton((5, 5, 30, 40), "◑", callback=self.rotateSide)
        self.view.controlGroup.buttonSide.enable(False)
        self.view.controlGroup.buttonTop = vanilla.SquareButton((40, 50, 40, 30), "◓", callback=self.rotateTop)
        self.view.controlGroup.buttonTop.enable(False)
        self.view.controlGroup.enableBox = vanilla.CheckBox((13, -38, 25, 25), "", callback=self.enableDisableCallback)
        
        addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
        addObserver(self, "fontWillSave", "glyphWindowWillClose")
        addObserver(self, "fontWillSave", "fontWillSave")
        addObserver(self, "fontDidSave", "fontDidSave")
        addObserver(self, "mouseUp", "mouseUp")

    def stop(self):
        super(ProjectionViewControl, self).stop()
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "glyphWindowWillClose")
        removeObserver(self, "fontWillSave")
        removeObserver(self, "fontDidSave")
        removeObserver(self, "fontResignCurrent")
        removeObserver(self, "fontBecameCurrent")
    
    
    # Window Callbacks
    
    def enableDisableCallback(self, sender):
        # Enable/disable the projection view
        # When disabled, rotate back to the front and stop reading/writing lib data
        self.enableProjection = self.view.controlGroup.enableBox.get()
        self._updateXYZPointData() # If enabling, need to get the point data
        self.rotate("front")
        self.updateButtons()
    
    def updateButtons(self):
        # Enable/disable buttons to match the current state
        self.view.controlGroup.buttonFront.enable(self.enableProjection)
        self.view.controlGroup.buttonSide.enable(self.enableProjection)
        self.view.controlGroup.buttonTop.enable(self.enableProjection)
        self.view.controlGroup.enableBox.set(self.enableProjection)
        if self.enableProjection:
            if self.currentView == "front":
                self.view.controlGroup.buttonFront.enable(False)
            if self.currentView == "side":
                self.view.controlGroup.buttonSide.enable(False)
            if self.currentView == "top":
                self.view.controlGroup.buttonTop.enable(False)
    
    
    # Observer Callbacks
    
    def mouseUp(self, info):
        # Write to the lib when the mouse is unclicked
        if not self.glyph == None:
            if self.enableProjection:
                self.libWriteGlyph()
    
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
    
    def currentGlyphChanged(self, info):
        # @@@ Problem?
        # @@@ When the window closes and reopens, the currentGlyph is still the same because it's selected in the font window
        # @@@ ...and the lib data doesn't properly read/write?
        # @@@ I think I need to redo this for viewDidChangeGlyph / willChangeGlyph since I only want to track the view changing
        if self.debug: print("currentGlyphChanged", info["glyph"])
        # Changed to a new glyph
        # If the glyph really did change...
        if not self.glyph == info["glyph"]:
            # Take care of the old glyph (remove observer, rotate points back to the front, update lib)
            if not self.glyph == None:
                self.glyph.removeObserver(self, "Glyph.Changed")
                #self.glyph.removeObserver(self, "Glyph.BeginUndo")
                #self.glyph.removeObserver(self, "Glyph.EndUndo")
                #self.glyph.removeObserver(self, "Glyph.BeginRedo")
                #self.glyph.removeObserver(self, "Glyph.EndRedo")
                self.rotate("front")
                self.libWriteGlyph()
            # Set the new glyph
            self.glyph = info["glyph"]
            self.pointData = {}
            # Disable the projection control for now, until we know if the glyph has point data
            self.view.controlGroup.enableBox.set(0)
            self.enableProjection = False
            # Add a new observer and fetch the glyph lib data
            if not self.glyph == None:
                self.glyph.addObserver(self, "glyphDataChanged", "Glyph.Changed")
                #self.glyph.addObserver(self, "glyphWillUndo", "Glyph.BeginUndo") # @@@ Doesn't work? Using glyphDataChanged for now
                #self.glyph.addObserver(self, "glyphDidUndo", "Glyph.EndUndo")
                #self.glyph.addObserver(self, "glyphWillUndo", "Glyph.BeginRedo")
                #self.glyph.addObserver(self, "glyphDidUndo", "Glyph.EndRedo")
                self.libReadGlyph()
            #if self.debug: print("currentGlyphChanged, pointData", self.pointData)
            # If there was no pointData, disable editing on this glyph
            if len(self.pointData.keys()) > 0:
                self.view.controlGroup.enableBox.set(1)
                self.enableProjection = True
            self.updateButtons()
    
    def _updateXYZPointData(self):
        if self.debug: print("_updateXYZPointData (glyph drawing changed)")
        # The glyph drawing changed, clean up the 3D point data
        if not self.glyph == None:
            if self.enableProjection:
                # Collect all point names in this glyph
                allNames = []
                for c in self.glyph.contours:
                    for pt in c.points:
                        if pt.name: allNames.append(pt.name)
                # Hold aside the previous point ident
                for c in self.glyph.contours:
                    prevIdent = None
                    for pt in c.points:
                        ident = pt.name#getIdentifier()
                        # Make a new point name if it doesn't have one yet
                        if ident == None:
                            ident = makeUniqueName()#getUniqueName(kind="waypoint", otherNames=list(self.pointData.keys()))
                            pt.name = ident
                        # Fix dupliate point names, if this name is being iused in another point
                        # (This would happen if the same contour was pasted back into the glyph)
                        if allNames.count(ident) > 1:
                            oldIdent = ident
                            # Get a new ident for this point
                            ident = makeUniqueName()#getUniqueName(kind="waypoint", otherNames=allNames)
                            pt.name = ident
                            # Make a new entry in self.pointData with this new name and all the copied info
                            if ident in self.pointData:
                                self.pointData[ident] = self.pointData[oldIdent].copy()
                        # If it has an ident but isn't in the point data, 
                        # either start it out with its previous neighbor's data
                        # or with zeroes for now (it will be updated in a moment)
                        if not ident in self.pointData:
                            if prevIdent:
                                self.pointData[ident] = self.pointData[prevIdent].copy()
                            else: self.pointData[ident] = dict(x=0, y=0, z=0)
                        
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
                    
                        # Hold aside the point ident for the next time through
                        prevIdent = ident
    
    def glyphDataChanged(self, notification):
        if self.debug: print("glyphDataChanged, hold:", self.holdChanges)
        # Glyph data changed
        # If it was because of an undo, the self.currentView wouldn't match what's in the lib
        libCurrentView = None
        if self.LIBKEYVIEW in self.glyph.lib:
            libCurrentView = self.glyph.lib[self.LIBKEYVIEW]
        if not self.currentView == libCurrentView:
            self.currentView = libCurrentView
            self.updateButtons()
        # Update the self.pointData
        if not self.holdChanges:
            glyph = notification.object
            if glyph == self.glyph.naked():
                self._updateXYZPointData()
    
    
    # Helper functions
    
    def libReadGlyph(self):
        if self.debug: print("libReadGlyph", self.glyph) # @@@ is it still the old glyph?
        # Read the zPosition data out of the glyph lib, but retain a dictionary of x,y,z in self.pointData for easy rotation
        self.pointData = {}
        # Rotate to the front
        self.rotate("front")
        # Read the lib data
        if not self.glyph == None:
            if self.LIBKEY in self.glyph.lib:
                libData = self.glyph.lib[self.LIBKEY]
            else: libData = {}
            #print("libData", libData)
            # Read data out of the lib
            for c in self.glyph.contours:
                for pt in c.points:
                    # bring in the "z" location if it was in the lib (only for points that still exist)
                    ident = pt.name#getIdentifier()
                    if ident:
                        if ident in libData:
                            self.pointData[ident] = dict(x=pt.x, y=pt.y, z=libData[ident])
    
    def _dataCheck(self):
        # Make sure the point data looks valid
        # A rare bug causes the (x, y) data to be applied to the z when switching glyphs
        exactX = True
        exactY = True
        for ptId, loc in self.pointData.items():
            if not loc["x"] == loc["z"]:
                exactX = False
            if not loc["y"] == loc["z"]:
                exactY = False
        if exactX or exactY:
            for ptId, loc in self.pointData.items():
                print(ptId, loc)
            return False
        else: return True
        
             
    def libWriteGlyph(self):
        if self.debug: print("libWriteGlyph", self.glyph, self.enableProjection)
        if self.debug:
            if self.LIBKEYVIEW in self.glyph.lib:
                if not self.glyph.lib[self.LIBKEYVIEW] == self.currentView:
                    # Don't write, because the lib thinks it should be in a different view
                    print("VIEW PROBLEM when writing, glyph", self.glyph.lib[self.LIBKEYVIEW], "current", self.currentView)
                    # @@@ Rotate back to the front?
        # Write the point data back to the glyph lib
        if self.enableProjection:
            if not self.glyph == None:
                if not len(self.glyph.contours):
                    if self.LIBKEY in self.glyph.lib:
                        del(self.glyph.lib[self.LIBKEY])
                else:
                    # Data check: make sure that all of the "z" data isn't exactly the same as the "x" or "y" data
                    if not self._dataCheck():
                        print("Problem with point data", self.glyph.name)
                    else:
                        self.glyph.lib[self.LIBKEY] = {}
                        libData = {}
                        for ident, pointLoc in self.pointData.items():
                            libData[ident] = pointLoc["z"]
                        self.glyph.lib[self.LIBKEY].clear()
                        self.glyph.lib[self.LIBKEY] = copy.deepcopy(libData) # @@@.update(libData)
    
    def rotate(self, viewDirection, isSaving=False):
        if self.debug: print("rotate")
        # Rotate the points in the glyph window
        if self.enableProjection:
            self.glyph.prepareUndo("Rotate")
            self.holdChanges = True
            if not self.glyph == None:
                if len(self.glyph.contours) > 0:
                    for c in self.glyph.contours:
                        for pt in c.points:
                            ident = pt.name#getIdentifier()
                            if ident == None:
                                allNames = self.pointData.keys()
                                ident = makeUniqueName()#getUniqueName(kind="waypoint", otherNames=allNames)
                                pt.name = ident
                            pointLoc = self.pointData[ident]
                            if viewDirection == "front":
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
            # Update the lib
            self.glyph.lib[self.LIBKEYVIEW] = viewDirection
            self.glyph.performUndo()
            self.holdChanges = False
            
    def rotateFront(self, sender):
        self.rotate("front")

    def rotateSide(self, sender):
        self.rotate("side")
    
    def rotateTop(self, sender):
        self.rotate("top")


registerControlClass(ProjectionViewControl)