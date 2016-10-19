# otterInspect.py
# -------------
# This tool was developed by Sravana Reddy (sravana.reddy@wellesley.edu)
# and Daniela Kreimerman (dkreimer@wellesley.edu), built upon the framework
# provided by the Berkeley AI evaluation scripts.

# imports from python standard library
import imp
import argparse
import os
import re
import sys
import random

# module imports
import inspector.util as util
import inspector.grading as grading
from inspector.hintmap import ERROR_HINT_MAP

inspectorModDir = os.path.dirname(os.path.realpath(__file__))

random.seed(0)

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
def evaluate(testRoot, moduleDict, exceptionMap=ERROR_HINT_MAP, htmlOutput=False, logOutput=False, showGrades=False, questionToGrade=None, projectName='', timeout=60, coverSheetScore=0):
    #TODO: this is ugly -- fix it
    # imports of testbench code.  note that the testClasses import must follow
    # the import of student code due to dependencies
    import inspector.testParser as testParser
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
        for t in sorted(tests, key=lambda x:int(x.split('_')[-1])):
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
                return lambda grades: testCase.execute(grades, moduleDict, solutionDict, showGrades)
            question.addTestCase(testCase, makefun(testCase, solution_file))

        # Note extra function is necessary for scoping reasons
        def makefun(question):
            f= lambda grades: question.execute(grades)
            #print [f(grades) for _, f in question.testCases]
            return f
        setattr(sys.modules[__name__], q, makefun(question))
        questions.append((q, question.getMaxPoints()))

    studentinfo = util.parseCoverPy(moduleDict['honorcode'])
    grades = grading.Grades(projectName,
                            questions,
                            htmlOutput=htmlOutput,
                            logOutput=logOutput,
                            timeout=timeout,
                            showGrades=showGrades,
                            coverSheetScore=coverSheetScore,
                            studentinfo=studentinfo)
    if questionToGrade == None:
        for q in questionDicts:
            for prereq in questionDicts[q].get('depends', '').split():
                grades.addPrereq(q, prereq)

    grades.grade(sys.modules[__name__], syntaxErrors, funcNotDefined, exceptionMap)
    return grades.points

def main(showGrades, htmlOutput):
    # edit this for each problem set
    STUDENT_CODE_DIR = '.'
    STUDENT_CODE_LIST = 'wordsearch.py,tictactoe.py,honorcode.py'
    PROJECT_TEST_CLASSES = 'inspector/testClasses.py'
    PROJECT_NAME = 'Problem Set 05 (Due Oct 17)'
    TIME_OUT = 60
    COVERSHEET = 10
    # done editing

    codePaths = STUDENT_CODE_LIST.split(',')

    moduleDict = {}
    for cp in codePaths:
        moduleName = re.match('.*?([^/]*)\.py', cp).group(1)
        moduleDict[moduleName] = loadModuleFile(moduleName, os.path.join(STUDENT_CODE_DIR, cp))
    moduleName = re.match('.*?([^/]*)\.py', PROJECT_TEST_CLASSES).group(1)
    moduleDict['projectTestClasses'] = loadModuleFile(moduleName, PROJECT_TEST_CLASSES)

    evaluate('inspector/test_cases',
             moduleDict,
             htmlOutput=htmlOutput,
             logOutput=True,
             showGrades=showGrades,
             questionToGrade=None,
             projectName=PROJECT_NAME,
             timeout=TIME_OUT,
             coverSheetScore=COVERSHEET)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--showGrades',
                      dest = 'showGrades',
                      action = 'store_true',
                      default = False,
                      help = 'Won\'t show grades on html output or write grade.json file')
    parser.add_argument('--htmlOutput',
                    dest = 'htmlOutput',
                    action = 'store_false',  # becomes false when specified
                    default = True,
                    help = 'Generate and show HTML output files')
    args = parser.parse_args()
    main(args.showGrades, args.htmlOutput)
