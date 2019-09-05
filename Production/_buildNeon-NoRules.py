from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Neon/Masters/Tilt-Neon_D.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Neon/Rotated NoRules2", 
    glyphNames=["G"],#[n for n in "ADEGHINORSUaehilnopst"]+["period"],
    compositionType="rotate", 
    outlineAmount=50, 
    doForceSmooth=True,
    overlappingCurveFix=False,
    alwaysConnect=False,
    familyName="Tilt Neon",
    styleName="Regular")
    