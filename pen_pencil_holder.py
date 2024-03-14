import math

import cadquery as cq
import gridfinity

block_x = 1
block_y = 1
block_height = 6

diameter = 8
taper = 2.5
depth = (block_height - 1) * 7 + 6
taper_pad = depth * math.sin((taper / 180) * math.pi)

spacing = 0.4

clearance= 0.15

block = (
    cq.Workplane("XY")
    .gridfinity_block(block_x, block_y, block_height))

cutout = (
    block.faces(">Z")
    .placeSketch(
        cq.Sketch().circle(diameter / 2 + clearance + taper_pad))
    .extrude(-depth, combine=False, taper=taper))

block = (
    block
    .rarray(diameter + (clearance + taper_pad) * 2 + spacing, diameter + (clearance + taper_pad) * 2 + spacing, 3, 3)
    .eachpoint(lambda loc: cutout.val().moved(loc), combine="cut")
    .gridfinity_block_lip(block_x, block_y, screw_depth=3)
    .gridfinity_block_stack(block_x, block_y))

#block = block.faces(">Z").chamfer(0.5)

#del block

del cutout

cq.exporters.export(block, "pen_pencil_holder.step")
cq.exporters.export(block, "pen_pencil_holder.stl")