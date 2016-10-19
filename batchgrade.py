import os
from inspector.util import fillHTMLTemplate
import json
from otterInspect import *

# assume student submissions are stored as L01/studentname
# where studentname is the directory containing the code for the problem set
# run usernames_by_section.sh on tempest
# and then download.sh locally to get the data in this format

outfilename = 'summary.html'

summary = {'scores': []}
for section in ['L0'+str(i) for i in range(1, 5)]:  # edit as needed
    for student in os.listdir(section):
        print student
        os.chdir(os.path.join(section, student))

        os.system('python otterInspect.py --showGrades --htmlOutput')
        os.chdir('../..')
        #this creates a grade.json file in each student directory
        score = json.load(open(os.path.join(section,
                                            student,
                                            'grade.json')))
        score['name'] = student
        summary['scores'].append(score)

fillHTMLTemplate('sumtemplate.html', summary, outfilename)
print 'Wrote summary to', outfilename
