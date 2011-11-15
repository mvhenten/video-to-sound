"""
Supercollider client placeholder
"""
import random
import os
import commands
import math
import scsynth

from sc import *

class SCClient( object ):
    _contours   = {};
    _remove     = {};
    _changed    = False;
    _scServer   = None;
    _lastContours = [];
    _lost = []
    _gid = 1;
    _scrunning = [];

    def __init__( self, synthName = 'color', scsynthPath = 'Applications/SuperCollider' ):
        print "I: SCLient says Hello World!";

        try:
            sc.start( exedir=scsynthPath, verbose=0, spew=0 )
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


    def onNew( self, contour ):
        if not self._scServer:
            return


        msg = ['/s_new', 'clar', contour["oid"], 0, self._gid, 'buf', 1, 'freq', contour['pan'][0], 'p_m', contour['amp']]
        #msg = ['/s_new', 'EnvelopedSine', contour["oid"], 0, self._gid, 'freq', contour["x"], 'amp', 0.5, 'a', 0.00, 'd', 0.00, 's', 0.00, 'r', 0.1, 'gate', 1]
        self._scServer.sendMsg(*msg)

    def onChanged( self, contour ):
        # print "*** changed", contour["oid"]
        if not self._scServer:
            return

        msg = ['/n_set', contour["oid"], 'p_m', contour['amp']]
        self._scServer.sendMsg(*msg)
        msg = ['/n_set', contour["oid"], 'freq', contour["pan"][0]]
        self._scServer.sendMsg(*msg)

    def onLost( self, contour ):
        cid = contour["oid"]

        # print "*** lost", cid
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
            
            #server = scsynth.connect(verbose=True,iphost="10.0.135.15")
            server = scsynth.connect(verbose=True)
            self._scServer = server

            #register some handler
            #server.register( '/n_go', self.onSynthCreated ) #
            #server.register( '/done', self.onDone ) #

            #send commands
            #serversendMsg('/b_alloc',1,512,1); #allocate a buffer in supercollider
            #server.sendMsg('/d_loadDir', os.path.abspath('../sc')); #load synthdefs, we should wait till sc has said something
            server.sendMsg('/g_new',self._gid,0,0)



        except OSError:
            print "E: could not start Super Collider"

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


    #hue  -> pitch (moet conceptueel)
    #size -> noise_ratio , groter is ook harder
    #xpos -> pan logisch
    
    def getPitch( self, contour ):
        x,y,amp,hue,id = contour
        
        
        ranges = [(0,10),(10, 20),(20, 40),(40, 90),(90, 120),(120, 160),(160,180)]        
        range = [r for r in ranges if r[0] <= hue and hue <= r[1]]
        
        
        p = ranges.index(range[0])

        oct = [1.0, 9.0/8, 5.0/4, 4.0/3, 3.0/2, 5.0/3, 15.0/8]
        pitch = oct[p] * 100;
    
        if amp < 0.1:
            pitch = pitch * 4
        elif amp < 0.2:
            pitch = pitch * 2# oct[p] * 400
        
            
        return pitch;

    def onNew( self, contour ):
        if not self._scServer:
            return;

        x,y,amp,hue,id = contour
        
        
        #ranges = [(0,10),(10, 30),(30, 60),(60, 90),(90, 120),(120, 160),(160,180)]        
        #range = [r for r in ranges if r[0] <= hue and hue <= r[1]]
        #
        #
        #p = ranges.index(range[0])
        #
        #oct = [1.0, 9.0/8, 5.0/4, 4.0/3, 3.0/2, 5.0/3, 15.0/8]
        #pitch = oct[p] * 200;
        #
        #if amp < 0.1:
        #    pitch = pitch * 2# oct[p] * 400
        
        pitch = self.getPitch( contour )
        damping = 0.99#0.8 - (y/5)
                
        #pitch = hue * 100 + 100
        amp = 0.2 + (amp * 0.8) #minimal amp needed
        msg = ['/s_new', 'pluckbow', id, 0 , 0, "drive_in", 0, "noise_ratio",amp,"driver_smoothing", 0.996, "damping", damping, "refl", 0.995, "pitch_in", pitch, "pan", x ]
        self._scServer.sendMsg(*msg)

    def onChanged( self, contour ):
        if not self._scServer:
            return
        
        x,y,amp,hue,id = contour
        
        damping = 0.9 - (y/10)
        auto = amp * 0.1
        amp = 0.2 + (amp * 0.8)
        refl = 0.98 + (y /50)
        
        
        pitch = self.getPitch( contour )
        drive = math.sqrt(x*x+y*y) * 0.6
        
        # dp = drive point
        dp = y
        if dp < 0.2:
            dp = 0.2 #voorkomt te vals worden
        if dp > 0.8:
            dp = 0.8

        # dp kan er gewoon uit
        msg = ['/n_set', id, 'drive_in', drive, "drive_point",dp, "auto",auto,"damping",damping,"noise_ratio",amp,"pan", x,"refl",refl, 'pitch', pitch] #,"refl",0.9 + amp/10];

        self._scServer.sendMsg(*msg)

    def onLost( self, cid ):
        #print "lost"
        #print contour["oid"]
        #print contour;
        #cid = conto
        self._lost.append(cid)
        if not self._scServer:
            return;

        msg = ['/n_set', cid, 'live', 0 ];
        #msg = ['/n_free', cid];
        self._scServer.sendMsg(*msg)

    def atExit( self ):
        print commands.getoutput('killall scsynth')
        print "we die"



#SCCLient
