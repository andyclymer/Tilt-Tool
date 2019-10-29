from copy import deepcopy

# Close glyph window and run

f = CurrentFont()
g0 = f["n"]
g1 = f["h"]

libkey = "com.andyclymer.zPosition"
g1.lib[libkey] = deepcopy(g0.lib[libkey])
g1.changed()

print(g1.lib[libkey])
for c in g1.contours:
    for p in c.points:
        print(p.name)