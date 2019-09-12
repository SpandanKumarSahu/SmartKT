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

isClean = False
if sys.argv[1] == "clean":
    isClean = True
project_name = sys.argv[2]
vocab_file = sys.argv[3]
problem_domain_file = sys.argv[4]
executable = sys.argv[5]
test_input = None
if len(sys.argv) > 6:
    test_input = sys.argv[6]

(dependencies, sourcefile, objectfile) = pickle.load(open("dependencies.p", "rb"))

# [TODO]
# Instead of combining by exclusive parsing, we can simply echo out to file
# See combine_all_domain.sh, for example

def combine(ls, execpath):
    # Takes a list of CPP files, and outputs a single XML file, a concatenation
    # of (Clang+PYGCCXML) of each related CPP
    global project_name
    root = Element("EXEC_STATIC")
    root.set("executable", execpath)
    ls = ['/'.join(x.split('/')[x.split('/').index(project_name):]) for x in ls]
    ls = [x.split('.')[0]+"_combined.xml" for x in ls]
    for x in ls:
        stree = ET.parse(x)
        sroot = stree.getroot()
        root.append(sroot)
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    filename = "static.xml"
    with open(filename, "w") as f:
        f.write(xmlstr)

def get_linkage_helper(filename):
    os.system("python parsers/linkerHelper.py "+ filename)

def generate_static_info(execpath):
    # This function extract the dependencies of the binary under study, and
    # recursively finds out the list of source files responsible for this executable
    # and gets the executable's DWARF information and concats them
    print("Starting Static!")
    global dependencies, sourcefile, objectfile
    abspath = os.path.abspath(execpath)

    ls = dependencies[abspath]
    for x in dependencies[abspath]:
        if x[-2:] != '.o':
            ls.extend(dependencies[x])
            ls.remove(x)
    src_files = [sourcefile[x] for x in ls]
    combine(src_files, execpath)
    get_linkage_helper("static.xml")
    print("Static Done!")
    return "static.xml"

def generate_dynamic_info(path, test=None):
    # Add dynamic_information to the combined static XML
    print("Starting Dynamic!")
    if test is None:
        os.system("./pin.sh {}".format(path))
    else:
        os.system("./pin.sh {} {}".format(path, test))
    print("Dynamic Done!")
    return "dynamic.xml"

def generate_comments_info(project_name, vocab_file, problem_domain_file):
    # Return relative path (wrt to this file) to the comments' XML output
    print("Starting Comments!")
    if not os.path.exists("comments/temp"):
        os.mkdir("comments/temp")
    if not os.path.exists("comments/temp/"+project_name):
        os.mkdir("comments/temp/"+project_name)
    os.system("python2 comments/GenerateCommentsXMLForAFolder.py /workspace/projects/ " + project_name + 
    	" /workspace/" + project_name + " " + vocab_file + " " + problem_domain_file+ " " + 
    	"/workspace/comments/temp/"+project_name)
    os.system("python2 comments/MergeAllCommentsXML.py " + "/workspace/comments/temp/" + project_name + 
    	" /workspace/" + project_name + " " + "/workspace/projects/"+ project_name + 
    	" /workspace/comments.xml")
    print("Comments Done!")
    return "comments.xml"

def generate_vcs_info(project_name):
    print("Starting VCS!")
    os.system("python vcs.py")
    print("VCS Done!")
    return "vcs.xml"

def start_website():
    # Start the user inerface to query
    os.system("cp static.xml website/static.xml")
    os.system("cp dynamic.xml website/dynamic.xml")
    os.system("cp vcs.xml website/vcs.xml")    
    os.system("cp comments.xml website/comments.xml")
    os.system("cp dependencies.p website/dependencies.p")
    os.chdir("website")
    os.system("chmod +x setup.sh")
    os.system("./setup.sh")

static_file = generate_static_info(executable)
abspath = os.path.abspath(executable)
dynamic_file = generate_dynamic_info(executable, test_input)
if isClean:
    comments_file = generate_comments_info(project_name, vocab_file, problem_domain_file)
    vcs_file = generate_vcs_info(project_name)
start_website()
