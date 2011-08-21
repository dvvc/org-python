"""
Parsed Org-Tree to HTML conversion

"""

import StringIO

# Processor functions
def headline_to_html(hl):
    pass



def org_to_html(tree):
    """Traverse the org tree and execute the appropriate function to generate
    html code.
    """
    
    elements = []
    output = StringIO.StringIO()

    elements.append(tree.root)

    # Traverse the tree pre-order
    while len(elements) != 0:

        el = elements.pop(0)
        
        class_name = el.__class__.__name__
        
        # Handle the node
        if class_name == 'HeadlineNode':
            if el.level != 0:
                output.write("<h%d>%s</h%d>\n" % (el.level, el.text, el.level))
        elif class_name == 'TextNode':
            output.write('<p>%s</p>\n' % str(el))
        elif class_name == 'ListNode':
            output.write('<ul>')
        elif class_name == 'ListItemNode':
            output.write('<li>%s</li>\n' % el.text)
        # End Handling the node

        elements = el.children + elements

    result = output.getvalue()
    output.close()

    return result
