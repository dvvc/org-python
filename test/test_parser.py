import unittest

from orgpython.parser import parser


class TestParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_empty_str(self):
        """Parsing an empty string should return an empty document"""

        empty_str = ""
        doc = parser.parse(empty_str)

        self.assertTrue(isinstance(doc, parser.OrgDoc))
        self.assertEqual(len(doc.children()), 0)


    def test_comments(self):
        """Comments are disregarded"""

        comment_str = "# This is a comment\n# This is another comment"
        doc = parser.parse(comment_str)

        self.assertEqual(len(doc.children()), 0)

        

    def test_single_line_text(self):
        """A line of text creates a TextNode child"""

        text_str = "This is a line of text"
        doc = parser.parse(text_str)

        self.assertEqual(len(doc.children()), 1)

        text_node = doc.children()[0]

        self.assertTrue(isinstance(text_node, parser.TextNode))
        self.assertEqual(len(text_node.children), 1)
        self.assertEqual(text_node.children[0], text_str)


    def test_single_headline(self):
        """A line starting with one or more asterisks is a HeadlineNode"""

        text = "Example headline"

        for i in range(1,6):
            headline_str = '*' * i + ' ' + text
            doc = parser.parse(headline_str)

            headline_node = doc.children()[0]

            self.assertTrue(isinstance(headline_node, parser.HeadlineNode))
            self.assertEqual(headline_node.level, i)
            self.assertEqual(headline_node.text, text)

        
