#!/usr/bin/env python
"""
A color tracker using OpenCV

@description
1. Find most common hue ranges in the hue channel using a histogram
2. For each range, create separate image and do some contour tracking
3. Gather information about the contour: size, most prominent hsv values by histogram
4. Remove the processed image from the hue channel to prevent overlapping
@author Matthijs van Henten <matthijs@waag.org>
@license GNU GPL 3.0
@requires OpenCV 2.0 Python API
"""
from cv import *;
from ContourStorage import *;

import time, operator;

class ColorTracker:
    """ color segmented contour tracker """
    _fps       = 25; # adds delay if processing < 1/fps; warns otherwise.
    _mode      = 0;  # variable to switch display types
    _minHSV    = [1, 40, 50];
    _maxHSV    = [180, 256, 255];
    _hasFrame   = False;
    _rawFrame   = None;

    _imageSize  = ( 352, 288 );
    _totalPix   = 0;
    _imageRGB   = None;
    _imageHSV   = None;
    _copyHSV    = None;
    _imgContours   = None;
    _capture    = None;
    _histRanges = None;
#    _maxRanges  = 7; # chosen as premature optimzation; look for 7 distinct ranges, group colors

    _histHue    = None; # hold histogram for hue
    _maxSegments = 6;   # maximum segments for color segmentation
    _histHueBins = 12;  # no. of bins in histogram for color segmentation

    _histBins   = 45;   # no. of bins for histogram per hue/contour ( s,v == 25 )
    _satMin     = 85; # high threshold for webcam input
    _valMin     = 70; # filter out stuff close to grey
    _blurFact   = 11;
    _minContourArea = 0.8;

    _contourStorage = None;
    _handlers = None;

    def __init__( self, useLiveFeed = False, source = '', imageSize = (352, 288), handlers = {} ):
        # window and trackbar
        NamedWindow( "Preview", 1 );
        CreateTrackbar('Sat', 'Preview', self._satMin,
            255, self.setSaturationThreshold );
        CreateTrackbar('Val', 'Preview', self._valMin,
            255, self.setValueThreshold );
        CreateTrackbar('Blur', 'Preview', self._blurFact,
            255, self.setBlur );
        CreateTrackbar('Min-size', 'Preview', int(self._minContourArea*10),
            1000, self.setMinContourArea );


        SetMouseCallback( "Preview", self.onMouse );

        self._imageSize = imageSize;
        self._totalPix  = imageSize[0] * imageSize[1];

        self._imageHSV = CreateImage( self._imageSize, 8, 3 );
        self._imageRGB = CreateImage( self._imageSize, 8, 3 );
        self._imgContours = CreateImage( self._imageSize, 8, 3 );
        self._imageTmp = CreateImage( self._imageSize, 8, 3 );

        self._bin = CreateImage( self._imageSize, IPL_DEPTH_8U, 1 );
        self._mask = CreateImage( self._imageSize, IPL_DEPTH_8U, 1 );
        self._hueMask = CreateImage( self._imageSize, IPL_DEPTH_8U, 1 );
        self._hue = CreateImage( self._imageSize, IPL_DEPTH_8U, 1 );
        self._sat = CreateImage( self._imageSize, IPL_DEPTH_8U, 1 );
        self._val = CreateImage( self._imageSize, IPL_DEPTH_8U, 1 );

        self._histHSV = CreateHist([self._histBins, 25,25], CV_HIST_SPARSE, [[0, 180],[0, 255],[0, 255]]);
        self._histHue = CreateHist([self._histHueBins], CV_HIST_SPARSE, [[0, 180]]);
        self._memStorage = CreateMemStorage();

        self._contourStorage = ContourStorage( self._imageSize, handlers );

        if not useLiveFeed:
            # @todo try to set capture properties here. won't really do.
            self._capture = CaptureFromFile( source );
        else:
            self._capture = CaptureFromCAM( source );

        print "I: Source width:", GetCaptureProperty(self._capture, CV_CAP_PROP_FRAME_WIDTH);
        print "I: Source height:", GetCaptureProperty(self._capture, CV_CAP_PROP_FRAME_HEIGHT);

    def setSaturationThreshold( self, value ):
        print "I: Set min saturation:", value;
        self._satMin = value;

    def setValueThreshold( self, value ):
        print "I: Set min value:", value;
        self._valMin = value;

    def setBlur( self, value ):
        print "I: Blur by:", value;
        self._blurFact = value;

    def setMinContourArea( self, value ):
        value = max( 0.01, float(value)/10 );
        print "I: Min contour area: %.2f%%" % value;
        self._minContourArea = value;

    """ Grab frames in a separate thread. somehow this speeds things up """
    """ @TODO implement python processes instead """
    def frameGrabber( self ):
        print "I: Frame grabber started";
        while True:
            if not self._hasFrame:
                self._rawFrame = QueryFrame( self._capture );

                if not self._rawFrame:
                    # @todo this doesn't always work ( segfault )
                    SetCaptureProperty( self._capture, CV_CAP_PROP_POS_FRAMES, 1 );
                    continue;

                if self._rawFrame.width != self._imageSize[0] or self._rawFrame.height != self._imageSize[1]:
                    Resize( self._rawFrame, self._imageRGB );
                else:
                    #self._imageRGB = Clone( self._rawFrame );#clone segfaults
                    Copy( self._rawFrame, self._imageRGB );

                CvtColor( self._imageRGB, self._imageHSV, CV_BGR2HSV );
                # release memory; countour tracker doesn't need it anymore, prevent leaking
                # cheaper call to alloc in different thread?
                self._memStorage = CreateMemStorage();
                self._hasFrame = True; #allow processing when done.

            time.sleep(0.01); # minimal sleep time, prevent CPU hogging

    """ Mouse callback. Show info about clicked pixel """
    def onMouse( self, event, mouseX, mouseY, flags, param ):
        if( event == 1 ): #mousedown
            pix = self._imageTmp[mouseY, mouseX];
            print "I: MASK: X, Y >> H, S, V:", [mouseX, mouseY], pix;
            pix = self._imageHSV[mouseY, mouseX];
            print "I: HSV: X, Y >> H, S, V:", [mouseX, mouseY], pix;

    """ apply pre-processing and houskeeping """
    def contourTracker( self ):
        while True:
            if not self._hasFrame:
                time.sleep( 0.01 );
            else:
                t = time.time();
                Zero( self._imageTmp );
                Zero( self._imgContours );
#                Set( self._imgContours, [0, 0, 255] );

                blur = max(1, self._blurFact ); # cannot be 0
                Smooth( self._imageHSV, self._imageHSV, CV_BLUR, blur, blur);

                InRangeS( self._imageHSV, [0, self._satMin, self._valMin], [181, 256, 256], self._mask );

                # apply the mask over the input HSV to filter out black
                AddS( self._imageHSV, [1, 1, 1, 1], self._imageTmp, self._mask );
                Split( self._imageTmp, self._hue, self._val, self._sat, None );

                self.findContours();

                t = 0.04 - (time.time() - t);
                if t > 0:
                    time.sleep( t );
                else:
                    print "W: framedrop ", abs(t);

                font    = InitFont(CV_FONT_HERSHEY_PLAIN, 0.8, 1, 0, 1, 4);

                for contour in self._contourStorage._previous:
                    (width, height) =  self._imageSize
                    if 'oid' in contour:
                        txt = "%d: %d/%d/%d" % (contour['oid'], contour['h'], contour['s'], contour['v']);
                        PutText( self._imageRGB, txt, (int(contour['x']), int(contour['y'])), font, CV_RGB(255, 0, 0));
                        PutText( self._imgContours, txt, (int(contour['x']), int(contour['y'])), font, CV_RGB(255, 255, 255));

                #set = self._contourStorage.getContours()
                #removed = self._contourStorage.flush()



                self.showImage();
                self._hasFrame = False;

    def findContours( self ):
        self.findRanges();

        contourStorage = [];

        for start, end in self._histRanges:
            InRangeS( self._hue, max(start,1), end, self._hueMask );

            if CountNonZero( self._hueMask ) < 100:
                continue;

            contours = FindContours( self._hueMask, self._memStorage,
                mode=CV_RETR_EXTERNAL, method=CV_CHAIN_APPROX_SIMPLE, offset=(0,0));

            self.parseContours( contours, contourStorage );
        self._contourStorage.set( contourStorage );

    """ process contours """
    def parseContours( self, contours, contourStorage ):
        while contours:
            c = contours;
            size = abs(ContourArea(c));
            (center, p2, px) = MinAreaRect2( c, self._memStorage );

            if size == 0 or (size*100 / self._totalPix) < self._minContourArea:
                contours = contours.h_next();
                continue;

            Zero( self._hueMask );
            roi = BoundingRect( c, 0 );

            # re-build a mask for histogram
            DrawContours( self._hueMask, c, CV_RGB(255,255,255), -1, -1 );

            images = [self._hue, self._val, self._sat, self._hueMask];

            self.setROI( roi, images )

            CalcHist([self._hue, self._val, self._sat], self._histHSV, 0, self._hueMask );
            (_, _, _, maxBin) = GetMinMaxHistValue( self._histHSV );

            # raise offset and multiply bins to best HSV values
            (h, s, v) = [x + 1 for x in maxBin];
            (hv, sv, vv) = ( 180/self._histBins, 255/25, 255/25);
            values = (h*hv, s*sv, v*vv);

            self.resetROI( images );

            #
            #values = self.getHistValues( self._hueMask, rect );

            # draw contour into the hue channel, removing the detected contour
            # and a small area around it to prevent surrounding contours.
            DrawContours( self._hue, c, 0, 0, -1, 12 );
            DrawContours( self._hue, c, 0, 0, -1, -1 );

            DrawContours( self._imgContours, c, values, values, -1, 12);
            DrawContours( self._imgContours, c, values, values, -1, -1);

            # a blue cross in the middle
            x, y = int(center[0]), int(center[1]);
            Line( self._imgContours, (x-10, y), (x+10, y), CV_RGB(0,0,255), 1, 4);
            Line( self._imgContours, (x, y-10), (x, y+10), CV_RGB(0,0,255), 1, 4);

            contourStorage.append({"size":size,"x":center[0],"y":center[1],"h":values[0],"s":values[1],"v":values[2]});
            contours = contours.h_next();

    def setROI( self, roi, images ):
        for img in images:
            SetImageROI( img, roi );

    def resetROI(self, images ):
        for img in images:
            ResetImageROI( img );

    """ retrieve most prominent HSV values for current hsv channels/roi """
    def getHistValues( self, mask, roi ):
        print "hello world";

    """ show different stages in processing depending on key presses """
    def showImage( self ):
        if self._mode == 104 or self._mode == 1048680:#h
            ShowImage( "Preview", self._hue );
            print "hue";
        elif self._mode == 99 or self._mode == 1048675:#c
            CvtColor( self._imgContours, self._imgContours, CV_HSV2BGR );
            ShowImage( "Preview", self._imgContours );
        elif self._mode == 109 or self._mode == 1048685:#m
            ShowImage( "Preview", self._mask );
        elif self._mode == 115:
            ShowImage( "Preview", self._imageHSV );
        elif self._mode == 114:
            ShowImage( "Preview", self._rawFrame );
        else:
            ShowImage( "Preview", self._imageRGB );

    """ optimize ranges for segmentation """
    def findRanges( self ):
        bins      = self._histHueBins;
        binSize   = float(180)/bins;
        values    = [];
        self._histRanges = [];
        CalcHist([self._hue], self._histHue, 0, self._mask );

        for i in range( bins ):
            value = GetReal1D( self._histHue.bins, i );
            values.append( (value, float(i)) );

        # sort histogram bins in size, slice, and sort by bin-order
        values.sort( reverse = True );
        values = values[:self._maxSegments];
        values.sort( key=operator.itemgetter(1) );

        for i in range( len( values ) ):
            bin  = values[i][1];

            if i > 0:
                start = ((values[i-1][1]+values[i][1])/2)*binSize;
            else:
                start = 0;
            if i < len(values) - 1:
                end = ((values[i+1][1]+values[i][1])/2)*binSize;
            else:
                end = self._histBins * binSize;

            self._histRanges.append((round(start,2), round(end,2)));


#colorTracker
