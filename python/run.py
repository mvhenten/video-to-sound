#!/usr/bin/env python
import cv
import numpy as np


class Main(object):
    index = 0
    canvas = None
    """  """
    def __init__( self, cam="/dev/video0"):
        cv.NamedWindow( "main", 1 );


        self.cam = cv.CaptureFromCAM( 0 )

        cv.SetCaptureProperty( self.cam, cv.CV_CAP_PROP_FRAME_WIDTH, 960.00 )
        cv.SetCaptureProperty( self.cam, cv.CV_CAP_PROP_FRAME_HEIGHT, 720.00 )

        self.canvas = cv.CreateImage( (960, 720), 8, 3 )

        while True:
            self.run()
            key = cv.WaitKey(10)
            if( key % 0x100 == 27 ): break;
        #
        #
        #
        #self.run()
        #cv.SetMouseCallback( "ColorPicker", self.onMouse );
        #
        #self._imageRGB = cv.LoadImage( "ctypes-opencv/hue.png" );
        #self._imageHSV = cv.CreateImage( cv.GetSize( self._imageRGB ), 8, 3 );
        #
        #cv.CvtColor( self._imageRGB, self._imageHSV, cv.CV_BGR2HSV );
        #cv.ShowImage( "ColorPicker", self._imageRGB );
        #
        #print( "Keys:\n"
        #    "    ESC - quit the program\n"
        #    "    b - switch to/from backprojection view\n"
        #    "To initialize tracking, drag across the object with the mouse\n" )

    def grab( self ):
        return cv.QueryFrame( self.cam );

    def onMouse( self, event, mouseX, mouseY, flags, param ):
        if( event == MOUSE_DOWN ):
            pix = self._imageHSV[mouseY, mouseX];
            print "X, Y >> H, S, V:", [mouseX, mouseY], pix;
#            print self._colorImage[100, 100]


    def run( self, size=(320,240)):
        frame = self.grab()
        dest = cv.CreateImage( size, 8, 3 )
        tmp = cv.CreateImage( size, 8, 3 )
        hue = cv.CreateImage( size, 8, 1 )
        mask = cv.CreateImage( size, 8, 1 )
        width, height = size


        cv.Zero(tmp)

        pos = ((0,0),(1,0),(2,0),(0,1),(0,1),(0,1))
        (x, y) = pos[self.index]

        cv.Resize( frame, dest );

        cv.CvtColor( dest,dest, cv.CV_BGR2HSV );

        cv.InRangeS( dest, [0, 150, 30], [181, 256, 256], mask );

        cv.ShowImage('mask', mask )


        cv.ShowImage('hsv1', dest)
                # apply the mask over the input HSV to filter out black
        cv.AddS( dest, [1, 1, 1, 1], tmp, mask);


        cv.ShowImage('hsv', tmp)
                #Split( self._imageTmp, self._hue, self._val, self._sat, None );

        cv.Split( tmp, hue, None, None, None );


        hist = cv.CreateHist([180], cv.CV_HIST_SPARSE, [[0, 180]]);
        cv.CalcHist( [hue], hist );

        bins = np.array([hist.bins[i] for i in range(0,180)])

        print bins[0:10]

        (minVal, maxVal, minPos, maxPos ) = cv.GetMinMaxHistValue( hist )
        print (minVal, maxVal, minPos, maxPos )

        idx = []

        for i in range(minVal+100, maxVal, 100):
            n = np.where( bins < minVal + i )[0]
            edge = np.abs([n[i]-n[i-1] for i in range(0, len(n))])
            a = sum(edge)/len(edge)

            print edge

            print "average: %s" %a;

            print "median: %s" % ((max(edge)-min(edge))/2)
            #print np.avg(edge)
            #print "avg", float(sum(edge[0]))/len(edge[])
            edge = np.where(np.abs(edge) > a )

            l = len(edge[0])

            if l > len(idx):
                print l > 4
                idx = edge[0]
                nbins = n[idx]
            if l < len(idx):
                break

            if l > 4:
                print "l more then 4"
                break;


        print "Found bins", nbins;





            #CalcHist([self._hue, self._val, self._sat], self._histHSV, 0, self._hueMask );


        #cv.Split()


        #cv.KMeans2(hue, 7, mask, (cv.CV_TERMCRIT_ITER, 10, 0))

        #cv.SetImageROI( self.canvas, (x*width, y*height, width, height))

        #cv.Copy( dest, self.canvas )



        #cv.ResetImageROI(self.canvas)

        cv.ShowImage( "main", hue )
        self.index = ( self.index + 1 ) % 6




if __name__=="__main__":
    Main()
