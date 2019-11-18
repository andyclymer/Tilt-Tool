from RotateMaster import buildDesignSpace

buildDesignSpace(
    masterPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Neon/Masters/Tilt-Neon.ufo", 
    destPath="/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Neon/Rotated", 
    #glyphNames=[n for n in "HODRanos"] + ["period", "comma"],
    #glyphNames = ('B', 'G', 'I', 'K', 'L', 'N', 'P', 'T', 'V', 'Y', 'g', 'i', 'v', 'y', 'one', 'two', 'three', 'braceleft', 'braceright', 'at', 'space'),

    # All of the placeholder glyphs
    glyphNames = ('four', 'five', 'seven', 'nine', 'colon', 'semicolon', 'periodcentered', 'ellipsis', 'exclam', 'exclamdown', 'question', 'questiondown', 'quotesingle', 'quotedbl', 'quoteleft', 'quoteright', 'quotesinglbase', 'quotedblleft', 'quotedblright', 'quotedblbase', 'guilsinglleft', 'guilsinglright', 'guillemetleft', 'guillemetright', 'parenleft', 'parenright', 'bracketleft', 'bracketright', 'slash', 'bar', 'brokenbar', 'backslash', 'fraction', 'divisionslash', 'bullet', 'hyphen', 'hyphensoft', 'endash', 'emdash', 'underscore', 'plus', 'minus', 'multiply', 'divide', 'plusminus', 'equal', 'less', 'greater', 'logicalnot', 'mu.math', 'asciicircum', 'asciitilde', 'degree', 'onesuperior', 'twosuperior', 'threesuperior', 'four.superior', 'onequarter', 'onehalf', 'threequarters', 'ordmasculine', 'ordfeminine', 'copyright', 'registered', 'numbersign', 'dollar', 'cent', 'sterling', 'yen', 'Euro', 'currency', 'ampersand', 'section', 'paragraph', 'dieresis', 'grave', 'macron', 'acute', 'cedilla', 'circumflex', 'ring', 'tilde', 'Agrave', 'Aacute', 'Acircumflex', 'Atilde', 'Adieresis', 'Aring', 'AE', 'Ccedilla', 'Egrave', 'Eacute', 'Ecircumflex', 'Edieresis', 'Igrave', 'Iacute', 'Icircumflex', 'Idieresis', 'Eth', 'Ntilde', 'Ograve', 'Oacute', 'Ocircumflex', 'Otilde', 'Odieresis', 'Oslash', 'OE', 'Ugrave', 'Uacute', 'Ucircumflex', 'Udieresis', 'Yacute', 'Ydieresis', 'Thorn', 'germandbls', 'agrave', 'aacute', 'acircumflex', 'atilde', 'adieresis', 'aring', 'ae', 'ccedilla', 'egrave', 'eacute', 'ecircumflex', 'edieresis', 'igrave', 'iacute', 'icircumflex', 'idieresis', 'dotlessi', 'eth', 'ntilde', 'ograve', 'oacute', 'ocircumflex', 'otilde', 'odieresis', 'oslash', 'oe', 'ugrave', 'uacute', 'ucircumflex', 'udieresis', 'yacute', 'thorn', 'ydieresis', 'space', 'a.alt', 'dieresis.cap', 'grave.cap', 'macron.cap', 'acute.cap', 'circumflex.cap', 'ring.cap', 'tilde.cap'),

    compositionType="rotate", 
    outlineAmount=45, 
    doForceSmooth=True,
    doMakeSubSources=True,
    familyName="Tilt Neon",
    styleName="Regular")
    
    
