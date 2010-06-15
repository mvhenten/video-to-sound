from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import time

window = None
#frame_grabber = None
fullscreen = False
captureImageCallback = None
processImageCallback = None
setModeCallback = None
prev_time = 0;

#class t:
#    def __init__:
        

def display():
    global fullscreen
    global window
    glutSetWindow(window);
    glClearColor (0.0, 0.0, 1.0, 0.0)
    glClear (GL_COLOR_BUFFER_BIT)
    
    #get out dimenstions
    screen_w = float(glutGet(GLUT_WINDOW_WIDTH))
    screen_h = float(glutGet(GLUT_WINDOW_HEIGHT))
    
    #dit is nodig
    glLoadIdentity();
    glOrtho(0.0, screen_w, 0.0, screen_h, -1.0, 1.0)
    
    #grab frame and processs    
    captureImageCallback()
    #process the frame and retrieve it
    frame = processImageCallback()
    
    
    global prev_time
    t = time.time();
    if (prev_time != 0):
        fps = 1 / (t - prev_time)
        print fps
    prev_time = t

    #set fullscreen or not    
    if fullscreen:
            glutFullScreen()
    else:
            glutReshapeWindow(frame.width,frame.height)

    #scale the frame    
    scale_w = screen_w/float(frame.width)
    scale_h = screen_h/float(frame.height)
    glPixelZoom(scale_w, -scale_h);
    
    #paint op de juist plek
    glRasterPos2d(0,frame.height);
    glBitmap (0, 0, 0, 0, 0, screen_h - frame.height , 0); #move the bitmap
    if frame.nChannels==1:
            glDrawPixels(frame.width, frame.height, GL_LUMINANCE, GL_UNSIGNED_BYTE, frame.tostring())
    else:
            glDrawPixels(frame.width, frame.height, GL_BGR, GL_UNSIGNED_BYTE, frame.tostring())
    
    # #draw the teapot
    # matrix = glGetDouble( GL_PROJECTION_MATRIX )
    # glLoadMatrixd( matrix )
    # glutWireTeapot( .2 )
    glFlush ()
    glutSwapBuffers()

def reshape( *args ):
    glViewport( *( (0,0)+args) )
    display()

def idle():
    glutPostRedisplay()
       
def keyboard(key,x,y):
    if("f" == key):
            global fullscreen
            fullscreen = not fullscreen
            print fullscreen
    
    setModeCallback(ord(key))
    
    print "pressed:", key

def initGL(captureImageCB,processImageCB,setModeCB):
    global captureImageCallback
    global processImageCallback
    global setModeCallback
    global window 
    captureImageCallback = captureImageCB
    processImageCallback = processImageCB
    setModeCallback = setModeCB    

    newArgv = glutInit(sys.argv)
    print 'newArguments', newArgv
    glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
    glutInitWindowSize(640,480)
    glutInitWindowPosition(100, 100)
    
    window = glutCreateWindow("hello")
    print 'window', repr(window)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    #glutMouseFunc(printFunction( 'Mouse' ))
    #glutEntryFunc(printFunction( 'Entry' ))
    glutKeyboardFunc( keyboard )
    #glutKeyboardUpFunc( printFunction( 'KeyboardUp' ))
    #glutMotionFunc( printFunction( 'Motion' ))
    #glutPassiveMotionFunc( printFunction( 'PassiveMotion' ))
    #glutVisibilityFunc( printFunction( 'Visibility' ))
    #glutWindowStatusFunc( printFunction( 'WindowStatus' ))
    #glutSpecialFunc( printFunction( 'Special' ))
    #glutSpecialUpFunc( printFunction( 'SpecialUp' ))
    #glutTimerFunc( 1000, ontimer, 23 )
    glutIdleFunc( idle )
    glutMainLoop()