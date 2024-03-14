import math

import cadquery as cq
import gridfinity

block_x = 1
block_y = 1
block_height = 4

base_x = 14.2
base_y =17.4
top_x = 5
top_y = 5
height = 8.6

pan_spacing = 2

extra_depth = 3

clearance= 0.15

block = (
    cq.Workplane("XY")
    .gridfinity_block(block_x, block_y, block_height)
    .faces(">Z")
    .placeSketch(gridfinity.inset_profile(1, 1, gridfinity.block_spacing + 2.6))
    .cutBlind(-10)
    .gridfinity_block_stack(block_x, block_y))

eraser_space = (cq.Workplane("XY")
    .circle(5 / 2 + clearance)
    .extrude(25.5, taper=-2))
    #.translate((0, 0, -(gridfinity.stacking_mating_depth))))

block = (
    block
    .rarray(top_x + pan_spacing, top_y + pan_spacing, 5, 5)
    .eachpoint(lambda loc: eraser_space.val().moved(loc), combine="cut")
    .gridfinity_block_lip(block_x, block_y, screw_depth=3))

#block = block.faces(">Z").chamfer(0.5)
del eraser_space
#del halfpan_cutut

cq.exporters.export(block, "derwent_eraser_tip_storage.step")
cq.exporters.export(block, "derwent_eraser_tip_storage.stl")
