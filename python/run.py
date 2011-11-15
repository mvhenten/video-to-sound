#!/usr/bin/env python
"""  video to sound - convert images to sound using OpenCV and SuperCollider """
import cv
import sys
import numpy as np
import argparse

sys.path.append('./lib')


from Grabber import *
from ColorSegmenter import *
from GLWindow import *

parser = argparse.ArgumentParser(description='run video to sound',)

parser.add_argument('-d', '--device', type=int,default=0,
    help='Video4linux device for capturing')
parser.add_argument('-s', '--size', type=int, nargs=2,
    help='Image size for capturing',  default=[960,720] )
parser.add_argument('-p', '--profile',
    help='Guvc profile to calibrate with', default='support/default.gpfl')
parser.add_argument('-g', '--use-opengl', type=bool,
    help='Use opengl for displaying', default=True )
parser.add_argument('-t', '--treshold-hsv', type=int, nargs=3,
    help='Threshold values for HSV [0,80,30]', default=[0,80,30])

ARGS = parser.parse_args()

for (key, value) in vars(ARGS).items():
    print 'I: "%s" is set to "%s"' % (key, value )


class Buf(object):
    _frames = []
    _length = 25
    _index  = 0
    
    def __init__( self, len=25 ):
        self._lenght = 25
    
    def push_frame( self, cv_image ):
        idx = self._index % 25
        
        if len(self._frames) >= self._length:
            retval = self._frames[idx]
            self._frames[idx] = cv_image
            
        else:
            self._frames.append(cv_image)
            retval = cv_image
        
        self._index+=1
        return retval
    

class Main(object):
    grabber = Grabber( ARGS )
    segment = ColorSegmenter( ARGS )
    
    frame_stack = Buf();

    def __init__( self, args ):
        ReadGPFL.apply( args.profile, args.device );
        
    
    def run( self ):
        self.grabber.query();
        
        out = self.segment.segment( self.grabber.frame() );        
        cv.CvtColor( out, out, cv.CV_HSV2BGR );


        #out2 = self.frame_stack.push_frame(out);
        #cv.ShowImage( 'buf', out2);
        
        return out;
    
    


if __name__=="__main__":
    
    if ARGS.use_opengl:
        GLWindow( Main( ARGS ).run );
    else:
        main = Main( ARGS );
        while True:
            cv.ShowImage( 'main', main.run());
            key = cv.WaitKey(40)
            if( key % 0x100 == 27 ): break;
