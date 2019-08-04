import sys
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom

def set_offsets(cnode, dnode):
    # Add linkage_name if there:
    if "linkage_name" in dnode.attrib:
        cnode.set("linkage_name", dnode.attrib['linkage_name'])

    # Variable declarations
    for var in dnode.findall(".//variable"):
        linenum = int(var.attrib['decl_line'], 16)
        for v in cnode.findall(".//VAR_DECL"):
            if v.attrib['linenum'] == str(linenum) and v.attrib['spelling'] == var.attrib['name']:
                v.set('offset', str(int(var.attrib['location'].split()[-1]) + 16))

    # Function params handler
    for parm in dnode.findall(".//formal_parameter"):
        if 'name' in parm.attrib:
            if parm.attrib['name'] == "this":
                sub = SubElement(cnode, "THIS_PARM_ARTIFICIAL")
                sub.set("id", parm.attrib['id'])
                sub.set("spelling", parm.attrib['name'])
                try:
                    sub.set("offset", str(int(parm.attrib['location'].split()[-1]) + 16))
                except:
                    # Constructors don't have offset information
                    continue
                sub.set("linenum", cnode.attrib['linenum'])
                for this_decl in cnode.findall(".//*[@spelling='this']"):
                    try:
                        this_decl.set('offset', str(int(var.attrib['location'].split()[-1]) + 16))
                    except:
                        continue
            else:
                for p in cnode.findall(".//PARM_DECL"):
                    if p.attrib['spelling'] == parm.attrib['name']:
                        try:
                            p.set('offset', str(int(parm.attrib['location'].split()[-1]) + 16))
                        except:
                            continue
    return cnode

def get_type(id):
    global root
    type=root.find(".//*[@id='" + str(id) + "']")
    return type

def match_signature(cnode, dnode):
    return True

dwarfxml_filename = sys.argv[1]
clangxml_filename = sys.argv[2]

dtree = ET.parse(dwarfxml_filename)
droot = dtree.getroot()
ctree = ET.parse(clangxml_filename)
croot = ctree.getroot()
dparent_map = dict((c, p) for p in droot.getiterator() for c in p)
cparent_map = dict((c, p) for p in croot.getiterator() for c in p)

# add offsets from dwarf to clang
# for structs we are already getting offset information
for dfunc in droot.findall(".//subprogram"):
    found = False

    if 'decl_line' not in dfunc.attrib:
        continue

    # First filter on the basis of line number
    for cfunc in croot.findall(".//FUNCTION_DECL"):
        if cfunc.attrib['linenum'] == str(int(dfunc.attrib['decl_line'], 16)):
            if match_signature(cfunc, dfunc):
                cfunc = set_offsets(cfunc, dfunc)
                found = True
                break
    if not found:
        for cfunc in croot.findall(".//CXX_METHOD"):
            if cfunc.attrib['linenum'] == str(int(dfunc.attrib['decl_line'], 16)):
                if match_signature(cfunc, dfunc):
                    cfunc = set_offsets(cfunc, dfunc)
                    found = True
                    break
    if not found:
        for cfunc in croot.findall(".//CONSTRUCTOR"):
            if cfunc.attrib['linenum'] == str(int(dfunc.attrib['decl_line'], 16)):
                if match_signature(cfunc, dfunc):
                    cfunc = set_offsets(cfunc, dfunc)
                    found = True
                    break
    if not found:
        for cfunc in croot.findall(".//DESTRUCTOR"):
            if cfunc.attrib['linenum'] == str(int(dfunc.attrib['decl_line'], 16)):
                if match_signature(cfunc, dfunc):
                    cfunc = set_offsets(cfunc, dfunc)
                    found = True
                    break
    if not found:
        for c in croot.findall(".//CLASS_DECL"):
            if c.attrib['spelling'] == dparent_map[dfunc].attrib['name'] and c.attrib['linenum'] == str(int(dparent_map[dfunc].attrib['decl_line'], 16)):
                sub = SubElement(c,"CONSTRUCTOR" )
                sub.set("spelling", dfunc.attrib['name'])
                sub.set("linkage_name", dfunc.attrib['linkage_name'])
                sub.set("parent_id", c.attrib['id'])
                sub.set("type", "CONSTRUCTOR")
    # match function signatures to handle function overloading

xmlstr = minidom.parseString(ET.tostring(croot)).toprettyxml(indent="   ")
filename = clangxml_filename.split('.')[0][:-6] + "_combined.xml"
with open(filename, "w") as f:
    f.write(xmlstr)
print("File written to: ", filename)
