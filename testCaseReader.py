# Author: Daniela Kreimerman Arroyo and Sravana Reddy
# Created to allow easy input for test cases in CS111 autograder

import sys
import os
import optparse
import pickle

def dataFromFile(filename):
    '''Returns a list of dictionaries corresponding to each line in the file,
    with header attribute mapped to data
    '''
    with open(filename, 'r') as inputFile:
        header = inputFile.readline().strip().split('|')
        caseRawList = [line.strip().split('|') for line in inputFile.readlines()]
        caseDictList = [dict(zip(header, line)) for line in caseRawList if len(line)==len(header)]
    return caseDictList

def generateTestFile(caseDict,filename):
    '''Creates a .test file from a single dictionary containing information about
    the case'''
    arguments = caseDict['arguments'] #stores test case arguments as a list
    if arguments.endswith(".pickle'"):
        #load data from pickle file
        arguments = pickle.load(open(os.path.join('pickled', arguments)))
    with open(filename,'w') as f:
        #writes test file with information from the list
        if caseDict['result'].endswith('.png'):
            f.write("class: \"ImageTest\"\n")
        elif eval(caseDict['print']):
            f.write("class: \"PrintTest\"\n")
        else:
            f.write("class: \"EvalTest\"\n")
        f.write("call: \""+caseDict['functionname']+"("+caseDict['arguments']+")\"\n")
        f.write("success: \""+caseDict['description']+"\"\n")
        f.write("failure: \""+caseDict['description']+"\"\n")
        f.write("\n# A python expression to be evaluated.  This expression must return the\n")
        f.write("# same result for the student and instructor's code.\n")
        f.write("test: \""+caseDict['modulename']+"."+caseDict['functionname']+'('+caseDict['arguments']+')\"\n')
        f.write("weight: \""+caseDict['weight']+"\"")

def generateSolutionFile(caseDict,filename):
    '''Creates a .test file from a single list containing information about
    the case'''
    with open(filename,'w') as f:
        #writes the solution file with information from the list
        f.write("# This is the solution file for "+filename.split('.')[0]+'.test.\n')
        f.write("# The result of evaluating the test must equal the value below.\n")
        f.write("result: \""+caseDict['result']+"\"\n")

def generateCONFIGFile(directory,numPoints):
    '''Creates a CONFIG file for each folder to indicate number of points'''
    filename = os.path.join('inspector','test_cases',directory,'CONFIG')
    with open(filename,'w')as f:
        f.write("max_points: \""+str(numPoints)+"\"\n")
        f.write("class: \"WeightedCasesQuestion\"\n")

def main():
    parser = optparse.OptionParser(description = 'Convert list of test cases provided by problem set designer')
    parser.add_option('--casefile',
                      dest = 'casefile',
                      default = 'casefile_creator.txt',
                      help = 'Filename with test cases')
    options, _ = parser.parse_args(sys.argv)

    amountOfSolutionsDict={} #will store how many solutions a certain function has
    #(so we don't overwrite the same solution file a buncha times)
    testsPerQDict={}

    caseDictList = dataFromFile(options.casefile)

    if 'test_cases' not in os.listdir('inspector'):
        os.mkdir('inspector/test_cases')

    for caseDict in caseDictList:
        if caseDict['directory'] not in os.listdir('inspector/test_cases'):
            os.mkdir(os.path.join('inspector/test_cases', caseDict['directory']))

        amountOfSolutionsDict[caseDict['functionname']] = amountOfSolutionsDict.get(caseDict['functionname'],0)+1
        testsPerQDict[caseDict['directory']]=testsPerQDict.get(caseDict['directory'],0)+int(caseDict['weight'])
        testFile=os.path.join('inspector', 'test_cases', caseDict['directory'], caseDict['functionname']+'_'+str(amountOfSolutionsDict[caseDict['functionname']]))
        generateTestFile(caseDict,testFile+".test")
        generateSolutionFile(caseDict,testFile+".solution")

    for question in testsPerQDict:
        generateCONFIGFile(question, testsPerQDict[question])

    with open(os.path.join('inspector', 'test_cases', 'CONFIG'), 'w') as o:
        o.write('order: "')
        for q in sorted(testsPerQDict.keys()):
            o.write(q+' ')
        o.write('"\n')

if __name__=='__main__':
    main()
