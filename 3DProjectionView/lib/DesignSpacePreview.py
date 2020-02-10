from AppKit import NSScreen
import os

import vanilla
from defconAppKit.controls.glyphView import GlyphView
from mojo.UI import GetFile, OpenGlyphWindow, AllFontWindows
from mojo.events import addObserver, removeObserver

from fontTools.designspaceLib import DesignSpaceDocument
from ufoProcessor import DesignSpaceProcessor

from euclid import Vector3


def measureBCPs(bPt):
    # Measure BCP handle lengths
    vBcpIn = Vector3(*bPt.bcpIn)
    vBcpOut = Vector3(*bPt.bcpOut)
    return (vBcpIn.magnitude(), vBcpOut.magnitude())

    
def shiftBPoint(bPt, targetMeasurements=(1, 1), roundPoints=True, moveAnchor=True):
    # Shift the BCPs, and then the entire bPoint, to get the handles to match the ratio of targetMeasurements
    vBcpIn = Vector3(*bPt.bcpIn)
    vBcpOut = Vector3(*bPt.bcpOut)
    totalLength = vBcpIn.magnitude() + vBcpOut.magnitude()
    # Find the target ratios for the BCPs
    targetIn = targetMeasurements[0] / sum(targetMeasurements)
    targetOut = targetMeasurements[1] / sum(targetMeasurements)
    # Recalculate BCPs
    vBcpInNew = vBcpIn.copy()
    vBcpInNew.normalize()
    vBcpInNew *= targetIn * totalLength
    vBcpOutNew = vBcpOut.copy()
    vBcpOutNew.normalize()
    vBcpOutNew *= targetOut * totalLength
    # Move the BCPs
    bPt.bcpIn = (vBcpInNew[0], vBcpInNew[1])
    bPt.bcpOut = (vBcpOutNew[0], vBcpOutNew[1])
    # Shift the entire BCP to spread the movement between the BCPs
    if moveAnchor:
        bcpMoved = (vBcpInNew - vBcpIn) * -0.5
        bPt.moveBy((bcpMoved[0], bcpMoved[1]))
    if roundPoints:
        bPt.round()
        

def scaleMagnitude(bPt, value, roundPoints=True):
    # Scale the magnitude of both BCPs without moving the anchor
    vBcpIn = Vector3(*bPt.bcpIn)
    vBcpOut = Vector3(*bPt.bcpOut)
    vBcpIn *= value
    vBcpOut *= value
    # Move the points
    bPt.bcpIn = (vBcpIn[0], vBcpIn[1])
    bPt.bcpOut = (vBcpOut[0], vBcpOut[1])
    bPt.round()
    bPt.glyph.changed()
            


def getScreenInfo():
    # Collect screen info into a dictinary
    screenInfo = []
    mainScreenDescription = NSScreen.mainScreen().deviceDescription()
    for screen in NSScreen.screens():
        # Screen info
        thisScreenDescription = screen.deviceDescription()
        frame = screen.frame()
        origin = (frame.origin.x, frame.origin.y)
        size = (frame.size.width, frame.size.height)
        # Find the orientation
        h = 1 if origin[0]>0 else -1 if origin[0]<0 else 0
        v = 1 if origin[1]>0 else -1 if origin[1]<0 else 0
        orientations = [
            (-1,1), (0,1), (1,1), 
            (-1,0), (0,0), (1,0),
            (-1,-1), (0,-1), (1,-1)]
        orientationSymbols = ["↖️", "⬆️", "↗️", "⬅️", "⏺", "➡️", "↙️", "⬇️", "↘️"]
        o = orientationSymbols[orientations.index((h,v))]
        # Screen name and info
        thisScreenInfo = dict(name=None, origin=origin, size=size, isMain=False, orientation=o)
        if thisScreenDescription["NSScreenNumber"] == mainScreenDescription["NSScreenNumber"]:
            thisScreenInfo["name"] = "Main screen (%s × %s)" % (int(size[0]), int(size[1]))
            thisScreenInfo["isMain"] = True
        else: thisScreenInfo["name"] = "Other screen (%s × %s)" % (int(size[0]), int(size[1]))
        screenInfo.append(thisScreenInfo)
        
    return screenInfo

    


class PreviewWindow(object):
    
    def __init__(self):
        
        self.screenInfo = getScreenInfo()
        self.screenNames = []
        for screen in self.screenInfo:
            for location in ["↖︎","↗︎"]:
                self.screenNames += ["%s %s" % (location, screen["name"])]
        self.dsPath = None
        self.ds = None
        
        self.sourceFonts = {}
        
        step = 10
        
        self.w = vanilla.Window((660, 600), "Rotated DesignSpace Preview", minSize=(320, 500), autosaveName="Rotated DesignSpace Preview")
        
        self.w.openButton = vanilla.SquareButton((10, step, 150, 25), "Open Designspace", sizeStyle="small", callback=self.openDesignSpace)
        self.w.reloadButton = vanilla.SquareButton((10, step+35, 150, 25), "Update/Reload Fonts", sizeStyle="small", callback=self.reloadDesignSpace)
        #self.w.saveButton = vanilla.SquareButton((10, step+70, 40, 25), "Save", sizeStyle="small", callback=self.saveSources)
        self.w.screenChoice = vanilla.PopUpButton((10, step+65, 150, 25), self.screenNames, sizeStyle="small", callback=self.positionSourceWindows)
        
        self.w.vr1 = vanilla.VerticalLine((170, 10, 1, 100))
        
        self.w.glyphNameTitle = vanilla.TextBox((190, step+5, 100, 25), "Glyph name:")
        self.w.glyphName = vanilla.EditText((190, step+35, 100, 25), "", callback=self.glyphChanged)
        self.w.fillBox = vanilla.CheckBox((190, step+65, 100, 25), "Fill Preview", callback=self.settingsChanged)
        
        self.w.vr2 = vanilla.VerticalLine((310, 10, 1, 100))
        
        
        mid = 330
        
        self.w.selectedPointTitle = vanilla.TextBox((mid, step+5, 100, 25), "Selected BCP:")
        
        self.w.setRatioButton = vanilla.SquareButton((mid, step+35, 175, 25), "Match “default” master ratio...", sizeStyle="small", callback=self.setPointRatio)
        self.w.setRatioButton.id = "ratio"
        self.w.setRatioButton2 = vanilla.SquareButton((mid+174, step+35, 135, 25), "...move off-curves only", sizeStyle="small", callback=self.setPointRatio)
        self.w.setRatioButton2.id = "ratioLeaveAnchor"
        mid = 439
        self.w.magTitle = vanilla.TextBox((mid-100, step+70, 100, 25), "Scale off-curves:", sizeStyle="small")
        self.w.magButton0 = vanilla.SquareButton((mid, step+64, 51, 25), "-20", sizeStyle="small", callback=self.pointMagCallback)
        self.w.magButton0.value = 0.8
        self.w.magButton1 = vanilla.SquareButton((mid+50, step+64, 51, 25), "-5", sizeStyle="small", callback=self.pointMagCallback)
        self.w.magButton1.value = 0.95
        self.w.magButton2 = vanilla.SquareButton((mid+100, step+64, 51, 25), "+5", sizeStyle="small", callback=self.pointMagCallback)
        self.w.magButton2.value = 1.05
        self.w.magButton3 = vanilla.SquareButton((mid+150, step+64, 50, 25), "+20", sizeStyle="small", callback=self.pointMagCallback)
        self.w.magButton3.value = 1.2
        #self.w.closeButton = vanilla.SquareButton((550, step+35, 40, 25), "Close", sizeStyle="small", callback=self.closeSourceWindows)
        
        self.w.hr1 = vanilla.HorizontalLine((10, 110, -10, 1))
        
        step += 110
        
        # Sliders
        for tag in ["HROT", "VROT"]:
            posSize = (10, step+5, 50, 25)
            control = vanilla.TextBox(posSize, tag, sizeStyle="small")
            setattr(self.w, "label_%s"%tag, control)
            posSize = (50, step, 60, 25)
            control = vanilla.EditText(posSize, 0, callback=self.valueChangedCallback)
            control.id = tag
            setattr(self.w, "value_%s"%tag, control)
            posSize = (120, step, -10, 25)
            control = vanilla.Slider(posSize, callback=self.sliderChangedCallback, tickMarkCount=1)
            control.id = tag
            # axis min, max, default
            control.setMinValue(-45)
            control.setMaxValue(45)
            control.set(0)
            setattr(self.w, "slider_%s"%tag, control)
            step += 30
        
        self.w.glyphPreview = GlyphView((10, step, -10, -10))
        
        #self.w.bind("close", self.windowClosed)
        self.settingsChanged()
        self.w.open()
    
    def openDesignSpace(self, sender, path=None):
        if path == None:
            path = GetFile()
        if not path == None:
            self.dsPath = path
            self.ds = DesignSpaceProcessor(useVarlib=True)
            self.ds.read(path)
            self.ds.loadFonts()
            # Open new font objects
            self.sourceFonts = {}
            for sourceName in self.ds.fonts:
                df = self.ds.fonts[sourceName]
                f = OpenFont(df.path, showInterface=True)
                self.sourceFonts[sourceName] = f
            # Finish setup
            self.positionSourceWindows()
            self.updatePreview()

    def positionSourceWindows(self, sender=None):
        # Find screen and location based on the popup choice
        choice = self.w.screenChoice.get()
        screenIdx = int(choice/2)
        locationIdx = choice % 2
        # Windows are (400x300)
        winSize = (400, 350)
        menubarSize = 66
        # 9 masters are 3x3, 16 masters are 4x4 
        if len(self.sourceFonts.keys()) == 9:
            totalWidth = winSize[0] * 3
            positionNames = [
                ["HROTn_VROTn", "HROTd_VROTn", "HROTx_VROTn"],
                ["HROTn_VROTd", "HROTd_VROTd", "HROTx_VROTd"],
                ["HROTn_VROTx", "HROTd_VROTx", "HROTx_VROTx"]]
        else:
            totalWidth = winSize[0] * 4
            positionNames = [
                ["HROTn_VROTn", "HROTd_VROTn", "HROTdd_VROTn", "HROTx_VROTn"],
                ["HROTn_VROTdd","HROTd_VROTdd","HROTdd_VROTdd","HROTx_VROTdd"],
                ["HROTn_VROTd", "HROTd_VROTd", "HROTdd_VROTd", "HROTx_VROTd"],
                ["HROTn_VROTx", "HROTd_VROTx", "HROTdd_VROTx", "HROTx_VROTx"]]
        # Find the starting offset based on screen choice and position
        screen = self.screenInfo[screenIdx]
        origin = list(screen["origin"])
        if locationIdx == 1: # Shift the offset to start from the top right
            origin[0] += screen["size"][0] - totalWidth
        # Reposition the windows
        for w in AllFontWindows():
            for vIdx in range(len(positionNames)):
                for hIdx in range(len(positionNames[vIdx])):
                    fileName = positionNames[vIdx][hIdx]
                    if w.document.font.path:
                        if "%s.ufo" % fileName in w.document.font.path:
                            winPosSize = (
                                origin[0] + hIdx*winSize[0],
                                origin[1] + vIdx*winSize[1] + menubarSize, 
                                winSize[0] - 2, winSize[1] - menubarSize - 2)
                            w.window().setPosSize(winPosSize)
    
    def saveSources(self, sender=None):
        # Find the font objects and save them, for all open sources
        # 9 masters are 3x3, 16 masters are 4x4 
        if len(self.sourceFonts.keys()) == 9:
            positionNames = [
                ["HROTn_VROTn", "HROTd_VROTn", "HROTx_VROTn"],
                ["HROTn_VROTd", "HROTd_VROTd", "HROTx_VROTd"],
                ["HROTn_VROTx", "HROTd_VROTx", "HROTx_VROTx"]]
        else:
            positionNames = [
                ["HROTn_VROTn", "HROTd_VROTn", "HROTdd_VROTn", "HROTx_VROTn"],
                ["HROTn_VROTdd","HROTd_VROTdd","HROTdd_VROTdd","HROTx_VROTdd"],
                ["HROTn_VROTd", "HROTd_VROTd", "HROTdd_VROTd", "HROTx_VROTd"],
                ["HROTn_VROTx", "HROTd_VROTx", "HROTdd_VROTx", "HROTx_VROTx"]]
        for w in AllFontWindows():
            for vIdx in range(len(positionNames)):
                for hIdx in range(len(positionNames[vIdx])):
                    fileName = positionNames[vIdx][hIdx]
                    if w.document.font.path:
                        if "%s.ufo" % fileName in w.document.font.path:
                            w.document.font.save()
        
        
    def closeSourceWindows(self, sender=None):
        # 9 masters are 3x3, 16 masters are 4x4 
        if len(self.sourceFonts.keys()) == 9:
            positionNames = [
                ["HROTn_VROTn", "HROTd_VROTn", "HROTx_VROTn"],
                ["HROTn_VROTd", "HROTd_VROTd", "HROTx_VROTd"],
                ["HROTn_VROTx", "HROTd_VROTx", "HROTx_VROTx"]]
        else:
            positionNames = [
                ["HROTn_VROTn", "HROTd_VROTn", "HROTdd_VROTn", "HROTx_VROTn"],
                ["HROTn_VROTdd","HROTd_VROTdd","HROTdd_VROTdd","HROTx_VROTdd"],
                ["HROTn_VROTd", "HROTd_VROTd", "HROTdd_VROTd", "HROTx_VROTd"],
                ["HROTn_VROTx", "HROTd_VROTx", "HROTdd_VROTx", "HROTx_VROTx"]]
        docs = []
        for w in AllFontWindows():
            for vIdx in range(len(positionNames)):
                for hIdx in range(len(positionNames[vIdx])):
                    fileName = positionNames[vIdx][hIdx]
                    if w.document.font.path:
                        if "%s.ufo" % fileName in w.document.font.path:
                            docs.append(w.document)
        for doc in docs:
            doc.close()


    def reloadDesignSpace(self, sender):
        self.openDesignSpace(None, path=self.dsPath)
        # if self.ds:
        #     self.ds.loadFonts(reload=True)
        #     self.positionSourceWindows()
        #     self.updatePreview()
    
    def glyphChanged(self, sender):
        self.updatePreview(None)
    
    def settingsChanged(self, sender=None):
        doFill = self.w.fillBox.get()
        view = self.w.glyphPreview._glyphView
        view.setShowStroke_(not doFill)
        view.setShowFill_(True)
        view.setShowMetrics_(not doFill)
        view.setShowMetricsTitles_(False)
        view.setShowOnCurvePoints_(not doFill)
        view.setShowOffCurvePoints_(not doFill)
        view.setShowPointCoordinates_(False)
        view.setShowAnchors_(False)
    
    def valueChangedCallback(self, sender):
        sliderControlName = "slider_%s" % sender.id
        sliderControl = getattr(self.w, sliderControlName)
        sliderControl.set(int(sender.get()))
        self.updatePreview(None)
    
    def sliderChangedCallback(self, sender):
        valueControlName = "value_%s" % sender.id
        valueControl = getattr(self.w, valueControlName)
        valueControl.set(sender.get())
        self.updatePreview(None)

    def updatePreview(self, sender=None):
        glyphName = self.w.glyphName.get()
        if glyphName == "":
            cg = CurrentGlyph()
            if not cg == None:
                glyphName = CurrentGlyph().name
        if self.ds:
            location = {}
            for tag in ["HROT", "VROT"]:
                if tag == "HROT": axisName = "Horizontal Rotation"
                if tag == "VROT": axisName = "Vertical Rotation"
                control = getattr(self.w, "slider_%s"%tag)
                location[axisName] = control.get()
            # Make new instance
            i = self.ds.newInstanceDescriptor()
            i.location = location
            f = self.ds.makeInstance(i, doRules=False, glyphNames=[glyphName])
            if glyphName in f:
                g = f[glyphName]
            else: g = None
            # Update
            self.w.glyphPreview.set(g)
    
    
    def setPointRatio(self, sender=None):
        if self.ds:
            cg = CurrentGlyph()
            if not cg == None:
                cf = cg.font
                nf = self.ds.getNeutralFont()
                if cg.name in nf.keys():
                    ng = RGlyph(nf[cg.name])
                    cg.prepareUndo("Shift BCPs")
                    for cIdx, c in enumerate(cg.contours):
                        for ptIdx, bPt in enumerate(c.bPoints):
                            if bPt.selected:
                                meas = measureBCPs(ng.contours[cIdx].bPoints[ptIdx])
                                if sender.id == "ratioLeaveAnchor":
                                    moveAnchor = False
                                else: moveAnchor = True
                                shiftBPoint(bPt, targetMeasurements=meas, roundPoints=True, moveAnchor=moveAnchor)
                    cg.changed()
                    cg.performUndo()
    
    
    def pointMagCallback(self, sender):
        value = sender.value
        if self.ds:
            cg = CurrentGlyph()
            cg.prepareUndo("Move handles")
            if not cg == None:
               for cIdx, c in enumerate(cg.contours):
                    for ptIdx, bPt in enumerate(c.bPoints):
                        if bPt.selected:
                            scaleMagnitude(bPt, value)
            cg.performUndo()
    
    
PreviewWindow()