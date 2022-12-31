import math

import cadquery as cq
import gridfinity

block_x = 1
block_y = 1
block_height = 3

taper = 2.5
bottle_width_x = 34.40/2
bottle_width_y = 17.80/2
bottle_sep = 1
bottle_angle = 0
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
    .cut(cutout.translate((0, -(bottle_width_y + taper_pad + bottle_sep / 2), 0)))
    .cut(cutout.translate((0, +(bottle_width_y + taper_pad + bottle_sep / 2), 0)))
    .gridfinity_block_lip(block_x, block_y))

block = block.faces(">Z").chamfer(0.3)

del cutout

cq.exporters.export(block, "zap_a_gap_ca_glue_0p5oz_x2_holder.step")
cq.exporters.export(block, "zap_a_gap_ca_glue_0p5oz_x2_holder.stl")
