# This tool was developed by Sravana Reddy (sravana.reddy@wellesley.edu)
# and Daniela Kreimerman (dkreimer@wellesley.edu), built upon the framework
# provided by the Berkeley AI evaluation scripts. See below.
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


import cgi
import time
import sys
import traceback
import pdb
from collections import defaultdict, Counter
import inspector.util as util
import os
import webbrowser
import json

inspectorModDir = os.path.dirname(os.path.realpath(__file__))

class Grades:
  "A data structure for project grades, along with formatting code to display them"
  def __init__(self, projectName, questionsAndMaxesList, htmlOutput=False, logOutput=False, timeout=30, showGrades=True, coverSheetScore=0, studentinfo = None, outputDir='.'):
    """
    Defines the grading scheme for a project
      projectName: project name
      questionsAndMaxesDict: a list of (question name, max points per question)
    """
    self.studentinfo = studentinfo

    self.questions = [el[0] for el in questionsAndMaxesList]
    self.maxes = dict(questionsAndMaxesList)

    self.maxes['coversheet'] = coverSheetScore

    self.points = Counter()

    self.messages = defaultdict(list)

    self.project = projectName

    self.currentQuestion = None # Which question we're grading

    self.htmlOutput = htmlOutput
    self.log = logOutput
    self.outputDir = outputDir

    self.prereqs = defaultdict(set)
    self.timeout = timeout  # max time for any of the questions
    self.showGrades = showGrades #toggle to show/not show grades on html output
    self.errorHints = {}

    self.loggedMessage = {}
    self.loggedMessage['start_time'] = time.localtime()[1:6]

  def addPrereq(self, question, prereq):
    self.prereqs[question].add(prereq)

  def grade(self, gradingModule, moduleErrors, funcNotDefined, exceptionMap = {}):
    """
    Grades each question
      gradingModule: the module with all the grading functions (pass in with sys.modules[__name__])
    """
    self.moduleErrors = moduleErrors
    self.funcNotDefined = funcNotDefined

    self.exceptionMap=exceptionMap
    completedQuestions = set([])

    for q in self.questions:
      self.errorHints[q]={}

      self.loggedMessage[q] = {}
      self.loggedMessage[q]['exceptions'] = []
      self.loggedMessage[q]['messages'] = []

      self.currentQuestion = q

      if q in self.funcNotDefined:
          self.loggedMessage[q]['funcNotDefined'] = self.funcNotDefined[q]

      incompleted = self.prereqs[q].difference(completedQuestions) #TODO: make use of this?
      if len(incompleted) > 0:
          prereq = incompleted.pop()
          continue

      try:
        util.TimeoutFunction(getattr(gradingModule, q), self.timeout)(self) # Call the question's function
      except Exception, inst:
        self.addExceptionMessage(inst)
        print Exception, inst  #TODO: handle this better?
        self.loggedMessage[q]['exceptions'].append(str(inst))

      if self.points[q] >= self.maxes[q]:
        completedQuestions.add(q)

      self.loggedMessage[q]['max'] = self.maxes[q]
      self.loggedMessage[q]['points'] = self.points[q]

    self.loggedMessage['end_time'] = time.localtime()[1:6]

    if self.studentinfo:
        if self.maxes['coversheet']:
            self.points['coversheet'] = int(self.maxes['coversheet']*len(self.studentinfo['filled'])/float(len(self.studentinfo)-2))
    else:
        if self.maxes['coversheet']:
            self.points['coversheet'] = 0

    if self.htmlOutput:
        self.produceOutput()

    if self.showGrades:
        with open(os.path.join(self.outputDir, 'grade.json'), 'w') as o:
            gradeDict = {'tasks': {q: (self.points[q], self.maxes[q]) for q in self.points.keys()}}
            gradeDict['total'] = (sum(self.points.values()),
                                  sum(self.maxes.values()))
            json.dump(gradeDict, o)

    if self.log:
        # Store results of current run
        if not os.path.isdir(os.path.join(self.outputDir, '.logs')):
            os.mkdir(os.path.join(self.outputDir, '.logs'))
        current = [int(filename.split('.')[-1]) for filename in os.listdir(os.path.join(self.outputDir, '.logs')) if filename.startswith('log')]
        if current:
            ctr = max(current)+1
        else:
            ctr = 0
        with open(os.path.join(self.outputDir, '.logs', 'log.'+str(ctr)), 'w') as o:
            json.dump(self.loggedMessage, o)

  def addExceptionMessage(self, inst):
      self.loggedMessage[self.currentQuestion]['exceptions'].append(str(inst))


  def addErrorHints(self,errorInstance):
    typeOf = str(type(errorInstance))
    if typeOf in self.errorHints[self.currentQuestion]:
        # no need to add hint twice
        return

    #questionName = 'q' + questionNum
    errorHint = ''

    # question specific error hints
    questionMap = self.exceptionMap.get(self.currentQuestion, self.exceptionMap['general'])
    if questionMap.get(typeOf):
        errorHint = questionMap.get(typeOf)
    else:
        errorHint = ''
    if errorHint is not '':
        self.errorHints[self.currentQuestion][typeOf] = errorHint

  def produceOutput(self):
    """Passes dictionary of parameters to fill in the Jinja template,
    writes filled-in HTML and grade to files"""
    paramsDict = {}
    paramsDict['pstitle'] = self.project

    urlDict = dict([line.split() for line in open(os.path.join(inspectorModDir,
                                                               'urls.txt')).readlines()])  # mapping from question numbers to URLs

    if self.studentinfo:
        paramsDict['studentinfo'] = self.studentinfo

    paramsDict['totalpossible'] = sum(self.maxes.values())
    paramsDict['totalscore'] = sum(self.points.values())
    paramsDict['showGrades'] = self.showGrades

    paramsDict['questions'] = []

    for q in self.questions:
        passedcases = defaultdict(list)
        failedcases = defaultdict(list)
        images = defaultdict(list)

        num = str(self.questions.index(q)+1)

        correctness = util.correctnessColor(self.points[q], self.maxes[q])

        score=self.points[q]
        qmax=self.maxes[q]
        badge = '{0}/{1}'.format(score, qmax)

        for (status, funcname, msg) in self.messages[q]:
            if status == 'PASS':
                passedcases[funcname].append(msg.nohighlight().replace(r"\n","<br>"))
            elif status == 'FAIL':
                failedcases[funcname].append(msg.nohighlight().replace(r"\n","<br>"))
            elif status == 'IMAGE':
                images[funcname].append(msg.nohighlight().replace('\n', '<br>'))
                badge="Image Test"

        undefined = ['<pre>The function '+funcname+' is not defined.</pre>' for funcname in self.funcNotDefined[q]]

        syntaxerrors = ['<pre>Error in {0}, line {1}, column {2}:<br>{3}</pre>'.format(error.filename, error.lineno, error.offset,
                        util.codeHighlight(error.text, error.offset))
                        for error in self.moduleErrors[q]]

        paramsDict['questions'].append({'num': num,
                                        'name': q,
                                        'correctness':correctness,
                                        'badge':badge,
                                        'passedcases':dict(passedcases),
                                        'failedcases':dict(failedcases),
                                        'funcNotDefined': undefined,
                                        'moduleErrors': syntaxerrors,
                                        'images': dict(images),
                                        'hints': self.errorHints[q],
                                        'url': urlDict[q]})

    paramsDict['coversheet'] = {'correctness': util.correctnessColor(self.points['coversheet'], self.maxes['coversheet']),
                                'badge': str(self.points['coversheet'])+"/"+str(self.maxes['coversheet'])}

    util.fillHTMLTemplate(os.path.join(inspectorModDir,
                                       'jinjatemplate.html'),
                          paramsDict,
                          os.path.join(self.outputDir,
                                       'your_result.html'))

    webbrowser.open(os.path.join('file:' + os.path.abspath(self.outputDir), 'your_result.html'),
                    new=0,
                    autoraise=True)

  def assignZeroCredit(self):
    self.points[self.currentQuestion] = 0

  def addPoints(self, amt):
    self.points[self.currentQuestion] += amt

  def deductPoints(self, amt):
    self.points[self.currentQuestion] -= amt

  def addMessage(self, message):
    self.loggedMessage[self.currentQuestion]['messages'].append((message[0], message[1], message[2].jsonify()))
    self.messages[self.currentQuestion].append(message)
