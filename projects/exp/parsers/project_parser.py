import re
import os
import sys
import pprint
import pickle

#[TODO]: Support more compilers, for projects that are multi-lingual (NOT A PRIORITY)
# The compiler used by the project. In the docker, it is `/usr/bin/cc` for C and '/usr/bin/c++' for C++
C_COMPILER = '/usr/bin/cc '
CXX_COMPILER = '/usr/bin/c++ '

#[TODO]: Implement support for other archivers (NOT A PRIORITY)
STATIC_ARCHIVER = '/usr/bin/ar '

CHANGE_DIRECTORY_CMD = 'cd '

# filename: The make_log.txt file, which contains the verbose output of the build
# We try to extract various dependencies using this file
filename = sys.argv[1]

with open(filename, 'r') as f:
    data = f.readlines()
'''
We open the make_log.txt file and try to find 3 types of essential commands:
1. CXX_COMMANDS: These commands including compiling and linking instructions 
                (line num, last cd command, cxx command)
2. CD_COMMANDS: We use these commands to keep track of the directory of the files
                we are compiling/linking
                (line num, cd command)
3. AR_COMMANDS: Archiving commands. Combine multiple object files into one.
                (line num, last cd command, ar command)

The algorithm is pretty simple. The way CMake generates the Makefile and the way
Makefile builds objects and binaries, is very standard, making the parsing
straightforward. We are just looking for the occurance of the three commands
mentioned above, and store relevant information in lists.
'''
cxx_cmds = []
cd_cmds = []
static_link_cmds = []
cur_path = ''

for line_num, x in enumerate(data):
    # expects only one cd in any command - true for cmake generated and any other sensible make file
    if CHANGE_DIRECTORY_CMD in x:
        temp_ls = x.split()
        cd_index = temp_ls.index(CHANGE_DIRECTORY_CMD.strip())
        # check for relative cd's... will see if useful with libpng @VISHESH
        cd_path = temp_ls[cd_index+1]
        if cd_path[0] != '/':
            if cur_path == '':
                print (cd_path)
                print (line_num, x)
                raise Exception('Not an absolute address. Anything may go wrong now.')
            cd_path = cur_path + '/' + cd_path
        cd_path = os.path.abspath(cd_path)
        cur_path = cd_path
        cd_cmd = CHANGE_DIRECTORY_CMD + cd_path
        # end of check
        cd_cmds.append((line_num, cd_cmd))
        # again, expects only one cxx in any command - true for cmake generated and any other sensible make file
        if CXX_COMPILER in x: 
            cxx_cmds.append((line_num, cd_cmds[-1][1], ' '.join(temp_ls[temp_ls.index(CXX_COMPILER.strip()):])))
        if C_COMPILER in x: 
            cxx_cmds.append((line_num, cd_cmds[-1][1], ' '.join(temp_ls[temp_ls.index(C_COMPILER.strip()):])))
    # again, expects only one cxx in any command - true for cmake generated and any other sensible make file
    elif CXX_COMPILER.strip() in x:
        # need to check why this ';' split is required @VISHESH
        cxx_cmds.append((line_num, cd_cmds[-1][1], ' '.join(x[x.index(CXX_COMPILER.strip()):].strip().split(';'))))
    elif C_COMPILER in x: 
        cxx_cmds.append((line_num, cd_cmds[-1][1], ' '.join(x[x.index(C_COMPILER.strip()):].strip().split(';'))))
    elif STATIC_ARCHIVER in x:
        static_link_cmds.append((line_num, cd_cmds[-1][1], x.strip()))

for u in cd_cmds:
    print (u)
print
for u in cxx_cmds:
    print (u)
print
for u in static_link_cmds:
    print (u)
print


dependencies = {}
objectfile = {}
sourcefile = {}

# For this small project, it is sufficient to print this
for line_num, path, data in cxx_cmds: # these commands create some executable
    cwd = path.split()[1]
    d = data.split()
    if '-o' not in d:
        # default for linux systems
        executable = cwd+'/a.out'
    else:
        executable = d[d.index('-o')+1]
        if executable[0] != '/':
            executable = cwd+'/'+executable
        executable = os.path.abspath(executable)
    # an object creation command
    if '-c' in d:
        # again, expecting only one file in here per cxx -c invocation
        # might not be true for a self-made makefile
        filename = os.path.abspath(d[d.index('-c') + 1])
        dependencies[filename] = []
        for x in d:
            # dependencies are in this form -I/include/directory/
            if x[:2] == '-I':
                if x[2] == '/':
                    depname = os.path.abspath(x[2:])
                else:
                    depname = os.path.abspath(cwd+'/'+x[2:])
                dependencies[filename].append('-I'+depname)
        objectfile[filename] = executable
        sourcefile[executable] = filename
    else:
        # must be a linking instruction
        dependencies[executable] = []
        rdynamic_lib = []   # allows for multiple rdynamic links
        linker_opts = ['-rpath', '.']   # by default you look in cwd... i don't completely understand this...
                                        # the manual says you shouldn't but expt run otherwise
        for idx, x in enumerate(d):
            if x[-2:] == '.o' or x[-2:] == '.a' or x[-3:] == '.so':
                if x[0] != '/':
                    x = cwd+'/'+x
                dependencies[executable].append(os.path.abspath(x))
            # cmake links the dynamic libraries via rdynamic by default
            # we will need to check for -l type linkages that are done via -l<whatever> -L<library/paths>
            elif x == '-rdynamic':
                if idx != len(d)-1:
                    rdynamic_lib.append(d[idx+1]) # don't have the absolute path just yet, need to search over rpaths
            # in cmake generated rdynamic links, rpath is passed to the linker as an argument to -Wl
            # so we need to find all options passed via -Wl
            elif x.find('-Wl') != -1:
                linker_opts += x.split(',')[1:]
        rpaths = [linker_opts[i+1] for i, x in enumerate(linker_opts) if x == '-rpath']
        rpaths = [os.path.abspath(u) if u[0] == '/' else os.path.abspath(cwd+'/'+u) for u in rpaths]
        # look for libraries in the rdynamic lookup paths like the linker would have
        for rlib in rdynamic_lib:
            for path in rpaths:
                lib_abspath = os.path.abspath(path+'/'+rlib)
                if os.path.exists(lib_abspath):
                    dependencies[executable].append(lib_abspath)
                    break

# This is for libraries. Libraries are created by combining object files
for line_num, path, data in static_link_cmds:
    cwd = path.split()[1]
    d = data.strip().split()
    # qc is specific to cmake... ar options order guarantees that archive is the third elements (2nd being the options)
    # libfile = cwd+'/'+d[d.index('qc')+1]
    libfile = d[2]
    if libfile[0] != '/':
        libfile = cwd + libfile
    libfile = os.path.abspath(libfile)
    dependencies[libfile] = []
    for x in d:
        if x[-2:] == '.o' or x[-2:] == '.a': # added check for archives getting linked to bigger archives
            if x[0] != '/':
                x = cwd+'/'+x
            dependencies[libfile].append(os.path.abspath(x))

pickle.dump((dependencies, sourcefile, objectfile), open('dependencies.p', 'wb'))
