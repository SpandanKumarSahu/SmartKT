# To use:
# python linkerHelper.py <DWARF+CLANG XML>

import sys
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom

def generate_function(node, filename):
    # Search for all functions and prints it name, linkage_name and id
    outfile = filename.split('.')[0]+".func"
    with open(outfile, "w") as f:
        for func in node.findall(".//FUNCTION_DECL"):
            if "linkage_name" in func.attrib:
                func_name = func.attrib['linkage_name']
            else:
                func_name = func.attrib['spelling']
            s = func_name + "\t" + func.attrib['id'] + "\n"
            f.write(s)
        for func in node.findall(".//CXX_METHOD"):
            if "linkage_name" in func.attrib:
                func_name = func.attrib['linkage_name']
            else:
                func_name = func.attrib['spelling']
            s = func_name + "\t" + func.attrib['id'] + "\n"
            f.write(s)
    print("Function ID File written to: ", outfile)
        # for func in node.findall(".//FUNCTION_DECL"):
        #     f.write(func.attrib['spelling'], "\t", func.attrib['id'])
        #

def generate_var(node, filename):
    # For all variable declarations, print the function it belongs to, the id of
    # the function, the id of the variable and the parent of the variable
    outfile = filename.split('.')[0]+".offset"
    with open(outfile, "w") as f:
        for func in node.findall(".//FUNCTION_DECL"):
            if "linkage_name" in func.attrib:
                func_name = func.attrib['linkage_name']
            else:
                func_name = func.attrib['spelling']
            for var in func.findall(".//VAR_DECL"):
                if 'offset' not in var.attrib:
                    continue
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\n"
                f.write(s)
            for var in func.findall(".//PARM_DECL"):
                if 'offset' not in var.attrib:
                    continue
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\n"
                f.write(s)
        for func in node.findall(".//CXX_METHOD"):
            if "linkage_name" in func.attrib:
                func_name = func.attrib['linkage_name']
            else:
                func_name = func.attrib['spelling']
            for var in func.findall(".//VAR_DECL"):
                if 'offset' not in var.attrib:
                    continue
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\n"
                f.write(s)
            for var in func.findall(".//PARM_DECL"):
                if 'offset' not in var.attrib:
                    continue
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\n"
                f.write(s)
            for var in func.findall(".//THIS_PARM_ARTIFICIAL"):
                if 'offset' not in var.attrib:
                    continue
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\n"
                f.write(s)
    print("Variable Offset File written to: ", outfile)

filename = sys.argv[1]
tree = ET.parse(filename)
root = tree.getroot()

# generate_function(root, filename)
generate_var(root, filename)
