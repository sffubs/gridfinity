import math

import cadquery as cq

plugBack = 15.053
plugFront = 15.534
plugDepth = 8
plugChamfer = 0.5
diameterPlugFront = (plugFront) * math.cos(math.pi/6)

spacing = 40.88

def bracket():
    outer_points = [
        (0, 0),                                  # Bottom left
        (spacing + plugFront, 0),                                 # Bottom right
        (spacing + plugFront, 7.5),
        (spacing + plugFront-100, 45),
        (0, 7.5),
        (0, 0)                                   # Back to start
    ]
    
    # Create inner cutout offset from edges
    #inner_points = [
    #    (wall_thickness, wall_thickness),
    #    (bracket_width - wall_thickness, wall_thickness),
    #    (bracket_width - wall_thickness, base_depth - wall_thickness),
    #    (2 * wall_thickness, base_depth - wall_thickness),
    #    (2 * wall_thickness, bracket_height - wall_thickness),
    #    (wall_thickness, bracket_height - wall_thickness),
    #    (wall_thickness, wall_thickness)
    #]
    
    bracket_sketch = (
        cq.Sketch()
        .polygon(outer_points)
    )
    
    # Create the 3D bracket by extruding
    bracket = (cq.Workplane("XY")
               .placeSketch(bracket_sketch)
               .extrude(diameterPlugFront))
    
    # Fillet edges not on Y=0
    edges_to_fillet = []
    for edge in bracket.edges("|Z").vals():
        center = edge.Center()
        if center.y > 0.001:  # Not on Y=0
            edges_to_fillet.append(edge)
    
    if edges_to_fillet:
        bracket = bracket.newObject(edges_to_fillet).fillet(3)
    
    # Shell the object, removing top and bottom faces (normal to Z)
    faces_to_remove = bracket.faces(">Z").vals() + bracket.faces("<Z").vals()
    bracket = bracket.newObject(faces_to_remove).shell(-2.4)

    return bracket

def plug():        
    skPlugBack = cq.Sketch().regularPolygon(plugBack/2, 6, 30)
    skPlugFront = cq.Sketch().regularPolygon(plugFront/2, 6, 30)
    
    diameterPlugFront = (plugFront) * math.cos(math.pi/6)
    
    plug = (cq.Workplane("top")
        .placeSketch(
            skPlugBack.moved(cq.Location(cq.Vector(0, (plugFront - plugBack) / 2, -plugDepth))),
            skPlugFront.moved(cq.Location(cq.Vector(0, 0, 0)))).loft()
        .faces("<Y").chamfer(plugChamfer)
        #.faces().workplane(offset=plugDepth)
        #.placeSketch(cq.Sketch().regularPolygon(plugBack/2, 6, 30).edges()).close()
        #.loft(combine=True)
        #.extrude(plugDepth)
        .translate((plugFront / 2, 0, (diameterPlugFront / 2)))
        )
    
    return plug

def misc():
    hexSpacing = 40.88
    
    numPlugSpaces = (math.floor((42 * numX) / hexSpacing) - 1)
    gap = numPlugSpaces * hexSpacing
    
    plugs = plug
    
    for i in range(1, numPlugSpaces + 1):
        if (i < numPlugSpaces / 2 and i % 2 == 0) or (i >= numPlugSpaces/2 and i % 2 == numPlugSpaces % 2):
            plug2 = plug.translate((i * hexSpacing, 0, 0))
            plugs = plugs.union(plug2)
            del plug2
    
    del plug
    
    plugs = plugs.translate((-21 + (numX * 42) / 2 - gap / 2, 0, 0))
    
    model = model.union(plugs)
    
    del plugs

model = bracket()

# Union two plugs with spacing of 40.88 on the Y=0 plane
#plug1 = plug().rotateAboutCenter((1, 0, 0), 90)  # Rotate to align with Y=0 plane
#plug2 = plug().rotateAboutCenter((1, 0, 0), 90).translate((spacing, 0, 0))
#model = model.union(plug1).union(plug2)

model = model.union(plug())
model = model.union(plug().translate((spacing, 0, 0)))

cq.exporters.export(model, "honeycomb_shoe_holder.step")
cq.exporters.export(model, "honeycomb_shoe_holder.stl")