"""
Parsed Org-Tree to HTML conversion

"""

import StringIO


class EnterElement:
    def __init__(self, element):
        self.element = element

    def generate(self):
        
        class_name = self.element.__class__.__name__

        if class_name == 'HeadlineNode' and self.element.level != 0:
            return '<h%d>%s</h%d>' % (self.element.level, self.element.text, \
                                          self.element.level)

        elif class_name == 'TextNode':
            return '<p>%s</p>' % str(self.element)

        elif class_name == 'ListNode':
            return '<ul>'
        elif class_name == 'ListItemNode':
            return'<li>%s' % self.element.text
        

class LeaveElement:
    def __init__(self, element):
        self.element = element

    def generate(self):
        class_name = self.element.__class__.__name__

        if class_name == 'ListNode':
            return '</ul>'
        elif class_name == 'ListItemNode':
            return '</li>'

def org_to_html(tree):
    """Traverse the org tree and execute the appropriate function to generate
    html code.
    """
    
    events = []
    output = StringIO.StringIO()

    events.append(EnterElement(tree.root))

    # Traverse the tree pre-order
    while len(events) != 0:

        event = events.pop(0)

        # Handle the node
        output.write(event.generate())

        # Add leave event and children if this is an EnterElement event
        if isinstance(event, EnterElement):
            children = [EnterElement(child) for child in event.element.children]
            leave_event = [LeaveElement(event.element)]
            events = children + leave_event + events

    result = output.getvalue()
    output.close()

    return result
