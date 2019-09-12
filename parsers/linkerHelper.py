# python linkerHelper.py <DWARF+CLANG XML>

import sys, os
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

def helper(var, var_class, var_container=None):
    if "mangled_name" in var.attrib:
        var_name = var.attrib['mangled_name']
    else:
        var_name = var.attrib['spelling']
    s = var_name + "\t" + var.attrib['id'] + "\t" + var.attrib['type'] + \
     "\t"+ var.attrib['size'] + "\t"+ var.attrib['parent_id'] + "\t" + var_class
    if var_container is not None:
        s += "\t" + var_container
    s += "\n"
    return s

def generate_var(croot, filename):
    # writing globals
    # NAME ID TYPE SIZE PARENT_ID CLASS CONTAINER
    outfile = filename.split('.')[0]+"_global.offset"
    printed = set()
    with open(outfile, "w") as f:
        # First out all global variables
        s = ""
        for var in croot.findall('file/STATICROOT/TRANSLATION_UNIT/VAR_DECL[@storage_class]'):
            # if 'storage_class' in var.attrib and var.attrib['is_definition']:
            if var.attrib['storage_class'] == "STATIC":
                s += helper(var, "STATIC")
            # mention globals only once
            else:
                if "mangled_name" in var.attrib:
                    var_name = var.attrib['mangled_name']
                else:
                    var_name = var.attrib['spelling']
                if var_name not in printed:
                    printed.add(var_name)
                    s += helper(var, "GLOBAL")

        f.write(s)

        # Get all static variables from functions (Pure functions)
        for func in croot.findall('.//FUNCTION_DECL'):
            if "mangled_name" in func.attrib:
                func_name = func.attrib['mangled_name']
            else:
                func_name = func.attrib['spelling']
            s = ""
            for var in func.findall('.//VAR_DECL[@storage_class="STATIC"]'):
                s += helper(var, "FUNCSTATIC", func_name)
            if(len(s) > 0):
                f.write(s)

        # Get all static variables from functions (Class Methods)
        for func in croot.findall('.//CXX_METHOD'):
            if "mangled_name" in func.attrib:
                func_name = func.attrib['mangled_name']
            else:
                func_name = func.attrib['spelling']
            s = ""
            for var in func.findall('.//VAR_DECL[@storage_class="STATIC"]'):
                s += helper(var, "FUNCSTATIC", func_name)
            if(len(s) > 0):
                f.write(s)

        # Get all static variables from classes
        for c in croot.findall('.//CLASS_DECL'):
            if "mangled_name" in c.attrib:
                class_name = c.attrib['mangled_name']
            else:
                class_name = c.attrib['spelling']
            s = ""
            for var in c.findall('./VAR_DECL[@storage_class="STATIC"]'):
                s += helper(var, "CLASSSTATIC", class_name)
            if(len(s) > 0):
                f.write(s)

        # Get all static variables from classes
        for c in croot.findall('.//STRUCT_DECL'):
            if "mangled_name" in c.attrib:
                struct_name = c.attrib['mangled_name']
            else:
                struct_name = c.attrib['spelling']
            s = ""
            for var in c.findall('./VAR_DECL[@storage_class="STATIC"]'):
                s += helper(var, "STRUCTSTATIC", struct_name)
            if(len(s) > 0):
                f.write(s)
    print("Global Offset File written to: ", outfile)

    # For all variable declarations, print the function it belongs to, the id of
    # the function, the id of the variable and the parent of the variable
    # FUNCTION OFFSET ID VARIABLE TYPE SIZE PARENT_ID
    outfile = filename.split('.')[0]+".offset"
    with open(outfile, "w") as f:
        for func in croot.findall(".//FUNCTION_DECL"):
            if "mangled_name" in func.attrib:
                func_name = func.attrib["mangled_name"]
            elif "linkage_name" in func.attrib:
                func_name = func.attrib['linkage_name']
            else:
                func_name = func.attrib['spelling']
            for var in func.findall(".//VAR_DECL[@offset]"):
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\t"+ var.attrib['type']\
                 + "\t"+ var.attrib['size'] + "\t"+ var.attrib['parent_id'] + "\n"
                f.write(s)
            for var in func.findall(".//PARM_DECL[@offset]"):
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\t"+ var.attrib['type']\
                 + "\t"+ var.attrib['size'] + "\t"+ str(var.attrib['parent_id']) + "\n"
                f.write(s)
        for func in croot.findall(".//CXX_METHOD"):
            if "mangled_name" in func.attrib:
                func_name = func.attrib["mangled_name"]
            elif "linkage_name" in func.attrib:
                func_name = func.attrib['linkage_name']
            else:
                func_name = func.attrib['spelling']
            for var in func.findall(".//VAR_DECL[@offset]"):
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\t"+ var.attrib['type']\
                 + "\t"+ var.attrib['size']+ "\t"+ str(var.attrib['parent_id']) + "\n"
                f.write(s)
            for var in func.findall(".//PARM_DECL[@offset]"):
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling'] + "\t"+ var.attrib['type']\
                 + "\t"+ var.attrib['size']+ "\t"+ str(var.attrib['parent_id']) + "\n"
                f.write(s)
            for var in func.findall(".//THIS_PARM_ARTIFICIAL[@offset]"):
                s = func_name + "\t" + str(abs(int(var.attrib['offset']))) + "\t"\
                 + var.attrib['id'] + "\t" + var.attrib['spelling']+ "\t"+ var.attrib['type']\
                 + "\t"+ var.attrib['size']+ "\t"+ str(var.attrib['parent_id']) + "\n"
                f.write(s)
    print("Variable Offset File written to: ", outfile)

def fix_global_address(droot, croot):
    for dvar in droot.findall("variable"):
        # Can't set global address for external global headers
        if 'external' in dvar.attrib:
            continue

        # For everything else, find the appropriate file and set address
        linenum = int(dvar.attrib['decl_line'], 16)
        fname = str(dvar.attrib['decl_file'].split()[-1])

        cfile = croot.find('file[@name="'+fname+'"]').find("STATICROOT")
        for cvar in cfile.findall("TRANSLATION_UNIT/VAR_DECL[@linenum='"+str(linenum)+"']"):
            if cvar.attrib['spelling'] == dvar.attrib['name']:
                cvar.set('offset', str(int(dvar.attrib['location'].split()[-1], 0)))


filename = sys.argv[1]
project = sys.argv[2]
exefile = sys.argv[3]

dest = '/'.join(exefile.split('/')[exefile.split('/').index(project):])

croot = ET.parse(filename).getroot()

# Generate dwarfdump for the executable
os.system("dwarfdump "+exefile+" > "+dest+".dwarfdump")

# Generate XML from the dwarfdump parse
os.system("python parsers/dwarfdump_parser.py "+dest+".dwarfdump")

# Update global vars offset
droot = ET.parse(dest+"_dwarfdump.xml").getroot()
fix_global_address(droot, croot)

# generate_function(root, filename)
generate_var(croot, filename)

