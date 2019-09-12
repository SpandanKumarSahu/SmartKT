# Make a `config.txt` file containing the following things in order
# username
# password
# repo (like: dealii/dealii)


from github import Github
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree
from xml.dom import minidom
import sys

if sys.version_info > (3, 0):
	import urllib.request as ul
else:
	import urllib2 as ul

def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def parse_content(content):
	content = content.split('\n')
	content = [i[3:].strip() for i in content if (i[:3] == '+++' or i[:3] == '---')]
	content = [i[2:] for i in content if (i[:2]=="a/" or i[:2]=="b/")]
	return list(set(content))

try:
	with open('config.txt', 'r') as f:
		username, ouathtoken, repoURL = f.read().split()
except:
	print("Please provide the config file!")
	exit()

g = Github(username, oauthtoken)
repo = g.get_repo(repoURL)

issues = []

for i in repo.get_issues(state='all'):
	issues.append(i)

print(len(issues), " issues collected")

# Store the information in XML format
root = Element('VCS')
iroot = SubElement(root, "ISSUES")

for idx, i in enumerate(issues, start=1):
	s = SubElement(iroot, "ISSUE")
	s.set('ID', str(i.id))
	s.set('STATE', i.state.encode('ascii', 'ignore'))
	s.set('TITLE', i.title.encode('ascii', 'ignore'))
	f = SubElement(s, 'FILES')
	pr = i.pull_request
	if pr is not None:
		content = ul.urlopen(pr.diff_url).read()
		files = parse_content(content)
		for file in files:
			temp = SubElement(f, 'FILE')
			temp.text = str(file)
	print(idx, " issues processed out of ", len(issues))

s = prettify(root)
filename = "vcs.xml"
with open(filename, 'wb') as f:
	f.write(s)
print("XML file has been written to ", filename)
