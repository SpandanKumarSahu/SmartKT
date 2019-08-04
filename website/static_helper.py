from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os

def to_dot (li, fn):
    with open(fn + '.dot', 'w') as fp:
        fp.write('digraph G{\n')
        for el in list(set(li)):
            fp.write('"{}"->"{}"[label="{}"]\n'.format(el[0], el[1], el[2]))
        fp.write('}\n')
    os.system("dot -Tpng {}.dot -o {}.png".format(fn, fn))

def classmap():
    tree = ET.parse("final.xml")
    root = tree.getroot()
    ls = []
    for file in root:
        for c in file.findall(".//class_t"):
            base_classes = c.find("base_classes")
            if base_classes is not None:
                for x in base_classes.findall(".//class"):
                    if x.find("virtual_inheritance").attrib['value'] == "True":
                        ls.append((c.attrib['value'], x.attrib['value'][2:], "virtual " +
                        x.find("access_type").attrib['value'] ))
                    else:
                        ls.append((c.attrib['value'], x.attrib['value'][2:],
                        x.find("access_type").attrib['value'] ))
    filename = "classmap"
    to_dot(ls, filename)
    return filename + ".png"

def findvar(el, varname):
    path = varname.split('::')
    for locn in path:
        el = el.find('.//*[@spelling="{}"]'.format(locn))
    return el

def analyze_pattern():
    pass

if __name__ == "__main__":
    print(classmap())
