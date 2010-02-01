#!/usr/bin/env python
"""
@title Simple storage object
@description Keep track of contours
@author Matthijs van Henten <matthijs+cc@ischen.nl>
@license GNU GPL 3.0
"""
class ContourStorage:
    _contours = {};
    _current  = {};
    _new      = None;
    _size     = None;
    _totalPix = None;

    def getContours( self ):
        self._contours.update( self._current );

        contours = dict( self._current );
        self._current = {};

        return contours;

    """ add a new contour to the current list. recycle ids """
    def add( self, size, center, values ):
        contour = ( center, size, values );
        id      = None;

        # search for an contour that has not been detected yet

        if not len( self._contours ):
            id = 1;
            if len( self._current ):
                id = max( self._current.keys() ) + 1;
        else:
            keys = [key for key in self._contours if self.compare( key, contour ) and key not in self._current];
            if len( keys ):
                id = min( keys );
            else:
                collect = dict( self._contours );
                collect.update( self._current );
                keys = [ key - 1 for key in collect.keys() if key - 1 not in collect and key - 1 > 0];

                if len(keys):
                    id = min( keys );
                else:
                    id = max(collect.keys()) + 1;

        self._current[id] = contour;

    """ Compare contour with a saved contour at key. HSV and position must be within 10% """
    def compare(self, key, contour ):
        contour2 = self._contours[key];
        bounds   = ( self._size[0] / 10, self._size[1] / 10 );

        pos =  min( [abs(a-b) < c for (a, b, c) in zip( contour[0], contour2[0], bounds)] );
        hsv =  min( [abs(a-b) < c for (a, b, c) in zip( contour[2], contour2[2], ( 9, 13, 13 ))] );

        if pos and hsv:
            return True;
        return False;

    def setSize(self, size ):
        self._totalPix = size[0] * size[1];
        self._size = size;

# contour storage
