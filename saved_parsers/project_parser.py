import re
import sys
import pprint
import pickle

# The compiler used by the project. In this example, it would `/usr/bin/cc `
# because it is a C-based project. Assuming default is C++. Can be changed by user
CXX_COMPILER = "/usr/bin/cc "

#[TODO]: Implement support for other archivers (NOT A PRIORITY)
STATIC_ARCHIVER = "/usr/bin/ar "

CHANGE_DIRECTORY_CMD = "cd "

# filename: The make_log.txt file, which contains the verbose output of the build
# We try to extract various dependencies using this file
filename = sys.argv[1]

# for C++ projects, it would be "/usr/bin/c++ "
# for C projects, it would be "/usr/bin/cc "
#[TODO]: Support multiple number of compilers, for projects that are multi-lingual
if len(sys.argv) > 2 and sys.argv[2] == "C++":
    CXX_COMPILER = "/usr/bin/c++ "

with open(filename, "r") as f:
    data = f.readlines()
'''
We open the make_log.txt file and try to find 3 types of essential commands:
1. CXX_COMMANDS: These commands including compiling and linking instructions
2. CD_COMMANDS: We use these commands to keep track of the directory of the files
                we are compiling/linking
3. AR_COMMANDS: Archiving commands. NOT RELEVANT NOW. But this command helps to
                code structure, and if there is a library (internal) being used.
                Might become useful in future

The algorithm is pretty simple. The way CMake generates the Makefile and the way
Makefile builds objects and binaries, is very standard, making the parsing
straightforward. We are just looking for the occurance of the three commands
mentioned above, and store relevant information in lists.
'''
cxx_cmds = []
cd_cmds = []
static_link_cmds = []

for line_num, x in enumerate(data):
    if CHANGE_DIRECTORY_CMD in x:
        if CXX_COMPILER in x:
            temp_ls = x.split()
            cd_cmds.append((line_num, ' '.join(temp_ls[temp_ls.index(CHANGE_DIRECTORY_CMD.strip()):temp_ls.index(CHANGE_DIRECTORY_CMD.strip())+2])))
            cxx_cmds.append((line_num, cd_cmds[-1][1], ' '.join(temp_ls[temp_ls.index(CXX_COMPILER.strip()):])))
        else:
            temp_ls = x.split()
            cd_cmds.append((line_num, ' '.join(temp_ls[temp_ls.index(CHANGE_DIRECTORY_CMD.strip()):temp_ls.index(CHANGE_DIRECTORY_CMD.strip())+2])))
    elif CXX_COMPILER.strip() in x:
        cxx_cmds.append((line_num, cd_cmds[-1][1], ' '.join(x[x.index(CXX_COMPILER.strip()):].strip().split(';'))))
    elif STATIC_ARCHIVER in x:
        static_link_cmds.append((line_num, cd_cmds[-1][1], x.strip()))

dependencies = {}
objectfile = {}
sourcefile = {}

# For this small project, it is sufficient to print this
for line_num, path, data in cxx_cmds:
    cwd = path.split()[1]
    d = data.split()
    if "-c" in d:
        filename = d[d.index("-c") + 1]
        dependencies[filename] = []
        for x in d:
            # dependencies are in this form
            if x[:2] == "-I":
                dependencies[filename].append(x)
        objectfile[filename] = cwd + "/" + d[d.index("-o") + 1]
        sourcefile[cwd + "/" + d[d.index("-o") + 1]] = filename
    else:
        # must be a linking instruction
        executable = cwd + "/" + d[d.index("-o") + 1]
        dependencies[executable] = []
        for idx, x in enumerate(d):
            if x[-2:] == ".o" or x[-2:] == ".a":
                dependencies[executable].append(cwd + "/" + x)
            elif x == "-rdynamic":
                for y in d:
                   if y.find("-rpath") != -1:
                       p = y[y.find("-rpath")+len("-rpath")+1:]
                       while not p[-1].isalnum():
                           p = p[:-1]
                       dependencies[executable].append(p+"/"+d[idx+1]) 

# This is for libraries. Libraries are created by combining object files
for line_num, path, data in static_link_cmds:
    cwd = path.split()[1]
    d = data.strip().split()
    libfile = cwd+"/"+d[d.index('qc')+1]
    dependencies[libfile] = []
    for x in d:
        if x[-2:] == ".o":
            dependencies[libfile].append(cwd + "/" + x)

pickle.dump((dependencies, sourcefile, objectfile), open("dependencies.p", "wb"))
