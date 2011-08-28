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
        self.assertEqual(len(text_node.children), 0)


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


    def test_doc_representation(self):
        """Just having a default representation of the document for easier
        debugging.
        """
        doc_str = "# This is a comment\n* One\nText text"
        doc = parser.parse(doc_str)

        self.assertEqual(str(doc), doc_str)

        doc_str = "Text\nMore text\n\n\nSome empty lines and text\n* HL"
        doc = parser.parse(doc_str)

        self.assertEqual(str(doc), doc_str)

        doc_str = "- List one\n + Slist one\n + Slist two"
        doc = parser.parse(doc_str)

        self.assertEqual(str(doc), doc_str)
        
    def test_unordered_lists(self):
        """List items start with zero or more spaces, a list character (which
        can be either -, + or *), a space and some text
        """
        list_str = '- Item 1\n- Item 2\n- Item 3'
        doc = parser.parse(list_str)

        self.assertEqual(len(doc.children()), 1)

        ul = doc.children()[0]
        self.assertEqual(len(ul.children), 3)

        li1 = ul.children[0]
        self.assertTrue(isinstance(li1, parser.ListItemNode))
        self.assertEqual(li1.parent.char, '-')
        self.assertEqual(li1.parent.level, 0)
        self.assertEqual(li1.text, 'Item 1')
        
        list_str = '- One\n + One.One\n + One.Two'
        doc = parser.parse(list_str)

        self.assertEqual(len(doc.children()), 1)

        ul = doc.children()[0]
        self.assertEqual(len(ul.children), 1)
        
        li1 = ul.children[0]
        self.assertEqual(len(li1.children), 1)

        ul2 = li1.children[0]
        self.assertEqual(len(ul2.children), 2)

        list_str = '* H\n- L\ntext\n** H\n + L\n  + L'
        doc = parser.parse(list_str)

        self.assertEqual(len(doc.children()), 1)
        
        h1 = doc.children()[0]
        # H has three children: the list, the text, the 2nd level HL
        self.assertEqual(len(h1.children), 3)

        ul = h1.children[0]
        self.assertEqual(len(ul.children), 1)

        li = ul.children[0]
        self.assertEqual(len(li.children), 0)

        text = h1.children[1]
        self.assertEqual(''.join(text.lines), 'text')

        h2 = h1.children[2]
        self.assertEqual(len(h2.children), 1)

        ul = h2.children[0]
        self.assertEqual(len(ul.children), 1)

        list_str = '- L0\n   + L3\n  + L2\n - L1'
        doc = parser.parse(list_str)

        self.assertEqual(len(doc.children()), 1)

        ul1 = doc.children()[0]
        self.assertEqual(len(ul1.children), 1)
        self.assertTrue(isinstance(ul1.children[0], parser.ListItemNode))

        l0 = ul1.children[0]
        self.assertEqual(len(l0.children), 3)

        list_str = '* HL\n- A\n- B\n\n\ntext after list'
        doc = parser.parse(list_str)

        hl = doc.children()[0]

        # Since there are two empty lines after the list, the TextNode should be
        # a child of the HeadlineNode, not the last ListItemNode. Since we
        # represent empty lines as empty TextNodes, there are three children
        # under the HL: the list, the (empty) TextNode and the other TextNode
        self.assertEqual(len(hl.children), 3)

        list_str = 'text\n   - L3\n- L0'
        doc = parser.parse(list_str)

        self.assertTrue(len(doc.children()), 3)
        self.assertTrue(len(doc.children()[1].children), 1)
        self.assertTrue(len(doc.children()[2].children), 1)


        # A text node with the equal or less indentation than the last list item
        # ends that list
        list_str = '- list item\ntext'
        doc = parser.parse(list_str)
        self.assertEqual(len(doc.children()), 2)

        # If the text node has more indentation, it is part of the list item
        list_str = '- list item\n text'
        doc = parser.parse(list_str)
        self.assertEqual(len(doc.children()), 1)
        self.assertEqual(len(doc.children()[0].children[0].children), 0)

        # If there is an empty line after the list item, then the TextNode is a
        # child of the item
        list_str = '- list item\n\n  text'
        doc = parser.parse(list_str)
        self.assertEqual(len(doc.children()), 1)
        li = doc.children()[0].children[0]

        # list item has an empty TextNode and another one with text
        self.assertEqual(len(li.children), 2)


    def test_ordered_lists(self):
        """Ordered lists are the same as Unordered ones, but have numbers and
        either the character '.' or ')' after it
        """

        list_str = '1. One'
        
        doc = parser.parse(list_str)
        self.assertEqual(len(doc.children()), 1)

        ol = doc.children()[0]
        self.assertTrue(isinstance(ol, parser.ListNode))

        self.assertEqual(str(doc), list_str)

        list_str = '- One\n 1. OneOne\n 2. OneTwo'

        doc = parser.parse(list_str)
        self.assertEqual(len(doc.children()), 1)

        ul = doc.children()[0]
        self.assertEqual(len(ul.children), 1)

        li = ul.children[0]
        ol = li.children[0]

        self.assertEqual(len(ol.children), 2)


    def test_list_representation(self):
        """Test that different list representations are correct"""
        
        lr = ['- L1\n- L2\n- L3',
              'text\n- L1\n- L2\ntext\n- L3',
              '* H\n- L1\n - L2\n** H\n- L3',
              '   - L1\n  - L2\n - L3',
              '- L1\n   - L2\n - L3'
              ]

        for l in lr:
            self.assertEqual(l, str(parser.parse(l)))
            
    def test_options(self):
        """The document may have options in the form #+NAME: VALUE"""

        options_str = '# One comment\n#+TITLE: The title'

        doc = parser.parse(options_str)

        self.assertEqual(doc.options['TITLE'], 'The title')

        self.assertEqual(str(doc), options_str)


    def test_horizontal_rule(self):
        """An horizontal rule has 5 or more dashes. It breaks the flow of lists
        and text"""

        doc_str = '------'
        doc = parser.parse(doc_str)
        
        self.assertEqual(len(doc.children()), 1)
        self.assertTrue(isinstance(doc.children()[0], parser.HRuleNode))
        self.assertEqual(str(doc), doc_str)

        doc_str = '  - li 1\n-----\n  - li 2'
        doc = parser.parse(doc_str)

        self.assertEqual(len(doc.children()), 3)
        self.assertEqual(str(doc), doc_str)
