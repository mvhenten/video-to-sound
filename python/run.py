#!/usr/bin/env python
import cv
import sys
import numpy as np
sys.path.append('./lib')


from Grabber import *
from ColorSegmenter import *
from GLWindow import *

class CONFIG(object):
    CAM_DEVICE = 1
    GPFL_FILE = 'support/wktafel.gpfl'
    HSV_THRESHOLD_START = [0, 80, 30]
    DIMENSIONS  = (960, 720)
    USE_OPENGL  = True

class Main(object):
    grabber = Grabber( CONFIG() )
    segment = ColorSegmenter( CONFIG() )
    
    def run( self ):
        self.grabber.query();
        out = self.segment.segment( self.grabber.frame() );        
        cv.CvtColor( out, out, cv.CV_HSV2BGR );
        
        return out;


if __name__=="__main__":
    config = CONFIG();
    
    if config.USE_OPENGL:
        GLWindow( Main().run );
    else:
        main = Main();
        while True:
            main.run();
            key = cv.WaitKey(40)
            if( key % 0x100 == 27 ): break;
