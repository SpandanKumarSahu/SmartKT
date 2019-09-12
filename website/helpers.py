from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os

# Input: a list, a filename
# Output: a PNG file by the same name
def to_dot (li, fn):
    with open(fn + '.dot', 'w') as fp:
        fp.write('digraph G{\n')
        for el in list(set(li)):
            if type(el) in [list, tuple]:
                fp.write('"{}"->"{}"[label="{}"]\n'.format(el[0], el[1], el[2]))
            else:
                fp.write('"{}"\n'.format(el))
        fp.write('}\n')
    os.system("dot -Tpng {}.dot -o {}.png".format(fn, fn))

# Input: a list
# Returns: an HTML code
def to_html(li):
    s = "<HTML> <BODY> " + "\n"
    for l in li:
        if type(l) in [list, tuple]:
            s += str("&emsp; ".join(l)) + "<br>"
        else:
            s += str(l) + "<br>"
    s += "</BODY> </HTML>"
    return s

# Input: an XML node
# Ouput: Writes to XML file
def to_xml(xmlnode, filename):
    xmlstr = minidom.parseString(ET.tostring(xmlnode)).toprettyxml(indent="    ")
    with open(filename, "w") as f:
        f.write(xmlstr)

def getfullname(sroot, nid, el = None):
    if el is None:
        el = sroot.find('.//*[@id="{}"]'.format(nid))
    k = []
    if 'spelling' in el.attrib:
        name = ''
        if 'type' in el.attrib and el.attrib['type'] != 'None':
            name += el.attrib['type']
        name = name + ' ' + el.attrib['spelling']
        k = [name]
        if 'parent_id' in el.attrib:
            k.extend(getfullname(sroot, el.attrib['parent_id']))
    return k

def getfunc(sroot, linknm):
    el = sroot.find('.//*[@spelling="{}"]'.format(linknm))
    if el is None:
        el = sroot.find('.//*[@mangled_name="{}"]'.format(linknm))
    elif el is None:
        el = sroot.find('.//*[@linkage_name="{}"]'.format(linknm))
    else:
        return None
    k = getfullname(sroot, 0, el)
    return k
