import os
import sys
from os.path import join as PJOIN
import xml.etree.ElementTree as ET



def MergeAll(folder_name):
    global COMMENT_ID
    for file in os.listdir(folder_name):
        if os.path.isdir(PJOIN(folder_name, file)):
            MergeAll(PJOIN(folder_name, file))
            continue

        print("Merging... ",PJOIN(folder_name, file))
        tree = ET.parse(PJOIN(folder_name, file))
        root = tree.getroot()
        for comment in root.getchildren():
            file_path = comment.attrib["file_path"]
            if file_path[:2] == '..':
                file_path = file_path[3:]
            comment.set('file_path',file_path)
	    comment.set('id', str(COMMENT_ID))
	    COMMENT_ID += 1
            ROOT.append(comment)


if len(sys.argv) != 5:
    print("Give 4 arguments - Folder to merge, Project Name, Project Path, Output XML FILE")

COMMENT_ID = 1
ROOT = ET.Element('COMMENTS')
ROOT.set('project_name', sys.argv[2])
ROOT.set('project_path', sys.argv[3])
MergeAll(sys.argv[1])

xml_data = ET.tostring(ROOT)
with open(sys.argv[4],'wb') as f:
    f.write(xml_data)
