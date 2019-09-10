from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Warp/Masters/Tilt-Warp_D.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Warp/Rotated Shadow", 
    glyphNames=[n for n in "ADEGHINORSUaehilnopst"]+["period"],
    compositionType="rotate and shadow", 
    outlineAmount=0, 
    doForceSmooth=False,
    doMakeSubSources=False,
    familyName="Tilt Warp Shadow",
    styleName="Regular")
    