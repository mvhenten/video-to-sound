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
            key = cv.WaitKey(40)
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
        
    def histEdges(self, bins):
        """ gets boundaries between "top hats" of the histogram. each index is the start of a top """

        m = np.mean(bins);
        idx = np.where(bins > m)[0] # indexes ( bin nr. ) bins that have high values
        dif = np.array([idx[i]-idx[i-1] for i in range(len(idx))]) # difference with previous - gives edges
        
        edges = np.where( dif != 1 ) # find start of continous areas
        idx   = idx[edges] # gives us bin nr. of those areas
        
        return idx


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
        tmp1d = cv.CreateImage( size, 8, 1 )
        width, height = size


        cv.Zero(tmp)

        pos = ((0,0),(1,0),(2,0),(0,1),(0,1),(0,1))
        (x, y) = pos[self.index]

        cv.Resize( frame, dest );
        
        cv.ShowImage('orig', dest )
        cv.Smooth( dest, dest, cv.CV_GAUSSIAN, 9, 9)
        cv.CvtColor( dest,dest, cv.CV_BGR2HSV );
        cv.InRangeS( dest, [0, 100, 10], [181, 256, 256], mask );
        cv.AddS( dest, [1, 1, 1, 1], tmp, mask);
        cv.Split( tmp, hue, None, None, None );
        cv.Zero(tmp)


        hSize = 180

        hist = cv.CreateHist([hSize], cv.CV_HIST_SPARSE, [[0, 180]]);
        cv.CalcHist( [hue], hist );

        bins = np.array([hist.bins[i] for i in range(hSize)])
        
        idx = self.histEdges(bins)
        
        totPix = size[0] * size[1]

       
        for i in range(len(idx)):
            start = idx[i]
            end   = 180
            
            
            start = start+1
            
            if i+1 < len(idx):
                end = idx[i+1]-1
            
            cv.Zero(tmp1d)

            cv.InRangeS( hue, int(start), int(end), mask );
            cv.AddS( hue, 1, tmp1d, mask);
            
            a = cv.Avg( tmp1d, mask )
            a = a[0]
            
            contours = cv.FindContours( tmp1d, cv.CreateMemStorage(), cv.CV_RETR_CCOMP )
            cv.DrawContours(tmp, contours, cv.CV_RGB(255,255,a),cv.CV_RGB(255,255,a),1,-1,1)

        cv.CvtColor( tmp, tmp, cv.CV_HSV2BGR );
        cv.ShowImage( "tmp", tmp );
        
        #cv.KMeans2(hue, 7, mask, (cv.CV_TERMCRIT_ITER, 10, 0))
        #cv.SetImageROI( self.canvas, (x*width, y*height, width, height))
        #cv.Copy( dest, self.canvas )



        #cv.ResetImageROI(self.canvas)

        cv.ShowImage( "main", hue )
        self.index = ( self.index + 1 ) % 6




if __name__=="__main__":
    Main()
