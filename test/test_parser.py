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
        """Comments create a CommentNode"""

        comment_str = "# This is a comment\n# This is another comment"
        doc = parser.parse(comment_str)

        self.assertEqual(len(doc.children()), 2)

        

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

        
    def test_headlines_successors(self):
        """Adding multiple headlines with higher level makes them children of
        the previous one.
        """
        headline_str = "* First level\n** Second level\n*** Third level"
        doc = parser.parse(headline_str)
        self.assertEqual(len(doc.children()), 1)

        h1 = doc.children()[0]
        self.assertEqual(len(h1.children), 1)

        h2 = h1.children[0]
        self.assertEqual(len(h2.children), 1)

        h3 = h2.children[0]
        self.assertEqual(len(h3.children), 0)


    def test_headlines_samelevel(self):
        """Adding a headline with the same level as the previous one attaches it
        to the previous' parent.
        """
        headline_str = "* One\n** Two\n** Two\n**\
        Another one"
        doc = parser.parse(headline_str)
        self.assertEqual(len(doc.children()), 1)

        h1 = doc.children()[0]
        self.assertEqual(len(h1.children), 3)

    def test_headlines_predecessors(self):
        """Adding a headline with a lower level than the previous one makes the
        new one a direct child of the previous' first ancestor with lower level
        than the new one.
        """
        headline_str = "* One\n** Two\n*** Three\n** Two\n*** Three\n* One"

        doc = parser.parse(headline_str)
        self.assertEqual(len(doc.children()), 2)

        h1_1 = doc.children()[0]
        h1_2 = doc.children()[1]

        self.assertEqual(len(h1_1.children), 2)
        self.assertEqual(len(h1_2.children), 0)

        h2_1 = h1_1.children[0]
        h2_2 = h1_1.children[1]

        self.assertEqual(len(h2_1.children), 1)
        self.assertEqual(len(h2_2.children), 1)

    # Perhaps test some edge cases of headlines?
 
    def test_doc_representation(self):
        """Just having a default representation of the document for easier
        debugging.
        """
        # NOTE: Consider whether the representation should be the same as the
        # oiginal text, or whether it should prettify it. (E.g. multiple \n's)
        
        doc_str = "# This is a comment\n* One\nText text"
        doc = parser.parse(doc_str)

        self.assertEqual(str(doc), doc_str)

        
