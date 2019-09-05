from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Neon/Masters/Tilt-Neon_D.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Neon/Rotated Shadow", 
    glyphNames=[n for n in "ADEGHINORSUaehilnopst"]+["period"],
    compositionType="rotate and shadow", 
    outlineAmount=50, 
    doForceSmooth=True,
    overlappingCurveFix=True,
    familyName="Tilt Neon Shad",
    styleName="Regular")
    