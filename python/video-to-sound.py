#!/usr/bin/env python
"""
@title A color-segmented contour tracker
"""
import sys, types, thread, atexit;
sys.path.append('./lib');
USE_REF = True;

from cv import *
from ColorTracker import *

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

#try:
#    index = sys.argv.index( '-p' ) + 1;
#    SC_PORT = int( sys.argv[index] );
#    print "I: Using port %d" % SC_PORT;
#except:
#    print "I: Using default port %d" % SC_PORT;


if __name__=="__main__":


    sc = SCClient( SYNTH_NAME );

    handlers = {'onNew': [getattr(sc, "onNew")] , 'onChanged': [getattr(sc, "onChanged")],  'onLost': [getattr(sc, "onLost")]  } #dictionary with arrays of handlers to be called for events
    main = ColorTracker( LIVE_FEED, SOURCE, (352, 288), handlers )
    #main.run()

    atexit.register(getattr(sc, "atExit"))

    try:
        thread.start_new_thread(main.frameGrabber, ())
        thread.start_new_thread(main.contourTracker, ())
    except Exception, errtxt:
        print "exception", errtxt

    while True:
        c = WaitKey(10);

        if c == 27 or c == 1048603:
            exit(0);
        elif c != -1:
            print "I: mode change %d" % c;
            main._mode = c;
