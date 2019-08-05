from roboHUD import BaseRoboHUDControl, registerControlClass, RoboHUDController
from mojo.events import addObserver, removeObserver
from ac.data.names import getUniqueName
import vanilla
import math




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
        
        self.debug = False
        
        # Glyph and font data
        self.glyph = None
        self.LIBKEY = "com.andyclymer.zPosition"
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
        # Changed to a new glyph
        # If the glyph really did change...
        if not self.glyph == info["glyph"]:
            # Take care of the old glyph (remove observer, rotate points back to the front, update lib)
            if not self.glyph == None:
                self.glyph.removeObserver(self, "Glyph.Changed")
                self.rotate("front")
                self.libWriteGlyph()
            # Set the new glyph
            self.glyph = info["glyph"]
            self.pointData = {}
            # Add a new observer and fetch the glyph lib data
            if not self.glyph == None:
                self.glyph.addObserver(self, "glyphDataChanged", "Glyph.Changed")
                self.libReadGlyph()
            if self.debug: print(self.pointData)
            # If there was no pointData, disable editing on this glyph
            if len(self.pointData.keys()) == 0:
                self.enableProjection = False
            else: self.enableProjection = True
            self.updateButtons()
    
    def _updateXYZPointData(self):
        if self.debug: print("_updateXYZPointData")
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
                            ident = getUniqueName(kind="waypoint", otherNames=list(self.pointData.keys()))
                            pt.name = ident
                        # Fix dupliate point names, if this name is being used in another point
                        # (This would happen if the same contour was pasted back into the glyph)
                        if allNames.count(ident) > 1:
                            oldIdent = ident
                            # Get a new ident for this point
                            ident = getUniqueName(kind="waypoint", otherNames=allNames)
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
        if self.debug: print("glyphDataChanged")
        # Glyph data changed, update the self.pointData
        if not self.holdChanges:
            glyph = notification.object
            if glyph == self.glyph.naked():
                self._updateXYZPointData()
    
    
    # Helper functions
    
    def libReadGlyph(self):
        if self.debug: print("libReadGlyph")
        # Read the zPosition data out of the glyph lib, but retain a dictionary of x,y,z in self.pointData for easy rotation
        self.pointData = {}
        # Rotate to the front
        self.rotate("front")
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
             
    def libWriteGlyph(self):
        if self.debug: print("libWriteGlyph", self.enableProjection)
        # Write the point data back to the glyph lib
        if self.enableProjection:
            if not self.glyph == None:
                if not len(self.glyph.contours):
                    if self.LIBKEY in self.glyph.lib:
                        del(self.glyph.lib[self.LIBKEY])
                else:
                    self.glyph.lib[self.LIBKEY] = {}
                    libData = {}
                    for ident, pointLoc in self.pointData.items():
                        libData[ident] = pointLoc["z"]
                    self.glyph.lib[self.LIBKEY].update(libData)
    
    def rotate(self, viewDirection, isSaving=False):
        if self.debug: print("rotate")
        # Rotate the points in the glyph window
        if self.enableProjection:
            self.holdChanges = True
            if not self.glyph == None:
                if len(self.glyph.contours) > 0:
                    # Clean up the data, just in case if the tool missed something
                    self._updateXYZPointData()
                    for c in self.glyph.contours:
                        for pt in c.points:
                            ident = pt.name#getIdentifier()
                            if ident == None:
                                allNames = self.pointData.keys()
                                ident = getUniqueName(kind="waypoint", otherNames=allNames)
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
            self.holdChanges = False
            # Update the interface
            self.currentView = viewDirection
            self.updateButtons()
            
    def rotateFront(self, sender):
        self.rotate("front")

    def rotateSide(self, sender):
        self.rotate("side")
    
    def rotateTop(self, sender):
        self.rotate("top")


registerControlClass(ProjectionViewControl)