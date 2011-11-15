import cv
import numpy as np
from SCClientRef import *


class Grabber(object):
    _frame  = None
    _source = None;
    _config = None;
    
    def __init__( self, CONFIG ):
        self._config = CONFIG;

        self._source = cv.CaptureFromCAM( self._config.device )        
        width, height = self._config.size #[float(n) for n in size]

        cv.SetCaptureProperty( self._source, cv.CV_CAP_PROP_FRAME_WIDTH, width )
        cv.SetCaptureProperty( self._source, cv.CV_CAP_PROP_FRAME_HEIGHT, height )
        frame = self.query()
        
    def frame( self ):
        return self._frame;
        
    def query( self ):
        self._frame = cv.QueryFrame( self._source );
        return self._frame;
    
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

