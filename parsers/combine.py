from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
from collections import defaultdict
import sys

DEBUG = False

dwarfxml_filename = sys.argv[1]
clangxml_filename = sys.argv[2]
dtree = ET.parse(dwarfxml_filename)
droot = dtree.getroot()

ctree = ET.parse(clangxml_filename)
croot = ctree.getroot()

dtree_hashmap = defaultdict(list) # contains global constructs hash
dtree_subtree_hash = defaultdict(list) # contains local variables and formal parameter hash

#variable comparison basis
def variable_hash(dnode):
    return ('variable', dnode.attrib['decl_file'].split()[1], 
        str(int(dnode.attrib['decl_line'], 16)), dnode.attrib['name'])

#variable comparison basis
def variable_hash_cnode(v):
    return ('variable', v.attrib['location'].split('[')[0], v.attrib['linenum'],v.attrib['spelling'])

# Parameter comparison basis
def parameter_hash(dnode):
    return ('parameter', dnode.attrib['name'])

# Build Hash of all variables and formal parameters of a Scope
def subtree_hash_builder(dnode,cnode):
    if(DEBUG):
        print(dnode,cnode)
    # add variables into hash
    if dnode.tag=="variable" and 'decl_line' in dnode.attrib:
        dtree_subtree_hash[variable_hash(dnode)].append(dnode)

    # add formal parameters
    if dnode.tag=="formal_parameter":
        if 'name' in dnode.attrib:
            if dnode.attrib['name'] == "this":
                sub = SubElement(cnode, "THIS_PARM_ARTIFICIAL")
                sub.set("id", dnode.attrib['id'])
                sub.set("spelling", dnode.attrib['name'])
                try:
                    sub.set("offset", str(int(dnode.attrib['location'].split()[-1]) + 16))
                    sub.set("linenum", cnode.attrib['linenum'])
                    for this_decl in cnode.findall(".//*[@spelling='this']"):
                        if(DEBUG):
                            print(dnode,this_decl)
                        this_decl.set('offset', str(int(dnode.attrib['location'].split()[-1]) + 16))
                    
                except Exception as e:
                    print(e)
            else:
                dtree_subtree_hash[parameter_hash(dnode)].append(dnode)
    
    for child in dnode:
        subtree_hash_builder(child,cnode)

def patch_offset(cnode, dnode):
    m = dnode.attrib['location'].split()
    if m[-2] == 'DW_OP_addr':
        cnode.set('address', str(int(m[-1], 16)))
    elif m[-2] == 'DW_OP_fbreg':
        cnode.set('offset', str(abs(int(m[-1], 10) + 16)))
    return cnode

def set_offsets_by_hash(cnode, dnode):
    if(DEBUG):
        print(cnode.tag,"   ",dnode.tag)

    if cnode.tag == 'VAR_DECL':
        if 'location' in dnode.attrib:
            cnode = patch_offset(cnode, dnode)
        return cnode

    # Add linkage_name(mangle name) if there:
    if "linkage_name" in dnode.attrib:
        cnode.set("linkage_name", dnode.attrib['linkage_name'])

    dtree_subtree_hash.clear()
    subtree_hash_builder(dnode,cnode)

    #print(dtree_subtree_hash)
    # Variable declarations
    for v in cnode.findall(".//VAR_DECL"):
        if(DEBUG):
            print(('variable',v.attrib['linenum'],v.attrib['spelling']))
        for var in dtree_subtree_hash[variable_hash_cnode(v)]:
            if(DEBUG):
                print(var,v)
            try:
                v = patch_offset(v, var)
            except Exception as e:
                print ('An Exception occured: ', e)
                print(('variable',v.attrib['linenum'],v.attrib['spelling']))
                print(var)

    for p in cnode.findall(".//PARM_DECL"):
        for parm in dtree_subtree_hash[('parameter',p.attrib['spelling'])]:
            if(DEBUG):
                print(parm,p)
            p.set('offset', str(int(parm.attrib['location'].split()[-1]) + 16))
            
    return cnode


cnodeUpdateTag = ['FUNCTION_DECL','CXX_METHOD','CONSTRUCTOR','DESTRUCTOR']

def matchNeeded(cnode, level):
    if cnode.tag == 'VAR_DECL' and level == 3:
        return True
    return cnode.tag in cnodeUpdateTag

def ExactMatch(cnode,dnode):
    if(DEBUG):
        print("CNODE")
        print(cnode.tag, variable_hash_cnode(cnode))
        print("\nDNODE")
        print(dnode.tag, variable_hash(dnode))
        print '\n\n'
    return True

def GetDNodeHash(dnode):
    return (dnode.attrib['decl_file'].split()[1], str(int(dnode.attrib['decl_line'], 16)), dnode.attrib['name'])

def GetCNodeHash(cnode):
    return (cnode.attrib['location'].split('[')[0], cnode.attrib['linenum'], cnode.attrib['spelling'])

# DFS on the dwarfdump tree to create hashmap

def CreateHashMapDtree(dnode, level):
    if dnode.tag == 'variable' and level == 2:
        dtree_hashmap[GetDNodeHash(dnode)].append(dnode)
    elif dnode.tag=='subprogram' and  'decl_line' in dnode.attrib:
        dtree_hashmap[GetDNodeHash(dnode)].append(dnode)
    for child in dnode:
        CreateHashMapDtree(child,level+1)

# DFS on the Clang_tree to update
def UpdateCtree(cnode,level):
    if matchNeeded(cnode, level):
        potential_match = dtree_hashmap[GetCNodeHash(cnode)]
        if DEBUG:
            # if cnode.tag == 'VAR_DECL':
                # print (variable_hash_cnode(cnode))
                # print (len(potential_match))
            if (len(potential_match) > 0):
                print (variable_hash_cnode(cnode))
                print([(u.tag, u.attrib['name']) for u in potential_match])
            #check in line number hashmap if any potentials
        #can be improved to incorporate tuples as needed
        for dnode in potential_match:
            if ExactMatch(cnode,dnode):
                # match with the first exact match
                set_offsets_by_hash(cnode,dnode)
                break

    for child in cnode:
        UpdateCtree(child,level+1)


CreateHashMapDtree(droot,0)
# if(DEBUG):
#     for k, v in dtree_hashmap.iteritems():
#         print(k, [(u.tag, u.attrib['name']) for u in v])
UpdateCtree(croot,0)

xmlstr = minidom.parseString(ET.tostring(croot)).toprettyxml(indent="   ")
filename = clangxml_filename.split('.')[0][:-6] + "_combined.xml"
with open(filename, "w") as f:
    f.write(xmlstr)
print("File written to: ", filename)