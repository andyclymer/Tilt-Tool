import os
import glob

from RotateMaster import buildDesignSpace

# glyphNames = ['space', 'dollar', 'degree', 'C', 'parenleft', 'braceright', 'plus', 'equal', 'hyphen', 'guilsinglright', 'less', 'exclamdown', 'cedilla', 'six', 'backslash', 'U', 'asciicircum', 'X', 'Euro', 'logicalnot', 'divisionslash', 'divide', 'nine', 'T', 'asterisk', 'E', 'tilde', 'five', 'asciitilde', 'F', 'bullet', 'macron', 'at', 'OE', 'ampersand', 'Y', 'acute', 'brokenbar', 'onesuperior', 'minus', 'quotedbl', 'quotesingle', 'fraction', 'seven', 'endash', 'A', 'ring', 'mu.math', 'Thorn', 'R', 'emdash', 'quoteleft', 'grave', 'circumflex', 'paragraph', 'B', 'comma', 'threesuperior', 'guillemetright', 'O', 'Oslash', 'bracketleft', 'ordmasculine', 'one.alt', 'four.superior', 'ordfeminine', 'yen', 'N', 'G', 'plusminus', 'braceleft', 'numbersign', 'K', 'cent', 'guilsinglleft', 'P', 'two', 'eight', 'currency', 'multiply', 'period', 'M', 'dieresis', 'V', 'onequarter', 'slash', 'threequarters', 'parenright', 'Q', 'Ccedilla', 'registered', 'AE', 'exclam', 'question', 'sterling', 'guillemetleft', 'four', 'percent', 'onehalf', 'copyright', 'I', 'section', 'twosuperior', 'L', 'underscore', 'H', 'Q.alt', 'J', 'Eth', 'W', 'greater', 'three', 'bar', 'questiondown', 'one', 'zero', 'Z', 'S', 'D', 'bracketright']
glyphNames = []

masterPath = "/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Monument/Masters/Tilt-Monument-Separated.ufo"
destPath = "/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Monument/"
destInline = os.path.join(destPath, "Rotated 01 Inline 16 Shifted")
destOutline = os.path.join(destPath, "Rotated 02 Outline 16 Shifted")
destCombined = os.path.join(destPath, "Rotated 03 Combined 16 Shifted")

doInline = True
doOutline = True
doCombine = True

if doInline:
    buildDesignSpace(
        masterPath=masterPath, 
        destPath=destInline, 
        glyphNames=glyphNames,
        compositionType="rotate", 
        outlineAmount=8, 
        doForceSmooth=True,
        doMakeSubSources=False,
        alwaysConnect=True, # Temporary, force connections to have extra points for compatibility
        cap="Butt",
        connection="Round",
        familyName="Tilt Monument",
        styleName="Regular",
        zOffset=60)
     
if doOutline:
    buildDesignSpace(
        masterPath=masterPath, 
        destPath=destOutline, 
        glyphNames=glyphNames,
        compositionType="rotate", 
        outlineAmount=8, 
        doForceSmooth=True,
        doMakeSubSources=False,
        alwaysConnect=False,
        cap="Roundsimple",
        connection="Round",
        layerName="outline",
        familyName="Tilt Monument",
        styleName="Regular",
        zOffset=60)


if doCombine:
    if not os.path.exists(destCombined):
        os.makedirs(destCombined)
    for outlinePath in glob.glob(os.path.join(destOutline, "*.ufo")):
        fileName = os.path.split(outlinePath)[1]
        inlinePath = os.path.join(destInline, fileName)
        destPath = os.path.join(destCombined, fileName)
        fOutline = OpenFont(outlinePath, showInterface=False)
        fInline = OpenFont(inlinePath, showInterface=False)
        for gn in fOutline.keys():
            gOut = fOutline[gn]
            gIn = fInline[gn]
            for c in gOut.contours:
                gIn.appendContour(c)
        fInline.save(destPath)
        