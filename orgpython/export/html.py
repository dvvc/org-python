"""
Parsed Org-Tree to HTML conversion

"""

import StringIO
import re

# text substitutions
# Explanation for text formatting: We want to match text surrounded by a special
# character (e.g. /, *, _). However, if before the (first) special char there is
# a backslash, then do not match. That produces the expression ([^\\]|\A)
# --either a character which is not a backslash, or the start of a string--
text_subs = [
    # italics
    (r'([^\\]|\A)/([^/\s][^/]+[^/\s\\])/', r'\1<i>\2</i>'),
    # bold
    (r'([^\\]|\A)\*([^*\s][^*]+[^*\s\\])\*', r'\1<b>\2</b>'),
    # underscore
    (r'([^\\]|\A)_([^_\s][^_]+[^_\s\\])_', r'\1<u>\2</u>'),
    # datetime
    (r'<(\d{4}-\d{2}-\d{2} [a-zA-Z]{3} \d{2}:\d{2})>',
     r'<span class="datetime">\1</span>'),
    # date
    (r'<(\d{4}-\d{2}-\d{2} [a-zA-Z]{3})>', r'<span class="date">\1</span>'),
    # external link
    (r'\[\[([a-zA-Z]+://[^\]]+)\]\[([^\]]+)\]\]',
     r'<a href="\1">\2</a>'),
    # internal link
    (r'\[\[([^\]]+)\]\[([^\]]+)\]\]',
     r'<a href="#\1">\2</a>'),
    # escaped symbols
    (r'\\([\*/_])', r'\1'),
    ]

# Global export options, set up in org_to_html
_default_options = {
    'remove_empty_p': False
}

_export_options = {}


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

            text_str = text_to_html(str(self.element))
            if _export_options['remove_empty_p'] and re.match('^\s*$', text_str):
                output = ''
            else:
                output = '<p>%s</p>' % text_str

            return output

        elif class_name == 'ListNode':
            if self.element.ordered:
                return '<ol>'
            else:
                return '<ul>'
   
        elif class_name == 'ListItemNode':
            return '<li>%s' % text_to_html(self.element.text)

        elif class_name == 'HRuleNode':
            return '<hr/>'

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

def org_to_html(tree, **export_options):
    """Traverse the org tree and execute the appropriate function to generate
    html code.
    """
    
    # update global options
    # FIXME: Perhaps there's a better way of doing this?
    _export_options.update(_default_options)
    _export_options.update(export_options)

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
