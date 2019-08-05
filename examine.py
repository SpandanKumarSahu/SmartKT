# To use:
# python examine.py <project_name> <path to executable>


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
(dependencies, sourcefile, objectfile) = pickle.load(open("dependencies.p", "rb"))

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
    filename = "final.xml"
    with open(filename, "w") as f:
        f.write(xmlstr)

def get_linkage_helper(filename):
    os.system("python parsers/linkerHelper.py "+ filename)

def get_combined_file(execpath):
    # This function extract the dependencies of the binary under study, and
    # recursively finds out the list of source files responsible for this executable
    # and gets the executable's DWARF information and concats them
    global dependencies, sourcefile, objectfile
    abspath = os.path.abspath(execpath)

    ls = dependencies[abspath]
    for x in dependencies[abspath]:
        if x[-2:] != '.o':
            ls.extend(dependencies[x])
            ls.remove(x)
    src_files = [sourcefile[x] for x in ls]
    combine(src_files, execpath)
    get_linkage_helper("final.xml")

def add_dynamic_information(path):
    # Add dynamic_information to the combined static XML
    exe = path.split('/')[-1]
    os.system("./pin.sh {} {}".format(path, exe))
    pass

def start_website():
    # Start the user inerface to query
    os.chdir("website")
    os.system("chmod +x start_website.sh")
    os.system("./start_website.sh")

get_combined_file(executable)
add_dynamic_information(executable)
start_website()
