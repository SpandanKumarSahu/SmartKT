from flask import Flask, jsonify, abort, request, make_response, url_for,redirect,send_file
import sys, os
import numpy as np
from PIL import Image
import random
import time
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom
from analyze import main
import helpers, comments_helper, dynamic_helper, static_helper, vcs_helper

croot, droot, sroot, vroot = None, None, None, None
cfile, dfile, sfile, vfile = None, None, None, None

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

@app.route('/makequery', methods=['GET', 'POST'])
def makeQuery():
    global croot, droot, sroot, vroot, cfile, dfile, sfile, vfile
    query = request.args['query']
    queryType, query = process_query(query)
    print(queryType, query)

    if 0 <= queryType < 50:
        # Static queries
        if queryType == 1:
            return send_file(static_helper.get_var_type(sroot, query), cache_timeout=-1)
        elif queryType == 2:
            return send_file(static_helper.get_parent(sroot, query), cache_timeout=-1)
        elif queryType == 3:
            return send_file(sfile, cache_timeout=-1)
        elif queryType == 4:
            return send_file(static_helper.classmap(sroot), cache_timeout=-1)
        elif queryType == 5:
            return send_file(static_helper.structmap(sroot), cache_timeout=-1)
        elif queryType == 6:
            return send_file(static_helper.structclassmap(sroot), cache_timeout=-1)
        elif queryType == 7:
            return send_file(static_helper.get_global_variables(sroot), cache_timeout=-1)
        elif queryType == 8:
            return send_file(static_helper.get_dependencies(query), cache_timeout=-1)
        elif queryType == 9:
            return send_file(static_helper.print_details(sroot, query), cache_timeout=-1)
        elif queryType == 10:
            return send_file(static_helper.get_return_details(sroot, query), cache_timeout=-1)

        elif queryType == 30:
            return send_file(main(), cache_timeout=-1)
        else:
            return "Hello Static"

    elif 50 <= queryType < 100:
        # VCS Queries
        if queryType == 50:
            return send_file(vcs_helper.get_contributors(vroot, query), cache_timeout=-1)
        elif queryType == 51:
            return send_file(vcs_helper.get_files_in_commit(vroot, query), cache_timeout=-1)
        elif queryType == 52:
            return send_file(vcs_helper.last_modified(vroot, query), cache_timeout=-1)
        else:
            return "Hello VCS"

    elif 100 <= queryType < 150:
        # Comments Query
        if queryType == 100:
            return send_file(comments_helper.code_talks_about(query), cache_timeout=-1)
        elif queryType == 101:
            return send_file(comments_helper.files_using_macro(query), cache_timeout=-1)
        else:
            return "Hello Comments!"

    elif 150 <= queryType < 200:
        # Dynamic Queries
        if queryType == 150:
            return send_file(dynamic_helper.callgraph(droot, sroot), mimetype='image/png', cache_timeout=-1)
        elif queryType == 151:
            return send_file(dynamic_helper.activity(droot, sroot, query), cache_timeout=-1)
        else:
            return "Hello Dynamic!"
    else:
        return "Hello"

@app.route('/map', methods = ['GET'])   #Hosts map at http://127.0.0.1:5000/map
def getMap():
    return send_file('map.png', mimetype='image/png',cache_timeout=-1)

def process_query(query):
    if query.lower().find('type') != -1 and query.lower().find('return') == -1:
        return 1, query.split()[query.split().index("of")+1]
    elif query.lower().find('parent') != -1:
        return 2, query.split()[query.split().index("of")+1]
    elif query.lower().find('all') != -1 and query.lower().find("static") != -1:
        return 3, ""
    elif query.lower().find('structclassmap') != -1:
        return 6, ""
    elif query.lower().find('classmap') != -1:
        return 4, ""
    elif query.lower().find('structmap') != -1:
        return 5, ""
    elif query.lower().find('all global variables') != -1:
        return 7, ""
    elif query.lower().find('dependencies') != -1:
        return 8, query.split()[query.lower().split().index("of")+1]
    elif query.lower().find('details about function') != -1:
        return 9, query.split()[query.lower().split().index("function")+1]
    elif query.lower().find('return') != -1:
        return 10, query.split()[query.lower().split().index("return")-1]
    elif query.lower().find("design pattern") != -1:
        return 30, ""

    elif query.lower().find("people associated") != -1 or query.lower().find("contributed") != -1:
        return 50, query.split()[-1]
    elif query.lower().find("files") != -1 and query.lower().find("commit") != -1:
        return 51, query.split()[query.lower().split().index("commit")+1]
    elif query.lower().find("last modified") != -1:
        return 52, query.split()[query.lower().split().index("last")-1]

    elif query.lower().find('talk about ') != -1:
        concept = query[query.lower().find('talk about ')+len('talk about '):]
        if concept[-1] == '?':
            concept = concept[:-1]
            return 100, concept
    elif query.lower().find('macro') != -1 and query.lower().find('use') != -1 and query.lower().find('file') != -1:
            return 101, query.split()[query.split().index("macro")+1]

    elif query.lower().find('call graph') != -1:
        return 150, 'cg'
    elif query.lower().find('activity') != -1:
        nq = query.split()
        for el in nq:
            try:
                f = int(el)
                return 151, el
            except:
                continue

    else:
        return 200, ""

def setup():
    global croot, droot, sroot, vroot, cfile, dfile, sfile, vfile
    cfile, dfile = "comments.xml", "dynamic.xml"
    sfile, vfile = "static.xml", "vcs.xml"
    #croot = ET.parse(cfile).getroot()
    droot = ET.parse(dfile).getroot()
    sroot = ET.parse(sfile).getroot()
    vroot = ET.parse(vfile).getroot()

setup()

# default port is 5000
if  __name__=="__main__":
    app.run(debug = True, host='0.0.0.0')
