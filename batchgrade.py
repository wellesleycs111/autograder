import os
import autograder
from inspector.util import fillHTMLTemplate
import json

# assume student submissions are stored as L01/studentname
# where studentname is the directory containing the code for the problem set
# run usernames_by_section.sh on tempest
# and then download.sh locally to get the data in this format

filenames = raw_input('Enter .py student filenames to look for, separated by commas: ')

summary = {'scores': []}
for section in ['L0'+str(i) for i in range(1, 5)]:  # edit as needed
    for student in os.listdir(section):
        #autograder.main(['--student-code=honorcode.py,'+filenames,
        #                 '--code-directory={0}/{1}'.format(section, student),
        #                  '--show-grades',
        #                  '--output-dir={0}/{1}'.format(section, student)])
        #this creates a grade.json file in each student directory
        score = json.load(open(os.path.join(section,
                                            student,
                                            'grade.json')))
        score['name'] = student
        summary['scores'].append(score)

fillHTMLTemplate('sumtemplate.html', summary, 'summary.html')
