from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os
from helpers import *

def edits_file(commit, filename):
    return filename in [f.attrib["FILENAME"] for f in commit.findall("./FILES/FILE")]

def get_files_in_commit(root, commit_id):
    ls = ["<b>FILES IN COMMIT</b>"]
    ls.extend([f.attrib["FILENAME"] for f in root.findall('./COMMITS/COMMIT[@ID="{}"]/FILES/FILE'.format(commit_id))])
    with open("temp.html", "w") as f:
        f.write(to_html(ls))
    return "temp.html"

def get_contributors(root, filename):
    ls = ["<b>AUTHORS</b>"]
    ls.extend([c.attrib["AUTHOR"] for c in root.findall("./COMMITS/COMMIT") if edits_file(c, filename) == True])
    ls = sorted(set(ls), key=ls.index)
    with open("temp.html", "w") as f:
        f.write(to_html(ls))
    return "temp.html"

def last_modified(root, filename):
    ls = [c.attrib["COMMITTER_DATE"] for c in root.findall("./COMMITS/COMMIT")\
        if edits_file(c, filename) == True and c.attrib["COMMITTER_DATE"] is not None]
    ls.sort(reverse=True)
    ls = [ls[0], "was the last time "+filename+" was edited"]
    with open("temp.html", "w") as f:
        f.write(to_html(ls))
    return "temp.html"
