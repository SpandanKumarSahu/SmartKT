import sys
from xml.etree import ElementTree as ET

def getsign(func):
    if 'mangled_name' in func.attrib:
        func_name = func.attrib['mangled_name']
    else:
        func_name = func.attrib['spelling']
    row = func_name + '\t'
    ret = (func.attrib['type'].split('('))[0]
    argc = 0
    args = ''
    for parm in func:
        if parm.tag == 'PARM_DECL':
            argc += 1
            args += (parm.attrib['type'] + '\t')
    row += str(argc) + '\t' + args + ret.strip()
    return row

def generate_funcinfo(node, fname):
    outfile = (filename.split('/')[-1]).split('.')[0]+'.funcargs'
    with open(outfile, 'w') as f:
        s = ''
        # Get pure functions
        for func in croot.findall('.//FUNCTION_DECL'):
            s += getsign(func) + '\n'
        if(len(s) > 0):
            f.write(s)

        s = ''
        # Get all class methods
        for func in croot.findall('.//CXX_METHOD'):
             s += getsign(func) + '\n'
        if(len(s) > 0):
            f.write(s)

    print('Function Signatures written to: ', outfile)


filename = sys.argv[1]
croot = ET.parse(filename).getroot()
generate_funcinfo(croot, filename)