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
    arguments = caseList[6:] #stores test case arguments as a list
    with open(filename,'w') as f:
        #writes test file with information from the list
        if caseList[4].endswith('.png'):
            f.write("class: \"ImageTest\"\n")
        else:
            f.write("class: \"EvalTest\"\n")
        f.write("success: \""+caseList[1]+"("+','.join(arguments)+") returns "+caseList[3]+"\"\n")
        f.write("failure: \""+caseList[1]+"("+','.join(arguments)+") must return "+caseList[3]+"\"\n")
        f.write("\n# A python expression to be evaluated.  This expression must return the\n")
        f.write("# same result for the student and instructor's code.\n")
        f.write("test: \""+caseList[2]+"."+caseList[1]+'('+','.join(arguments)+')\"\n')
        f.write("weight: \""+caseList[5]+"\"")

def generateSolutionFile(caseList,filename):
    '''Creates a .test file from a single list containing information about
    the case'''
    with open(filename,'w') as f:
        #writes the solution file with information from the list
        f.write("# This is the solution file for "+filename.split('.')[0]+'.test.\n')
        f.write("# The result of evaluating the test must equal the below when cast to a string.\n")
        f.write("result: \""+caseList[4]+"\"\n")

def generateCONFIGFile(directory,numPoints):
    '''Creates a CONFIG file for each folder to indicate number of points'''
    filename = os.path.join('test_cases',directory,'CONFIG')
    with open(filename,'w')as f:
        f.write("max_points: \""+str(numPoints)+"\"\n")
        f.write("class: \"WeightedCasesQuestion\"")

def main():
    caseList=[]
    if len(sys.argv)>1:
        caseList=linesFromFile(sys.argv[1]) #if user provides argument, use that
    else:
        caseList=linesFromFile("casefile_creator.txt") #default file otherwise
    amountOfSolutionsDict={} #will store how many solutions a certain function has
    #(so we don't overwrite the same solution file a buncha times)
    testsPerQDict={}
    for line in caseList:
        line=line.split(',')
        amountOfSolutionsDict[line[1]] = amountOfSolutionsDict.get(line[1],0)+1
        testsPerQDict[line[0]]=testsPerQDict.get(line[0],0)+int(line[5])
        testFile=os.path.join('test_cases', line[0], line[1]+'_'+str(amountOfSolutionsDict[line[1]]))
        generateTestFile(line,testFile+".test")
        generateSolutionFile(line,testFile+".solution")
    for key in testsPerQDict:
        generateCONFIGFile(key,testsPerQDict[key])

if __name__=='__main__':
    main()
