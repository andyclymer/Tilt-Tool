import vanilla
from RotateMaster import buildDesignSpace
from defconAppKit.controls.fontInfoView import NumberEditText
import os
from mojo.UI import GetFolder


"""
RotateFontWindow
by Andy Clymer

An interface for some of the basic functions of the RotateMaster extension.

"""

    
def getFontName(f):
    
    familyName = None
    if f.info.openTypeNamePreferredFamilyName:
        familyName = f.info.openTypeNamePreferredFamilyName
    elif f.info.familyName:
        familyName = f.info.familyName
    
    styleName = None
    if f.info.openTypeNamePreferredSubfamilyName:
        styleName = f.info.openTypeNamePreferredSubfamilyName
    elif f.info.familyName:
        styleName = f.info.styleName
    
    if None in [familyName, styleName]:
        if f.path:
            fullName = os.path.split(f.path)[1]
        else:
            fullName = str(f)
    else: fullName = "%s %s" % (familyName, styleName)
    
    return fullName   
    
    
    
class RotateMasterWindow:
    
    def __init__(self):
        
        self.fontList = AllFonts()
        self.fontNames = [getFontName(f) for f in self.fontList]
        
        self.w = vanilla.Window((300, 200), "Build Rotated Masters")
        
        self.w.descriptionText = vanilla.TextBox((10, 10, -10, 50), "Rotate a UFO that has “3D Projection View” glyph depth data. Nine UFO masters and a designSpace file will be created.", sizeStyle="small")
        
        self.w.fontChoice = vanilla.PopUpButton((10, 60, -10, 25), self.fontNames)
        
        self.w.glyphChoice = vanilla.PopUpButton((10, 90, -10, 25), ["All glyphs", "Selected glyphs"])
        
        self.w.outlineBox = vanilla.CheckBox((10, 125, -10, 25), "Outline Paths", callback=self.outlineChanged)
        self.w.outlineAmount = NumberEditText((115, 125, 50, 25), "90", 
            allowFloat=False, allowNegative=False, minimum=1)
        self.w.outlineAmount.enable(False)
        self.w.unitsTitle = vanilla.TextBox((170, 129, -10, 25), "units")
        
        self.w.copyButton = vanilla.SquareButton((10, 165, -10, 25), "Rotate!", callback=self.rotateFont)
        self.w.open()

    def outlineChanged(self, sender):
        self.w.outlineAmount.enable(self.w.outlineBox.get())

    def rotateFont(self, sender):
        
        if len(self.fontList):
            
            master = self.fontList[self.w.fontChoice.get()]
            destPath = GetFolder()
            
            if destPath:
            
                if self.w.glyphChoice.get() == 1:
                    glyphNames = master.selection
                else: glyphNames = []
                
                if self.w.outlineBox.get():
                    outlineAmount = self.w.outlineAmount.get()
                    outlineAmount *= 0.5
                else: outlineAmount = 0
                
                buildDesignSpace(
                    masterFont=master,
                    destPath=destPath, 
                    glyphNames = glyphNames,
                    outlineAmount=outlineAmount)
    
RotateMasterWindow()

