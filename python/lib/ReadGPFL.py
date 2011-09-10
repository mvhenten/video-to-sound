#!/usr/bin/python
from string import *
import re
import sys
import os

def read( filename ):
    fh = open(filename, 'r')
    
    lines = fh.readlines()
    
    lines = lines[3:];
    
    for i in range((len(lines)-1)/2):
        n = i * 2
        name  = strip(strip(lines[n], '#'));
        value,  = re.compile(r'VAL{(\d+)}').findall(lines[n+1])
        print name, value
        
        print "uvcdynctrl -d video1 -s '%s' %s" % (name,value)
        
        os.system("uvcdynctrl -d video1 -s '%s' %s " % (name,value));

if __name__=="__main__":
    _, filename, = sys.argv
    read(filename);
    
    