import sys, thread, time
from cv import *;

captureImageCallback = None
processImageCallback = None
hasFrame = False

def videoInLoop():
    global hasFrame

    print "I: Frame grabber started";
    while True:
        if not hasFrame:
            captureImageCallback()
            print "i"
            hasFrame = True;
        else:
            time.sleep(0.01) # minimal sleep time, prevent CPU hogging

def videoOutLoop():
    global hasFrame 
    
    while True:
        if not hasFrame:
            time.sleep( 0.01 );
        else:   
            print "o"
            frame = processImageCallback()
            ShowImage( "Preview", frame );
            hasFrame = False;

def initHGControls(controls):
    NamedWindow( "Controls", 1 );
    
    for param, (min, max, callback) in controls.items(): 
                        CreateTrackbar(param, 'Controls', min, max, callback );
    #SetMouseCallback( "Preview", self.onMouse );


def initHGVideo(captureImageCB,processImageCB,setModeCB):
    global captureImageCallback
    global processImageCallback
  
    captureImageCallback = captureImageCB
    processImageCallback = processImageCB 
    
    # window and trackbar
    NamedWindow( "Preview", 1 );
    
    try:
        thread.start_new_thread(videoInLoop, ())
        thread.start_new_thread(videoOutLoop, ())
    except Exception, errtxt:
        print "exception", errtxt

    while True:
        c = WaitKey(10);

        if c == 27 or c == 1048603:
            exit(0);
        elif c != -1:
            print "I: mode change %d" % c;
            setModeCB(c);