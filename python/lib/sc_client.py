"""
Supercollider client placeholder
"""
import random
import os
import commands
import math
import scsynth

from sc import *

"""
16/5/2014 simplified code, no longer stops and starts supercollider, connects
to external server instead, remove cruft.

Simplified parameters, back to hue (pitch), position (panning) and size (amplitude)
for the sake of simplicity.
"""

class SCClient( object ):
    _scServer   = None;
    _gid = 1;

    def __init__( self, synthName = 'color' ):
        print "I: SCLient says Hello World!";

        self._synthName = synthName;

        try:
            server = scsynth.connect(verbose=True)
            self._scServer = server
            server.sendMsg('/g_new',self._gid,0,0)

        except OSError:
            print "E: could not connect to Super Collider"

    
    def getNote( self, contour ):
        x,y,amp,hue,id = contour

        ranges = [(0,10),(10, 20),(20, 40),(40, 90),(90, 120),(120, 160),(160,181)]
        range = [r for r in ranges if r[0] <= hue and hue <= r[1]]
        
        # octave shifting
        color = ranges.index(range[0])

        # mapping colors to midi notes
        notes = { 6: 1, 0: 3, 1: 5, 2: 6, 3: 8, 4: 10, 5: 12 }
        note = notes[color];
        
        # These are "sweetspots" established by trial
        # and error. e.g. when "tiny" shift to a higher octave.
        # These number may have to be adusted per location

        amp = math.log(amp*10,10);

        if amp < 0.15:
            return color + 26;

        if amp < 0.70:
            return color + 13;

        return color;


    def onNew( self, contour ):
        x,y,amp,hue,cid = contour

        self.sendMessage( [ '/s_new', self._synthName, cid, 0, 0, 'amp', math.log(amp*10,8), 'panning', x, 'note', self.getNote(contour) ] );


    def onChanged( self, contour ):
        x,y,amp,hue,cid = contour

        self.sendMessage( [ '/n_set', cid, 'amp', math.log(amp*10,8), 'panning', x, 'note', self.getNote(contour) ] );


    def onLost( self, cid ):
        self.sendMessage( ['/n_set', cid, 'gate', 0 ] );

    def sendMessage( self, msg ):
        if not self._scServer:
            return;

        # debug only, output consumes cpu
        # print 'message:', msg

        self._scServer.sendMsg(*msg)

