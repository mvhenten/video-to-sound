from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import time
import cv

class GLWindow(object):
    _window             = None
    _full_screen         = False
    _set_mode_callback  = None
    _image_callback     = None;
    
    def __init__( self, image_callback ):
        self._image_callback = image_callback
        newArgv = glutInit(sys.argv)
    
        glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
        
        self._window = glutCreateWindow("hello")
    
        glutDisplayFunc( self.display )        
        glutKeyboardFunc( self.keyboard )    
        glutIdleFunc(self.idle )

        glutMainLoop()
        
    def get_image( self ):
        return self._image_callback();
        
    def display( self ):        
        glutSetWindow( self._window )
        glClearColor (0.0, 0.0, 1.0, 0.0)
        glClear (GL_COLOR_BUFFER_BIT)
        
        #get out dimenstions
        screen_w = float(glutGet(GLUT_WINDOW_WIDTH))
        screen_h = float(glutGet(GLUT_WINDOW_HEIGHT))
        
        glLoadIdentity();
        glOrtho(0.0, screen_w, 0.0, screen_h, -1.0, 1.0)        
        frame = self.get_image()
        
        #set fullscreen or not    
        if self._full_screen:
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
        
        glFlush ()
        glutSwapBuffers()
    
    def reshape( self, *args ):
        glViewport( *( (0,0)+args) )
        self.display()
    
    def idle( self ):
        glutPostRedisplay()
        
    def _dump_image( self ):
        filename = 'vts_dump_%d.jpg' % time.time()
        cv.SaveImage( filename, self.get_image() )
        
        print 'saving "%s" ' % filename
           
    def keyboard( self, key,x,y):        
        if( key == 'q' ):
            exit();
            
        if( key == 'f' ):
            self._full_screen = not self._full_screen
            
        if( key == 'i' ):
            self._dump_image()
