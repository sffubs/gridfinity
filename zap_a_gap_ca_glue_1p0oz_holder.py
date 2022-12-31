import math

import cadquery as cq
import gridfinity

block_x = 1
block_y = 1
block_height = 3

taper = 5
bottle_width_x = 44.30/2
bottle_width_y = 22.90/2
bottle_sep = 4
bottle_angle = 45
depth = (block_height - 1) * 7 + 3
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
    .gridfinity_block_lip(block_x, block_y))

block = block.faces(">Z").chamfer(0.5)

del cutout

cq.exporters.export(block, "zap_a_gap_ca_glue_1p0oz_holder.step")
cq.exporters.export(block, "zap_a_gap_ca_glue_1p0oz_holder.stl")