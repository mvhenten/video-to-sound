#!/usr/bin/env python

import cv

MOUSE_MOVE  = 0;
MOUSE_DOWN  = 1;
MOUSE_UP    = 4;

class ColorPicker:
    """ simple colorpicker to see HSV values from openCV """
    _imageRGB = None;
    _imageHSV = None;

    def __init__( self ):
        cv.NamedWindow( "ColorPicker", 1 );
        cv.SetMouseCallback( "ColorPicker", self.onMouse );

        self._imageRGB = cv.LoadImage( "ctypes-opencv/hue.png" );
        self._imageHSV = cv.CreateImage( cv.GetSize( self._imageRGB ), 8, 3 );

        cv.CvtColor( self._imageRGB, self._imageHSV, cv.CV_BGR2HSV );
        cv.ShowImage( "ColorPicker", self._imageRGB );

        print( "Keys:\n"
            "    ESC - quit the program\n"
            "    b - switch to/from backprojection view\n"
            "To initialize tracking, drag across the object with the mouse\n" )

    def onMouse( self, event, mouseX, mouseY, flags, param ):
        if( event == MOUSE_DOWN ):
            pix = self._imageHSV[mouseY, mouseX];
            print "X, Y >> H, S, V:", [mouseX, mouseY], pix;
#            print self._colorImage[100, 100]

    def run( self ):
        while True:
            c = cv.WaitKey(10)
            if c == 27:
                break
#//colorPicker

if __name__=="__main__":
    demo = ColorPicker()
    demo.run()
