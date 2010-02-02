"""
Supercollider client placeholder
"""
class SCClient( object ):
    _contours   = {};
    _remove     = {};
    _changed    = False;

    def __init__( self ):
        print "I: SCLient says Hello World!";

    def setChanged( self, value = True ):
        self._changed = value;
        # do stuff

    changed = property( None, setChanged );

    def setContours( self, contours ):
        # contour has hue, val, sat, amp, pan. pan is a tuple(x, y) center pair
        for c in contours:
            print "Hue is:", c.hue;
            for key, value in c:
                print key, value; # alternative access

    contours = property( None, setContours );

    def setRemove( self, remove ):
        self._remove = remove;

    remove = property( None, setRemove );

#SCCLient
