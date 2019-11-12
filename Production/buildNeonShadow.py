from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Neon/Masters/Tilt-Neon.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Neon/Rotated Shadow", 
    glyphNames=["o", "a", "ring", "aring"],
    compositionType="rotate and shadow", 
    outlineAmount=45, 
    doForceSmooth=True,
    doMakeSubSources=True,
    familyName="Tilt Neon Shadow",
    styleName="Regular")
     