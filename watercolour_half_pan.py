import math

import cadquery as cq
import gridfinity

block_x = 1
block_y = 1
block_height = 2

base_x = 14.2
base_y = 17.4
top_x = 15.6
top_y = 18.8
height = 8.6

pan_spacing = 1.2

extra_depth = 3

clearance= 0.15

block = (
    cq.Workplane("XY")
    .gridfinity_block(block_x, block_y, block_height))
    #.gridfinity_block_stack(block_x, block_y))

halfpan_cutout = (
    block.faces(">Z")
    .placeSketch(
        cq.Sketch().rect(top_x + clearance * 2, top_y + clearance * 2),
        cq.Sketch().rect(base_x + clearance * 2, base_y + clearance * 2)
        .moved(cq.Location(cq.Vector(0, 0, -height)))
        )
    .loft(combine=False)
    .faces(">Z")
    .rect(top_x + clearance * 2, top_y + clearance * 2).extrude(10)
    #.translate((0, 0, -(gridfinity.stacking_mating_depth + extra_depth)))
    .translate((0, 0, -extra_depth))
    )

block = (
    block
    .gridfinity_block_stack(block_x, block_y)
    .faces("<Z")
    .rarray(top_x + pan_spacing, top_y + pan_spacing, 2, 2)
    .eachpoint(lambda loc: halfpan_cutout.val().moved(loc), combine="cut")
    .gridfinity_block_lip(block_x, block_y, screw_depth=3))


#block = block.faces(">Z").chamfer(0.5)

del halfpan_cutout

cq.exporters.export(block, "watercolour_half_pan.step")
cq.exporters.export(block, "watercolour_half_pan.stl")
