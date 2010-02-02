#!/usr/bin/env python
"""
@title A color-segmented contour tracker
"""
import sys, types, time, operator, thread;

sys.path.append('./lib');

from cv import *
from contourStorage import *
from ColorTracker import *

MOUSE_MOVE  = 0;
MOUSE_DOWN  = 1;
MOUSE_UP    = 4;

MOVIE_PATH  = None;
SC_PORT     = 5720;
LIVE_FEED   = False;

p = NamedWindow( 'paling' );

print "Simple HSV color-contour tracker. Press <ESC> to quit";

try:
    index = sys.argv.index( '--live-feed' ) + 1;
    LIVE_FEED = True;
    print "I: Using live feed as a capture source";
except:
    print "I: Using file as a capture source";


if not LIVE_FEED:
    try:
        index = sys.argv.index( '-f' ) + 1;
        MOVIE_PATH = sys.argv[index];
        print "I: Reading from %s" % MOVIE_PATH;
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
    main = ColorTracker()
    #main.run()

    thread.start_new_thread(main.frameGrabber, ())
    thread.start_new_thread(main.contourTracker, ())

    while True:
        c = cv.WaitKey(10);

        if c == 27 or c == 1048603:
            exit(0);
        elif c != -1:
            print "I: mode change %d" % c;
            main._mode = c;