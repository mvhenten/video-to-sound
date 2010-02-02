#!/usr/bin/env python
"""
@title Simple storage object
@description Keep track of contours
@author Matthijs van Henten <matthijs+cc@ischen.nl>
@license GNU GPL 3.0
"""
class Contour(object):
    _data = {}
    _iter = None

    def __init__( self, id, values ):
        data = {};
        (data['pan'], data['amp'], (data['hue'], data['sat'], data['val'])) = values;
        data['id'] = id;
        self._data = data;

    def __getattr__( self, name ):
        if name in self._data:
                return self._data[name];

    def __iter__( self ):
        return self;

    def next( self ):
        if not self._iter:
                self._iter = iter( self._data );

        try:
                value = self._iter.next();
                return (value, self._data[value]);
        except:
                self._iter = None;
                raise StopIteration;

class ContourStorage(object):
    _bufferSize   = 25; # how many frames are stored.
    _contourBuffer = [];
    _contours = {}; # holds the last values for active ids'
    _flushed  = {}; # hold id's that have been flushed
    _current  = {}; # current colleciton of contours added
    _size     = (0,0);
    _totalPix = None;

    def __init__( self, size = (None, None) ):
        self.setSize( size );

    def setSize(self, size ):
        self._totalPix = size[0] * size[1];
        self._size = size;

    def getSize( self ):
        return self._size;

    size = property( getSize, setSize );

    def getContours( self ):
        contours = [];

        for id, contour in self._contours.iteritems():
            contours.append( Contour( id, contour ) );

        return contours;

    contours = property( getContours );

    """
        Flush the current collection of contours.
        Contours are stored in a buffer to counter for video inaccuracies or objects
        that are shortly dissapearing.

        @return flushed Contours that have been flushed from the buffer
    """
    def flush( self ):
        toRemove = {};
        contours = {};

        # add the _current to the contourbufer
        self._contourBuffer.append( dict(self._current) );

        # clean the aggregate container
        self._contours = {};
        self._current = {};

        # remove the first (oldest) contour collection from buffer
        if len( self._contourBuffer ) > self._bufferSize:
            contours = self._contourBuffer.pop(0);


        # self._contours hold all the contours, but only their last values
        for contour in self._contourBuffer:
            self._contours.update( contour ); # last in, overwrites previous

        return contours;

    """ collect contour data in a list, creates an id per contour """
    def append( self, size, center, values ):
        x, y = center;
        width, height = self._size;

        center = (round((float(x)/width), 2), round((float(y)/height), 2));
        size   = round( (float(size) / self._totalPix), 4 );

        #print center, size;

        #print "%.2f, %.2f, %.2f, %.2f" % ( center, self._size );

        #center = (float("%.2f" % (float(x) / float(width))), float("%.2f" % float(y) / float(height) ));
#        size   = float( "%.2f" % size );

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
                id = max( keys ); # always the last one
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
        bounds   = ( self._size[0] * 0.15, self._size[1] * 0.11 ); # allow for 15% jitter - about 50 pixels to the left or right

        pos =  min( [abs(a-b) < c for (a, b, c) in zip( contour[0], contour2[0], bounds)] );
        hsv =  min( [abs(a-b) < c for (a, b, c) in zip( contour[2], contour2[2], ( 9, 13, 13 ))] );

        if pos and hsv:
            return True;
        return False;

#ContourStorage
