"""
Supercollider client placeholder
"""
import random
import os
import commands
import math
import scsynth

from sc import *

# reference implementation? @todo sort this out
class SCClientRef( object ):
    _contours   = {};
    _remove     = {};
    _changed    = False;
    _scServer   = None;
    _lastContours = [];
    _lost = []
    _gid = 1;
    _scrunning = [];

    def __init__( self, synthName = 'color' ):
        print "I: SCLient says Hello World!";

        self._synthName = synthName;

        try:
            server = scsynth.connect(verbose=True)
            self._scServer = server
            server.sendMsg('/g_new',self._gid,0,0)

        except OSError:
            print "E: could not start Super Collider"

    def onDone(self,msg):
        print 'on done'

    def onSynthCreated(self,msg):
    	self._scrunning.append(msg[1])

    #hue  -> pitch (moet conceptueel)
    #size -> noise_ratio , groter is ook harder
    #xpos -> pan logisch
    
    def getNote( self, contour ):
        x,y,amp,hue,id = contour
        
        
        ranges = [(0,10),(10, 20),(20, 40),(40, 90),(90, 120),(120, 160),(160,181)]
        range = [r for r in ranges if r[0] <= hue and hue <= r[1]]
        
        
        p = ranges.index(range[0])

        return p;

        #print 'note', p
        #
        #oct = [1.0, 9.0/8, 5.0/4, 4.0/3, 3.0/2, 5.0/3, 15.0/8]
        #pitch = oct[p] * 100;
        #
        #print pitch;


        #
        #if amp < 0.1:
        #    pitch = pitch * 4
        #elif amp < 0.2:
        #    pitch = pitch * 2# oct[p] * 400
        #
        #
        #return pitch;

    def onNew( self, contour ):
        x,y,amp,hue,cid = contour

        self.sendMessage( [ '/s_new', self._synthName, cid, 0, 0, 'amp', amp, 'hue', hue/180, 'panning', x ] );


    def onChanged( self, contour ):
        x,y,amp,hue,cid = contour

        self.sendMessage( [ '/n_set', cid, 'amp', amp, 'hue', hue/180, 'panning', x, 'midinote', self.getNote(contour) ] );


    def onLost( self, cid ):
        self._lost.append(cid)

        self.sendMessage( ['/n_set', cid, 'amp', 0 ] );
        self.sendMessage(['/n_free', cid ])

    def sendMessage( self, msg ):
        if not self._scServer:
            return;

        print 'message:', msg

        self._scServer.sendMsg(*msg)

    def atExit( self ):
        print commands.getoutput('killall scsynth')
        print "we die"

#SCCLient
