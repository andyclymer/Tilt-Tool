from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Neon/Masters/Tilt-Neon.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Neon/Rotated", 
    #glyphNames=[n for n in "HODRanos"] + ["period", "comma"],
    #glyphNames=[n for n in ""],
    glyphNames=["Q"],
    #glyphNames = ('D', 'H', 'O', 'Q', 'R', 'U', 'a', 'e', 'l', 'm', 'n', 'o', 'p', 's', 'v', 'zero', 'three', 'six', 'eight', 'period', 'comma', 'braceleft', 'braceright', 'S', 'E', 'V', 'r', 't', 'one', 'question', 'c', 'C', 'A'),
    compositionType="rotate", 
    outlineAmount=45, 
    doForceSmooth=True,
    doMakeSubSources=True,
    familyName="Tilt Neon",
    styleName="Regular")
    
    
