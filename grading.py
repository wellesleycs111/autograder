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
from collections import defaultdict
import util
import os
import webbrowser


class Grades:
  "A data structure for project grades, along with formatting code to display them"
  def __init__(self, projectName, questionsAndMaxesList, htmlOutput=False, logOutput=False, timeout=30, showGrades=True):
    """
    Defines the grading scheme for a project
      projectName: project name
      questionsAndMaxesDict: a list of (question name, max points per question)
    """
    self.questions = [el[0] for el in questionsAndMaxesList]
    self.maxes = dict(questionsAndMaxesList)
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

  def grade(self, gradingModule, funcNotDefined, exceptionMap = {}, bonusPic = False):
    """
    Grades each question
      gradingModule: the module with all the grading functions (pass in with sys.modules[__name__])
    """

    self.undefined = funcNotDefined
    self.exceptionMap=exceptionMap
    completedQuestions = set([])
    for q in self.questions:
      self.errorHints[q]=[]
      self.printedMessage += '\nQuestion %s\n' % q
      self.printedMessage += '=' * (9 + len(q))
      self.printedMessage += '\n'
      self.currentQuestion = q

      if q in self.undefined:
          for func in self.undefined[q]:
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
    self.printedMessage += 'Total: %d/%d\n' % (self.points.totalCount(), sum(self.maxes.values()))

    if self.htmlOutput:
        self.produceOutput()
    else:
        print self.printedMessage

    if self.log:
        # Store results of current run
        if not os.path.isdir('logs'):
            os.mkdir('logs')
        current = [int(filename.split('.')[-1]) for filename in os.listdir('logs')]
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
    #questionName = 'q' + questionNum
    errorHint = ''

    # question specific error hints
    if self.exceptionMap.get(self.currentQuestion):
      questionMap = self.exceptionMap.get(self.currentQuestion)
      if (questionMap.get(typeOf)):
        errorHint = questionMap.get(typeOf)
    # fall back to general error messages if a question specific
    # one does not exist
    elif (self.exceptionMap.get(typeOf)):
      errorHint = self.exceptionMap.get(typeOf)

    # dont include the HTML if we have no error hint
    if errorHint=='':
      return ''

    for line in errorHint.split('\n'):
      self.errorHints[self.currentQuestion].append(line)

  def produceOutput(self):
    """Passes dictionary of parameters to fill in the Jinja template,
    writes filled-in HTML and grade to files"""
    paramsDict = {}

    paramsDict['psid'] = open('psid.txt').read().strip().upper()
    urlDict = dict([line.split() for line in open('urls.txt').readlines()])  # mapping from question numbers to URLs

    studentinfo = util.parseCoverPy()
    if studentinfo:
        paramsDict.update(studentinfo) # not passing keys signifies something's wrong

    paramsDict['totalpossible'] = sum(self.maxes.values())
    paramsDict['totalscore'] = sum(self.points.values())
    paramsDict['showGrades'] = self.showGrades
    paramsDict['questions']=[]

    for q in self.questions:
        num = str(self.questions.index(q)+1)
        if self.maxes[q] == 0:
            correctness='info'

        elif self.points[q] == self.maxes[q]:
            correctness='success'

        elif self.points[q] == 0:
            correctness='danger'

        else:
            correctness='warning'

        score=self.points[q]
        qmax=self.maxes[q]
        badge = str(score)+"/"+str(qmax)
        passedcases = [util.codeHighlight(message[6:]).replace(r"\n","<br>") for message in self.messages[q] if message.startswith('PASS')]
        failedcases = [util.codeHighlight(message[6:]).replace(r"\n","<br>") for message in self.messages[q] if message.startswith('FAIL')]
        undefined = ['<pre>Function %s() is not defined.</pre>' % message for message in self.undefined[q]]
        images = ['<pre>{0}\nExpected image:\n<img src={1}>\nYour image:\n<img src={2}></pre>'.format(message.split(',')[1],message.split(',')[2],message.split(',')[3]) for message in self.messages[q] if message.startswith('IMAGE')]
        if len(images)>0:
            badge="Image Test"
        paramsDict['questions'].append({'num':num,'correctness':correctness,'badge':badge,'passedcases':passedcases,'failedcases':failedcases, 'undefined': undefined, 'images': images, 'hints': self.errorHints[q], 'url': urlDict[q]})

    with open('grader_result.html', 'w') as o:
          o.write(util.fillHTMLTemplate(open('jinjatemplate.html').read(), paramsDict))

    with open('grade', 'w') as o:
        o.write(str(self.points.totalCount()))

    webbrowser.open(os.path.join('file:' + os.getcwd(), 'grader_result.html'))

  def produceOutputOld(self):  # archived the original
    htmlOutput = open('grader_result.html', 'w')
    htmlOutput.write("<div>")

    # first sum
    total_possible = sum(self.maxes.values())
    total_score = sum(self.points.values())
    checkOrX = '<span class="incorrect"/>'
    if (total_score >= total_possible):
        checkOrX = '<span class="correct"/>'
    header = """
        <h3>
            Total score ({total_score} / {total_possible})
        </h3>
    """.format(total_score = total_score,
      total_possible = total_possible,
      checkOrX = checkOrX
    )
    htmlOutput.write(header)

    for q in self.questions:
      if len(q) == 2:
          name = q[1]
      else:
          name = q
      checkOrX = '<span class="incorrect"/>'
      if (self.points[q] == self.maxes[q]):
        checkOrX = '<span class="correct"/>'
      #messages = '\n<br/>\n'.join(self.messages[q])
      messages = "<pre>%s</pre>" % '\n'.join(self.messages[q])
      output = """
        <div class="test">
          <section>
          <div class="shortform">
            Question {q} ({points}/{max}) {checkOrX}
          </div>
        <div class="longform">
          {messages}
        </div>
        </section>
      </div>
      """.format(q = name,
        max = self.maxes[q],
        messages = messages,
        checkOrX = checkOrX,
        points = self.points[q]
      )
      # print "*** output for Question %s " % q[1]
      # print output
      htmlOutput.write(output)
    htmlOutput.write("</div>")
    htmlOutput.close()
    htmlOutput = open('grade', 'w')
    htmlOutput.write(str(self.points.totalCount()))
    htmlOutput.close()

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

  def addMessageToEmail(self, message):
    print "WARNING**** addMessageToEmail is deprecated %s" % message
    for line in message.split('\n'):
      pass
      #print '%%% ' + line + ' %%%'
      #self.messages[self.currentQuestion].append(line)





class Counter(dict):
  """
  Dict with default 0
  """
  def __getitem__(self, idx):
    try:
      return dict.__getitem__(self, idx)
    except KeyError:
      return 0

  def totalCount(self):
    """
    Returns the sum of counts for all keys.
    """
    return sum(self.values())
