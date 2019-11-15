from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Desktop/rotate test pattern/TestMaster.ufo", 
    destPath="/Users/clymer/Desktop/rotate test pattern/Rotated 2", 
    glyphNames=[n for n in "ABCD"],
    compositionType="rotate", 
    outlineAmount=45, 
    doForceSmooth=True,
    doMakeSubSources=True,
    familyName="Tilt Neon",
    styleName="Regular")
    
    
