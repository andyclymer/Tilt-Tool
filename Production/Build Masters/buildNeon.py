from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Neon/Masters/Tilt-Neon.ufo",
    destPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Neon/Rotated", 
    #glyphNames=[n for n in "HODRanos"] + ["period", "comma"],
    #glyphNames = ('B', 'G', 'I', 'K', 'L', 'N', 'P', 'T', 'V', 'Y', 'g', 'i', 'v', 'y', 'one', 'two', 'three', 'braceleft', 'braceright', 'at', 'space'),


    glyphNames = ["threesuperior"],
    compositionType="rotate", 
    outlineAmount=45, 
    doForceSmooth=True,
    doMakeSubSources=True,
    familyName="Tilt Neon",
    styleName="Regular")
    
    
