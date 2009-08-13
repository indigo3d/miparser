#! /usr/bin/python

import sys, re

p = re.compile( r'([A-Z0-9]+)_\b' ) 

f = open( sys.argv[1] , 'r')
s = f.read()
f.close()
s = p.sub( r'\1', s)
f = open( sys.argv[1] , 'w')
f.write(s)
f.close()
