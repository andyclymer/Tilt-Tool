# Tilt-Tool

This repo contains RoboFont extensions to draw fonts that have the appearance of being 3D, created for the Tilt typeface design. The tools are composed of two related extensions:

- **3D Projection View** gives the designer the ability to add `z` coordinate values to points, view the glyph drawing from the front, side and bottom, and preview the 3D drawing in a separate window, and,
- **Rotate Master** takes the 3D data and builds out the required 9 or 16 masters and the designSpace document to build a variable font which can be rotated along horizontal and vertical axis.

The code is currently being reorganized and cleaned up for release. I'll keep my to-do list here:

- [ ] This repo should be reoragnized as a more universal tool for interacting with 3D point data, any scripts or utilities that were made for the Tilt typeface should be moved to the `Tilt-Typeface` repo
- [ ] `z` coordinate data is still saved in the lib under the `com.andyclymer.zPosition` key, change this to a `public` named key (and update the font data in the `Tilt-Typeface` repo)
- [ ] Point IDs are still being set to the point name, which was a technique to get around a temporary undo bug in RoboFont, but I should be able to switch back to using the standard identifiers.
- [ ] There are a few very small dependencies to my own `ac` library and to the `roboHUD` extension which I should go ahead and clear up
- [ ] Turn the `Rotate Master` build script into a simple tool with an interface, to make the separate build scripts optional (but keep the Python interface)
- [ ] Documentation needs to be written
