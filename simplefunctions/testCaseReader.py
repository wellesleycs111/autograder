# Author: Daniela Kreimerman Arroyo
# linesFromFile function from CS111 materials
# Created to allow easy input for test cases in CS111 autograder

import sys
import os

def linesFromFile(filename):
    '''Returns a list of all the lines from a file with the given filename.
       In each line, the terminating newline has been removed.'''
    with open(filename, 'r') as inputFile: # open the file
        # read each line in the file
        strippedLines = [line.strip() for line in inputFile.readlines()][1:] # skip header row
    return strippedLines
    
def generateTestFile(caseList,filename):
    '''Creates a .test file from a single list containing information about
    the case'''
    arguments = caseList[5:] #stores test case arguments as a list
    with open(filename,'w') as f:
        #writes test file with information from the list
        f.write("class: \"EvalTest\"\n");
        f.write("success: \""+caseList[1]+" returns "+caseList[3]+"\"\n")
        f.write("failure: \""+caseList[1]+" must return "+caseList[3]+"\"\n")
        f.write("\n# A python expression to be evaluated.  This expression must return the\n")
        f.write("# same result for the student and instructor's code.\n")
        f.write("test: \""+caseList[2]+"."+caseList[1]+'('+','.join(arguments)+')\"\n')
    
def generateSolutionFile(caseList,filename):
    '''Creates a .test file from a single list containing information about
    the case'''
    with open(filename,'w') as f:
        #writes the solution file with information from the list
        f.write("# This is the solution file for "+filename.split('.')[0]+'.test.\n')
        f.write("# The result of evaluating the test must equal the below when cast to a string.\n")
        f.write("result: \""+caseList[4]+"\"\n")

def main():
    caseList=[]
    if len(sys.argv)>1:
        caseList=linesFromFile(sys.argv[1]) #if user provides argument, use that
    else:
        caseList=linesFromFile("casefile_creator.txt") #default file otherwise
    amountOfSolutionsDict={} #will store how many solutions a certain function has
    #(so we don't overwrite the same solution file a buncha times)
    for line in caseList:
        line=line.split(',')
        amountOfSolutionsDict[line[0]] = amountOfSolutionsDict.get(line[0],0)+1
        testFile=os.path.join('test_cases', line[0], line[1]+str(amountOfSolutionsDict[line[0]]))
        generateTestFile(line,testFile+".test")
        generateSolutionFile(line,testFile+".solution")
    
if __name__=='__main__':
    main()
