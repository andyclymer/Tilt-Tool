from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Monument/Masters/Tilt-Monument.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/Bitbucket/tilt-typeface/sources/Tilt Monument/Rotated", 
    glyphNames=[n for n in "ADEFGHILNORSTUVhios"]+["period", "zero", "one", "one.alt", "three", "eight", "quoteleft", "quoteright"],
    compositionType="rotate", 
    outlineAmount=10, 
    doForceSmooth=True,
    doMakeSubSources=False,
    familyName="Tilt Monument",
    styleName="Regular")
    