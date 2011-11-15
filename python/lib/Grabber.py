import cv

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
