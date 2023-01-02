import math

import cadquery as cq
import gridfinity

block_x = 2
block_y = 1
block_height = 3

taper = 5
bottle_width_x = 58.00/2
bottle_width_y = 36.40/2
bottle_sep = 4
bottle_angle = 0
depth = (block_height - 1) * 7 + 5
clearance= 0.15
taper_pad = depth * math.sin((taper / 180) * math.pi)

block = (
    cq.Workplane("XY")
    .gridfinity_block(block_x, block_y, block_height))

cutout = (
    block.faces(">Z")
    .placeSketch(
        cq.Sketch()
        .ellipse(
            bottle_width_x + taper_pad + clearance,
            bottle_width_y + taper_pad + clearance,
            angle=bottle_angle))
    .extrude(-depth, combine=False, taper=taper))

block = (
    block
    .cut(cutout)
    .gridfinity_block_lip(block_x, block_y, screw_depth=3))


block = block.faces(">Z").chamfer(0.3)

del cutout

cq.exporters.export(block, "windsor_and_newton_masking_fluid_holder.step")
cq.exporters.export(block, "windsor_and_newton_masking_fluid_holder.stl")
