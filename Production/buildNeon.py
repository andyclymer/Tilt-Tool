from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Neon/Masters/Tilt-Neon_D3.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Neon/Rotated", 
    glyphNames=[n for n in "ADEGHINORSUaehilnopst"]+["period"],
    compositionType="rotate", 
    outlineAmount=50, 
    doForceSmooth=True,
    doMakeSubSources=True,
    familyName="Tilt Neon",
    styleName="Regular")
    
    
