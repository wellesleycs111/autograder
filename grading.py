# grading.py
# ----------
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


"Common code for autograders"

import cgi
import time
import sys
import traceback
import pdb
from collections import defaultdict, Counter
import util
import os
import webbrowser


class Grades:
  "A data structure for project grades, along with formatting code to display them"
  def __init__(self, projectName, questionsAndMaxesList, htmlOutput=False, logOutput=False, timeout=30, showGrades=True, coverSheetScore=0, studentinfo = None):
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
    self.messages = dict([(q, []) for q in self.questions])
    self.project = projectName
    self.start = time.localtime()[1:6]
    self.sane = True # Sanity checks
    self.currentQuestion = None # Which question we're grading
    self.htmlOutput = htmlOutput
    self.log = logOutput
    self.prereqs = defaultdict(set)
    self.timeout = timeout  # max time for any of the questions
    self.showGrades = showGrades #toggle to show/not show grades on html output
    self.errorHints = {}

    self.printedMessage = 'Starting on %d-%d at %d:%02d:%02d' % self.start

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
      self.printedMessage += '\nQuestion %s\n' % q
      self.printedMessage += '=' * (9 + len(q))
      self.printedMessage += '\n'
      self.currentQuestion = q

      if q in self.funcNotDefined:
          for func in self.funcNotDefined[q]:
              self.printedMessage+= '***Function %s() not defined.\n' % func

      incompleted = self.prereqs[q].difference(completedQuestions)
      if len(incompleted) > 0:
          prereq = incompleted.pop()
          self.printedMessage += """*** NOTE: Make sure to complete Question %s before working on Question %s,
*** because Question %s builds upon your answer for Question %s.
""" % (prereq, q, q, prereq)
          continue

      try:
        util.TimeoutFunction(getattr(gradingModule, q), self.timeout)(self) # Call the question's function
      except Exception, inst:
        #self.addExceptionMessage(q, inst, traceback)
        #self.addErrorHints(inst, q[1])
        print Exception, inst
      except:
        self.fail('FAIL: Terminated with a string exception.')

      if self.points[q] >= self.maxes[q]:
        completedQuestions.add(q)

      self.printedMessage += '\n### Question %s: %d/%d ###\n' % (q, self.points[q], self.maxes[q])


    self.printedMessage += '\nFinished at %d:%02d:%02d' % time.localtime()[3:6]
    self.printedMessage += "\nProvisional grades\n==================\n"

    for q in self.questions:
      self.printedMessage += 'Question %s: %d/%d\n' % (q, self.points[q], self.maxes[q])
    self.printedMessage += '------------------\n'
    self.printedMessage += 'Total: %d/%d\n' % (sum(self.points.values()), sum(self.maxes.values()))

    if self.htmlOutput:
        self.produceOutput()
    else:
        print self.printedMessage

    if self.log:
        # Store results of current run
        if not os.path.isdir('logs'):
            os.mkdir('logs')
        current = [int(filename.split('.')[-1]) for filename in os.listdir('logs') if filename.startswith('log')]
        if current:
            ctr = max(current)+1
        else:
            ctr = 0
        with open(os.path.join('logs', 'log.'+str(ctr)), 'w') as o:
            o.write(self.printedMessage)

  def addExceptionMessage(self, q, inst, traceback):
    """
    Method to format the exception message, this is more complicated because
    we need to cgi.escape the traceback but wrap the exception in a <pre> tag
    """
    #self.fail('FAIL: Exception raised: %s' % inst)
    self.addMessage('')
    for line in traceback.format_exc().split('\n'):
        self.addMessage(line)

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

    paramsDict['psid'] = open('psid.txt').read().strip().upper()
    urlDict = dict([line.split() for line in open('urls.txt').readlines()])  # mapping from question numbers to URLs

    if self.studentinfo:
        paramsDict['studentinfo'] = self.studentinfo
        if self.maxes['coversheet']:
            self.points['coversheet'] = int(self.maxes['coversheet']*len(self.studentinfo['filled'])/float(len(self.studentinfo)-2))
    else:
        if self.maxes['coversheet']:
            self.points['coversheet'] = 0

    paramsDict['totalpossible'] = sum(self.maxes.values())
    paramsDict['totalscore'] = sum(self.points.values())
    paramsDict['showGrades'] = self.showGrades

    paramsDict['questions']=[]

    for q in self.questions:
        num = str(self.questions.index(q)+1)

        correctness = util.correctnessColor(self.points[q], self.maxes[q])

        score=self.points[q]
        qmax=self.maxes[q]
        badge = str(score)+"/"+str(qmax)

        passedcases = [util.codeHighlight(message[6:]).replace(r"\n","<br>") for message in self.messages[q] if message.startswith('PASS')]
        failedcases = [util.codeHighlight(message[6:]).replace(r"\n","<br>") for message in self.messages[q] if message.startswith('FAIL')]

        undefined = ['<pre>The function '+funcname+' is not defined.</pre>' for funcname in self.funcNotDefined[q]]
        syntaxerrors = ['<pre>Error in {0}, line {1}, column {2}:<br>{3}</pre>'.format(error.filename, error.lineno, error.offset,
                        util.codeHighlight(error.text, error.offset))  
                        for error in self.moduleErrors[q]]

        images = ['<pre>{0}\nExpected image:\n<img src={1}>\nYour image:\n<img src={2}></pre>'.format(message.split(',')[1],message.split(',')[2],message.split(',')[3]) for message in self.messages[q] if message.startswith('IMAGE')]
        if len(images)>0:
            badge="Image Test"
        paramsDict['questions'].append({'num':num,
                                        'correctness':correctness,
                                        'badge':badge,
                                        'passedcases':passedcases,
                                        'failedcases':failedcases,
                                        'funcNotDefined': undefined,
                                        'moduleErrors': syntaxerrors,
                                        'images': images,
                                        'hints': self.errorHints[q],
                                        'url': urlDict[q]})

    paramsDict['coversheet'] = {'correctness': util.correctnessColor(self.points['coversheet'], self.maxes['coversheet']),
                                'badge': str(self.points['coversheet'])+"/"+str(self.maxes['coversheet'])}

    with open('grader_result.html', 'w') as o:
          o.write(util.fillHTMLTemplate(open('jinjatemplate.html').read(), paramsDict))

    if self.showGrades:
        with open('grade', 'w') as o:
            for q in self.points:
                o.write(q+':'+str(self.points[q])+'\n')
            o.write('total:'+str(sum(self.points.values()))+'\n')

    webbrowser.open(os.path.join('file:' + os.getcwd(), 'grader_result.html'),
                    new=0,
                    autoraise=True)

  def fail(self, message, raw=False):
    "Sets sanity check bit to false and outputs a message"
    self.sane = False
    self.addMessage(message, raw)

  def assignZeroCredit(self):
    self.points[self.currentQuestion] = 0

  def addPoints(self, amt):
    self.points[self.currentQuestion] += amt

  def deductPoints(self, amt):
    self.points[self.currentQuestion] -= amt

  def assignFullCredit(self, message="", raw=False):
    self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
    if message != "":
      self.addMessage(message, raw)

  def addMessage(self, message, raw=False):
    if not raw:
        # We assume raw messages, formatted for HTML, are printed separately
        self.printedMessage += '*** ' + message + '\n'
        message = cgi.escape(message)
    self.messages[self.currentQuestion].append(message)
