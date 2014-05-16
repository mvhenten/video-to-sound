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

        print 'HUE', hue

        # 8 = orange
        # 25 = yellow
        # 88 = green
        # 110 = blue
        # 133 = blue
        # 137 = purple blue
        # 145 - 150 = purple
        # 174 = red

        mapping = [
            ('orange', 0, 15, 3),
            ('yellow', 15, 50, 5),
            ('green', 50, 100, 6),
            ('blue', 100, 134, 8),
            ('purple', 134, 160, 10),
            ('red', 160, 181, 1)
        ]

        [[color, start, stop, note ]] = [r for r in mapping if r[1] <= hue and hue <= r[2] ]

        # DEBUG
        # print 'COLOR,NOTE', color, note

        amp = math.log(amp*10,8);

        if amp < 0.15:
            return note + 26;

        if amp < 0.70:
            return note + 13;

        return note;


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

