import unittest

from orgpython.parser import parser
from orgpython.export.html import org_to_html

class TestHtml(unittest.TestCase):

    def setUp(self):
        pass

    def test_empty_doc(self):
        """An empty tree exported to HTML should generate an empty string"""
        doc_str = ''

        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), '')
        

    def test_headline(self):
        """Headlines should produce <hx> tags"""

        doc_str = '* Hello'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), '<h1>Hello</h1>\n')

        doc_str = '* One\n** One.One\n** One.Two\n*** One.Two.One'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), 
                         '<h1>One</h1>\n<h2>One.One</h2>\n<h2>One.Two</h2>\n\
<h3>One.Two.One</h3>\n')

