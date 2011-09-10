import cv
import numpy as np
from SCClientRef import *


class ColorSegmenter( object ):
    tracker = None;

    min_contour_size   = 2000
    max_histogram_size = 180
    
    def __init__( self, CONFIG ):
        self.config = CONFIG;
        
        
    def get_tracker( self ):
        if self.tracker == None:
            self.tracker = Tracker();
            
        return self.tracker;

    def get_hist_edges(self, bins):
        """ gets boundaries between "top hats" of the histogram. each index is the start of a top """

        m = np.mean(bins);
        idx = np.where(bins > m)[0] # indexes ( bin nr. ) bins that have high values
        dif = np.array([idx[i]-idx[i-1] for i in range(len(idx))]) # difference with previous - gives edges
        
        edges = np.where( dif > 1 ) # find start of continous areas
        idx   = idx[edges] # gives us bin nr. of those areas
        
        return idx
    
    def find_color_bounds( self, hue ):
        """ retrieve hue boundaries for most prevailing colors of the image """
        hSize = self.max_histogram_size;

        hist = cv.CreateHist([hSize], cv.CV_HIST_SPARSE, [[0, 180]]);
        cv.CalcHist( [hue], hist );

        bins = np.array([hist.bins[i] for i in range(hSize)])
        
        start_pt = list(self.get_hist_edges( bins ))
        end_pt   = start_pt[1:]
        end_pt.append(self.max_histogram_size);
        
        return zip( start_pt, end_pt );
                
    def pre_process_source( self, cv_source_image ):
        size = ( cv_source_image.width, cv_source_image.height );
        src     = cv.CloneImage( cv_source_image );
        
        hue     = cv.CreateImage( size, 8, 1 )
        mask    = cv.CreateImage( size, 8, 1 )
        tmp     = cv.CreateImage( size, 8, 3 )

        cv.Zero(tmp)
        cv.Resize( cv_source_image, src );
        
        cv.Smooth( src, src, cv.CV_GAUSSIAN, 13, 13 )
        cv.CvtColor( src,src, cv.CV_BGR2HSV );
        
        #rough thresholding to filter out noisie
        cv.InRangeS( src, self.config.HSV_THRESHOLD_START, [181, 256, 256], mask );        
        cv.AddS( src, [1, 1, 1, 1], tmp, mask);
        cv.Split( tmp, hue, None, None, None );
        
        return hue;
    
    def extract_hue_channel( self, cv_hue_image, bound_range ):
        size = ( cv_hue_image.width, cv_hue_image.height );
        tmp     = cv.CreateImage( size, 8, 1 )
        mask    = cv.CreateImage( size, 8, 1 )
        
        start, end = bound_range;

        cv.Zero(tmp)

        cv.InRangeS( cv_hue_image, int(start), int(end), mask );
        # copy pixels in range from hue
        cv.AddS( cv_hue_image, 1, tmp, mask);

        avg_hue = cv.Avg( tmp, mask )
        avg_hue = avg_hue[0]

        return tmp, avg_hue;
        
        
    def segment( self, cv_source_image ):
        self.get_tracker().flush()
        
        hue    = self.pre_process_source( cv_source_image );        

        size   = ( hue.width, hue.height )
        cv_out = cv.CreateImage( size, 8, 3 )
        cv.Zero(cv_out);
        bounds    = self.find_color_bounds( hue )
        
        for bound in bounds:
            
            ( tmp1d, avg_hue ) = self.extract_hue_channel( hue, bound );

            contours = cv.FindContours( tmp1d, cv.CreateMemStorage(), cv.CV_RETR_CCOMP )
            
            while contours:
                cSize = abs(cv.ContourArea(contours));
                
                if cSize < self.min_contour_size:
                    contours = contours.h_next()
                    continue
                
                (_, center, radius) = cv.MinEnclosingCircle( contours )
                
                center = (int(center[0]), int(center[1]));                
                id = self.get_tracker().add( center, radius, avg_hue, size )
                
                cv.DrawContours( cv_out, contours, cv.CV_RGB(255,255,avg_hue),cv.CV_RGB(255,255,avg_hue),1,-1,1)
                
                contours = contours.h_next()
                
                #font    = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 0.8, 1, 0, 1, 4);
                #cv.Circle( cv_out, (x,y), int(radius), cv.CV_RGB(255,255,int(avg_hue)), 1 );
                #cv.PutText( cv_out, "%d:%d"%(id, avg_hue), (x,y), font, cv.CV_RGB(255,255,150));
                

                
        return cv_out;

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
