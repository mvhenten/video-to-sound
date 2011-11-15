#!/usr/bin/python
""" simple utilit to read gpfl files and execute uvcdynctrl """
from string import *
import re
import sys
import os

def apply( filename, device ):
    settings = parse(read(filename))
    
    for ( name, value ) in settings:
        set( device, name, value )
                

def read( filename ):
    fh = open(filename, 'r')
    lines = fh.readlines()    
    lines = lines[3:];
    
    return lines;
    
def parse( lines ):
    collect = []
    for i in range(0, len(lines), 2):
        name    = strip(strip(lines[i], '#'));
        value,  = re.compile(r'VAL{(\d+)}').findall(lines[i+1])
        collect.append((name,value))

    return collect

def set( device, name, value ):
    cmd = "uvcdynctrl -d video%d -s '%s' %s" % (device,name,value)
    os.system( cmd )
    print cmd    
    
