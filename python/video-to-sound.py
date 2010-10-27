#!/usr/bin/env python
"""
@title A color-segmented contour tracker
"""
import sys, types, thread, atexit;
sys.path.append('./lib');
USE_REF = True;

SCSYNTH_PATH = '/usr/bin';

from cv import *
from ColorTracker import *
import glSupport
import hgSupport

if USE_REF:
    from SCClientRef import *;
else:
    from SCClient import *;

MOUSE_MOVE  = 0;
MOUSE_DOWN  = 1;
MOUSE_UP    = 4;

SOURCE  = None;
SC_PORT     = 5720;
LIVE_FEED   = False;
SYNTH_NAME  = 'default';

(HIGHGUI,GLUT) = range(0,2)
OUTPUT = GLUT

print "Simple HSV color-contour tracker. Press <ESC> to quit";

try:
    index = sys.argv.index( '--synth-name' ) + 1;
    SYNTH_NAME = sys.argv[index];
    print "I: Playing synth %s" % SYNTH_NAME
except:
    print "I: No synth name! use --synth-name <name>";
    exit(1);

try:
    index = sys.argv.index( '--live-feed' ) + 1;
    LIVE_FEED = True;

    try:
        SOURCE = int(sys.argv[index]);
    except:
        SOURCE = 0;

    print "I: Using live feed %d as a capture source" % SOURCE;
except:
    print "I: Using file as a capture source";


if not LIVE_FEED:
    try:
        index = sys.argv.index( '-f' ) + 1;
        SOURCE = sys.argv[index];
        print "I: Reading from %s" % SOURCE;
    except:
        #$IndexError or ValueError:
        print "E: No file given; use -f </path/to/movie.avi> or --live-feed for camera";
        exit(1);

        
if __name__=="__main__":

    #super collider client will start, stop and control synths
    sc = SCClient( SYNTH_NAME, SCSYNTH_PATH );

    #dictionary with arrays of handlers to be called for events of tracked objects
    handlers = {    'onNew': [getattr(sc, "onNew")] , 
                    'onChanged': [getattr(sc, "onChanged")],  
                    'onLost': [getattr(sc, "onLost")]  }  
    
    main = ColorTracker( LIVE_FEED, SOURCE, (352, 288), handlers )
    
    atexit.register(getattr(sc, "atExit"))
	
    if OUTPUT == GLUT: #using GLUT for output
        #start the main loop for outputing video using glut
        glSupport.initGL(getattr(main, "captureImage"),
                         getattr(main, "getProcessedImage"),
                         getattr(main, "setMode"));
    elif OUTPUT == HIGHGUI:
        #controls: slider label, minimum slider value, maximum slider value, callback function
        controls = {'saturation threshold' : (85,255,getattr(main, "setSaturationThreshold")),
                    'value threshold' : (70,255,getattr(main, "setValueThreshold")),
                    'blur' : (11,255,getattr(main, "setBlur")),
                    'minimum contour' : (8,1000,getattr(main, "setMinContourArea"))} #= times 10

        #make Highgui create the sliders
        hgSupport.initHGControls(controls);
        #start the main loop for outputing video using the openCV highgui 
        hgSupport.initHGVideo(getattr(main, "captureImage"),
                              getattr(main, "getProcessedImage"),
                              getattr(main, "setMode"));
