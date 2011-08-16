"""
This module provides a parser method for org-mode files. It basically performs
line-by-line parsing and constructs an internal representation of a document.

Supported features:
  - Options
  - Comments
  - Text
  - Headlines

TODO: When adding a node to the hierarchy, having to add the parent in the
constructor and then calling append is redundant  
TODO: Should we consider Comments as nodes? or just disregard them?
"""
import re
import StringIO


class OrgDoc:
    """An org document"""
    def __init__(self):
        # this is a special Headline, which shouldn't be printed. It is just
        # used to keep the tree hierarchy
        self.root = HeadlineNode(None, 0, None) 

    def children(self):
        return self.root.children

    def __str__(self):
        return str(self.root)

class OrgNode:
    """A node"""
    def __init__(self, parent):
        self.children = []
        self.parent = parent

    def append(self, child):
        self.children.append(child)

    def __str__(self):
        return "".join([str(ch) for ch in self.children])
        

# TODO: Not sure if treating lines as children is intuitive
class TextNode(OrgNode):
    """Just text"""
    def __init__(self, parent):
        OrgNode.__init__(self, parent)

class CommentNode(OrgNode):
    def __init__(self, parent, text):
        OrgNode.__init__(self, parent)
        self.text = text

    def __str__(self):
        return '#' + self.text

    
class HeadlineNode(OrgNode):
    """A headline"""
    def __init__(self, parent, level, text):
        OrgNode.__init__(self, parent)
        self.level = level
        self.text = text

    def __str__(self):

        if self.level != 0:
            hl_str = self.level * '*' + ' ' + self.text + '\n'
        else:
            hl_str= ''

        children_str = OrgNode.__str__(self)
        return hl_str + children_str

class LineMatcher:
    """Helper class for compiling all possible patterns and performing line by
    line matching.
    """
    ## List of regexes
    RE = {'COMMENT': re.compile(r'^#.*'),
          'OPTION': re.compile(r'^#\+([A-Z_]+):(.*)$'),
          'HEADLINE': re.compile(r'^(\*+)\s+(.*)$')
          }

    def __init__(self):
        self.line = ''
        self.match = None

    def matches(self, line, linetype):

        # We need to reset these, since a matcher can be used multiple times
        self.line = line
        self.match = None

        try:
            pattern = self.RE[linetype]
            self.match = pattern.match(line)
        except KeyError:
            pass

        return self.match

def __find_parent(level, prev):
    """Find the parent of a new node with the given level in the tree hierarchy,
    if the previous considered node is prev.
    """
    while level < prev.level:
        prev = prev.parent

    # Determine this node's parent
    if level > prev.level:
        parent = prev
    else: # Must be level == prev.level because of the first loop
        parent = prev.parent

    return parent

def parse(doc):
    """Parse an org document.

    It receives either a string or a file handle, and returns its
    representation. 
    """

    if isinstance(doc, str):
        doc_handle = StringIO.StringIO(doc)
    else:
        raise Exception('Not supported')

    orgdoc = OrgDoc()

    matcher = LineMatcher()

    prev_node = orgdoc.root

    for line in doc_handle:
    
        if matcher.matches(line, 'COMMENT'):
            comment_node = CommentNode(orgdoc.root, line[1:])
            orgdoc.root.append(comment_node)

        elif matcher.matches(line, 'HEADLINE'):
            level = matcher.match.group(1).count('*')
            text = matcher.match.group(2)

            parent = __find_parent(level, prev_node)

            headline_node = HeadlineNode(parent, level, text)
            parent.append(headline_node)
            prev_node = headline_node
        else:
            text_node = TextNode(prev_node)
            text_node.append(line)
            orgdoc.root.append(text_node)

    doc_handle.close()

    return orgdoc
    
