# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
from django.test import TestCase

from translator import base
import views

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class MockTranslator(base.Translator):
    def translate(self, text, target, source=None):
        return u'a'

    def group_translate(self, texts, target, source=None):
        return [u'a' for e in texts]

class HtmlTranslateTest(TestCase):
    def setUp(self):
        # mock _get_translator() function
        views._get_translator = lambda: MockTranslator(None)

    def testIgnoreScriptAndStyleElement(self):
        src = u'<html><head><style>html{background:white;}//注释</style><script>function(){alert("您好");}</script></head><body></body></html>'
        actual = views._translate(src, 'en')
        actual = actual.replace('\n', '').replace('\t', '')
        self.assertEqual(src, actual)
        # ascii str content
        src = '<html><head><style>html{background:white;}</style><script>function(){alert("hello");}</script></head><body></body></html>'
        actual = views._translate(src, 'en')
        actual = actual.replace('\n', '').replace('\t', '')
        self.assertEqual(src, actual)

    def testTranslateDesiredElements(self):
        src = u'<html><head><title>标题</title></head><body><h1>标题一</h1><h2>标题二</h2><h3>标题三</h3><h4>标题4</h4><p>正文</p><div><a href="#">链接</a></div></body></html>'
        expect = u'<html><head><title>a</title></head><body><h1>a</h1><h2>a</h2><h3>a</h3><h4>a</h4><p>a</p><div><a href="#">a</a></div></body></html>'
        actual = views._translate(src, 'en')
        actual = actual.replace('\n', '').replace('\t', '')
        self.assertEqual(expect, actual)

    def testTranslateIgnoreComment(self):
        src = u'<html><body><!--comment--></body></html>'
        actual = views._translate(src, 'en')
        actual = actual.replace('\n', '').replace('\t', '')
        self.assertEqual(src, actual)

    def testGroupTranslateDesiredElements(self):
        src = u'<html><head><title>标题</title></head><body><h1>标题一</h1><h2>标题二</h2><h3>标题三</h3><h4>标题4</h4><p>正文</p><div><a href="#">链接</a></div></body></html>'
        expect = u'<html><head><title>a</title></head><body><h1>a</h1><h2>a</h2><h3>a</h3><h4>a</h4><p>a</p><div><a href="#">a</a></div></body></html>'
        actual = views._translate(src, 'en')
        actual = actual.replace('\n', '').replace('\t', '')
        self.assertEqual(expect, actual)

    def test_group_translate_test_page(self):
        path = os.path.join(os.path.dirname(__file__), '../static/test.html')
        f = open(path, 'r')
        src = f.read()
        actual = views._translate(src, 'en', 'zh-CHS')
