"""
Parsed Org-Tree to HTML conversion

"""

import StringIO
import re

# text substitutions
text_subs = [
    (r'/([^/]*)/', r'<i>\1</i>'),
    (r'\*([^*]*)\*', r'<b>\1</b>'),
    (r'_([^_]*)_', r'<u>\1</u>'),
    (r'<(\d{4}-\d{2}-\d{2} [a-zA-Z]{3} \d{2}:\d{2})>',
     r'<span class="datetime">\1</span>'),
    (r'<(\d{4}-\d{2}-\d{2} [a-zA-Z]{3})>', r'<span class="date">\1</span>'),
    
    ]

def text_to_html(text):
    """Convert any special sequences in text to HTML. These can appear in
    Headlines, TextNodes or Lists.
    """
    for pattern, repl in text_subs:
        text = re.sub(pattern, repl, text)

    return text


class EnterElement:
    def __init__(self, element):
        self.element = element

    def generate(self):
        
        class_name = self.element.__class__.__name__

        if class_name == 'HeadlineNode' and self.element.level != 0:
            return '<h%d>%s</h%d>' % (self.element.level, self.element.text, \
                                          self.element.level)

        elif class_name == 'TextNode':
            return '<p>%s</p>' % text_to_html(str(self.element))

        elif class_name == 'ListNode':
            if self.element.ordered:
                return '<ol>'
            else:
                return '<ul>'
        elif class_name == 'ListItemNode':
            return'<li>%s' % self.element.text
        

class LeaveElement:
    def __init__(self, element):
        self.element = element

    def generate(self):
        class_name = self.element.__class__.__name__

        if class_name == 'ListNode':
            if self.element.ordered:
                return '</ol>'
            else:
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
