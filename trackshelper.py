"""
Module with various helper functions for track analysis:
time parsing, distance computation, reading from a file, and summarizing tracks.
DO NOT MAKE CHANGES TO THIS FILE.
"""

__author__ = 'Lyn Turbak, Sravana Reddy'

from math import radians, sqrt, sin, cos, atan2
from datetime import datetime

def linesFromFile(filename):
    '''Returns a list of all the lines from a file with the given filename.
       In each line, the terminating newline has been removed.'''
    inputFile = open(filename, 'r')
    strippedLines = [line.strip() for line in inputFile.readlines()]                        
    inputFile.close()
    return strippedLines

def twoPointsDistance(entrya, entryb):
    '''Returns the distance in miles between the lat/lon coordinates of two 
    track entries using the Haversine formula. For details on the formula used
    below, see http://www.movable-type.co.uk/scripts/latlong.html'''
    R = 3959   # radius of the earth in miles
    phi1 = radians(entrya[2]) # entrya[2] is lat1 in degrees
    lam1 = radians(entrya[3]) # entrya[3] is lon1 in degrees
    phi2 = radians(entryb[2]) # entryb[2] is lat2 in degrees
    lam2 = radians(entryb[3]) # entryb[3] is lon2 in degrees
    phiDiff = phi2 - phi1
    lamDiff = lam2 - lam1 
    a = sin(phiDiff/2.0)**2 + cos(phi1) * cos(phi2) * sin(lamDiff/2.0)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def translateTime(timeString):
    '''Convert string representation of time (09/25/2015 06:23:01 PM)
    to a datetime object for easy arithmetic'''
    d, t, ampm = timeString.split()   #d = date, t = time, ampm = is it am or pm
    hour, minute, sec = [int(x) for x in t.split(':')]
    if ampm == 'PM':
        hour += 12
    month, day, year = [int(x) for x in d.split('/')]
    return datetime(year, month, day, hour, minute, sec)

def diffTime(timeString1, timeString2):
    '''Number of seconds passed between the times timeString1 and timeString2,
       where times have the format MM/DD/YYYY HH:MM:SS AMorPM'''
    datetime1 = translateTime(timeString1)
    datetime2 = translateTime(timeString2)
    return (datetime2 - datetime1).total_seconds()


    
