from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Monument/Masters/Tilt-Monument_D.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Monument/Rotated Shadow", 
    glyphNames=[n for n in "ADEFGHILNORSTUVhios"]+["period", "zero", "one", "one.alt", "three", "eight", "quoteleft", "quoteright"],
    compositionType="rotate and shadow", 
    outlineAmount=10, 
    shadowLengthFactor=1.5,
    doForceSmooth=True,
    doMakeSubSources=False,
    familyName="Tilt M Shad",
    styleName="Regular")
    