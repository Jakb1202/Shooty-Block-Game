import math

def return_distance(p1, p2):
    # pythagoras
    # points given as tuples, (x, y)
    return (math.sqrt( (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 ))

def return_dydx(p1, p2):
    # gradient between 2 points
    dy = (p1[1]-p2[1])
    dx = (p1[0]-p2[0])
    if dy == 0:
        # both points are on the same Y
        return None
    elif dx == 0:
        # both points are on the same X 
        return 0
    # there is a gradient between the 2 points
    return ( dy/dx )

def to_radians(degrees):
    return (degrees*(math.pi/180))

def to_degrees(radians):
    return (radians*(180/math.pi))
