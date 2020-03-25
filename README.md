# 3D Projection View
by Andy Clymer

The *3D Projection View* RoboFont Extension enables you to add depth to a drawing by moving points along the "z" axis instead of only "x" and "y", can build a variable font designSpace that gives the appearance of being able to rotate glyph drawings.

![Interface](/images/ui-animation.gif?raw=true)

The workflow for drawing in 3D is broken out into four different functions —

### Enable 3D Projection View Control

This menu item add a control widget to the top left corner of a RoboFont glyph editing window, giving you the ability to view your glyph drawing from the ● front, ◑ side and ◓ bottom. Reopen any glyph windows to see the new control widget.

![UI Control](/images/ui-control.png?raw=true)

You’re probably accustomed to drawing in two dimensions, where each point location can be described as a having a horizontal value along the glyph’s width (which can be said to be on the “x” axis in a grid) and a vertical value along its height (on the “y” axis). To add depth to a drawing we need a way to move the points closer or further away (along the “z” axis).

When you rotate the view to the ◑ side, you’ll notice that all of the points in the glyph drawing flatten out  on the left side bearing. What's really happening is the horizontal location for each point, or its “x” value, is being swapped with its depth location, or “z” value.

It will feel strange at first to edit the depth data this way, but thankfully whichever points you select in the ● front view remain selected when switching to the ◑ side or ◓ bottom. I usually start by making a selection while viewing a glyph from the front, switch to either the side or bottom and nudge the points with the arrow keys to move them into place.

### 3D Projection Preview

Opens an interactive preview window to quickly view your 3D drawing data using the Zdog JavaScript drawing library. Click and drag the preview to rotate the drawing. Note that this preview is a fully 3D object that doesn't have the limitations of the final variable font file, but it's a helpful way to preview your drawing while you work.

### Build Rotated Masters

To make a variable font out of your 3D glyph, the points need to be flattened out into a handful of UFO masters that will then interpolate to give the appearance of rotation. This menu item will build a folder of UFOs along with a related designSpace document that can be used to build a variable font.

The glyphs are rotated +-45° and are saved into nine UFO masters — one default master in the middle with no rotation, surrounded by eight masters that are rotated to the maximum values on the two “HROT” and “VROT” axes.

The masters should be compatible for interpolation, but run them all through your favorite glyph compatibility extension to fix problems.

A design decision was made for the Tilt font family that this step will not add any perspective to a glyph drawing as it’s rotated. This keeps vertical metrics flat and horizontal strokes horizontal — the baseline and cap height will always be perfectly horizontal so that you can still use the typeface to set text while still keeping the illusion that glyphs are rotating.

### Rotated DesignSpace Preview

Once you have a compatible set of UFOs and a designSpace document, you can preview the entire family and make changes to your drawings with the “Rotated DesignSpace Preview...” menu item.

Opening the designSpace document will open and position all nine UFOs on screen. Choose a glyph by name, and preview how the points move along the “HROT” and “VROT” axes.

After editing a glyph, save the font and click “Update/Reload Fonts” button to refresh the preview in the window.

A few buttons are provided that perform actions on the “Selected BCP” — keeping off-curve point ratios the same between masters is very important to avoid kinks in an interpolation, the buttons will try to match the offCurve ratios to that of the “default” middle master which can be a helpful starting point when editing. Once the ratios are set, there are buttons to extend and retract offCurves at set percentages, which can also help with editing.

![Designspace](/images/designspace.png?raw=true)

### Build a Variable Font

You're already previewing a variable font designSpace that's compatible for interpolation, the only remaining step is building it into a font. Use the Batch extension to make your final build.

