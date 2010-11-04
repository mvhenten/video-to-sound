"""
Supercollider client placeholder
"""
import scsynth
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

    def __init__( self, synthName = 'color' ):
        print "I: SCLient says Hello World!";

        self._synthName = synthName;

        try:
            
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

    def onNew( self, contour ):
        if not self._scServer:
            return;

        id, amp, pan, hue, sat, val = contour["oid"], contour["size"], contour["x"], contour["hue"], contour["sat"], contour["val"];
        pitch = hue * 100 + 100
        # if amp < 0.1:
        # 	        pitch = pitch * 2 #octave
                
        amp = 0.1 + (amp * 0.8) #minimal amp needed


        #msg = ['/s_new', self._synthName, id, 0, self._gid, 'hue', hue, 'amp', amp, 'pan', pan, 'sat', sat, 'val', val];
        msg = ['/s_new', 'pluckbow', id, 0 , 0, "drive_in", 0, "noise_ratio",amp,"driver_smoothing", 0.995, "damping", 0.95, "refl", 0.999, "pitch_in", pitch, "pan", pan ]
        self._scServer.sendMsg(*msg)

    def onChanged( self, contour ):
        if not self._scServer:
            return

			
        id, amp, pan, hue, sat, val = contour["oid"], contour["size"], contour["x"], contour["hue"], contour["sat"], contour["val"];
        damping = 0.9 - (contour["y"] / 10)
        refl = 0.999# - (contour["y"] / 100)
        amp = 0.1 + (amp * 0.8)
        #refl = 0.9 + (contour["y"] / 10)

        msg = ['/n_set', id, 'drive_in', pan, "damping",damping,"noise_ratio",amp,"pan", pan,"refl",refl] #,"refl",0.9 + amp/10];

        self._scServer.sendMsg(*msg)

    def onLost( self, contour ):
        #print "lost"
        #print contour["oid"]
        #print contour;
        cid = contour["oid"]
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
