# To use:
# python clang_parser.py <filename> -I/a/a/ -I<more dependency>

import clang.cindex as cl
from clang.cindex import Index
from pprint import pprint
from optparse import OptionParser, OptionGroup
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os, signal
import faulthandler

faulthandler.enable()

def segfault_handler(signnum, frame):
  print("Segfault!")
  pass

#signal.signal(signal.SIGSEGV, segfault_handler)

# Set the clang shared object. The python interface is just a proxy for the actual clang
cl.Config.set_library_file("/usr/local/lib/libclang.so.6.0")

# Recursively visit each node and its children and store its information in a XML tree
def get_info(node, parent):
  #print(node.kind.name)
  global func_node, s
  try:
    sub = SubElement(parent, str(node.kind.name))
  except:
    sub = SubElement(parent, "Unknown")
# These are the list of attributes we are keeping track of. This becomes better
# with the intuitive parser  
  if node.referenced is not None:
    if node.hash != node.referenced.hash:
      sub.set('id', str(node.referenced.hash))
    else:
      sub.set('id', str(node.hash))
  else:
    sub.set('id', str(node.hash))
  if node.semantic_parent is not None:
    sub.set('parent_id', str(node.semantic_parent.hash))
  if node.lexical_parent is not None:
    sub.set('lex_parent_id', str(node.lexical_parent.hash))
  sub.set('usr', "None" if node.get_usr() is None else str(node.get_usr()))
  #print(dir(node), dir(node.spelling))
  sub.set('spelling', "None" if node.spelling is None else str(node.spelling))
  sub.set('location', "None" if (node.location is None or node.location.file is None) else str(node.location.file)+"["+str(node.location.line)+"]")
  sub.set('linenum', "None" if (node.location.line is None) else str(node.location.line))
  sub.set('extent.start', "None" if (node.extent.start is None or node.extent.start.file is None) else str(node.extent.start.file)+"["+ str(node.extent.start.line) + "]")
  sub.set('extent.end', "None" if (node.extent.end is None or node.extent.end.file is None) else str(node.extent.end.file)+"["+ str(node.extent.end.line) + "]")
  sub.set('is_definition', str(node.is_definition()))
  # print ('this worked', parent.tag, node.location.file, node.location.line)
  if node.access_specifier.name not in ["NONE", "INVALID"]:
    sub.set("access_specifier", node.access_specifier.name)  
  if node.storage_class.name not in ["NONE", "INVALID"]:
    sub.set("storage_class", str(node.storage_class.name))
  if node.linkage.name not in ["NO_LINKAGE", "INVALID"]:
    sub.set('linkage', str(node.linkage.name))
  if node.type.spelling is not None:
    sub.set('type', str(node.type.spelling))
    #sub.set('size', str(node.type.get_size()))
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
