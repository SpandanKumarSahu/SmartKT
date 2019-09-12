import sys, os
import numpy as np
from PIL import Image
import random
import time
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
from helpers import *

def callgraph(droot, sroot):
    count = 1
    funcidloc = dict()
    callmap = dict()
    r = list()
    for el in droot.findall('.//CALL'):
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
            p = getfunc(sroot, el)
            if p is not None:
                for entry in p:
                    fp.write ('->"{}"'.format(entry))
            fp.write('\n')
        fp.write('}')
    os.system("dot -Tpng callmap.dot -o callmap.png")
    return "callmap.png"

def activity(droot, sroot, query):
    tid = query
    s = '<HTML><BODY>Activity for thread: ' + tid + '<br>'
    for el in droot.findall('.//*[@THREADID="'+tid+'"]'):
        s = s + el.tag + '<br>'
        if 'VARID' in el.attrib:
            hh = sroot.find('.//*[@id="{}"]'.format(el.attrib['VARID']))
            s += 'VARIABLE: ' + hh.attrib['spelling'] + '<br>'
        if 'FUNCNAME' in el.attrib:
            hh = sroot.find('.//*[@spelling="{}"]'.format(el.attrib['FUNCNAME']))
            if hh is None:
                hh = sroot.find('.//*[@mangled_name="{}"]'.format(el.attrib['FUNCNAME']))
            elif hh is None:
                hh = sroot.find('.//*[@linkage_name="{}"]'.format(el.attrib['FUNCNAME']))
            if hh is not None:
                s += 'FUNCTION: ' + hh.attrib['spelling'] + '<br>'
            else:
                s += 'FUNCTION: ' + el.attrib['FUNCNAME'] + '<br>'
        if 'CALLERNAME' in el.attrib:
            hh = sroot.find('.//*[@spelling="{}"]'.format(el.attrib['CALLERNAME']))
            if hh is None:
                hh = sroot.find('.//*[@mangled_name="{}"]'.format(el.attrib['CALLERNAME']))
            elif hh is None:
                hh = sroot.find('.//*[@linkage_name="{}"]'.format(el.attrib['CALLERNAME']))
            if hh is not None:
                s += 'CALLER: ' + hh.attrib['spelling'] + '<br>'
            else:
                s += 'CALLER: ' + el.attrib['CALLERNAME'] + '<br>'
        if 'CALLEENAME' in el.attrib:
            hh = sroot.find('.//*[@spelling="{}"]'.format(el.attrib['CALLEENAME']))
            if hh is None:
                hh = sroot.find('.//*[@linkage_name="{}"]'.format(el.attrib['CALLEENAME']))
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
    return "temp.html"
