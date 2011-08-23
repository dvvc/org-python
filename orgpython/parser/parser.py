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
        self.options = {}

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
        

class TextNode(OrgNode):
    """Just text"""
    def __init__(self, parent):
        OrgNode.__init__(self, parent)
        self.lines = []

    def __str__(self):
        return "\n".join(self.lines)

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

class ListNode(OrgNode):
    """Base class for Lists"""
    def __init__(self, parent, char, level):
        OrgNode.__init__(self, parent)
        self.char = char
        self.level = level
        self.ordered = char[0].isdigit()

class ListItemNode(OrgNode):
    
    def __init__(self, parent, text):
        OrgNode.__init__(self, parent)
        self.text = text

    def __str__(self):
        hl_str = self.parent.level * ' ' + self.parent.char + ' ' + self.text
        children_str = OrgNode.__str__(self)

        if children_str != '':
            hl_str += '\n'

        return hl_str + children_str


class LineMatcher:
    """Helper class for compiling all possible patterns and performing line by
    line matching.
    """
    ## List of regexes
    RE = {'COMMENT': re.compile(r'^#.*'),
          'OPTION': re.compile(r'^#\+([A-Z_]+):(.*)$'),
          'HEADLINE': re.compile(r'^(\*+)\s(.*)$'),
          'ULIST': re.compile(r'^(\s*)([\+\-\*])\s(.*)$'),
          'OLIST': re.compile(r'^(\s*)(\d+[\.\)])\s(.*)$'),
          'EMPTYLINE': re.compile(r'^\s*$'),
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

# This works only with Headlines
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

def __find_list_parent(level, parent, char):
    """Similar to __find_parent, but in this case it tries to find a list's
    parent. The parent node can either be a ListItemNode or e.g. a
    HeadlineNode. In the first case we just return the LI's parent, in the
    second case we create a new ListNode with the --non-list-- parent and return
    it.
    """
    while level < parent.level:
        parent = parent.parent
        if isinstance(parent, ListItemNode):
            parent = parent.parent
        elif not isinstance(parent, ListNode):
            return ListNode(parent, char, level)
        else:
            raise Exception("ListNode is parent of ListNode!!")

    # There is an existing list
    if parent.level == level:
        # same level as previous list, it is a child
        return parent

    elif parent.level < level:
        # higher level, create a new list under the last child of the previous
        # list
        parent = parent.children[-1]
        return ListNode(parent, char, level)

    else:
        raise Exception("This shouldn't happen!")


    return parent
    

def parse(doc):
    """Parse an org document.

    It receives either a string or a file handle, and returns its
    representation. 
    """

    if isinstance(doc, str):
        doc_handle = StringIO.StringIO(doc)
    else:
        # Could check for other types, but let's assume doc is a file-like
        # object
        doc_handle = doc


    orgdoc = OrgDoc()

    matcher = LineMatcher()

    prev_node = orgdoc.root
    prev_hl = orgdoc.root
    prev_list = None
    prev_text = None

    for line in doc_handle:
    
        line = line.strip('\n')

        if matcher.matches(line, 'OPTION'):
            key = matcher.match.group(1)
            value = matcher.match.group(2).strip()
            orgdoc.options[key] = value

            # add the option line to the tree hierarchy to keep all info
            CommentNode(orgdoc.root, line[1:])

        elif matcher.matches(line, 'COMMENT'):
            CommentNode(orgdoc.root, line[1:])

        elif matcher.matches(line, 'HEADLINE'):
            level = matcher.match.group(1).count('*')
            text = matcher.match.group(2)

            parent = __find_parent(level, prev_hl)

            headline_node = HeadlineNode(parent, level, text)
            prev_node = headline_node
            prev_hl = headline_node
            prev_list = None
            prev_text = None

        elif matcher.matches(line, 'ULIST') or matcher.matches(line, 'OLIST'):
            level = len(matcher.match.group(1))
            char = matcher.match.group(2)
            text = matcher.match.group(3)

            # If there is no previous list, create a new one
            if prev_list == None:
                parent_list = ListNode(prev_node, char, level)
            else:
                # find the correct parent from the previous list
                parent_list = __find_list_parent(level, prev_list, char)

            list_item = ListItemNode(parent_list, text)

            prev_list = parent_list
            prev_node = list_item
            prev_text = None

        elif matcher.matches(line, 'EMPTYLINE'):
            # An empty line starts a new TextNode. We add an empty TextNode to
            # keep all information. In 'prettified' output those shouldn't be
            # used. Also, any current list is ended. Finally, we set the
            # prev_node to be a hl (since we want to forget about the current
            # list) 
            prev_text = None
            prev_list = None
            prev_node = prev_hl
            TextNode(prev_node)
        else:
            # Text
            if prev_text:
                # Add the line to the previous TextNode
                prev_text.lines.append(line)
            else:
                # start a new TextNode
                prev_text = TextNode(prev_node)
                prev_text.lines.append(line)


    doc_handle.close()

    return orgdoc
    
