# autograder.py
# -------------
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


# imports from python standard library
import grading
import imp
import optparse
import os
import re
import sys
import projectParams
import random
import util
from hintmap import ERROR_HINT_MAP
import pprint

random.seed(0)

# register arguments and set default values
def readCommand(argv):
    parser = optparse.OptionParser(description = 'Run public tests on student code')
    parser.set_defaults(htmlOutput=True, logOutput=True)
    parser.add_option('--test-directory',
                      dest = 'testRoot',
                      default = 'test_cases',
                      help = 'Root test directory which contains subdirectories corresponding to each question')
    parser.add_option('--student-code',
                      dest = 'studentCode',
                      default = projectParams.STUDENT_CODE_LIST,
                      help = 'comma separated list of student code files')
    parser.add_option('--code-directory',
                    dest = 'codeRoot',
                    default = projectParams.STUDENT_CODE_DIR,
                    help = 'Root directory containing the student code')
    parser.add_option('--test-case-code',
                      dest = 'testCaseCode',
                      default = projectParams.PROJECT_TEST_CLASSES,
                      help = 'class containing testClass classes for this project')
    parser.add_option('--no-grades',
                        dest = 'showGrades',
                        default = projectParams.SHOW_GRADES,
                        action = 'store_false',
                        help = 'Won\'t show grades on html output')
    parser.add_option('--html',
                    dest = 'htmlOutput',
                    action = 'store_true',
                    help = 'Generate HTML output files')
    parser.add_option('--log',
                    dest = 'logOutput',
                    action = 'store_true',
                    help = 'Log autograder runs')
    parser.add_option('--question', '-q',
                    dest = 'gradeQuestion',
                    default = None,
                    help = 'Grade one particular question.')
    (options, args) = parser.parse_args(argv)
    return options


# TODO: Fix this so that it tracebacks work correctly
# Looking at source of the traceback module, presuming it works
# the same as the intepreters, it uses co_filename.  This is,
# however, a readonly attribute.
def setModuleName(module, filename):
    functionType = type(readCommand)  #TODO: hacky
    classType = type(optparse.Option)

    for i in dir(module):
        o = getattr(module, i)
        if hasattr(o, '__file__'): continue

        if type(o) == functionType:
            setattr(o, '__file__', filename)
        elif type(o) == classType:
            setattr(o, '__file__', filename)
            # TODO: assign member __file__'s?
        #print i, type(o)


#from cStringIO import StringIO

def loadModuleString(moduleSource):
    # Below broken, imp doesn't believe its being passed a file:
    #    ValueError: load_module arg#2 should be a file or None
    #
    #f = StringIO(moduleCodeDict[k])
    #tmp = imp.load_module(k, f, k, (".py", "r", imp.PY_SOURCE))
    tmp = imp.new_module(k)
    exec moduleCodeDict[k] in tmp.__dict__
    setModuleName(tmp, k)
    return tmp

import py_compile

def loadModuleFile(moduleName, filePath):
    try:
        with open(filePath, 'r') as f:
            random.seed(0)
            return imp.load_module(moduleName, f, "%s.py" % moduleName, (".py", "r", imp.PY_SOURCE))
    except IOError, inst:
        pass # TODO: handle
    except SyntaxError, inst:
        return inst
    #TODO: propagate this down to the output

# returns all the tests you need to run in order to run question
def getDepends(testParser, testRoot, question):
    allDeps = [question]
    questionDict = testParser.TestParser(os.path.join(testRoot, question, 'CONFIG')).parse()
    if 'depends' in questionDict:
        depends = questionDict['depends'].split()
        for d in depends:
            # run dependencies first
            allDeps = getDepends(testParser, testRoot, d) + allDeps
    return allDeps

# get list of questions to grade
def getTestSubdirs(testParser, testRoot, questionToGrade):
    problemDict = testParser.TestParser(os.path.join(testRoot, 'CONFIG')).parse()
    if questionToGrade != None:
        questions = getDepends(testParser, testRoot, questionToGrade)
        if len(questions) > 1:
            print 'Note: due to dependencies, the following tests will be run: %s' % ' '.join(questions)
        return questions
    if 'order' in problemDict:
        return problemDict['order'].split()
    return sorted(os.listdir(testRoot))


# evaluate student code
def evaluate(testRoot, moduleDict, exceptionMap=ERROR_HINT_MAP, htmlOutput=False, logOutput=False, questionToGrade=None):
    #TODO: this is ugly -- fix it
    # imports of testbench code.  note that the testClasses import must follow
    # the import of student code due to dependencies
    import testParser
    import testClasses
    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    questions = []
    questionDicts = {}
    test_subdirs = getTestSubdirs(testParser, testRoot, questionToGrade)
    funcNotDefined={}
    syntaxErrors = {}
    for q in test_subdirs:
        funcNotDefined[q]=[]
        syntaxErrors[q] = set()

        subdir_path = os.path.join(testRoot, q)
        if not os.path.isdir(subdir_path) or q[0] == '.':
            continue

        # create a question object
        questionDict = testParser.TestParser(os.path.join(subdir_path, 'CONFIG')).parse()
        questionClass = getattr(testClasses, questionDict['class'])
        question = questionClass(questionDict)
        questionDicts[q] = questionDict

        # load test cases into question
        tests = filter(lambda t: re.match('[^#~.].*\.test\Z', t), os.listdir(subdir_path))
        tests = map(lambda t: re.match('(.*)\.test\Z', t).group(1), tests)
        for t in sorted(tests):
            test_file = os.path.join(subdir_path, '%s.test' % t)
            solution_file = os.path.join(subdir_path, '%s.solution' % t)
            test_out_file = os.path.join(subdir_path, '%s.test_output' % t)
            testDict = testParser.TestParser(test_file).parse()

            if isinstance(moduleDict[testDict['module']], SyntaxError):  # module has syntax errors
                syntaxErrors[q].add(moduleDict[testDict['module']])
                continue

            if testDict['func'] not in dir(moduleDict[testDict['module']]):
                if testDict['func'] not in funcNotDefined[q]:
                    funcNotDefined[q].append(testDict['func'])
                continue

            if testDict.get("disabled", "false").lower() == "true":
                continue
            testDict['test_out_file'] = test_out_file
            testClass = getattr(projectTestClasses, testDict['class'])
            testCase = testClass(question, testDict)
            def makefun(testCase, solution_file):
                # read in solution dictionary and pass as an argument
                testDict = testParser.TestParser(test_file).parse()
                solutionDict = testParser.TestParser(solution_file).parse()
                return lambda grades: testCase.execute(grades, moduleDict, solutionDict, projectParams.SHOW_GRADES)
            question.addTestCase(testCase, makefun(testCase, solution_file))

        # Note extra function is necessary for scoping reasons
        def makefun(question):
            f= lambda grades: question.execute(grades)
            #print [f(grades) for _, f in question.testCases]
            return f
        setattr(sys.modules[__name__], q, makefun(question))
        questions.append((q, question.getMaxPoints()))

    studentinfo = util.parseCoverPy(moduleDict['honorcode'])
    grades = grading.Grades(projectParams.PROJECT_NAME,
                            questions,
                            htmlOutput=htmlOutput,
                            logOutput=logOutput,
                            timeout=projectParams.TIME_OUT,
                            showGrades=projectParams.SHOW_GRADES,
                            coverSheetScore=projectParams.COVERSHEET,
                            studentinfo=studentinfo)
    if questionToGrade == None:
        for q in questionDicts:
            for prereq in questionDicts[q].get('depends', '').split():
                grades.addPrereq(q, prereq)

    grades.grade(sys.modules[__name__], syntaxErrors, funcNotDefined, exceptionMap)
    return grades.points

def checkme(question,filename):
    options = readCommand(sys.argv)
    codePaths = options.studentCode.split(',')

    moduleDict={}
    moduleName = re.match('.*?([^/]*)\.py', filename).group(1)
    moduleDict[moduleName] = loadModuleFile(moduleName, os.path.join(options.codeRoot, filename))
    moduleName = re.match('.*?([^/]*)\.py', options.testCaseCode).group(1)
    moduleDict['projectTestClasses'] = loadModuleFile(moduleName, options.testCaseCode)





if __name__ == '__main__':
    options = readCommand(sys.argv)
    codePaths = options.studentCode.split(',')

    moduleDict = {}
    for cp in codePaths:
        moduleName = re.match('.*?([^/]*)\.py', cp).group(1)
        moduleDict[moduleName] = loadModuleFile(moduleName, os.path.join(options.codeRoot, cp))
    moduleName = re.match('.*?([^/]*)\.py', options.testCaseCode).group(1)
    moduleDict['projectTestClasses'] = loadModuleFile(moduleName, options.testCaseCode)

    evaluate(options.testRoot, moduleDict, htmlOutput=options.htmlOutput,
             logOutput=options.logOutput, questionToGrade=options.gradeQuestion)
