from variableFontGenerator import BatchDesignSpaceProcessor

path = "/Users/clymer/Documents/Code/Git repos/GitHub/andyclymer/Tilt-Typeface/sources/Tilt Warp/Rotated Shadow/Tilt-Warp.designspace"
outputPath = path + ".ttf"
desingSpace = BatchDesignSpaceProcessor(path)
desingSpace.generateVariationFont(outputPath, autohint=False, releaseMode=True, fitToExtremes=False, report=None)

