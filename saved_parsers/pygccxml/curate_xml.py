import xml.etree.ElementTree as ET
import sys


filename = sys.argv[1]
myTree = ET.parse(filename)
root = myTree.getroot()
locs = root.findall(".//location")
parent_map = {c:p for p in root.iter() for c in p}

for loc in locs:
    if str(loc.attrib['value'][2:5]) == "usr" or str(loc.attrib['value'][1]) == "<" :
        parent = parent_map[loc]
        grandpa = parent_map[parent]
        grandpa.remove(parent)

myTree.write(filename)
