# 3D Projection View
by Andy Clymer

The 3D Projection View RoboFont extension was created for the Tilt typeface, to add 3D depth to a drawing and build a variable font designSpace that gives the appearance of being able to rotate glyph drawings.

The workflow for drawing in 3D is broken out into four different functions —

## Enable 3D Projection View Control

To get started, choose the “Enable 3D Projection View Control” menu item to add a widget to the top left corner of a RoboFont editing window. This new editing control gives you the ability to view your glyph drawing from the front, side and bottom. The glyph point positions are usually only recorded as “x” and “y” values for their horizontal and vertical position, but when viewing a glyph from the bottom or side you can also move points into a “z” position for depth.

After enabling the “3D Projection View Control” you will need to reopen a window to see the new control in a glyph window. Toggle the checkbox in the widget to turn the control on or off, and click the buttons to rotate your glyph view.

## 3D Projection Preview

Now that you're drawing in 3D, you can open a preview window with the “3D Projection Preview...” menu item. This preview takes your 3D point data and uses the Zdog JavaScript library to render a preview that you can click and drag to rotate. 

The preview won't update live as you edit a glyph drawing, click the “Reload glyph data” after editing to update the glyph preview. 

While this preview is a fully 3D object that you can rotate in any direction, please note the final font that you'll export from this extension will only have a limited range of rotation.

## Build Rotated Masters

After you're satisfied with your drawing, you can choose the “Build Rotated Masters...” menu item to flatten your 3D drawings out into a folder of UFO masters and a designSpace document. 

The glyphs are rotated +-45° into nine masters — one default master in the middle with no rotation, surrounded by eight masters that are rotated to the maximum values on the two “HROT” and “VROT” axes.

The masters should be compatible for interpolation, but run them all through your favorite glyph compatibility extension to fix problems.

A design decision was made for the Tilt font family that this step will not add any perspective to a glyph drawing as it’s roatated, to keep vertical metrics flat and horizontal strokes horizontal — the baseline and cap height will always be flat, so that you can still use the typeface to set text.

## Rotated DesignSpace Preview

Once you have a compatible set of UFOs and a designSpace document, you can preview the entire family and make changes to your drawings with the “Rotated DesignSpace Preview...” menu item.

Opening the designSpace document will open and position all nine UFOs on screen. Choose a glyph by name, and preview how the points move along the “HROT” and “VROT” axes. 

After editing a glyph, save the font and click “Update/Reload Fonts” button to refresh the preview in the window.

A few buttons are provided that perform actions on the “Selected BCP” — keeping off-curve point ratios the same between masters is very important to avoid kinks in an interpolation, the buttons will try to match the offCurve ratios to that of the “default” middle master which can be a helpful starting point when editing. Once the ratios are set, there are buttons to extend and retract offCurves at set percentages, which can also help with editing.

## Build a Variable Font

You're already previewing a variable font designSpace that's compatible for interpolation, the only remaining step is building it into a font. Use the Batch extension to make your final build.
