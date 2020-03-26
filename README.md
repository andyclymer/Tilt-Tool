# 3D Projection View
by Andy Clymer

The *3D Projection View* RoboFont Extension enables you add depth to a drawing and build UFO sources for a variable font with the appearance of horizontal and vertical rotation.

The extension was built for the Tilt typeface family.

![Interface](/images/ui-animation.gif?raw=true)

The workflow for drawing in 3D is broken out into four different functions, with their own menu items —

### “Enable 3D Projection View Control”

This menu item adds a control widget to the top left corner of a RoboFont glyph editing window, giving you the ability to view your glyph drawing from the ● front, ◑ side and ◓ bottom. Reopen any currently open glyph windows to link the new control widget.

![UI Control](/images/ui-control.png?raw=true)

You’re probably accustomed to drawing in two dimensions, where each point location can be described as a having a horizontal value along the glyph’s width (which can be said to be on the “x” axis in a grid) and a vertical value along its height (on the “y” axis). To add depth to a drawing we need a way to move the points closer to or further away from the viewer (along the “z” axis).

When you rotate the view to the ◑ side, you’ll notice that all of the points in your drawing flatten out on the glyph’s left side bearing. What's really happening is the horizontal location for each point, or its “x” value, is being temporarily swapped with its depth location, or “z” value.

Then, you're free to move the point (left/right when viewing from the ◑ side, or up/down when viewing from the ◓ bottom) to change the depth position of the point. From the ● front view you won't see the changes in depth, since they're moving directly further away or closer to you without any perspective.

It will feel strange at first to edit the depth data this way, but thankfully whichever points you select in the ● front view remain selected when switching to the ◑ side or ◓ bottom. It can be helpful to start by making a selection while viewing a glyph from the front, switch to either the side or bottom and nudge the points with the arrow keys to move them into place.

### “3D Projection Preview”

The "3D Projection Preview" menu item opens an interactive 3D preview window using the Zdog JavaScript drawing library. Click and drag within the preview to rotate the glyph drawing.

Note that this preview is a fully 3D object that doesn't have the limitations of a variable font, but it's a helpful way to preview your drawing while you work.

This extension was built for the Tilt typeface, so the preview window has the ability to preview a solid glyph or one with a stroke applied to it, since drawing from an outlined skeleton was the basis for working on the Tilt Neon style.

### “Build Rotated Masters”

To make a variable font out of your 3D glyph, the point locations need to be flattened out into a handful of UFO masters that will then interpolate to give the appearance of rotation. The "Build Rotated Masters" function will build a folder of UFOs along with a related designSpace document that can be used to build a variable font.

The glyphs are rotated through the range of ±45° and are saved into nine UFO masters — one default master in the middle with no rotation (essentially, the front view), surrounded by eight masters that are rotated to the maximum values on the two “HROT” and “VROT” axes.

| | | |
| :---: | :---: | :---: |
| ↖︎ | ↑ | ↗︎ | 
| ← | • | → |
| ↙︎ | ↓ | ↘︎ |

A note about the file names: masters are built on the “HROT” and “VROT” axes at “d” ***d***efault, “n” mi***n***imum and ”x” ma***x***imum locations. I found these three letters easier to keep track of in the file names instead of the numeric values — “Source-HROTn_VROTx.ufo” is at the minimum HROT value (-45) and the maximum VROT value (+45)

The UFO masters built this way should be compatible for interpolation, but run them all through your favorite glyph compatibility extension to check and fix any problems that may have come up.

Once again, since this tool was built for the Tilt typeface family, some design decisions have been baked in to the process. This step of building “rotated” masters transforms the glyphs in a way that doesn’t add any perspective so that vertical metrics flat and horizontal strokes stay horizontal. This keeps the alignments to the baseline (and cap-height, x-height, etc.) perfectly flat so that you can still use the typeface to set text while still keeping the illusion that glyphs are rotating. Without this change in perspective, each glyph would have looked like they were rotating on their own, instead of part of a rotating word.

### “Rotated DesignSpace Preview”

Once you have a compatible set of UFOs and a designSpace document from the previous step, you can preview the entire family and make changes to your drawings with the “Rotated DesignSpace Preview...” menu item.

Opening the designSpace document will open and position all nine UFOs on screen. Choose a glyph by name, and preview how the points move along the “HROT” and “VROT” axes by moving their sliders.

After editing a glyph, save the font and click “Update/Reload Fonts” button to refresh the preview in the window.

A few buttons are provided that perform actions on the “Selected BCP” — keeping off-curve point ratios the same between masters is very important to avoid kinks in an interpolation, the buttons will try to match the offCurve ratios to that of the “default” middle master. Once the ratios are set, there are buttons to extend and retract offCurves at set percentages.

![Designspace](/images/designspace.png?raw=true)

### Then, build a Variable Font

You're already previewing a variable font designSpace that's compatible for interpolation, the only remaining step is building it into a font. Use the RoboFont “Batch” extension or your tool of choice to make your final build.


