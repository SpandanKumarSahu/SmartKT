# To use:
# python combine_static_dynamic.py <staticXML> <dynamicXML>

import sys
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom

sfile = str(sys.argv[1])
dfile = str(sys.argv[2])

stree = ET.parse(sfile)
sroot = stree.getroot()

dtree = ET.parse(dfile)
droot = dtree.getroot()

# Nothing intelligent here. Just concat the two XMLs
root = Element("root")
root.set("id", "-2")
root.append(sroot)
root.append(droot)
xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
filename = dfile.split('.')[0] + "_final.xml"
with open(filename, "w") as f:
    f.write(xmlstr)
