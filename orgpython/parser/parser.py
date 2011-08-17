"""
This module provides a parser method for org-mode files. It basically performs
line-by-line parsing and constructs an internal representation of a document.

Supported features:
  - Options
  - Comments
  - Text
  - Headlines

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
        if parent:
            parent.append(self)

    def append(self, child):
        self.children.append(child)

    def __str__(self):
        return '\n'.join([str(ch) for ch in self.children])
        

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

    # FIXME: Ugly!
    def __str__(self):

        if self.level != 0:
            hl_str = self.level * '*' + ' ' + self.text
        else:
            hl_str= ''

        children_str = OrgNode.__str__(self)

        if children_str != '' and self.level != 0:
            hl_str += '\n'

        return hl_str + children_str

class UnorderedListNode(OrgNode):
    """An unordered list item"""
    def __init__(self, parent, char, level, text):
        OrgNode.__init__(self, parent)
        self.char = char 
        self.level = level
        self.text = text


    def __str__(self):
        hl_str = self.level * ' ' + self.char + ' ' + self.text
        children_str = OrgNode.__str__(self)

        if children_str != '':
            hl_str += '\n'

        return hl_str + children_str


class OrderedListNode(UnorderedListNode):
    """An ordered list node"""
    def __init__(self, parent, number, char, level, text):
        UnorderedListNode.__init__(self, parent, number+char, level, text)

class LineMatcher:
    """Helper class for compiling all possible patterns and performing line by
    line matching.
    """
    ## List of regexes
    RE = {'COMMENT': re.compile(r'^#.*'),
          'OPTION': re.compile(r'^#\+([A-Z_]+):(.*)$'),
          'HEADLINE': re.compile(r'^(\*+)\s(.*)$'),
          'ULIST': re.compile(r'^(\s*)([\+\-\*])\s(.*)$'),
          'OLIST': re.compile(r'^(\s*)(\d+)([\.\)])\s(.*)$')

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
    prev_hl = orgdoc.root
    prev_list = None

    for line in doc_handle:
    
        line = line.strip('\n')

        if matcher.matches(line, 'COMMENT'):
            comment_node = CommentNode(orgdoc.root, line[1:])

        elif matcher.matches(line, 'HEADLINE'):
            level = matcher.match.group(1).count('*')
            text = matcher.match.group(2)

            parent = __find_parent(level, prev_hl)

            headline_node = HeadlineNode(parent, level, text)
            prev_node = headline_node
            prev_hl = headline_node
            prev_list = None

        elif matcher.matches(line, 'OLIST'):
            level = len(matcher.match.group(1))
            number = matcher.match.group(2)
            char = matcher.match.group(3)
            text = matcher.match.group(4)

            if prev_list == None:
                parent = prev_node
            else:
                parent = __find_parent(level, prev_list)
            
            list_node = OrderedListNode(parent, number, char, level, text)
            prev_list = list_node
            prev_node = list_node


        elif matcher.matches(line, 'ULIST'):
            level = len(matcher.match.group(1))
            char = matcher.match.group(2)
            text = matcher.match.group(3)

            if prev_list == None:
                parent = prev_node
            else:
                parent = __find_parent(level, prev_list)
            
            list_node = UnorderedListNode(parent, char, level, text)
            prev_list = list_node
            prev_node = list_node

        else:
            # FIXME: Right now each line is a TextNode with a single child
            text_node = TextNode(prev_node)
            text_node.append(line)

    doc_handle.close()

    return orgdoc
    
