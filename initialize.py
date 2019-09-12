# To use:
# python initialize.py <path to project>
# The last name in the path is assumed the project name

import sys, os, pickle
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom

def combine(clangf, pygccf, cppfile):
    # This function combines the Clang output and PYGCCXML output into one XML
    try:
        ctree = ET.parse(clangf)
        croot = ctree.getroot()
    except:
        croot = Element('CLANG')
    try:
        ptree = ET.parse(pygccf)
        proot = ptree.getroot()
    except:
        proot = Element('PYGCCXML')

    root = Element('file')
    root.set("name", cppfile)
    root.append(croot)
    root.append(proot)
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(clangf, "w") as f:
        f.write(xmlstr)

def init(path, isDebug=False):
    # This function builds the project and in that process gets the make log file
    s = "cd " + path + "\n"
    s += "rm -rf build" + "\n"
    s += "mkdir build"+ "\n"
    s += "cd build"+ "\n"
    if isDebug:
        s += "cmake -DCMAKE_BUILD_TYPE=Debug .."+ "\n"
    else:
        s += "cmake .." + "\n"
    s += "make VERBOSE=1 > make_log.txt"+ "\n"
    s += "cp make_log.txt " + os.getcwd()+ "\n"
    with open("init.sh", "w") as f:
        f.write(s)
    os.system("chmod +x init.sh")
    os.system("./init.sh")
    os.system("rm init.sh")

def dependency_parser(isDebug=False):
    # Parses the make log and presents the output in a format which can be accessed later
    if isDebug:
        dep, src, obj = pickle.load(open("dependencies.p", "rb"))
    os.system("python parsers/project_parser.py make_log.txt")
    if isDebug:
        dep1, src1, obj1 = pickle.load(open("dependencies.p", "rb"))
        dep.update(dep1)
        src.update(src1)
        obj.update(obj1)
        pickle.dump((dep, src, obj), open("dependencies.p", "wb"))

def generate_clang_info(path, isDebug=False):
    # This function is responsible for generating static outputs for CPP files, whose
    # build instruction is available. The final XML contains, static analysis from pygccxml
    # and from Clang
    proj_name = path.split("/")[-1] if len(path.split("/")[-1]) > 0 else path.split("/")[-2]

    # Copy the directory structure of the project
    s = "cd " + path + "\n"
    s += "find . -type d > dirs.txt" + "\n"
    s += "mv dirs.txt " + os.getcwd() + "\n"
    s += "cd " + os.getcwd() + "\n"
    s += "mkdir -p " + proj_name  + "\n"
    s += "mv dirs.txt " + proj_name + "\n"
    s += "cd " + proj_name + "\n"
    s += "xargs mkdir -p < dirs.txt" + "\n"
    with open("cpstruc.sh", "w") as f:
        f.write(s)
    os.system("chmod +x cpstruc.sh")
    os.system("./cpstruc.sh")
    os.system("rm cpstruc.sh")
    os.system("rm "+proj_name+"/dirs.txt")

    # Readin the dependencies using pickle
    (dependencies, sourcefile, objectfile) = pickle.load(open("dependencies.p", "rb"))
    for f in objectfile:
        s = "python parsers/clang_parser.py " + f + " "
        for d in dependencies[f]:
            s += d + " "

        # Generate and copy the clang file
        try:
            os.system(s)
            src_file = f.split('.')[0] + "_clang.xml"
            dest_file = '/'.join(f.split('/')[f.split('/').index(proj_name):]).split('.')[0] + "_clang.xml"
            os.system("mv " + src_file + " " + dest_file)
        except Exception as e:
            print(e)
            continue
        
        if not isDebug:
            os.system("mv " + dest_file + " " + dest_file.split('.')[0][:-6] +"_combined.xml")
            # No need of generating pygcc also, only comments part would need it (comments don't need pygcc)
            continue
            
        # Generate and copy the dwarf file
        try:
            dwarfdump = dest_file.split('.')[0][:-6]+".dwarfdump"
            os.system("dwarfdump " + objectfile[f] + "> " + dwarfdump)
        except Exception as e:
            print(e)
            continue

        # Parse dwarfdump to XML
        try:
            os.system("python parsers/dwarfdump_parser.py "+dwarfdump)
        except:
            continue

        # Combine DWARF and CLANG
        try:
            os.system("python parsers/combine.py "+dwarfdump.split('.')[0]+ "_dwarfdump.xml "+ dest_file)
        except:
            continue

        # [TODO]: Remove PYGCCXML
        # Get PYGCCXML output
        try:
            s = "cd parsers/pygccxml" + "\n"
            s += "python main.py " + f + " "
            for d in dependencies[f]:
                s += d + " "
            s += "\n"
            src_file = f.split('.')[0] + "_pygccxml.xml"
            dest_file = '/'.join(f.split('/')[f.split('/').index(proj_name):]).split('.')[0] + "_pygccxml.xml"
            s += "cd "+ os.getcwd() + "\n"
            s += "mv " + src_file + " " + dest_file
            with open("pygcc.sh", "w") as fl:
                fl.write(s)
            os.system("chmod +x pygcc.sh")
            os.system("./pygcc.sh")
            os.system("rm pygcc.sh")
        except:
            continue

        # Combine files
        try:
            combine(dest_file.split('.')[0][:-8]+"combined.xml", dest_file, f)
        except:
            continue

init(sys.argv[1])
dependency_parser()
generate_clang_info(sys.argv[1])

init(sys.argv[1], True)
dependency_parser(True)
generate_clang_info(sys.argv[1], True)

