import math

import cadquery as cq
import gridfinity

block_x = 1
block_y = 1
block_height = 6

diameter = 8.5
taper = 2.5
depth = (block_height - 1) * 7 + 6
#taper_pad = 0
well_depth = 12
taper_pad = (depth / 2 - well_depth) * math.sin((taper / 180) * math.pi)

spacing = 3.6

clearance= 0.15

block = (
    cq.Workplane("XY")
    .gridfinity_block(block_x, block_y, block_height))

cutout = (
    block.faces(">Z")
    .placeSketch(
        cq.Sketch().circle(diameter / 2 + clearance + taper_pad))
    .extrude(-(depth / 2 - well_depth), combine=False, taper=taper)
    .faces("<Z").wires().toPending()
    .extrude(-depth / 2)
    .faces("<Z")
    .chamfer(length=18 * 0.35, length2=4 * 0.35)
    .faces("<Z").wires().toPending()
    .extrude(-well_depth))

block = (
    block
    .rarray(diameter + (clearance + taper_pad) * 2 + spacing, diameter + (clearance + taper_pad) * 2 + spacing, 3, 3)
    .eachpoint(lambda loc: cutout.val().moved(loc), combine="cut")
    .gridfinity_block_lip(block_x, block_y, screw_depth=3)
    .gridfinity_block_stack(block_x, block_y))

#block = block.faces(">Z").chamfer(0.5)

del block

#del cutout

#cq.exporters.export(block, "pencil_holder.step")
#cq.exporters.export(block, "pencil_holder.stl")