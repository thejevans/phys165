import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import difflib
from interruptingcow import timeout
import nbformat
from nbconvert import PythonExporter
import timeit

# function to convert a jupyter notebook to a python file
def convertNotebook(notebookPath, modulePath):
    
    with open(notebookPath) as fh:
        nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)
            
    exporter = PythonExporter()
    source, meta = exporter.from_notebook_node(nb)

    with open(modulePath, 'wb') as fh:
        fh.writelines([source.encode('utf-8')])

# read in submission directory
directory = sys.argv[1] if sys.argv[1][-1:] == '/' else ''.join([sys.argv[1],'/'])

comments = []

filenames = sorted(os.listdir(directory))

# grading loop
for filename in filenames:
    err = 'none'
    print(filename)
    # if file is a jupyter notebook, convert it to a python file
    if filename.endswith(".ipynb"):
        convertNotebook(''.join([directory,filename]), ''.join([directory,filename[:-6],'.py']))
        filename = ''.join([filename[:-6],'.py'])
        print(filename)
    # if file is a python file, try to run it
    if filename.endswith(".py"):
        start = timeit.default_timer()
        try:
            with open(''.join([directory,filename])) as file, timeout(120, exception=RuntimeError):
                exec(file.read())
                # show any plots created in the file using matplotlib
                plt.show()
                plt.close()
        except Exception as e:
            print('There was an error: ' + str(e))
            err = str(e)
            pass
        stop = timeit.default_timer()
    comments.append((filename, str(err), stop-start, 'True' if filename.endswith(".py") else 'False', input("Comments: ")))

# save grading csv
df = pd.DataFrame(comments, columns = ['Filename','Error','Runtime','.py file','Comments'])
df.to_csv(''.join([directory,'grades.csv']))

code = []
pyfiles = []

# diff loop to check file similarity
for filename in filenames:
    if filename.endswith(".py"):
        pyfiles.append(filename[:filename.find('_')])
        with open(''.join([directory,filename])) as file:
            code.append(file.read())

# build similarity matrix
diffs = [[difflib.SequenceMatcher(None, x, y).ratio() for x in code] for y in code]
# change main diag to 0s for easier conditional formatting of output
diffs = [[diffs[x][y] if diffs[x][y] != 1 else 0 for x in range(len(diffs))] for y in range(len(diffs))]
# average to make symmetric
sym_diffs = [[(diffs[x][y]+diffs[y][x])/2 for x in range(len(diffs))] for y in range(len(diffs))]

# save similarity matrix
df = pd.DataFrame(sym_diffs, columns = pyfiles)
df.to_csv(''.join([directory,'sym_diffs.csv']))
