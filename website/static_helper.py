from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os, pickle
from helpers import *

def classmap(root):
    ls = []
    for c in root.findall(".//CLASS_DECL"):
        # Inheritance edges
        ls.append(c.attrib['spelling'])
        for p in c.findall("./CXX_BASE_SPECIFIER"):
            ls.append((c.attrib['spelling'], p.attrib['type'], p.attrib['access_specifier']))
        # dependency edges
        for d in c.findall("./FIELD_DECL"):
            for t in d.findall(".//TYPE_REF"):
                ls.append((str(t.attrib['type'].split()[-1]), c.attrib['spelling'], d.attrib['access_specifier']))
    filename = "classmap"
    to_dot(ls, filename)
    return filename + ".png"

def structmap(root):
    ls = []
    # Do it for structs
    for c in root.findall(".//STRUCT_DECL"):
        # Inheritance edges
        ls.append(c.attrib['spelling'])
        for p in c.findall("./CXX_BASE_SPECIFIER"):
            ls.append((c.attrib['spelling'], p.attrib['type'], p.attrib['access_specifier']))
        # dependency edges
        for d in c.findall("./FIELD_DECL"):
            for t in d.findall(".//TYPE_REF"):
                ls.append((str(t.attrib['type'].split()[-1]), c.attrib['spelling'], d.attrib['access_specifier']))
    filename = "structmap"
    to_dot(ls, filename)
    return filename + ".png"

def structclassmap(root):
    ls = []
    # Do it for classes
    for c in root.findall(".//CLASS_DECL"):
        # Inheritance edges
        ls.append(c.attrib['spelling'])
        for p in c.findall("./CXX_BASE_SPECIFIER"):
            ls.append((c.attrib['spelling'], p.attrib['type'], p.attrib['access_specifier']))
        # dependency edges
        for d in c.findall("./FIELD_DECL"):
            for t in d.findall(".//TYPE_REF"):
                ls.append((str(t.attrib['type'].split()[-1]), c.attrib['spelling'], d.attrib['access_specifier']))

    # Do it for structs
    for c in root.findall(".//STRUCT_DECL"):
        # Inheritance edges
        ls.append(c.attrib['spelling'])
        for p in c.findall("./CXX_BASE_SPECIFIER"):
            ls.append((c.attrib['spelling'], p.attrib['type'], p.attrib['access_specifier']))
        # dependency edges
        for d in c.findall("./FIELD_DECL"):
            for t in d.findall(".//TYPE_REF"):
                ls.append((str(t.attrib['type'].split()[-1]), c.attrib['spelling'], d.attrib['access_specifier']))
    filename = "structclassmap"
    to_dot(ls, filename)
    return filename + ".png"

def findvar(el, varname):
    path = varname.split('::')
    for locn in path:
        el = el.find('.//*[@spelling="{}"]'.format(locn))
    return el

def analyze_pattern():
    pass

def get_global_variables(root, srcfilename=None):
    vars = [("<b>SPELL", "LOC", "LINE", "TYPE</b>")]
    if srcfilename is None:
        file = root.find('./file')
        for var in file.findall("./STATICROOT/TRANSLATION_UNIT/VAR_DECL"):
            vars.append((var.attrib["spelling"], var.attrib["location"], var.attrib["linenum"], var.attrib['type']))
    else:
        for file in root.findall('./EXEC_STATIC/file[@name="{}"]'.format(srcfilename)):
            for var in file.findall(".STATICROOT/TRANSLATION_UNIT/VAR_DECL"):
                vars.append((var.attrib["spelling"], var.attrib["location"], var.attrib["linenum"], var.attrib['type']))
    with open("temp.html", "w")as f:
        f.write(to_html(vars))
    return "temp.html"

def get_dependencies(file, dependencies="dependencies.p"):
    ls = []
    dep, src, obj = pickle.load(open(dependencies, "rb"))
    if file.split('.')[-1] in ["c", "cc", "cpp"]:
        for d in dep[file]:
            ls.append((d, file, "INCLUDE_FOLDER"))
    else:
        ls = [(d, file, "OBJ") for d in dep[file]]
        to_remove, to_add = [], []
        for d, f, t in ls:
            if d[-2:] != ".o":
                ls.extend([(c, d, "OBJ") for c in dep[d]])
                to_remove.append((d,f,t))
                to_add.append((d,f, "SO/DL"))
        for x, y in list(zip(to_remove, to_add)):
            ls.remove(x)
            ls.append(y)
        to_add = []
        for d,f,t in ls:
            if d[-2:] == ".o":
                to_add.append((src[d], d, "SRC"))
                if src[d] in dep:
                    to_add.extend([(c, src[d], "INCLUDE_FOLDER") for c in dep[src[d]]])
        ls.extend(to_add)
    filename = "dep"
    to_dot(ls, filename)
    return filename + ".png"

def print_details(root, name, tag="FUNCTION_DECL"):
    results = Element("DETAILS")
    for x in root.findall('.//'+tag+'[@spelling="{}"]'.format(name)):
        results.append(x)
    filename = "results.xml"
    to_xml(results, filename)
    return filename

def get_var_type(root, query):
    if "::" in query:
        var = findvar(root, query)
        return var.attrib['type']
    s = "<HTML><BODY>The following were found:<br><br>"
    vars = []
    for c in root.findall(".//*[@spelling='"+query.strip()+ "']"):
        ls = getfullname(root, c.attrib['id'])
        ls.reverse()
        vars.append("::".join(ls) + " -> " + c.attrib['type'] + "<br>")
    vars = list(set(vars))
    s += "/n".join(vars)
    s += "</BODY></HTML>"
    with open("temp.html", "w") as f:
        f.write(s)
    return "temp.html"

def get_parent(root, query):
    s = "<HTML><BODY>The following were found:<br><br>"
    vars = []
    for c in root.findall(".//VAR_DECL[@spelling='"+query.strip()+ "']"):
        ls = getfullname(root, c.attrib['id'])
        ls.reverse()
        vars.append(" -> ".join(ls[:-1]) + "<br>")
    vars = list(set(vars))
    s += "/n".join(vars)
    s += "</BODY></HTML>"
    with open("temp.html", "w") as f:
        f.write(s)
    return "temp.html"

def get_return_details(root, query):
    ls = []
    for func in root.findall('.//FUNCTION_DECL[@spelling="{}"]'.format(query)):
        t = func.attrib['type']
        print(t)
        ls.append((query, t[:t.index('(')]))
    for func in root.findall('.//FUNCTION_DECL[@mangled_name="{}"]'.format(query)):
        t = func.attrib['type']
        ls.append((query, t[:t.index('(')]))
    for func in root.findall('.//FUNCTION_DECL[@linkage_name="{}"]'.format(query)):
        t = func.attrib['type']
        ls.append((query, t[:t.index('(')]))
    if len(ls) == 0:
        s = "No such function was found."
    else:
        ls = list(set(ls))
        ls.insert(0,"FUNC RETURN")
        s = to_html(ls)
    with open("temp.html", "w") as f:
        f.write(s)
    return "temp.html"

if __name__ == "__main__":
    print(classmap())
