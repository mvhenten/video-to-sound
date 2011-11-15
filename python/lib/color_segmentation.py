import cv
import numpy as np
from cv_util import Tracker

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
        cv.InRangeS( src, self.config.treshold_hsv, [181, 256, 256], mask );        
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