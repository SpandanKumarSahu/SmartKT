import sys
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom

filename = str(sys.argv[1])		# event trace dump file
varmap = dict()

# creating function offset map from offset file
with open('final.offset', 'r') as fp:
	li = fp.readlines()
	for p in li:
		p = p.split()
		varmap[(p[0], p[1])] = p[2] # function x offset -> variable static id

# read the event trace
with open(filename, 'r') as f:
	li = f.readlines()

# create an element for dynamic event trace
# can keep dynamic event xml separate for live process tracing (??)
tree = Element('DYNAMICROOT')
tree.attrib['id'] = "-1"

for t in li:
	t = t.split()					# split every line
	i = 0
	entry = SubElement(tree, t[i])	# first word is event type
	i += 1
	while i < len(t):
		entry.attrib[t[i]] = t[i+1]	 # all other events come in key:value pairs
		if t[i] == 'SYNCS' and t[i+1] != 'ASYNC':	# synchronization locks are kept as children of events
			k = int(t[i+1])							# get number of locks
			i += 2
			for j in range(k):						# add a child for each lock held
				lock = SubElement(entry, 'POSIXLOCK')
				lock.attrib[t[i]] = t[i+1]			# lock type
				i += 2
				lock.attrib[t[i]] = t[i+1]			# lock address
				i += 2
		else:
			i += 2
	if 'OFFSET' in entry.attrib:					# get variable id info from the offset
		t = (entry.attrib['FUNCNAME'], entry.attrib['OFFSET'])
		if t in varmap:
			entry.attrib['VARID'] = varmap[t]
		else:										# if not found in the map
			tree.remove(entry)						# remove the entry
	# print (entry.tag, entry.attrib)

# get the static xml
ftree = ET.parse('final.xml')
root = ftree.getroot()

# add the dynamic data
root.append(tree)

# output to a file
xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
with open('ekdumfinal.xml', 'w') as f:
	f.write(xmlstr)
