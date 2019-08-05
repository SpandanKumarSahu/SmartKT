from flask import Flask, jsonify, abort, request, make_response, url_for,redirect,send_file
import sys, os
import numpy as np
from PIL import Image
import random
import time
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
from static_helper import classmap
from analyze import main

root = None

app = Flask(__name__, static_url_path = "")

@app.errorhandler(400)
def not_found1(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found2(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/', methods = ['GET'])
def getIndex():
    with open("index.html", "r") as f:
        html = f.read()
    return html

@app.route('/query', methods = ['GET'])
def getQuery():
    with open("query.html", "r") as f:
        html = f.read()
    return html

@app.route('/res', methods = ['GET'])
def getRes():
    with open("res.html", "r") as f:
        html = f.read()
    return html

def getfullname (tree, nid, el = None):
    if el is None:
        el = tree.find('.//*[@id="{}"]'.format(nid))
    k = []
    if 'spelling' in el.attrib:
        name = ''
        if 'type' in el.attrib and el.attrib['type'] != 'None':
            name += el.attrib['type']
        name = name + ' ' + el.attrib['spelling']
        k = [name]
        k.extend(getfullname(tree, el.attrib['parent_id']))
    return k

def getfunc (tree, linknm):
    el = tree.find('.//*[@spelling="{}"]'.format(linknm))
    if el is None:
        el = tree.find('.//*[@linkage_name="{}"]'.format(linknm))
    if el is None:
        return None
    k = getfullname(tree, 0, el)
    return k

@app.route('/makequery', methods=['GET', 'POST'])
def makeQuery():
    global root
    query = request.args['query']
    queryType, query = process_query(query)
    print(queryType, query)
    if queryType == 0:
        count = 1
        funcidloc = dict()
        callmap = dict()
        r = list()
        dtree = root.find("DYNAMICROOT")
        for el in dtree.findall('.//CALL'):
            clrnm = el.attrib['CALLERNAME']
            ceenm = el.attrib['CALLEENAME']
            if clrnm not in funcidloc:
                funcidloc[clrnm] = count
                count += 1
            if ceenm not in funcidloc:
                funcidloc[ceenm] = count
                count += 1
            t = (funcidloc[clrnm], funcidloc[ceenm])
            if t not in callmap:
                callmap[t] = list()
            callmap[t].append(el.attrib['id'])
            r.append(el.attrib['id'])
        r.sort()
        k = dict()
        for i in range(len(r)):
            k[r[i]] = i+1
        for el in callmap:
            callmap[el] = list(map(lambda x: k[x], callmap[el]))
        with open('callmap.dot', 'w') as fp:
            fp.write ('digraph G\n{')
            for el in callmap:
                fp.write('"P{}"->"P{}"[label="{}"]\n'.format(el[0], el[1], callmap[el]))
            for el in funcidloc:
                fp.write('"desc P{}"'.format(funcidloc[el]))
                p = getfunc(root, el)
                if p is not None:
                    for entry in p:
                        fp.write ('->"{}"'.format(entry))
                fp.write('\n')
            fp.write('}')
        os.system("dot -Tpng callmap.dot -o callmap.png")
        return send_file('callmap.png', mimetype='image/png',cache_timeout=-1)

    elif queryType == 1:
        if "::" in query:
            var = findvar(root, query)
            return var.attrib['type']
        s = "<HTML><BODY>The following were found:<br><br>"
        for c in root.findall(".//*[@spelling='"+query.strip()+ "']"):
            ls = getfullname(root, c.attrib['id'])
            ls.reverse()
            s += "::".join(ls) + " -> " + c.attrib['type'] + "<br>"
        s += "</BODY></HTML>"
        with open("temp.html", "w") as f:
            f.write(s)
        return send_file("temp.html", cache_timeout=-1)
    elif queryType == 2:
        s = "<HTML><BODY>The following were found:<br><br>"
        for c in root.findall(".//VAR_DECL[@spelling='"+query.strip()+ "']"):
            ls = getfullname(root, c.attrib['id'])
            ls.reverse()
            s += " -> ".join(ls[:-1]) + "<br>"
        s += "</BODY></HTML>"
        with open("temp.html", "w") as f:
            f.write(s)
        return send_file("temp.html", cache_timeout=-1)
    elif queryType == 3:
        return send_file('final.xml', cache_timeout=-1)
    elif queryType == 4:
        filename = classmap()
        return send_file(filename, cache_timeout=-1)
    elif queryType == 5:
        return send_file(main(), cache_timeout=-1)
    elif queryType == 6:
        tid = query
        tree = root
        s = '<HTML><BODY>Activity for thread: ' + tid + '<br>'
        for el in tree.findall('.//*[@THREADID="'+tid+'"]'):
            s = s + el.tag + '<br>'
            if 'VARID' in el.attrib:
                hh = tree.find('.//*[@id="{}"]'.format(el.attrib['VARID']))
                s += 'VARIABLE: ' + hh.attrib['spelling'] + '<br>'
            if 'FUNCNAME' in el.attrib:
                hh = tree.find('.//*[@spelling="{}"]'.format(el.attrib['FUNCNAME']))
                if hh is None:
                    hh = tree.find('.//*[@linkage_name="{}"]'.format(el.attrib['FUNCNAME']))
                if hh is not None:
                    s += 'FUNCTION: ' + hh.attrib['spelling'] + '<br>'
                else:
                    s += 'FUNCTION: ' + el.attrib['FUNCNAME'] + '<br>'
            if 'CALLERNAME' in el.attrib:
                hh = tree.find('.//*[@spelling="{}"]'.format(el.attrib['CALLERNAME']))
                if hh is None:
                    hh = tree.find('.//*[@linkage_name="{}"]'.format(el.attrib['CALLERNAME']))
                if hh is not None:
                    s += 'CALLER: ' + hh.attrib['spelling'] + '<br>'
                else:
                    s += 'CALLER: ' + el.attrib['CALLERNAME'] + '<br>'
            if 'CALLEENAME' in el.attrib:
                hh = tree.find('.//*[@spelling="{}"]'.format(el.attrib['CALLEENAME']))
                if hh is None:
                    hh = tree.find('.//*[@linkage_name="{}"]'.format(el.attrib['CALLEENAME']))
                if hh is not None:
                    s += 'CALLEE: ' + hh.attrib['spelling'] + '<br>'
                else:
                    s += 'CALLEE: ' + el.attrib['CALLEENAME'] + '<br>'
            if 'INVNO' in el.attrib:
                s += 'INVNO: ' + el.attrib['INVNO'] + '<br>'
            if 'SYNCS' in el.attrib:
                s += 'SYNCS: ' + el.attrib['SYNCS'] + '<br>'
            s += '<br>'
            s += '</BODY></HTML>'
        with open ('temp.html', 'w') as fp:
            fp.write(s)
        return send_file("temp.html", cache_timeout=-1)
    else:
        return "Hello"

@app.route('/map', methods = ['GET'])   #Hosts map at http://127.0.0.1:5000/map
def getMap():
    return send_file('map.png', mimetype='image/png',cache_timeout=-1)

def process_query(query):
    if query.lower().find('call graph') != -1:
        return 0, 'cg'
    elif query.lower().find('type') != -1:
        return 1, query.split()[query.split().index("of")+1]
    elif query.lower().find('parent') != -1:
        return 2, query.split()[query.split().index("of")+1]
    elif query.lower().find('all') != -1:
        return 3, ""
    elif query.lower().find('classmap') != -1:
        return 4, ""
    elif query.lower().find("design pattern") != -1:
        return 5, ""
    elif query.lower().find('activity') != -1:
        nq = query.split()
        for el in nq:
            try:
                f = int(el)
                return 6, el
            except:
                continue
    else:
        return 7
def setup():
    global root
    tree = ET.parse('final.xml')
    root = tree.getroot()

setup()

# default port is 5000

if  __name__=="__main__":
    app.run(debug = True, host='0.0.0.0')
