import os,subprocess

'''Contains programs for the management of lecture notes, slides, tables, and figures'''

def tex(x=None):
    '''Runs pdfLaTeX. Argument x can be either None, a string indicating the name of a single file, or a list. If x is None, then all files in the current directory ending with .tex will be typeset. Cleans up the residual auxiliary files.'''

    os.chdir(os.getcwd())

    if x==None:

        for files in os.listdir('.'):
            if files.endswith('.tex'):
                pdfLatex(x)

    elif type(x)==str:
        pdfLatex(x)

    else:
        for files in x:
            pdfLatex(files)

    for files in os.listdir('.'):
        if files.endswith('.aux') or files.endswith('.log') or files.endswith('.out') or files.endswith('.gz') or files.endswith('.snm') or files.endswith('.nav') or files.endswith('.toc'):
            os.remove(files)

def pdfLatex(fileName):
    '''Typesets filename using pdflatex'''

    FNULL = open(os.devnull, 'w')
    texfile = 'pdflatex '+fileName
    if texfile.endswith('.tex')==False:
        texfile = texfile+'.tex'
    subprocess.call(texfile,shell=True,stdout=FNULL)
    subprocess.call(texfile,shell=True,stdout=FNULL)

def handout(fileName):
    '''For Beamer lecture slides named fileName, a new file is created the preamble is modified to inclue the handout option.'''

    with open(fileName+'.tex') as oldLines, open('Handout'+fileName[6:]+'.tex', "w") as newLines:
        for n,line in enumerate(oldLines):
            if n==0:
                newLines.write(line[0:15]+'handout,'+line[15:])
            else:
                newLines.write(line)

def createHandouts(slideList):
    '''Returns a list of handout file names for each file name in slideList'''

    handoutList=[]
    for s in slideList:
        handoutList.append('Handout'+s[6:])
        handout(s)
    return handoutList

def pythonScript(script):
    '''Runs python. script can be either a string or a list of strings.'''

    if type(script)==str:
        if script.endswith('.py')==False:
            script = script+".py"
        run = subprocess.call("python "+script, shell=True)
    else:
        for s in script:
            if s.endswith('.py')==False:
                s = s+".py"
            run = subprocess.call("python "+s, shell=True)

def exportNb(notebookName):
    '''Exports the ipython notebook file notebookName to a python script'''
    if notebookName.endswith('.ipynb')==False:
        notebookName = notebookName+'.ipynb'
    run = subprocess.call('ipython nbconvert '+notebookName+' --to python', shell=True)
    with open(notebookName[:-6]+'.py') as Lines, open('file.tmp', "w") as newLines:
        for n,line in enumerate(Lines):
            if line[0:13]=='get_ipython()':
                newLines.write('# '+line[0:])
            else:
                newLines.write(line)
    os.remove(notebookName[:-6]+'.py')
    os.rename('file.tmp',notebookName[:-6]+'.py')