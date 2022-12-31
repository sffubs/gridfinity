import math

import cadquery as cq
import gridfinity

block_x = 1
block_y = 1
block_height = 2

taper = 5
bottle_width_x = 36.3
bottle_width_y = 36.3
depth = (block_height - 1) * 7 + 7
clearance= 0.15
taper_pad = depth * math.sin((taper / 180) * math.pi)

block = (
    cq.Workplane("XY")
    .gridfinity_block(block_x, block_y, block_height))

cutout = (
    block.faces(">Z")
    .placeSketch(
        cq.Sketch()
        .rect(
            bottle_width_x + 2*(taper_pad + clearance),
            bottle_width_y + 2*(taper_pad + clearance)))
    .extrude(-depth, combine=False, taper=taper)
    .edges("not (<Z or >Z)")
    .fillet(3))

block = (
    block
    .cut(cutout)
    .gridfinity_block_lip(block_x, block_y, screw_depth=3))

block = block.faces(">Z").chamfer(0.5)

del cutout

cq.exporters.export(block, "windsor_and_newton_ink_holder.step")
cq.exporters.export(block, "windsor_and_newton_ink_holder.stl")
