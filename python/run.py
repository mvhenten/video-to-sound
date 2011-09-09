#!/usr/bin/env python
import cv
import sys
import numpy as np
sys.path.append('./lib')
from SCClientRef import *
import ReadGPFL


def main_app():
    grabber   = Grabber();
    segment  = ColorSegmenter(); 

    while True:
        grabber.query();
        
        out = segment.segment( grabber.frame() );

        
        cv.CvtColor( out, out, cv.CV_HSV2BGR );

        cv.ShowImage( "test", out );

        
        key = cv.WaitKey(40)
        if( key % 0x100 == 27 ): break;




class CONFIG(object):
    CAM_DEVICE = 1
    GPFL_FILE = 'support/wktafel.gpfl'
    HSV_THRESHOLD_START = [0, 80, 30]
    
class Grabber(object):
    _frame  = None
    _source = None;
    
    def __init__( self, size =(800,600) ):
        self.config = CONFIG();
        self._source = cv.CaptureFromCAM( self.config.CAM_DEVICE )
        
        width, height = size #[float(n) for n in size]

        cv.SetCaptureProperty( self._source, cv.CV_CAP_PROP_FRAME_WIDTH, width )
        cv.SetCaptureProperty( self._source, cv.CV_CAP_PROP_FRAME_HEIGHT, height )
        frame = self.query()

        ReadGPFL.read( self.config.GPFL_FILE );
        
    def frame( self ):
        return self._frame;
        
    def query( self ):
        self._frame = cv.QueryFrame( self._source );
        return self._frame;
        
class ColorSegmenter( object ):
    tracker = None;

    min_contour_size = 2000;
    max_histogram_size = 180;
    
    def __init__( self ):
        self.config = CONFIG();
        
        
    def get_tracker( self ):
        if self.tracker == None:
            self.tracker = Tracker();
            
        return self.tracker;

    def get_hist_edges(self, bins):
        """ gets boundaries between "top hats" of the histogram. each index is the start of a top """

        m = np.mean(bins);
        idx = np.where(bins > m)[0] # indexes ( bin nr. ) bins that have high values
        dif = np.array([idx[i]-idx[i-1] for i in range(len(idx))]) # difference with previous - gives edges
        
        edges = np.where( dif != 1 ) # find start of continous areas
        idx   = idx[edges] # gives us bin nr. of those areas
        
        return idx
    
    def find_color_bounds( self, hue ):
        """ retrieve hue boundaries for most prevailing colors of the image """
        hSize = self.max_histogram_size;

        hist = cv.CreateHist([hSize], cv.CV_HIST_SPARSE, [[0, 180]]);
        cv.CalcHist( [hue], hist );

        bins = np.array([hist.bins[i] for i in range(hSize)])
        
        idx = self.get_hist_edges( bins )
        
        return idx
        
    def pre_process_source( self, cv_source_image ):
        src     = cv.CloneImage( cv_source_image );

        size = ( src.width, src.height );
        hue     = cv.CreateImage( size, 8, 1 )
        tmp     = cv.CreateImage( size, 8, 3 )
        mask    = cv.CreateImage( size, 8, 1 )

        cv.Zero(tmp)

        cv.Smooth( src, src, cv.CV_GAUSSIAN, 13, 13 )
        cv.CvtColor( src,src, cv.CV_BGR2HSV );
        
        #rough thresholding to filter out noisie
        cv.InRangeS( src, self.config.HSV_THRESHOLD_START, [181, 256, 256], mask );

        cv.AddS( cv_source_image, [1, 1, 1, 1], tmp, mask);
        cv.Split( tmp, hue, None, None, None );
        
        return hue;
    
    def extract_hue_channel( self, cv_hue_image, hue_start, hue_end ):
        size = ( cv_hue_image.width, cv_hue_image.height );
        tmp     = cv.CreateImage( size, 8, 1 )
        mask    = cv.CreateImage( size, 8, 1 )

        cv.Zero(tmp)

        cv.InRangeS( cv_hue_image, int(hue_start), int(hue_end), mask );
        # copy pixels in range from hue
        cv.AddS( cv_hue_image, 1, tmp, mask);

        avg_hue = cv.Avg( tmp, mask )
        avg_hue = avg_hue[0]

        return tmp, avg_hue;
        
        
    def segment( self, cv_source_image ):
        self.get_tracker().flush()
        
        hue    = self.pre_process_source( cv_source_image );        

        size   = ( hue.width, hue.height );
        cv_out = cv.CreateImage( size, 8, 3 )

        idx    = self.find_color_bounds( hue );
        
        print idx;
        
        
        totPix = size[0] * size[1]
       
        for i in range( len(idx) ):
            start = idx[i]
            end   = self.max_histogram_size;
            
            start = start + 1
            
            if i+1 < len(idx):
                end = idx[i+1]-1

            
            ( tmp1d, avg_hue ) = self.extract_hue_channel( hue, start, end );

            contours = cv.FindContours( tmp1d, cv.CreateMemStorage(), cv.CV_RETR_CCOMP )
            
            while contours:
                cSize = abs(cv.ContourArea(contours));
                
                if cSize < self.min_contour_size:
                    contours = contours.h_next()
                    continue
                
                (_, center, radius) = cv.MinEnclosingCircle( contours )
                center = (int(center[0]), int(center[1]));
                
                
                id = self.get_tracker().add( center, radius, (start+end)/2, size )
                
                cv.DrawContours( cv_out, contours, cv.CV_RGB(255,255,avg_hue),cv.CV_RGB(255,255,avg_hue),1,-1,1)
                contours = contours.h_next()
                
        return cv_out;
        
        

class Main(object):
    index = 0
    canvas = None
    min_contour_size = 2000;
    max_histogram_size = 180;
    
    """  """
    def __init__( self, size = (960,720)):        
        self.config = CONFIG();


        ReadGPFL.read( self.config.GPFL_FILE );
        self.cam = cv.CaptureFromCAM( self.config.CAM_DEVICE )
        
        width, height = size #[float(n) for n in size]

        cv.SetCaptureProperty( self.cam, cv.CV_CAP_PROP_FRAME_WIDTH, width )
        cv.SetCaptureProperty( self.cam, cv.CV_CAP_PROP_FRAME_HEIGHT, height )
        frame = self.grab()

        ReadGPFL.read( self.config.GPFL_FILE );


        self.canvas = cv.CreateImage( (width, height), 8, 3 )
        
        self.tracker = Tracker()

        while True:
            self.run( size );
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

    def run( self, size):
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
        
        #cv.ShowImage('orig', dest )
        cv.Smooth( dest, dest, cv.CV_GAUSSIAN, 13, 13)
        cv.CvtColor( dest,dest, cv.CV_BGR2HSV );
        
        cv.InRangeS( dest, self.config.HSV_THRESHOLD_START, [181, 256, 256], mask );
        cv.AddS( dest, [1, 1, 1, 1], tmp, mask);
        cv.Split( tmp, hue, None, None, None );
        cv.Zero(tmp)

        self.tracker.flush()

        hSize = self.max_histogram_size;

        hist = cv.CreateHist([hSize], cv.CV_HIST_SPARSE, [[0, 180]]);
        cv.CalcHist( [hue], hist );

        bins = np.array([hist.bins[i] for i in range(hSize)])
        
        idx = self.histEdges(bins)
        
        totPix = size[0] * size[1]
        font    = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 0.8, 1, 0, 1, 4);
        

        print idx;
       
        for i in range(len(idx)):
            start = idx[i]
            end   = self.max_histogram_size;
            
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
                
                if cSize < self.min_contour_size:
                    contours = contours.h_next()
                    continue
                
                #print i, size
                
                (_, center, radius) = cv.MinEnclosingCircle( contours )
                
                
                center = (int(center[0]), int(center[1]));
                
                
                id = self.tracker.add( center, radius, a, size )
                
                #cv.Circle( tmp, center, int(radius), cv.CV_RGB(255,255,int(a)), 1 );
                #cv.PutText( hue, "%d:%d"%(id, a), center, font, cv.CV_RGB(255,255,255));
                cv.DrawContours(tmp, contours, cv.CV_RGB(255,255,a),cv.CV_RGB(255,255,a),1,-1,1)
                contours = contours.h_next()

        cv.CvtColor( tmp, tmp, cv.CV_HSV2BGR );
        cv.ShowImage( "tmp", tmp );

        #cv.ShowImage( "main", hue )
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

        width, height = [float(n) for n in imgSize]
        #amp = radius/width
        
        #print self.tracked
        
        if len(self.tracked):        
            tracked = np.array(self.tracked[:]);
            dif = tracked[:,0:2] - (x/float(width),y/float(height))
            
            a,b = dif[:,0], dif[:,1]
            
            dists = np.sqrt((a*a)+(b*b))            
            idx = np.where(dists<0.5)
            
            
            if len(idx[0]):
                match = tracked[idx]
                
                dists = dists[idx[0]]
                nidx  = np.argsort(dists)
                    
                sidx = idx[0][nidx]                
                obj = self.tracked.pop(sidx[0])
                #if len(obj):
                #    print obj
        
        if len(obj) > 0:
            obj = (x/float(width), y/float(height), radius/float(width), hue, obj[4])
            
            #print "%d: %f, %f" % ( obj[4], x/float(width), y/height);
            
            self.client.onChanged( obj )

        else:
            id = self.id()
            obj = (x/float(width), y/float(height), radius/float(width), hue, id)
            #(185.5, 67.0, 30.869943618774414, 47.443262411347519, 15)
            
            # id, amp, pan, hue, sat, val
            
            self.client.onNew( obj )
            
        #print obj
            
        self.new.append(obj)
        return obj[4]
        
        
    




if __name__=="__main__":
    Main();
