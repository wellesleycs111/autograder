"""Python code for Henderson-like picture language abstraction built on top 
   of cs1graphics. In all cases, a "picture" is a drawable object that fits
   in a 200 x 200 square centered about the reference point (0,0)
   Lyn Turbak, Sep 2015."""

from cs1graphics import *

frameList = [] # Global list for keeping track of all displayed pictures

def displayPic (pic):
    """ 
    Create 600x600 canvas to display a picture.
    Clones picture, moves it to the center of the canvas, and scales by 3 to 
    fill the frame. (If we didn't clone, the resulting moved & scaled drawable 
    object would no longer satisfy the definition of picture -- i.e., 
    it would no longer be of size 200x200 or centered at (0,0).
    """
    global frameList
    frame = Canvas(600, 600,'white', 'Picture Frame')  # Create square canvas
    frameList.append(frame) # Remember for closing them all. 
    framedPic = pic.clone()
    framedPic.moveTo(300, 300)
    framedPic.scale(3)
    frame.add(framedPic)
    
def closeAllPics():
    global frameList
    for frame in frameList:
        frame.close()
    frameList = []

""" -------------------------------------------------------------------------
Define some simple 'primitive' pictures 
------------------------------------------------------------------------- """

def patch(color):
    """ A patch is a black-bordered square with a specified fill color """
    pic = Square(200)
    pic.setFillColor(color) 
    pic.setBorderColor('black') 
    return pic

def test_patch():
    rp = patch('red')
    bp = patch('blue')
    displayPic(rp)
    displayPic(bp)

def wedge(color):
    """A wedge is a triangle in the bottom half of a picture"""
    pic = Polygon(Point(100, 0),
                  Point(100,100), 
                  Point(-100, 100))
    # Shift reference point from (100,0) to (0,0)
    pic.adjustReference(-100,0) 
    pic.setFillColor(color)
    pic.setBorderColor(color) # no border!
    return pic

def triangles(LLcolor, URcolor): 
    """ Returns a square with colored lower left and upper right triangles"""
    newPic = Layer()
    LLtri = Polygon(Point(-100, -100), Point(100, 100), Point(-100, 100))
    LLtri.setFillColor(LLcolor)
    newPic.add(LLtri)
    URtri = Polygon(Point(-100, -100), Point(100, 100), Point(100, -100))
    URtri.setFillColor(URcolor)
    newPic.add(URtri)
    # borderColor of triangles is black by default
    return newPic

def test_wedge():
    gw = wedge('green')
    displayPic(gw)

def checkmark(downColor, upColor): 
    """A checkmark with different colors for downstroke and upstroke"""
    pic = Layer()
    downstroke = Path(Point(-100,0), Point(0,100))
    downstroke.setBorderColor(downColor)
    pic.add(downstroke)
    upstroke = Path(Point(0,100), Point(100,-100))
    upstroke.setBorderColor(upColor)
    pic.add(upstroke)
    return pic

def test_checkmark():
    mark = checkmark('red', 'blue')
    displayPic(mark)

def leaves(color):
    """ Returns a picture of two leaves on a stem of the specified color """ 
    newPic = Layer()
    
    # Leaf 1
    leaf1 = Polygon(Point(-100,100),Point(0,100),Point(100,50),Point(0,50))
    leaf1.setFillColor(color)
    leaf1.setBorderColor(color)
    newPic.add(leaf1)

    # Leaf 2
    leaf2 = Polygon(Point(-50,50),Point(-50,-25),Point(0,-100),Point(0,-25))
    leaf2.setFillColor(color)
    leaf2.setBorderColor(color)
    newPic.add(leaf2)    
    
    # Branch
    branch = Path(Point(-100,100),Point(0,0))
    branch.setBorderColor(color)
    newPic.add(branch)
    
    return newPic

def test_leaves():
    gl = leaves('green')
    displayPic(gl)
 
# The empty picture
def empty():
    return Layer()
    
""" -------------------------------------------------------------------------
Clockwise rotations of pictures. Unlike the .rotate() method, which 
changes a graphics object by side effect, these functions return a *new*
picture that is a rotated version of the given one
------------------------------------------------------------------------- """
    
def clockwisePic(pic, angle):
    newPic = pic.clone() # create new picture by cloning it. 
    newPic.rotate(angle) # if angle is a multiple of 90,
                         # result still satisfies definition                         
                         # of picture. 
    return newPic
    
def clockwise90 (pic):
    return clockwisePic (pic, 90)
  
def clockwise180 (pic):
    return clockwisePic (pic, 180)
    
def clockwise270(pic):
    return clockwisePic (pic, 270)

def test_clockwise():
    gw = wedge('green')
    displayPic(clockwise90(gw))
    displayPic(clockwise180(gw))
    displayPic(clockwise270(gw))

""" -------------------------------------------------------------------------
Flipped versions pictures. Unlike the .flip() method, which 
changes a graphics object by side effect, these functions return a *new*
picture that is a flipped version of the given one
------------------------------------------------------------------------- """

def flipPic (pic, angle):
    newPic = pic.clone() # create new picture by cloning it. 
    newPic.flip(angle)   # if angle is a multiple of 45,
                         # result still satisfies definition                     
                         # of picture. 
    return newPic 
   
def flipAcrossVert (pic): 
    return flipPic(pic, 0)
    
def flipAcrossHoriz (pic): 
    return flipPic(pic, 90)
    
def flipAcrossDiag(pic): 
    return flipPic(pic, 45) 

def test_flip():
    gw = wedge('green')
    displayPic(flipAcrossVert(gw))
    displayPic(flipAcrossHoriz(gw))
    displayPic(flipAcrossDiag(gw))

""" -------------------------------------------------------------------------
Overlaying two pictures
------------------------------------------------------------------------- """

def overlay(pic1, pic2): 
    '''Returns a new pic in which pic1 appears on top of pic2'''
    newPic = Layer()
    newPic.add(pic2) # bottom pic goes first
    newPic.add(pic1) # top pic goes last
    return newPic

def test_overlay():  
    gl = leaves('green')
    mark = checkmark('red', 'blue')
    displayPic(overlay(mark,gl))
    displayPic(overlay(gl,mark))

""" -------------------------------------------------------------------------
Combining four pictures into one. 
------------------------------------------------------------------------- """
    
def fourPics(a, b, c, d):
    """Given four pictures of the same size, returns a new picture of that size
    # with the four pictures in its quadrants."""
    newPic = Layer()
    aHalf = a.clone()
    aHalf.scale(0.5)
    bHalf = b.clone()
    bHalf.scale(0.5)
    cHalf = c.clone()
    cHalf.scale(0.5)
    dHalf = d.clone()
    dHalf.scale(0.5)
    aHalf.move(-50,-50)
    bHalf.move(50,-50)
    cHalf.move(-50,50)
    dHalf.move(50,50)
    newPic.add(aHalf)
    newPic.add(bHalf)
    newPic.add(cHalf)
    newPic.add(dHalf)
    return newPic

def test_fourPics():
    rp = patch('red')
    gw = wedge('green')
    mark = checkmark('red', 'blue')
    bp = patch('blue')
    displayPic(fourPics(rp, gw, mark, bp))
   
def fourSame(pic):
    """Given a picture, returns a new picture ith four half-sized copies of the 
    given picture in its quadrants."""
    return fourPics(pic, pic, pic, pic)

def test_fourSame():
    gl = leaves('green')
    displayPic(fourSame(gl))
    rp = patch('red')
    bp = patch('blue')
    displayPic(fourSame(fourSame(fourPics(rp,bp,bp,rp))))

def tiling(pic):
    return fourSame(fourSame(fourSame(fourSame(pic))))

def test_tiling():
    mark = checkmark('red', 'blue')
    displayPic(tiling(mark))
    
def checkerboard(color1, color2):
    return fourSame(fourSame(fourPics(patch(color1), patch(color2),
                                      patch(color2), patch(color1))))
                                      
def test_checkerboard():
    displayPic(checkerboard('black', 'red'))
    displayPic(checkerboard('magenta', 'cyan'))
                                            

def rotations(pic):
    """Returns a picture as the same size of the given picture
    with four rotations of the half-sized picture about center"""
    return fourPics(clockwise270(pic), pic, 
                    clockwise180(pic), clockwise90(pic))
                    
def wallpaper(pic):
    return rotations(rotations(rotations(rotations(pic))))
    
def test_wallpaper():
    gw = wedge('green')
    mark = checkmark('red', 'blue')
    displayPic(wallpaper(gw))
    displayPic(wallpaper(mark))
  
def rotations2(pic):
    """A version of rotations that rotates the quadrants differently"""
    return fourPics(pic,clockwise90(pic), 
                    clockwise180(pic), clockwise270(pic))
                    
def design(pic):
    return rotations2(rotations2(rotations2(rotations2(pic))))
    
def test_design():
    gw = wedge('green')
    mark = checkmark('red', 'blue')
    displayPic(design(gw))
    displayPic(design(mark))

if __name__=='__main__':
    test_checkerboard()
    # cs1graphics bug: displaying a simple picture afterwards makes the complex picture display
    gl = leaves('green')
    displayPic(wallpaper(gl))
    displayPic(gl)

