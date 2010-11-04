#!/usr/bin/env python
import cv
import sys
import numpy as np
sys.path.append('./lib');
from SCClientRef import *;

class Main(object):
    index = 0
    canvas = None
    """  """
    def __init__( self, cam=1):
        cv.NamedWindow( "main", 1 );


        self.cam = cv.CaptureFromCAM( cam )

        cv.SetCaptureProperty( self.cam, cv.CV_CAP_PROP_FRAME_WIDTH, 640.00 )
        cv.SetCaptureProperty( self.cam, cv.CV_CAP_PROP_FRAME_HEIGHT, 480.00 )

        self.canvas = cv.CreateImage( (960, 720), 8, 3 )
        
        self.tracker = Tracker()

        while True:
            self.run()
            key = cv.WaitKey(40)
            if( key % 0x100 == 27 ): break;

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
        cv.InRangeS( dest, [0, 130, 10], [181, 256, 256], mask );
        cv.AddS( dest, [1, 1, 1, 1], tmp, mask);
        cv.Split( tmp, hue, None, None, None );
        cv.Zero(tmp)

        self.tracker.flush()

        hSize = 180

        hist = cv.CreateHist([hSize], cv.CV_HIST_SPARSE, [[0, 180]]);
        cv.CalcHist( [hue], hist );

        bins = np.array([hist.bins[i] for i in range(hSize)])
        
        idx = self.histEdges(bins)
        
        totPix = size[0] * size[1]
        font    = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 0.8, 1, 0, 1, 4);
        

       
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
            
            while contours:
                cSize = abs(cv.ContourArea(contours));
                
                if cSize < 75:
                    contours = contours.h_next()
                    continue
                
                #print i, size
                
                (_, center, radius) = cv.MinEnclosingCircle( contours )
                
                
                id = self.tracker.add( center, radius, a, size )
                
                #cv.Circle( tmp, center, int(radius), cv.CV_RGB(255,255,int(a)), 1 );
                cv.PutText( hue, "%d:%d"%(id, a), center, font, cv.CV_RGB(255,255,255));
                cv.DrawContours(tmp, contours, cv.CV_RGB(255,255,a),cv.CV_RGB(255,255,a),1,-1,1)
                contours = contours.h_next()

        cv.CvtColor( tmp, tmp, cv.CV_HSV2BGR );
        cv.ShowImage( "tmp", tmp );

        cv.ShowImage( "main", hue )
        self.index = ( self.index + 1 ) % 6

class Tracker(object):
    #tracked = []
    #new     = []
    client  = None;
        
    count = 0;
    
    def __init__( self ):
        self.client = SCClient()
        self.tracked = []
        self.new     = []
        self.old    = []
    
    def id( self ):
        self.count += 1
        return self.count
    
    def flush( self ):
        self.tracked = self.new[:]
        
        if len(self.old):
            id1 = [o[4] for o in self.old]
            id2 = [o[4] for o in self.new]
            
            for id in id1:
                if id not in id2:
                    self.client.onLost(id)            
            #flush = [id for id in id1 if id not in id2]
            

        self.old = self.new[:]
        self.new = []
    
    def add( self, center, radius, hue, imgSize ):
        x, y = center
        obj = []

        width, height = imgSize
        #amp = radius/width
        
        #print self.tracked
        
        if len(self.tracked):        
            tracked = np.array(self.tracked[:]);
            dif = tracked[:,0:2] - (x/width,y/height)
            
            a,b = dif[:,0], dif[:,1]
            
            dists = np.sqrt((a*a)+(b*b))            
            idx = np.where(dists<0.3)
            
            
            if len(idx[0]):
                match = tracked[idx]
                
                dists = dists[idx[0]]
                nidx  = np.argsort(dists)
                    
                sidx = idx[0][nidx]                
                obj = self.tracked.pop(sidx[0])
                #if len(obj):
                #    print obj
        
        if len(obj) > 0:
            obj = (x/width, y/height, radius/width, hue, obj[4])
            self.client.onChanged( obj )
        else:
            id = self.id()
            obj = (x/width,y/height, radius/width, hue, id)
            #(185.5, 67.0, 30.869943618774414, 47.443262411347519, 15)
            
            # id, amp, pan, hue, sat, val
            
            self.client.onNew( obj )
            
        #print obj
            
        self.new.append(obj)
        return obj[4]
        
        
    




if __name__=="__main__":
    Main()
