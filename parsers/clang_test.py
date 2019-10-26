#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import clang.cindex as cl

# Set the clang shared object. The python interface is just a proxy for the actual clang
cl.Config.set_library_file("/usr/local/lib/libclang.so.6.0")

function_calls = []             # List of AST node objects that are function calls
function_declarations = []      # List of AST node objects that are fucntion declarations

# Traverse the AST tree
def traverse(node):
    # print node.kind.name
    if node.kind.name == 'CALL_EXPR':
        # print (node.extent)
        print '%s\t%s\t%s\t' % (node.location.file, node.location.line, node.spelling),
        for tok in node.get_tokens():
            print tok.spelling,# tok.location, tok.extent
        print
        # Add the node to function_calls
        # exit()

    # Recurse for children of this node
    for child in node.get_children():
        traverse(child)


index = cl.Index.create()

# Generate AST from filepath passed in the command line
tu = index.parse(sys.argv[1])

root = tu.cursor        # Get the root of the AST
traverse(root)