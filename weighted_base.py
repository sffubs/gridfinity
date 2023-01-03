import math

import cadquery as cq

# This is my attempt at reproducing Zack Freedman's weighted baseplate.
# Not quote operation-for-operation, but kind of.
# I skipped the screw holes and weights because I don't need them.
# I should have used gridfinity.py instead really.

numX = 5
numY = 3

nestingDepth = 5
nestingClearance = 0.25
magnetThiccness = 2.4
magnetDiameter = 6.3
baseThickness = 5.2

def lip():
    profile = (cq.Sketch()
               .polygon([(-5, 5), (0, 5), (2.4, 5 - 2.4), (2.4, 0.8), (2.4 + 0.8, 0), (-5, 0), (-5, 5)])
    )

    path = (cq.Workplane("top")
            .moveTo(-21 + 4, 21)
            .hLine(42 - 8).tangentArcPoint((4, -4))
            .vLine(-42 + 8).tangentArcPoint((-4, -4))
            .hLine(-42 + 8).tangentArcPoint((-4, 4))
            .vLine(42 - 8).tangentArcPoint((4, 4)).close()
    )

    lip = cq.Workplane("left").center(-21 - nestingClearance, 0).placeSketch(profile).sweep(path)

    snip = cq.Workplane("top").rect(42, 42).extrude(5 - 0.6)

    lip = cq.Workplane("top").rect(42, 42).extrude(5).intersect(lip).intersect(snip)

    return lip

#screwholes = (cq.Workplane("top").center(-21 + 8, -21 + 8).circle(3/2)
#    .center(0, 0).mirrorX().mirrorY().extrude(3))
    
magnetHoles = (cq.Workplane("top")
    .center(-21 + 8, -21 + 8).circle(magnetDiameter/2)
    .center(21 - 8, 21 - 8).mirrorX().mirrorY()
    .extrude(-magnetThiccness))

base = (cq.Workplane("top").rect(42, 42).extrude(-baseThickness).cut(magnetHoles))

del magnetHoles

plate = lip().union(base)

del base

model = cq.Workplane("top")

for i in range(0, numX):
    for j in range(0, numY):
        model = model.union(plate.translate((42 * i, 0, 42 * j)))

trimProfile = cq.Workplane("top").center((42 * numX) / 2 - 21, (-42 * numY) / 2 + 21).placeSketch(
    cq.Sketch().rect(42 * numX, 42 * numY).vertices().fillet(4))

model = model.intersect(trimProfile.extrude(5).union(trimProfile.extrude(-baseThickness)))

del trimProfile

del plate

weight_large_x = 19.2
weight_large_y = 23.5
weight_clearance = 1
weight_depth = 4.4

weight_large = (model.faces("<Y")
                .workplane()
                .rect(weight_large_x + weight_clearance, weight_large_y + weight_clearance)
                .extrude(-weight_depth, combine=False)
                .rotate((0, 0, 0), (0, 1, 0), 45))

for i in range(0, numX):
    for j in range(0, numY):
        model = model.cut(weight_large.translate((42 * i, 0, 42 * j)))

del weight_large

cq.exporters.export(model, "weighted_base.step")
cq.exporters.export(model, "weighted_base.stl")