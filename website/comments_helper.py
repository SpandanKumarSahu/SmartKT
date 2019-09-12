import xml.etree.ElementTree as ET
import sys

ALGORITHM_TYPES = ['Common Sorting/ Searching/ Traversal Algorithms', 'Divide and Conquer/ Greedy Algorithms',
                    'Dynamic Programming']
def _find_algo_for_a_comment(comment, algorithms):
    program_domains = comment.find('PROGRAM_DOMAINS')
    for pd in program_domains.getchildren():
        if any(algo_type in pd.attrib['type'] for algo_type in ALGORITHM_TYPES):
            algorithms.add(pd.attrib['word'])

def find_algorithm(symbol_id):
    tree = ET.parse("/workspace/comments_libpng.xml")
    root = tree.getroot()
    algorithms = set()
    for comment in root.getchildren():
        symbols = comment.find("SYMBOLS")
        if symbols == None:
            continue
        for symbol in symbols.getchildren():
            if int(symbol.attrib["id"]) == int(symbol_id):
                _find_algo_for_a_comment(comment, algorithms)
                break
    return list(algorithms)

def _find_problem_domains_for_a_comment(comment, problem_domains):
    all_problem_domains = comment.find('PROBLEM_DOMAINS')
    for pd in all_problem_domains.getchildren():
        problem_domains.add(pd.attrib['word'])

def find_problem_domains(symbol_id):
    tree = ET.parse("/workspace/comments_libpng.xml")
    root = tree.getroot()
    problem_domains = set()
    for comment in root.getchildren():
        symbols = comment.find("SYMBOLS")
        if symbols == None:
            continue
        for symbol in symbols.getchildren():
            if int(symbol.attrib["id"]) == int(symbol_id):
                _find_problem_domains_for_a_comment(comment, problem_domains)
                break
    return list(problem_domains)

def _find_all_symbols_for_a_comment(comment, symbols):
    all_symbols = comment.find("SYMBOLS")
    if all_symbols == None:
        return
    for symbol in all_symbols.getchildren():
        symbols.add(int(symbol.attrib['id']))

def find_all_symbols_for_application_concept(concept):
    tree = ET.parse("/workspace/comments_libpng.xml")
    root = tree.getroot()
    symbols = set()
    for comment in root.getchildren():
        all_problem_domains = comment.find("PROBLEM_DOMAINS")
	if all_problem_domains == None:
	    continue
        for pd in all_problem_domains.getchildren():
            if pd.attrib['word'] == concept:
                _find_all_symbols_for_a_comment(comment, symbols)
                break

    return list(symbols)

def keyword_search(keyword,attribs_to_return=None):
	tree = ET.parse("/workspace/comments_libpng.xml")
	root = tree.getroot()
	comment_info = {}
	all_comments = []
	for comment in root.getchildren():
		if keyword.strip() in comment.attrib['comment_text']:
			if attribs_to_return is None:
				all_comments.append(comment)
			for attrribute in attribs_to_return:
				try:
					myval = comment.attrib[attrribute]
					if myval is not None:
						if attrribute not in comment_info:
							comment_info[attrribute] = []
						comment_info[attrribute].append(myval)
				except:
					print("### Attribute " + attrribute +" NOT FOUND!")
	if attribs_to_return is None:
		return all_comments
	return comment_info

def code_talks_about(query):
    s="<HTML><BODY>"
    info = keyword_search(query, ["comment_scope_end","comment_scope_start","file_name"])
    if "file_name" not in info:
        s += "No Part of Code talks about " +query + " <br>"
    else:
        s += "Part of Code(s) that talk about " + query +" are:<br>"
        for (f, st, end) in zip(info['file_name'],info['comment_scope_start'],info['comment_scope_end']):
            s += "File: " + f + ", Lines: " + str(st) +" to " +str(end)+"<br>"
    s += '</BODY></HTML>'
    with open ('temp.html', 'w') as fp:
        fp.write(s)
    return "temp.html"

def files_using_macro(query):
    s="<HTML><BODY>"
    info = keyword_search(query, ["file_name"])
    if "file_name" not in info:
        s += "No file uses the macro " +query + " <br>"
    else:
        s += "File(s) which use the macro " + query +" are:<br>"
        all_f = set(info['file_name'])
        for f in all_f:
            s += f + "<br>"
    s += '</BODY></HTML>'
    with open ('temp.html', 'w') as fp:
        fp.write(s)
    return "temp.html"


if __name__ == '__main__':
    # Test id - 3376192215
    if len(sys.argv)!=2:
        print("Give 1 argument")
    print(keyword_search("stdio-free compilation",["comment_scope_end","comment_scope_start","file_name"]))
    # print("Algorithms")
    # print(find_algorithm(sys.argv[1]))
    # print("Problem Domains")
    # print(find_problem_domains(sys.argv[1]))
    # print("All Symbols for a Problem Domain")
    # print(find_all_symbols_for_application_concept('chunk'))
