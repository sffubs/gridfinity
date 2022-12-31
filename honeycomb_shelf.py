import math

import cadquery as cq

# This is my attempt at reproducing Zack Freedman's weighted baseplate.
# Not quote operation-for-operation, but kind of.
# I skipped the screw holes and weights because I don't need them.
# I should have used gridfinity.py instead really.

numX = 3
numY = 2

nestingDepth = 5
nestingClearance = 0.25
magnetThiccness = 2.4
magnetDiameter = 6.3
baseThickness = 5

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

model = model.intersect(trimProfile.extrude(5).union(trimProfile.extrude(-5)))

del trimProfile

del plate

plugBack = 15.053
plugFront = 15.534
plugDepth = 8
plugChamfer = 0.5

skPlugBack = cq.Sketch().regularPolygon(plugBack/2, 6, 30)
skPlugFront = cq.Sketch().regularPolygon(plugFront/2, 6, 30)

diameterPlugFront = (plugFront) * math.cos(math.pi/6)
areaPlugFront = math.sqrt(3) * (diameterPlugFront ** 2) / 2

skPlugConnection = cq.Sketch().rect(areaPlugFront / (baseThickness + 5 - 0.6), baseThickness + 5 - 0.6)

connectionDepth = 5

plug = (cq.Workplane("front")
    .placeSketch(
        skPlugBack.moved(cq.Location(cq.Vector(0, -(plugFront - plugBack) / 2, 0))),
        skPlugFront.moved(cq.Location(cq.Vector(0, 0, plugDepth)))).loft()
    .faces("<Z").chamfer(plugChamfer)
    #.faces().workplane(offset=plugDepth)
    #.placeSketch(cq.Sketch().regularPolygon(plugBack/2, 6, 30).edges()).close()
    #.loft(combine=True)
    #.extrude(plugDepth)
    .translate((0, (diameterPlugFront / 2) - baseThickness, -21 - plugDepth - connectionDepth))
    )

plugConnection = (cq.Workplane("front")
    .placeSketch(
        skPlugFront.moved(cq.Location(cq.Vector(0, 0, plugDepth))),
        skPlugConnection.moved(cq.Location(cq.Vector(0, (baseThickness + 5 - 0.6) / 2 - (diameterPlugFront / 2), plugDepth + connectionDepth)))).loft()
    #.faces("<Z").chamfer(plugChamfer)
    #.faces().workplane(offset=plugDepth)
    #.placeSketch(cq.Sketch().regularPolygon(plugBack/2, 6, 30).edges()).close()
    #.loft(combine=True)
    #.extrude(plugDepth)
    .translate((0, (diameterPlugFront / 2) - baseThickness, -21 - plugDepth - connectionDepth))
    )

plug = plug.union(plugConnection)
del plugConnection

hexSpacing = 40.88

numPlugSpaces = (math.floor((42 * numX) / hexSpacing) - 1)
gap = numPlugSpaces * hexSpacing

plugs = plug

for i in range(1, numPlugSpaces + 1):
    if (i < numPlugSpaces / 2 and i % 2 == 0) or (i >= numPlugSpaces/2 and i % 2 == numPlugSpaces % 2):
        plug2 = plug.translate((i * hexSpacing, 0, 0))
        plugs = plugs.union(plug2)
        del plug2

del plug

plugs = plugs.translate((-21 + (numX * 42) / 2 - gap / 2, 0, 0))

model = model.union(plugs)

del plugs

cq.exporters.export(model, "honeycomb_shelf.step")
cq.exporters.export(model, "honeycomb_shelf.stl")