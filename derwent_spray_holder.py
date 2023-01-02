import math

import cadquery as cq
import gridfinity

block_x = 1
block_y = 1
block_height = 5

taper = 3
bottle_diameter = 19.4
depth = (block_height - 1) * 7 + 9
clearance= 0.15
taper_pad = depth * math.sin((taper / 180) * math.pi)

block = (
    cq.Workplane("XY")
    .gridfinity_block(block_x, block_y, block_height)
    .gridfinity_block_stack(block_x, block_y)
    )

cutout = (
    block.faces(">Z")
    .circle(bottle_diameter / 2 + taper_pad + clearance)
    .extrude(-depth, combine=False, taper=taper))

block = (
    block
    .cut(cutout)
    .gridfinity_block_lip(block_x, block_y))


#block = block.faces(">Z").chamfer(0.5).gridfinity_block_stack(block_x, block_y)


del cutout

cq.exporters.export(block, "derwent_spray_holder.step")
cq.exporters.export(block, "derwent_spray_holder.stl")
