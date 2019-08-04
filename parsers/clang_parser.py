# To use:
# python clang_parser.py <filename> -I/a/a/ -I<more dependency>

import clang.cindex as cl
from clang.cindex import Index
from pprint import pprint
from optparse import OptionParser, OptionGroup
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom


# Set the clang shared object. The python interface is just a proxy for the actual clang
cl.Config.set_library_file("/usr/local/lib/libclang.so.6.0")

# Recursively visit each node and its children and store its information in a XML tree
def get_info(node, parent):
  global func_node
  try:
    sub = SubElement(parent, str(node.kind.name))
  except:
    sub = SubElement(parent, "Unknown")
# These are the list of attributes we are keeping track of. This becomes better
# with the intuitive parser
  sub.set('id', str(node.hash))
  sub.set('parent_id', str(0) if node.semantic_parent is None else str(node.semantic_parent.hash))
  sub.set('usr', "None" if node.get_usr() is None else str(node.get_usr()))
  sub.set('spelling', "None" if node.spelling is None else str(node.spelling))
  sub.set('location', "None" if (node.location is None or node.location.file is None) else str(node.location.file)+"["+str(node.location.line)+"]")
  sub.set('linenum', "None" if (node.location.line is None) else str(node.location.line))
  sub.set('extent.start', "None" if (node.extent.start is None or node.extent.start.file is None) else str(node.extent.start.file)+"["+ str(node.extent.start.line) + "]")
  sub.set('extent.end', "None" if (node.extent.end is None or node.extent.end.file is None) else str(node.extent.end.file)+"["+ str(node.extent.end.line) + "]")
  sub.set('is_definition', str(node.is_definition()))
  sub.set('type', str(node.type.spelling))
  children = [get_info(c, sub) for c in node.get_children()]
  return parent

# Helps parse the dependency in here
parser = OptionParser("usage: %prog [options] {filename} [clang-args*]")
parser.disable_interspersed_args()
(opts, args) = parser.parse_args()

# Get the translation unit
index = Index.create()
tu = index.parse(None, args)
if not tu:
  parser.error("unable to load input")

root = Element("STATICROOT")
root = get_info(tu.cursor, root)
root.set('id', str(0))
# print(ET.tostring(root, encoding='utf8').decode('utf8'))

# For pretty representation and writing to output
xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
outfilename = str(args[0].split('.')[0])+"_clang.xml"
with open(outfilename, "w") as f:
    f.write(xmlstr)
# print("The entire XML parse has been written at ", outfilename)
