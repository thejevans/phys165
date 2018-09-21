import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import difflib

directory = sys.argv[1]

comments = []

filenames = sorted(os.listdir(directory))

# grading loop
for filename in filenames:
    err = 'none'
    print(filename)
    if filename.endswith(".py"):
        try:
            with open(''.join([directory,filename])) as file:
                exec(file.read())
                plt.show()
                plt.close()
        except Exception as e:
            print('There was an error: ' + str(e))
            err = str(e)
            pass
    comments.append((filename, str(err), 'True' if filename.endswith(".py") else 'False', input("Comments: ")))

# save grading csv
df = pd.DataFrame(comments, columns = ['Filename','Error','.py file','Comments'])
df.to_csv(''.join([directory,'grades.csv']))

code = []
pyfiles = []

# diff loop
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
