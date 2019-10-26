# Before you can use, specify the details in config.txt file
# To use:
# python examine.py <clean/retain> <project_name> <vocab_file> <problem_domain_file> <path_to_executable> {path_to_input_file}


'''
Dynamic information is available for executables only. So we combine all static
information from multiple CPP files into one XML and then add the dynamic_information
into the XML. For more details, read the report.
'''

import sys, pickle, os
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom

project_name = sys.argv[1]
executable = sys.argv[2]
test_input = None

CALLDYN = True
CALLCOMM = False
n = 3

if CALLCOMM:
    n = 5
    vocab_file = sys.argv[3]
    problem_domain_file = sys.argv[4]

if len(sys.argv) > n:
    test_input = sys.argv[n]

# isClean = False
# if sys.argv[1] == 'clean':
#     isClean = True
# vocab_file = sys.argv[3]
# problem_domain_file = sys.argv[4]
# executable = sys.argv[5]
# test_input = None
# if len(sys.argv) > 6:
#     test_input = sys.argv[6]

(dependencies, sourcefile, objectfile) = pickle.load(open('dependencies.p', 'rb'))

# [TODO]
# Instead of combining by exclusive parsing, we can simply echo out to file
# See combine_all_domain.sh, for example

def combine_clang(ls, execpath):
    # Takes a list of CPP files, and outputs a single XML file, a concatenation
    # of (Clang+PYGCCXML) of each related CPP
    global project_name
    root = Element('EXEC_STATIC')
    root.set('executable', execpath)
    ls = ['/'.join(x.split('/')[x.split('/').index(project_name):]) for x in ls]
    ls = [x.split('.')[0]+'_clang.xml' for x in ls]
    for x in ls:
        stree = ET.parse(x)
        sroot = stree.getroot()
        root.append(sroot)
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent='   ')
    filename = 'static_clang.xml'
    with open(filename, 'w') as f:
        f.write(xmlstr)

    # generate dwarfdump for exec
    execname = execpath.split('/')[-1]
    os.system('dwarfdump -i ' + execpath + ' > ' + execname + '.dd')
    os.system('python parsers/dwarfdump_parser.py ' + execname + '.dd')
    os.system('python parsers/combine.py ' + execname + '_dwarfdump.xml static_clang.xml ')
    os.system('mv static_combined.xml static.xml')

def combine_calls(ls, execpath):
    # Takes a list of CPP files, and outputs a file containing all calls made within them
    global project_name
    ls = ['/'.join(x.split('/')[x.split('/').index(project_name):]) for x in ls]
    ls = [x.split('.')[0]+'.calls' for x in ls]
    os.system('> static.calls')
    for file in ls:
        os.system('cat ' + file + ' >> static.calls')
    print ('\nCalls collected in final.calls\n')

def get_linkage_helper(filename):
    os.system('python parsers/linkerHelper.py '+ filename)

def generate_static_info(execpath):
    # This function extract the dependencies of the binary under study, and
    # recursively finds out the list of source files responsible for this executable
    # and gets the executable's DWARF information and concats them
    print('Starting Static!')
    global dependencies, sourcefile, objectfile
    abspath = os.path.abspath(execpath)

    ls = dependencies[abspath]
    for x in dependencies[abspath]:
        if x[-2:] != '.o':
            ls.extend(dependencies[x])
            ls.remove(x)
    src_files = [sourcefile[x] for x in ls]
    print (src_files)
    combine_clang(src_files, execpath)
    combine_calls(src_files, execpath)
    get_linkage_helper('static.xml')
    os.system('python parsers/funcinfo_parser.py static.xml')
    print('Static Done!')
    return 'static.xml'

def generate_dynamic_info(path, test=None):
    # Add dynamic_information to the combined static XML
    print('Starting Dynamic!')
    if test is None:
        os.system('./pin.sh {}'.format(path))
    else:
        os.system('./pin.sh {} {}'.format(path, test))
    print('Dynamic Done!')
    return 'dynamic.xml'

def generate_comments_info(project_name, vocab_file, problem_domain_file):
    # Return relative path (wrt to this file) to the comments' XML output
    print('Starting Comments!')
    if not os.path.exists('comments/temp'):
        os.mkdir('comments/temp')
    if not os.path.exists('comments/temp/'+project_name):
        os.mkdir('comments/temp/'+project_name)
    os.system('python2 comments/GenerateCommentsXMLForAFolder.py /workspace/projects/ ' + project_name + 
        ' /workspace/' + project_name + ' ' + vocab_file + ' ' + problem_domain_file+ ' ' + 
        '/workspace/comments/temp/'+project_name)
    os.system('python2 comments/MergeAllCommentsXML.py ' + '/workspace/comments/temp/' + project_name + 
        ' /workspace/' + project_name + ' ' + '/workspace/projects/'+ project_name + 
        ' /workspace/comments.xml')
    print('Comments Done!')
    return 'comments.xml'

def generate_vcs_info(project_name):
    print('Starting VCS!')
    os.system('python vcs.py')
    print('VCS Done!')
    return 'vcs.xml'

def start_website():
    # Start the user inerface to query
    os.system('cp static.xml website/static.xml')
    os.system('cp dynamic.xml website/dynamic.xml')
    os.system('cp vcs.xml website/vcs.xml')    
    os.system('cp comments.xml website/comments.xml')
    os.system('cp dependencies.p website/dependencies.p')
    os.chdir('website')
    os.system('chmod +x setup.sh')
    os.system('./setup.sh')

def collect_results(project_name, executable):
    exec_name = executable.split('/')[-1]
    colpath = project_name + '/' + exec_name
    if not os.path.exists(colpath):
        os.mkdir(colpath)
    os.system('cp dependencies.p ' + colpath)
    os.system('cp static.xml ' + colpath)
    os.system('cp ' + exec_name + '.dd ' + colpath)
    os.system('cp ' + exec_name + '_dwarfdump.xml ' + colpath)
    os.system('cp static_clang.xml ' + colpath)
    os.system('cp static.funcargs ' + colpath)
    os.system('cp static_global.offset ' + colpath)
    os.system('cp static.calls ' + colpath)  
    os.system('cp static.offset ' + colpath) 
    if CALLDYN:
        os.system('cp dynamic.xml ' + colpath)
        os.system('cp PIN/Work/' + exec_name + '* ' + colpath)
        os.system('cp PIN/Work/final* ' + colpath)
    if CALLCOMM:
        os.system('cp comments.xml ' + colpath)
    if CALLDYN and CALLCOMM:
        os.system ('> final_universal.xml')
        os.system ('cat static.xml dynamic.xml comments.xml > final_universal.xml')
        os.system('cp final_universal.xml ' + colpath) 
    print ('Information collected in: ', colpath)


abspath = os.path.abspath(os.path.join(os.getcwd(), executable))
static_file = generate_static_info(abspath)

if CALLDYN:
    dynamic_file = generate_dynamic_info(executable, test_input)
if CALLCOMM:
    comments_file = generate_comments_info(project_name, vocab_file, problem_domain_file)
# if isClean:
#     vcs_file = generate_vcs_info(project_name)
collect_results(project_name, executable)

# start_website()
