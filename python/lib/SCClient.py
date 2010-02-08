"""
Supercollider client placeholder
"""
from sc import *
import time
import random 
import os

class SCClient( object ):
    _contours   = {};
    _remove     = {};
    _changed    = False;
    _scServer   = None;
    _lastContours = [];

    def __init__( self ):
        print "I: SCLient says Hello World!";
        
        try:
            sc.start( exedir='/Applications/SuperCollider', verbose=1, spew=1 )
            self._scServer = sc.server
            self._scServer.sendMsg('/d_loadDir', os.path.abspath('lib/synthdefs')); #load synthdefs, we should wait till sc has said something
            
        except OSError:
            print "could not start Super Collider"
        
       

    def onNew( self, contour ):
       print "*** new", contour["oid"]
    def onChanged( self, contour ):
       print "*** changed", contour["oid"]
    def onLost( self, contour ):
       print "*** lost", contour["oid"]
       
       
       
    #changed = property( None, setChanged );

    def setContours( self, contours ):
        # contour has hue, val, sat, amp, pan. pan is a tuple(x, y) center pair
        if self._scServer:
            msg = ['/s_new', 'EnvelopedSine', int(random.random() * 1000), 0, 0, 'freq', 400, 'amp', 0.5, 'a', 0.01, 'd', 0.01, 's', 0.01, 'r', 0.9, 'gate', 1]
            #self._scServer.sendMsg(*msg)
        
        #print type(contours) list
        
        for c in contours:
            a = c
            #if not c.id in self._lastContours
            #    print "new"
            #    print c.id
                
            #print c.id
            #print "Hue is:", c.hue;
            #for key, value in c:
            #    print key, value; # alternative access
        
        self._lastContours = contours[:]
    
    contours = property( None, setContours );

    def setRemove( self, remove ):
        self._remove = remove;

    remove = property( None, setRemove );
    
    def atExit( self ):
    	print "we die"
    

#SCCLient
