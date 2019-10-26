#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex as cl

# Set the clang shared object. The python interface is just a proxy for the actual clang
cl.Config.set_library_file("/usr/local/lib/libclang.so.6.0")

# Traverse the AST tree
def traverse(node):
    # print all calls
    if node.kind.name == 'CALL_EXPR':
        # print (node.extent)
        print '%s\t%s\t%s\t' % (node.location.file, node.location.line, node.spelling),
        for tok in node.get_tokens():
            print re.sub('\t', ' ', tok.spelling),
        print
        
    # Recurse for children of this node
    for child in node.get_children():
        traverse(child)


index = cl.Index.create()

# Generate AST from filepath passed in the command line
tu = index.parse(sys.argv[1])

root = tu.cursor        # Get the root of the AST
traverse(root)