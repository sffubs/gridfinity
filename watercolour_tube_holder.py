import math

import cadquery as cq
import gridfinity

block_x = 3
block_y = 1
block_height = 6

width = 22
length= 15
taper = 2.5
depth = (block_height - 1) * 7 + 6 - 1
#taper_pad = depth * math.sin((taper / 180) * math.pi)
taper_pad = 0

spacing = 1.8

clearance= 0.15

block = (
    cq.Workplane("XY")
    .gridfinity_block(block_x, block_y, block_height))
    #.gridfinity_block_stack(block_x, block_y))

cutout = (
    block.faces(">Z")
    .placeSketch(
        cq.Sketch().rect(width, length))
    .extrude(-depth, combine=False))

block = (
    block
    .rarray(width + spacing,
            length + spacing, 5, 2)
    .eachpoint(lambda loc: cutout.val().moved(loc), combine="cut"))
#    .gridfinity_block_lip(block_x, block_y, screw_depth=3))

block = (block
    .gridfinity_block_stack(block_x, block_y)
    .gridfinity_block_lip(block_x, block_y, screw_depth=3))

#block = block.faces(">Z").chamfer(0.5)

del cutout

cq.exporters.export(block, "watercolour_tube_holder.step")
cq.exporters.export(block, "watercolour_tube_holder.stl")