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
        self.assertEqual(org_to_html(doc), '<h1>Hello</h1>')

        doc_str = '* One\n** One.One\n** One.Two\n*** One.Two.One'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), 
                         '<h1>One</h1><h2>One.One</h2><h2>One.Two</h2>\
<h3>One.Two.One</h3>')

    def test_text(self):
        """Text nodes should be enclosed in <p> tags"""

        doc_str = 'Just some text'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), '<p>Just some text</p>')

        doc_str = 'Text line 1\nText line 2'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), '<p>Text line 1\nText line 2</p>')

        doc_str = 'Text\n\nText2'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), 
                         '<p>Text</p><p></p><p>Text2</p>')

    def test_lists(self):
        """Lists should produce <ul>/<ol> and <li> elements"""

        doc_str = '+ One\n+ Two'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), '<ul><li>One</li><li>Two</li></ul>')

        
        doc_str = '1. One\n2. Two'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), '<ol><li>One</li><li>Two</li></ol>')

        doc_str = '- A\n 1. B\n 2. C'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), '<ul><li>A<ol><li>B</li><li>C</li>\
</ol></li></ul>')

        doc_str = '- A\n   - B\n  - C'
        doc = parser.parse(doc_str)
        self.assertEqual(org_to_html(doc), '<ul><li>A<ul><li>B</li></ul><ul>\
<li>C</li></ul></li></ul>')
