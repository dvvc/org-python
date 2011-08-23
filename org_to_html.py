#!/usr/bin/python

"""
Convert from an org-file to HTML using the parsing and exporting capabilities of
org-python.

Usage: %s [-o outfile] input.org
"""

import getopt
import sys

from orgpython.parser import parser
from orgpython.export.html import org_to_html

def usage():
    print __doc__ % sys.argv[0]
    sys.exit(1)

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'o:', ['output='])
    except getopt.GetoptError, e:
        print e
        usage()

    output = None

    for opt, arg in opts:
        if opt in ('-o', '--output'):
            output = arg


    if len(args) != 1:
        print 'Need to specify input file'
        usage()

    input_file = args[0]

    try:
        fin = open(input_file, 'r')
    except IOError:
        print 'Could not find', input_file

    org_tree = parser.parse(fin)
    fin.close()

    if output:
        try:
            out = open(output, 'w')
        except IOError, e:
            print e
            sys.exit(1)

    else:
        out = sys.stdout

    out.write(str(org_to_html(org_tree)))

    out.close()
                        

    
    
