
# How it works (from a technical perspective)

First, keep in mind that this extension written quickly and built for the needs of the Tilt typeface. I'm sharing it so that some folks can continue development on Tilt and for others to learn from what I've done, but keep in mind that there are some hacks and workarounds in here!

## Editing and saving “z” point locations

Horizontal and vertical point locations in a glyph's drawings are stored as the same “x” and “y” values as you would find in any UFO, but the “z” values are kept in the glyph lib in a dictionary keyed to each point's name. 

*Note: I could/should have used point identifiers instead of names, but at a certain point I switched to get around a problem — when copying and pasting points within the same glyph the new point is assigned a new identifier and loses any connection to the old point, but the same name is carried forward with the copy. Then, the extension takes care of renaming the points with duplicate names and copying the “z” value to the new point.*

Only the “z” value is stored in the glyph lib, but while editing the tool keeps track of changes to “x”, “y” and “z” values so that it doesn't lose data when changing views. When you rotate to the side, the tool simply replaces all point “x” values with their “z” values, and likewise when switching to the bottom view the “y” value for each point is replaced with the “z” value.

Since this can be so destructive to a glyph drawing if another tool or script gets involved in editing the drawing, the tool is designed to switch back to the front view a little bit more often than it probably needs to (when a glyph window loses focus, when undoing, when saving).

## Previewing your 3D glyph

Very early on in the process I found the wonderful Zdog JavaScript library https://zzz.dog/ by Dave DeSandro, and used it to hack together a preview window. Clicking the “Reload glyph data” button in the 3D Projection Preview window scrapes the point locations out of the current glyph, writes a simple HTML file containing the glyph drawing in the Zdog API, and loads the HTML file in the preview window.

Keep in mind that the preview is a fully 3D representation of the glyph drawing, and doesn't have any of the limitations of a final variable font file.

## Turning it all into a font

For the Tilt typeface project I decided to limit myself to ±45° of rotation horizontally and vertically, to maintain some amount of legibility. However, in the end, a font needs to be made up of two-dimensional glyph drawings.

To give an easy answer to the solution, in an early test I found that interpolating between flat 2D snapshots of glyphs that were rotated to a few key angles worked pretty well when put back together into a variable font. Essentially, blending between flat drawings of a glyph that looks like it's pointing toward the corners of the designspace would give a very convincing impression of rotation. In the end, each glyph needs at least nine masters.

To rotate and flatten the glyph drawings, I was assisted by the pyeuclid library. Each point in the drawing was rotated around the center of the glyph, and only the “x” and “y” values were kept to flatten it out into two dimensions.

The extension has a “Build Rotated Masters” function that does the rotation and flattening and builds nine UFO masters from the single 3D source UFO that you started with. The interface simplifies some of the settings that I used for the Tilt typeface, but it also defaults itself to fit some of the decisions I made for Tilt — I chose to rotate the glyphs in an unusual way, removing the perspective and keeping the horizontal metrics flat (baseline, x-height, etc.). This way, a line of type will still set in a solid and more readable line, instead of each glyph rotating completely on its own.

### ...to be continued...
