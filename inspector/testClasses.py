# testClasses.py
# --------------
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


# import modules from python standard library
import inspect
import re
import sys
import os
import cStringIO

import inspector.util as util

# -- print --
class ReturnPrint:
    """Datatype returned by a function that also prints"""
    def __init__(self, returnval, printval):
        self.returnval = returnval
        self.printval = printval
    def __eq__(self, other):
        if type(self)==type(other):
            return self.returnval==other.returnval and self.printval==other.printval
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
    def __str__(self):
        if self.returnval:
            return '\nReturned value = '+str(self.returnval)+'\n'+'Printed value =\n'+str(self.printval)
        else:
            return '\n'+str(self.printval)

def capturePrint(func, arglist):
    """Redirect print output from func and return it alongwith the actual return value"""
    # adapted from https://wrongsideofmemphis.wordpress.com/2010/03/01/store-standard-output-on-a-variable-in-python/
    old_stdout = sys.stdout
    result = cStringIO.StringIO()
    sys.stdout = result
    returnval = func(*arglist)  # call the function
    printval = '\n'.join([line.rstrip() for line in result.getvalue().splitlines()])  # strip trailing spaces from ends
    sys.stdout = old_stdout
    return ReturnPrint(returnval, printval)

# -- raw_input --
def feedInput(func, arglist, s):
    """Execute a function that contains raw_input,
    feed in s instead of stdin"""
    old_stdin = sys.stdin
    old_stdout = sys.stdout

    tofeed = cStringIO.StringIO(s)
    result = cStringIO.StringIO()

    sys.stdin = tofeed
    sys.stdout = result

    returnval = func(*arglist)  # call the function
    printval = '\n'.join([line.rstrip() for line in result.getvalue().splitlines()])  # strip trailing spaces from ends

    sys.stdin = old_stdin
    sys.stdout = old_stdout

    return ReturnPrint(returnval, printval)

# Class which models a question in a project.  Note that questions have a
# maximum number of points they are worth, and are composed of a series of
# test cases
class Question(object):

    def raiseNotDefined(self):
        print 'Method not implemented: %s' % inspect.stack()[1][3]
        sys.exit(1)

    def __init__(self, questionDict):
        self.maxPoints = int(questionDict['max_points'])
        self.testCases = []

    def getMaxPoints(self):
        return self.maxPoints

    # Note that 'thunk' must be a function which accepts a single argument,
    # namely a 'grading' object
    def addTestCase(self, testCase, thunk):
        self.testCases.append((testCase, thunk))

    def execute(self, grades):
        self.raiseNotDefined()

class NumberPassedQuestion(Question):
    """Grade is the number of test cases passed."""

    def execute(self, grades):
        grades.addPoints([f(grades) for _, f in self.testCases].count(True))

class WeightedCasesQuestion(Question):
    """Grade is sum of weights of test cases passed"""
    def execute(self,grades):
        grades.addPoints(sum([int(case.weight) for case, f in self.testCases if f(grades)==True]))

# Template modeling a generic test case
class TestCase(object):

    def raiseNotDefined(self):
        print 'Method not implemented: %s' % inspect.stack()[1][3]
        sys.exit(1)

    def getPath(self):
        return self.path

    def __init__(self, question, testDict):
        self.question = question
        self.testDict = testDict
        self.path = testDict['path']
        self.weight = testDict['weight']
        self.messages = []

    def __str__(self):
        self.raiseNotDefined()

    def execute(self, grades, moduleDict, solutionDict, showGrades):
        self.raiseNotDefined()

    def writeSolution(self, moduleDict, filePath):
        self.raiseNotDefined()
        return True

    def addMessage(self, message):  #TODO: remove. is this ever used?
        self.messages.extend(message.split('\n'))

class Message:
    def __init__(self, casenum, description, error, expected, grade=None):
        self.casenum = casenum
        self.description = description
        self.error = error
        self.expected = expected
        self.grade = grade
    def highlight(self):
        m = '<pre>Case {0}.\n\t{1}{2}'.format(self.casenum,
                                              self.description,
                                              util.codeHighlight(str(self.error)+'\nExpected result: '+self.expected))
        if self.grade:
            m + '\n\tscore: {0}/{1}'.format(self.grade[0], self.grade[1])
        m += '</pre>'
        return m
    def nohighlight(self):
        m = '<pre>Case {0}.\n\t{1}{2}'.format(self.casenum,
                                              self.description,
                                              '<pre>{0}</pre>'.format(str(self.error)+'\nExpected result: '+self.expected))
        if self.grade:
            m + '\n\tscore: {0}/{1}'.format(self.grade[0], self.grade[1])
        m += '</pre>'
        return m

    def __str__(self):
        m = 'Case {0}.\n\t{1}\n\t{2}\n\t{3}'.format(self.casenum,
                                                    self.description,
                                                    str(self.error),
                                                    'Expected result: '+self.expected)
        if self.grade:
            m + '\n\tscore: {0}/{1}'.format(self.grade[0], self.grade[1])
        return m

    def __repr__(self):
        return self.__str__()

    def jsonify(self):
        return {'case': self.casenum,
             'student': str(self.error),
             'expected': self.expected,
             'score': self.grade}

class EvalTest(TestCase): # moved from tutorialTestClasses

    def __init__(self, question, testDict):
        super(EvalTest, self).__init__(question, testDict)
        self.preamble = compile(testDict.get('preamble', ""), "%s.preamble" % self.getPath(), 'exec')
        self.test = compile(testDict['test'], "%s.test" % self.getPath(), 'eval')
        self.success = testDict['call']+' '+testDict['success']
        self.failure = testDict['call']+' '+testDict['failure']

        basename = os.path.splitext(os.path.basename(self.path))[0]
        self.funcname, self.casenum = basename.split('_')

    def evalCode(self, moduleDict):
        bindings = dict(moduleDict)
        try:
            exec self.preamble in bindings
            return eval(self.test, bindings)
        except Exception, inst:
            self.inst=inst
            return 'Exception was raised'

    def areResultsEqual(self, val1, val2):
        """fuzzify float comparisons"""
        fuzzyFloatDigits = 5
        if type(val1) != type(val2):
            return False
        elif isinstance(val1, float): # Do "close enough" fuzzy equality on floats
          return round(val1,fuzzyFloatDigits) == round(val2,fuzzyFloatDigits)
        elif isinstance(val1, list):
          return len(val1) == len(val2) and all([self.areResultsEqual(v1, v2) for v1,v2 in zip(val1,val2)])
        elif isinstance(val1, tuple):
          return len(val1) == len(val2) and all([self.areResultsEqual(v1,v2) for v1,v2 in zip(val1,val2)])
        elif isinstance(val1, set):
          if len(val1) !=len(val2):
                return False
          else:
            sortedVals1 = sorted(val1)
            sortedVals2 = sorted(val2)
            return all([self.areResultsEqual(v1,v2) for v1,v2 in zip(sortedVals1,sortedVals2)])
        elif isinstance(val1, dict):
          if len(val1) !=len(val2):
                return False
          else:
            sortedItems1 = sorted(val1.items())
            sortedItems2 = sorted(val2.items())
            return all([key1 == key2 and self.areResultsEqual(v1,v2) for ((key1,v1),(key2,v2)) in zip(sortedItems1,sortedItems2)])
        else: # Do regular equality check
            return val1 == val2

    def execute(self, grades, moduleDict, solutionDict, showGrades):
        result = self.evalCode(moduleDict)

        if isinstance(solutionDict['result'], str):
            expected_result = '"{0}"'.format(solutionDict['result'])  # otherwise, "" are stripped
        else:
            expected_result = str(solutionDict['result'])

        if len(expected_result)>200:
            expected_result = expected_result[:200]+'...'  # truncate

        if isinstance(result, str):
            student_result = '"{0}"'.format(result)  # otherwise, "" are stripped
        else:
            student_result = str(result)

        if len(student_result)>200:
            student_result = student_result[:200]+'...' #truncate

        # exception
        if result=='Exception was raised':
            if showGrades:
                msg = Message(self.casenum,
                            self.failure,
                            'Exception raised: '+str(self.inst),
                            expected_result,
                            (0, self.weight))
            else:
                msg = Message(self.casenum,
                            self.failure,
                            'Exception raised: '+str(self.inst),
                            expected_result)

            grades.addMessage(('FAIL', self.funcname, msg))
            grades.addErrorHints(self.inst)
            return False

        # correct
        if self.areResultsEqual(result, solutionDict['result']):
            if showGrades:
                msg = Message(self.casenum,
                            self.success,
                            'Your result: '+student_result,
                            expected_result,
                            (self.weight, self.weight))
            else:
                msg = Message(self.casenum,
                            self.success,
                            'Your result: '+student_result,
                            expected_result)

            grades.addMessage(('PASS', self.funcname, msg))
            return True

        # incorrect
        if showGrades:
            msg = Message(self.casenum,
                        self.failure,
                        'Your result: '+student_result,
                        expected_result,
                        (0, self.weight))
        else:
            msg = Message(self.casenum,
                        self.success,
                        'Your result: '+student_result,
                        expected_result)

        grades.addMessage(('FAIL', self.funcname, msg))
        return False

class ImageTest(EvalTest):

    def execute(self,grades,moduleDict,solutionDict,showGrades):
        result = self.evalCode(moduleDict)

        if result == 'Exception was raised':
            if showGrades:
                msg = Message(self.casenum,
                            self.failure,
                            'Exception raised: '+str(self.inst),
                            expected_result,
                            (0, self.weight))
            else:
                msg = Message(self.casenum,
                            self.failure,
                            'Exception raised: '+str(self.inst),
                            expected_result)

            grades.addMessage(('FAIL', self.funcname, msg))
            grades.addErrorHints(self.inst)
            return False

        userimage = os.path.basename(solutionDict['result'])

        if showGrades:
            msg = Message(self.casenum,
                        self.success,
                        'Your image:\n'+'<img src="'+userimage+'" />',
                        '\n<img src="'+solutionDict['result']+'" />',
                        (self.weight, self.weight))
        else:
            msg = Message(self.casenum,
                        self.success,
                        'Your image:\n'+'<img src="'+userimage+'" />',
                        '\n<img src="'+solutionDict['result']+'" />')

        grades.addMessage(('IMAGE', self.funcname, msg))
        return True

class GradedImageTest(EvalTest):

    def execute(self,grades,moduleDict,solutionDict,showGrades):
        result = self.evalCode(moduleDict)

        # result is a cs1graphics frame

        # exception
        if result == 'Exception was raised':
            msg = 'Case {0}.\n\t{1}\n\tException raised: {2}\n\tExpected result: {3}'.format(self.casenum,
                                                                                                 self.failure,
                                                                                                 self.inst,
                                                                                                 solutionDict['result'])
            if showGrades:
                msg += '\n\tscore: {0}/{1}'.format(0, self.weight)
            grades.addMessage(('FAIL', self.funcname, msg))
            grades.addErrorHints(self.inst)
            return False

        # correct
        if result.equals(solutionDict['result']):
            msg = 'Case {0}.\n\t{1}'.format(self.casenum, self.success)
            if showGrades:
                msg += '\n\tscore: {0}/{1}'.format(self.weight, self.weight)
            grades.addMessage(('PASS', self.funcname, msg))
            return True

        # incorrect
        msg = 'Case {0}.\n\tstudent result: {1}\n\tcorrect result: {2}'.format(self.failure,
                                                                         result,
                                                                         solutionDict['result'])
        if showGrades:
            msg += '\n\tscore: {0}/{1}'.format(0, self.weight)
        grades.addMessage(('FAIL', self.funcname, msg))
        return False

class PrintTest(EvalTest):
    """Class for functions containing print"""
    def __init__(self,question,testDict):
        testDict['test']='projectTestClasses.capturePrint('+testDict['test'].split('(')[0]+',['+testDict['test'][:-1].split('(')[1]+'])'
        super(PrintTest, self).__init__(question, testDict)

class InputTest(EvalTest):
    """Class for functions containing raw_input (and possibly print)"""
    def __init__(self,question,testDict):
        testDict['test']='projectTestClasses.feedInput('+testDict['test'].split('(')[0]+',['+testDict['test'][:-1].split('(')[1]+']'+', "something")'  #TODO: how to encode sample inputs (something)?
        super(InputTest, self).__init__(question, testDict)
