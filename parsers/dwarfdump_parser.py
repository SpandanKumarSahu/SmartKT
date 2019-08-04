# To use:
# python dwarfdump_parser.py <dwarfdump_output>

'''
There is no clear algorithm here. Just hacks. I wrote this parser as I saw fit.
Can be prone to errors while parsing outputs that I haven't encountered yet.
I will try my best to explain what I have done, but I am no good.
'''

import sys
import os
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom

def count_spaces(line):
    count = 0
    for i in line:
        if i == " ":
            count += 1
        else:
            return count

def get_clear_tag_name(tag_name):
    s = tag_name[[i for i, c in enumerate(tag_name) if c.isupper()][-1]+2:]
    return s

def add_attrs(node, attrs):
    for attr in attrs:
        ls = attr.split()
        ls = [x for x in ls if x != ""]
        attr_name = get_clear_tag_name(attr.split()[0])
        attr_val = ' '.join(ls[1:])
        if len(attr_val.strip()) > 0:
            if attr_val[0] == '"' or attr_val[0] == "<":
                attr_val = attr_val[1:-1]
            node.set(attr_name, attr_val)
        else:
            if attr_name.find("yes") != -1:
                node.set(attr_name[:attr_name.find("yes")], attr_name[attr_name.find("yes"):])
            else:
                node.set(attr_name, "True")
    return node

def recfunc(parent, i, level):
    # Level helps to see if this is a new section or a continuation
    # If you see one output, you will see that there are "<" marks at the beginning
    # of what is supposed to be one node.
    # If new section, get the lines which correspond to the attributes of the new node
    # When done, there will be information about children.
    global data
    while(i < len(data)):
        l, d = data[i]
        if d[0] == "<" and int(d[1:3]) == level + 1:
            curr_level = int(d[1:3])
            tag_name = d[4:].split(' ')[-1]
            tag_name = get_clear_tag_name(tag_name)
            s = SubElement(parent, tag_name)
            s.set('id', d[4:].split()[0][1:-1])
            attrs = []
            i += 1
            if i < len(data):
                l, d = data[i]
            else:
                return parent, i
            while d[0] != "<":
                attrs.append(d)
                i += 1
                if i < len(data):
                    l, d = data[i]
                else:
                    s = add_attrs(s, attrs)
                    return parent, i
            s = add_attrs(s, attrs)
        elif d[0] == "<" and int(d[1:3]) > curr_level:
            s, i = recfunc(s, i, curr_level)
        elif d[0] == "<" and int(d[1:3]) < curr_level:
            return parent, i
        else:
            return parent, i
    return parent, i


def fill_params(root):
    # For class based functions
    for c in root.findall(".//class_type"):
        for func in  c.findall(".//subprogram"):
            # find the matching specification
            for f in root.findall(".//*[@specification='"+func.attrib['id'] +"']"):
                for key in f.attrib:
                    func.set(key, f.attrib[key])
                for child in list(func):
                    func.remove(child)
                for child in list(f):
                    func.append(child)
                root.remove(f)
                break
    return root

def fill_abstract(root):
    for f in root.findall(".//*"):
        if "abstract_origin" in f.attrib:
            # find the node with abstract_origin id
            for node in root.findall(".//*[@id='"+f.attrib['abstract_origin']+"']"):
                # copy the attributes except the abstract_origin attribute
                for key in f.attrib:
                    if key != 'abstract_origin':
                        node.set(key, f.attrib[key])
    for f in list(root.findall(".//*")):
        if 'abstract_origin' in f.attrib:
            try:
                root.remove(f)
            except:
                continue
    return root

'''
STEP One: Open the file, read the contents, split on lines.
Observations:
    * sections are separated by a newline
    * Each section represents one tag (at least)
Steps:
1. Filter the section of concern
2. Create a root, and try to parse the output recursively
'''

filename = str(sys.argv[1])
with open(filename, "r") as f:
    data = f.readlines()


on = False
for idx, sentence in enumerate(data):
    if sentence == "LOCAL_SYMBOLS:\n":
        start_pos = idx
        on = True
    elif on and sentence == "\n":
        data = data[start_pos+1:idx]
        break

data = [(count_spaces(x), x.strip()) for x in data]
root = Element('root')
# Get the dwarfdump information in XML format
root, _ = recfunc(root, 0, 0)

# Add the abstract_origin type outputs. encountered during Constructors
root = fill_abstract(root)
# Add the offsets for function parameters.
root = fill_params(root)

xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")

filename = str(filename.split('.')[0])+"_dwarfdump.xml"
with open(filename, "w") as f:
    f.write(xmlstr)
print("File written at: ", filename)
