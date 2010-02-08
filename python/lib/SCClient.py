"""
Supercollider client placeholder
"""
from sc import *
import time
import random 
import os
import commands

class SCClient( object ):
    _contours   = {};
    _remove     = {};
    _changed    = False;
    _scServer   = None;
    _lastContours = [];
    _lost = []
    _gid = 1;
    _scrunning = [];

    def __init__( self ):
        print "I: SCLient says Hello World!";
        
        try:
            sc.start( exedir='/Applications/SuperCollider', verbose=0, spew=0 )
            self._scServer = sc.server
            
            #register some handler
            sc.register( '/n_go', self.onSynthCreated ) # 
            sc.register( '/done', self.onDone ) #
            
            #send commands
            self._scServer.sendMsg('/b_alloc',1,512,1); #allocate a buffer in supercollider
            self._scServer.sendMsg('/d_loadDir', os.path.abspath('../sc')); #load synthdefs, we should wait till sc has said something
            self._scServer.sendMsg('/g_new',self._gid,0,0)
            
            
            
        except OSError:
            print "could not start Super Collider"
        
    def onDone(self,msg):
        if msg[1] == "/b_alloc":
            for i in range(512):
                fl = (float(i) / 256) - 1
                if (fl < 0.0):
                    fl = 0
                if (fl > 0.5):
                    fl = 1 - fl
                
                self._scServer.sendMsg('/b_set',1,i,fl)
                
                    
    
    
    def onSynthCreated(self,msg):
    	self._scrunning.append(msg[1])
        print "***** on" , msg[1]
       

    def onNew( self, contour ):
        print "*** new", contour["oid"]
        if not self._scServer:
            return
        
        print contour
        
        msg = ['/s_new', 'clar', contour["oid"], 0, self._gid, 'buf', 1, 'freq', contour['x'], 'p_m', float(contour['size'])/10000]
        #msg = ['/s_new', 'EnvelopedSine', contour["oid"], 0, self._gid, 'freq', contour["x"], 'amp', 0.5, 'a', 0.00, 'd', 0.00, 's', 0.00, 'r', 0.1, 'gate', 1]
        self._scServer.sendMsg(*msg)
       
    def onChanged( self, contour ):
        print "*** changed", contour["oid"]
        if not self._scServer:
            return
        
        msg = ['/n_set', contour["oid"], 'p_m', float(contour['size'])/10000]
        self._scServer.sendMsg(*msg)
        msg = ['/n_set', contour["oid"], 'freq', contour["x"]]
        self._scServer.sendMsg(*msg)
    
    def onLost( self, contour ):
        cid = contour["oid"]
        
        print "*** lost", cid
        self._lost.append(cid)
        if not self._scServer:
            return
        
        
        msg = ['/n_free', cid]
        self._scServer.sendMsg(*msg)
            #msg = ['/n_set', cid, 'gate', 0]
            #self._scServer.sendMsg(*msg)
            
        #for cid in self._lost:
        #    msg = ['/n_free', cid]
        #    self._scServer.sendMsg(*msg)
       
       #for cid in self._lost: 
       #    if self._scServer:
       #        #msg = ['/n_set', cid, 'gate', 0]
       #        msg = ['/n_free', cid]
       #        self._scServer.sendMsg(*msg)
           

    
    def atExit( self ):
        print commands.getoutput('killall scsynth')
        print "we die"
    	
    

#SCCLient
