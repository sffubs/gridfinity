import cadquery as cq
from math import sqrt, pow

## CADQuery helper utilities for designing Gridfinity blocks
## Gridfinity is a storage block system designed by Zach Freedman.

## Gridfinity basic parameters - don't touch unless you really want a custom
## grid that won't mate with anything on Thingiverse!
## 
## All dimensions derived from original Zach STLs with Blender.

# The size of a 1x1 baseplate.
grid_unit = 42 #mm

# The margin between two 1x1 storage blocks placed next to each other on a
# baseplate.
block_spacing = 0.5 #mm

# The depth of a 1x1x2 divider bin block, including stacking clearance.
# 
# Technically, this is *double* our "depth unit"; all plug-in depth
# calculations will be done on half this amount. However, you should not
# generate depth-1 storage blocks; the system wants blocks whose height is a
# multiple of 2 or 3 depth units.
grid_depth = 18.75 #mm

# The cutaway area on top of a Gridfinity block.
# 
# All Gridfinity blocks have this amount of space cut out off the top of the
# grid depth calculation to allow separating two stacked blocks.
stacking_clearance_depth = 0.954 #mm

## Mating surface

# Master radius for all fillets on the mating surfaces of a baseplate and
# block.
# 
# Fillet radius decreases in concert with the rectangle being rounded off
# such that all fillets have the same origin.
fillet_radius = 4 #mm

# The total depth of the block mating surface.
block_mating_depth = 4.75 #mm

# The total depth of the baseplate mating surface.
baseplate_mating_depth = 4.4 #mm

# The total depth of the upper mating surface used for stacking blocks onto
# other blocks.
#
# This is less than the baseplate mating depth because blocks have an inset top
# chamfer.
#stacking_mating_depth = 3.796 #mm
stacking_mating_depth = 4.4 #mm

# Inset of the XY profile for the non-chamfered part of the mating surface
# on blocks.
block_mating_inset = 2.4 #mm

# Inset of the XY profile for the non-chamfered part of the mating surface on
# baseplates and stacking lips.
baseplate_mating_inset = 2.15 #mm

# Chamfer radius for the block mating lip's bottom chamfer.
block_mating_chamfer = 0.8 #mm

# Width/radius of the block stacking lip.
block_stacking_lip = 0.77426 #mm

# Chamfer radius for the block stacking lip's bottom chamfer.
block_stacking_chamfer = 0.69645 #mm

## MAG-a-nets
##
## Gridfinity blocks have holes for optional magnets. Weighted baseplates, too.
## The holes are actually counterbores that also support M5 screws.

# Offset from the edge of the grid to the center of each magnet.
magnet_inset = 8 #mm

# The diameter of the magnets 
magnet_diameter = 6.5 #mm

magnet_depth = 2.4 #mm

## Screw boreholes

# Diameter of the counterbore hole for screws.
screw_diameter = 3.0 #mm

# Maximum depth of the screw borehole.
# 
# Gridfinity isn't entirely consistent with the depth of the screw bore; some
# blocks go all the way to the base of the block interior. IDK why lol
screw_depth = 6 #mm

## Utilities
def inset_profile(width, height, inset):
    """Generate a sketch for a rectangle of some size, inset by some amount.
    
    Amount must not exceed twice the Gridfinity fillet radius."""
    return cq.Sketch()\
        .rect(width * grid_unit - inset * 2, height * grid_unit - inset * 2)\
        .vertices()\
        .fillet(fillet_radius - inset)

def block_extrusion(depth):
    """Calculate the height of a block some number of units tall, discounting
    the mating lip at the bottom.
    
    This is used to extrude the height of a Gridfinity block."""
    return (grid_depth - block_mating_depth) / 2 * depth - stacking_clearance_depth

def block_top_surface(depth):
    """Calculate the height of a block some number of units tall, discounting
    the mating lip at the bottom and the stacking lip at the top.
    
    This is useful for picking faces or edges at the surface of a (non-hollow)
    Gridfinity block."""
    return block_extrusion(depth) - stacking_mating_depth

def block_cut_limit(depth):
    """Calculate the maximum you can cut into a block of a given depth without
    interfering with the screw counterbores."""

    return block_extrusion(depth) - max(screw_depth - block_mating_depth, 0) - stacking_mating_depth

def top_surface_length(length):
    """Calculate the interior length of the top surface of a Gridfinity block.

    This takes into account the stacking lip, so you can cut profiles into your
    block that are not going to interfere with it. A rectangle constructed
    using the dimensions of this function will end right at the start of the
    stacking lip chamfer.
    
    The length (width or height) is in grid units."""

    return length * grid_unit - block_mating_inset * 2 - block_stacking_chamfer * 2

## Plugins
def gridfinity_block(self, width, height, depth):
    """Create a Gridfinity block of a given width, height, and depth.
    
    The block depth will specifically exclude the height of the block lip. You
    should call `gridfinity_block_lip` with the same width and height at the
    end of constructing your block to add the mating surface necessary to
    attach your block to a baseplate.
    
    Depths that are not a multiple of 2 or 3 are not recommended."""

    return self.placeSketch(inset_profile(width, height, block_spacing / 2))\
        .extrude(block_extrusion(depth))

cq.Workplane.gridfinity_block = gridfinity_block

def gridfinity_block_stack(self, width, height):
    """Cut Gridfinity block stacking lip out of the >Z face.
    
    Face dimensions must match the width and height given here."""

    depth = self.faces(">Z").val().Center().toTuple()[2]
    
    #inset = cq.Workplane("XY")\
    #    .placeSketch(inset_profile(width, height, block_mating_inset))\
    #    .extrude(stacking_mating_depth * -1)\
    #    .translate([0, 0, depth])

    #profile = (cq.Sketch()
    #           .polygon([(0, 0), (0, 5), (2.4, 2.6), (2.4, 0.8), (3.2, 0)])
    #           .offset(0.25))
    profile = (cq.Sketch()
               .polygon([(0, 0), (0, 4.4), (1.9, 2.5), (1.9, 0.7), (2.6, 0), (0, 0)]))

    #path = (self.faces(">Z").workplane()
    #        .moveTo((-42 * width) / 2 + 4, (42 * height) / 2)
    #        .hLine(42 * width - 8).tangentArcPoint((4, -4))
    #        .vLine(-42 * height + 8).tangentArcPoint((-4, -4))
    #        .hLine(-42 * width + 8).tangentArcPoint((-4, 4))
    #        .vLine(42 * height - 8).tangentArcPoint((4, 4)).close())
    
    path = (cq.Workplane("XY")
            .placeSketch(inset_profile(width, height, block_spacing))
            .extrude(1)).faces(">Z").wires()

    lip = (cq.Workplane("YZ")
           .center(-(42 * height - block_spacing) / 2, depth)
           .placeSketch(profile)
           .sweep(path))

    return self.union(lip)
    
    return self.faces(">Z")\
        .cut(inset)\
        .edges(cq.NearestToPointSelector([0, 0, depth]))\
        .chamfer(block_mating_inset - block_spacing * 0.5 - block_stacking_lip)\
        .edges(cq.NearestToPointSelector([0, 0, depth - block_mating_depth]))\
        .chamfer(block_stacking_chamfer)\
        .edges(cq.NearestToPointSelector([width * grid_unit / 2, height * grid_unit / 2, depth + 10]))\
        .fillet(block_stacking_lip / 2)\
        .edges(cq.NearestToPointSelector([width * grid_unit / 2 - block_stacking_lip * 4, height * grid_unit / 2 - block_stacking_lip * 4, depth + 2]))\
        .fillet(block_stacking_lip)

cq.Workplane.gridfinity_block_stack = gridfinity_block_stack

def gridfinity_block_lip(self, width, height, screw_depth=screw_depth, holes=True):
    """Extrude Gridfinity block mating lip out of the <Z face.
    
    Face dimensions must match the width and height given here.
    
    Set `screw_depth=None` to allow the block lip's screw holes to go straight
    through.
    
    Set `holes=False` to disable magnet and screw holes."""
    
    #TODO: Can we recover the Gridfinity units from the selected face's dimensions?
    mating_profile = inset_profile(1, 1, block_mating_inset)
    lip = cq.Workplane("XY")\
        .placeSketch(mating_profile)\
        .extrude(block_mating_depth * -1)\
        .edges("<Z")\
        .chamfer(block_mating_chamfer)
    
    with_lips = self.faces("<Z")\
        .rarray(grid_unit, grid_unit, width, height)\
        .eachpoint(lambda c: lip.val().moved(c), combine="a", clean=True)
    
    filleted = with_lips
    
    for i in range(0, width):
        for j in range(0, height):
            x = (i * grid_unit) - (width * grid_unit / 2) + block_mating_inset
            y = (j * grid_unit) - (height * grid_unit / 2) + block_mating_inset
            
            try:
                filleted = filleted\
                    .edges(cq.NearestToPointSelector([x, y, 0]))\
                    .chamfer(block_mating_inset - block_spacing * 0.5 - 0.01)
            except:
                continue
    
    if holes:
        with_counterbore = (filleted.faces("<Z")
            .workplane()
            .rarray(grid_unit, grid_unit, width, height)
            .rect(grid_unit - magnet_inset * 2, grid_unit - magnet_inset * 2)
            .vertices()
            .cboreHoleTweak(screw_diameter, magnet_diameter, magnet_depth, screw_depth, tweakDepth=0.28))

        return with_counterbore
    else:
        return filleted

cq.Workplane.gridfinity_block_lip = gridfinity_block_lip

# Cloned and adjusted from cq.py. There is surely a better way.
from cadquery.occ_impl.geom import Vector
from cadquery.occ_impl.shapes import Solid

def cboreHoleTweak(
        self,
        diameter,
        cboreDiameter,
        cboreDepth,
        depth=None,
        clean=True,
        tweakDepth=0.2
):
    """
    Makes a counterbored hole for each item on the stack.
    :param diameter: the diameter of the hole
    :type diameter: float > 0
    :param cboreDiameter: the diameter of the cbore
    :type cboreDiameter: float > 0 and > diameter
    :param cboreDepth: depth of the counterbore
    :type cboreDepth: float > 0
    :param depth: the depth of the hole
    :type depth: float > 0 or None to drill thru the entire part.
    :param boolean clean: call :py:meth:`clean` afterwards to have a clean shape
    The surface of the hole is at the current workplane plane.
    One hole is created for each item on the stack.  A very common use case is to use a
    construction rectangle to define the centers of a set of holes, like so::
        s = (
            Workplane()
            .box(2, 4, 0.5)
            .faces(">Z")
            .workplane()
            .rect(1.5, 3.5, forConstruction=True)
            .vertices()
            .cboreHole(0.125, 0.25, 0.125, depth=None)
        )
    This sample creates a plate with a set of holes at the corners.
    **Plugin Note**: this is one example of the power of plugins. Counterbored holes are quite
    time consuming to create, but are quite easily defined by users.
    see :py:meth:`cskHole` to make countersinks instead of counterbores
    """
    if depth is None:
        depth = self.largestDimension()

    boreDir = Vector(0, 0, -1)
    center = Vector()
    # first make the hole
    hole = Solid.makeCylinder(
        diameter / 2.0, depth, center, boreDir
    )  # local coordinates!

    # add the counter bore
    cbore = Solid.makeCylinder(cboreDiameter / 2.0, cboreDepth + tweakDepth, Vector(), boreDir)
    r = hole.fuse(cbore)

    tweak = (cq.Solid.makeBox(
        cboreDiameter,
        (cboreDiameter - diameter) / 2,
        tweakDepth)
             .translate(
                 (-cboreDiameter / 2, -(cboreDiameter / 2), -(cboreDepth + tweakDepth))))

    r = r.cut(tweak).cut(tweak.mirror("XZ"))
    
    return self.cutEach(lambda loc: r.moved(loc), True, clean)

cq.Workplane.cboreHoleTweak = cboreHoleTweak
