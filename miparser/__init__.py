#!/usr/local/bin/python

"""
This is an mi parser *proof-of-concept* written in python.  It is based on the yacc scene grammar provided with mental ray 3.5.6, 
and it can already parse any 3.5.6 compatible mi file, however, only a small portion of the parsed data is currently being stored
in data structures. The yacc grammar was converted to python code compatible with PLY (Python Lex Yacc) using a utility call 
yply (included with PLY as an example).

I am trying to design the parser such that, once parsed, the data can be
manipulated and used to write out a new mi file.  to aid this, each parsed object has a 'text' attribute which should
store the original text representation of the object for use when serializing (though in many cases i'm currently 
skipping it). i imagine each object would have a 'dirty' flag that gets set when any of its data is manipulated via 
the class's properties, thus triggering the 'text' to be regenerated.  There is most likely a better way to do this, but for
now, i'm just trying to gather data into python structures while keeping an eye out for the end goal of re-writing mi files.

the parser is also designed to represent data as it is stored in the mi file as opposed to attempting to generate
the structs that would be available at render time.  below each rule you can see commented out the mental ray C api
code that is used to create a scene database from an mi file for rendering (it is quite enlightening to read). both 
structures -- one for the pure mi file, and one for the mr scene database -- could be created side-by-side
in this parser. 

Current Limitations:
    - only a very small portion of the possible mi syntax is converted to class objects (mostly focused on instances)

Future Direction:
    - the base Entity class needs traversal methods akin to python's built-in xml.etree.ElementTree
    - load an mi file, traverse the scene graph, make an edit, write out a new file
    - an additional layer to create maya/nuke files from mi

Other Thoughts:
    I really wanted to use ElementTree for this, but opted not to for several reasons:
        1. it was too xml-specific
        2. making new builders was not well-documented
        3. attribute data is stored in a dictionary, which has several limitations:
            - dicts don't maintain order
            - some objects are best represented as having data and no attributes (boolean, string, vector, transform) 
            - some objects have both data and attributes (instgroup has flags and a list of objects)
            
License: LGPL

"""

# project started by chad dombrova and luma pictures

import sys
sys.path.insert(0,"../..")

import mi_lexer
import mi_grammar

from ply import *




def parse(filename):
    """
    Returns a list of parsed objects. 
    
    >>> import miparser
    >>> data = miparser.parse('examples/test.mi')
    >>> data
    [None, None, None, None, None, None, None, None, None, None, None, None, <miparser.mi_grammar.NamedEntity object at 0x166a6f0>]
    >>> data[-1].attrs
    odict([('trace', Value('boolean','on',True)), ('shadow', Value('boolean','on',True)), ('shadowmap', Value('boolean','on',True)), ('visible', Value('boolean','on',True))])
    >>> data[-1].type
    'instance'
    >>> data[-1].name
    Value('string','"new.1_inst"','new.1_inst')
    """
    mi_grammar.parser.parse(open(filename).read(), debug=0)

    return mi_grammar.lexer.root



if __name__ == '__main__':
    if len(sys.argv) == 1:
        raise SystemExit
    
    res = parse(sys.argv[1])
    print res
