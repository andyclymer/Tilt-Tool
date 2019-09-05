from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Warp/Masters/Tilt-Warp_D.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Warp/Rotated", 
    glyphNames=[n for n in "ADEGHINORSUaehilnopst"]+["period"],
    compositionType="rotate", 
    outlineAmount=0, 
    doForceSmooth=False,
    overlappingCurveFix=False,
    familyName="Tilt Warp",
    styleName="Regular")
    