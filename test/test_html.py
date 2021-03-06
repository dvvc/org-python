import unittest

from orgpython.parser import parser
from orgpython.export.html import org_to_html

class TestHtml(unittest.TestCase):

    def setUp(self):
        pass

    def _assert_html(self, org_str, html_str, **export_options):
        """Helper method to assert the HTML representation of a given org string
        is what it should be.
        """
        doc = parser.parse(org_str)
        self.assertEqual(org_to_html(doc, **export_options), html_str)

    def test_empty_doc(self):
        """An empty tree exported to HTML should generate an empty string"""

        self._assert_html('', '')

    def test_headline(self):
        """Headlines should produce <hx> tags"""

        self._assert_html('* Hello', '<h1>Hello</h1>')

        self._assert_html('* A\n** A.1\n** A.2\n*** A.2.1',
                          '<h1>A</h1><h2>A.1</h2><h2>A.2</h2><h3>A.2.1</h3>')

    def test_text(self):
        """Text nodes should be enclosed in <p> tags"""

        self._assert_html('Just some text', '<p>Just some text</p>')

        self._assert_html('Text line 1\nText line 2', 
                          '<p>Text line 1\nText line 2</p>')
            
        self._assert_html('Text\n\nText2',
                          '<p>Text</p><p></p><p>Text2</p>')

        self._assert_html('Text\n\nText2',
                          '<p>Text</p><p>Text2</p>',
                          remove_empty_p=True)

        self._assert_html('Text\n\nText2',
                          '<p>Text</p><p></p><p>Text2</p>')


        self._assert_html('Text with *bold* words',
                          '<p>Text with <b>bold</b> words</p>')

        self._assert_html('*elisp shell scripting*',
                          '<p><b>elisp shell scripting</b></p>')

        self._assert_html('Text with /italics/',
                          '<p>Text with <i>italics</i></p>')

        self._assert_html('Text without / italics/',
                          '<p>Text without / italics/</p>')

        self._assert_html('/elisp shell scripting/',
                          '<p><i>elisp shell scripting</i></p>')

        self._assert_html('Text with _underscore_',
                          '<p>Text with <u>underscore</u></p>')

        self._assert_html('_elisp shell scripting_',
                          '<p><u>elisp shell scripting</u></p>')


        self._assert_html('Two *bold* *words*',
                          '<p>Two <b>bold</b> <b>words</b></p>')

    
    def test_escaping(self):

        self._assert_html('backslash \\', '<p>backslash \\</p>')


        self._assert_html('this is not \\/italics/',
                          '<p>this is not /italics/</p>')

        self._assert_html('escaped *bold\\*',
                          '<p>escaped *bold*</p>')


    def test_dates(self):

        self._assert_html('<2011-08-21 Sun>',
                          '<p><span class="date">2011-08-21 Sun</span></p>')

        self._assert_html('<2011-08-21 Sun 10:00>',
                          '<p><span class="datetime">2011-08-21 Sun 10:00\
</span></p>')



    def test_links(self):

        self._assert_html('[[http://www.itsahack.com][Go]]',
                          '<p><a href="http://www.itsahack.com">Go</a></p>')

        self._assert_html('[[sometag][Goto Tag]]',
                          '<p><a href="#sometag">Goto Tag</a></p>')

        self._assert_html('[[http://itsahack.com/projects/org-python][x]]',
                          '<p><a href="http://itsahack.com/projects/org-python"\
>x</a></p>')

    def test_lists(self):
        """Lists should produce <ul>/<ol> and <li> elements"""


        self._assert_html('+ One\n+ Two',
                          '<ul><li>One</li><li>Two</li></ul>')

        self._assert_html('1. One\n2. Two',
                          '<ol><li>One</li><li>Two</li></ol>')

        self._assert_html('- A\n 1. B\n 2. C',
                          '<ul><li>A<ol><li>B</li><li>C</li></ol></li></ul>')

        self._assert_html('- A\n   - B\n  - C',
                          '<ul><li>A<ul><li>B</li></ul><ul><li>C</li></ul>\
</li></ul>')

    def test_text_in_lists(self):

        self._assert_html('- [[A][B]]\n- *bold*',
                          '<ul><li><a href="#A">B</a></li><li><b>bold</b></li>\
</ul>')


    def test_hr(self):
        
        self._assert_html('-----', '<hr/>')
        
        self._assert_html('- li1\n-----\n- li2',
                          '<ul><li>li1</li></ul><hr/><ul><li>li2</li></ul>')

        self._assert_html('text\n-----\ntext',
                          '<p>text</p><hr/><p>text</p>')


    def test_hl_offset(self):
        """When specifying a level_offset, add it to the headlines' level"""

        self._assert_html('* foo', '<h1>foo</h1>')

        self._assert_html('* foo', '<h2>foo</h2>', hl_offset=1)
