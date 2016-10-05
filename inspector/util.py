# util.py
# -------
# This autograder was developed by Sravana Reddy (sravana.reddy@wellesley.edu)
# and Daniela Kreimerman (dkreimer@wellesley.edu), built upon the framework
# provided by the Berkeley AI autograding scripts. See below.
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import sys
import inspect
import heapq, random
import jinja2
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.token import Text, Error
import re

class MyPythonLexer(PythonLexer):
    """Adds syntaxerror highlighting at offsets"""
    def __init__(self, offset, delimiter='|'):
        PythonLexer.__init__(self)
        self.offset = offset
        self.delimiter = delimiter  #TODO: use this to escape highlighting when desired

    def get_tokens_unprocessed(self, text):
        for index, token, value in PythonLexer.get_tokens_unprocessed(self, text):
            if index==self.offset-1:  # need to shift by 1
                yield index, Error, value
            else:
                yield index, token, value

def codeHighlight(message, offset = -1):
    return highlight(message, MyPythonLexer(offset), HtmlFormatter())

def correctnessColor(pt, mx):
    if mx == 0:
        return 'info'
    elif pt == mx:
        return 'success'
    elif pt == 0:
        return 'danger'
    return 'warning'

def fillHTMLTemplate(templateFile, paramsDict, outfile):
    """Invokes the jinja2 methods to fill in the slots
       in the template.
    """
    templateObject = jinja2.Template(open(templateFile).read())
    with open(outfile, 'w') as o:
        o.write(templateObject.render(paramsDict))

class ModuleError(object):
    def __init__(self, exceptionType, detail):
        self.exceptionType = exceptionType
        self.detail = detail

def raiseNotDefined():
    fileName = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print "*** Method not implemented: %s at line %s of %s" % (method, line, fileName)
    sys.exit(1)

def lookup(name, namespace):
    """
    Get a method or class from any imported module from its name.
    Usage: lookup(functionName, globals())
    """
    #TODO: can we use this to detect missing or duplicate functions?
    dots = name.count('.')
    if dots > 0:
        moduleName, objName = '.'.join(name.split('.')[:-1]), name.split('.')[-1]
        module = __import__(moduleName)
        return getattr(module, objName)
    else:
        modules = [obj for obj in namespace.values() if str(type(obj)) == "<type 'module'>"]
        options = [getattr(module, name) for module in modules if name in dir(module)]
        options += [obj[1] for obj in namespace.items() if obj[0] == name ]
        if len(options) == 1: return options[0]
        if len(options) > 1: raise Exception, 'Name conflict for %s'
        raise Exception, '%s not found as a method or class' % name

def pause():
    """
    Pauses the output stream awaiting user feedback.
    """
    print "<Press enter/return to continue>"
    raw_input()


# code to handle timeouts
#
# FIXME
# NOTE: TimeoutFuncton is NOT reentrant.  Later timeouts will silently
# disable earlier timeouts.  Could be solved by maintaining a global list
# of active time outs.  Currently, questions which have test cases calling
# this have all student code so wrapped.
#
import signal
import time

class TimeoutFunctionException(Exception):
    """Exception to raise on a timeout"""
    def __init__(self, timeout):
        self.message = 'Your code should terminate within {0} seconds. Can you find a simpler solution?'.format(timeout)
    def __str__(self):
        return repr(self.message)


class TimeoutFunction:
    def __init__(self, function, timeout):
        self.timeout = timeout
        self.function = function

    def handle_timeout(self, signum, frame):
        raise TimeoutFunctionException(self.timeout)

    def __call__(self, *args, **keyArgs):
        # If we have SIGALRM signal, use it to cause an exception if and
        # when this function runs too long.  Otherwise check the time taken
        # after the method has returned, and throw an exception then.
        if hasattr(signal, 'SIGALRM'):
            old = signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.timeout)
            try:
                result = self.function(*args, **keyArgs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
        else:
            startTime = time.time()
            result = self.function(*args, **keyArgs)
            timeElapsed = time.time() - startTime
            if timeElapsed >= self.timeout:
                self.handle_timeout(None, None)
        return result



_ORIGINAL_STDOUT = None
_ORIGINAL_STDERR = None
_MUTED = False

class WritableNull:
    def write(self, string):
        pass

def mutePrint():
    global _ORIGINAL_STDOUT, _ORIGINAL_STDERR, _MUTED
    if _MUTED:
        return
    _MUTED = True

    _ORIGINAL_STDOUT = sys.stdout
    #_ORIGINAL_STDERR = sys.stderr
    sys.stdout = WritableNull()
    #sys.stderr = WritableNull()

def unmutePrint():
    global _ORIGINAL_STDOUT, _ORIGINAL_STDERR, _MUTED
    if not _MUTED:
        return
    _MUTED = False

    sys.stdout = _ORIGINAL_STDOUT
    #sys.stderr = _ORIGINAL_STDERR

def parseCoverPy(honorcode):
    try:
        info = honorcode.__dict__
    except: # something wrong in file formatting
        return False

    builtin_attrs = filter(lambda k: k.startswith('_'), info.keys())
    map(info.pop, builtin_attrs) # remove built-ins

    info['missing'] = filter(lambda field: info[field]=='',
                             ['YourFullName',
                              'YourUsername',
                              'PartnerFullName',
                              'PartnerUsername']) + filter(lambda field: info[field]==0,
                                                           [fieldname for fieldname in info.keys() if fieldname.startswith('Time') or fieldname=='HowWeWorked'])

    info['filled'] = filter(lambda field: info[field]!='' and info[field]!=0 and field!='missing' and field!='filled', info.keys())

    return info

def parseCoverSheet():
    """Parse the plaintext coversheet"""
    # deprecated?
    info = {}
    for line in open('coversheet.txt').readlines():
        line = line.split(':')
        if len(line)<2:
            continue
        k = line[0].strip()
        v = line[1].strip()
        if k.startswith('Name'):
            info['studentname'] = v
        elif k.startswith('Username'):
            info['studentid'] = v
        elif k.startswith('Partner Name'):
            info['partnername'] = v
        elif k.startswith('Partner Username'):
            info['partnerid'] = v
        elif k.startswith('Collaborators'):
            info['collaborators'] = v
        elif k.startswith('Time spent on'):
            info['time'+k[-2]] = v
    return info
