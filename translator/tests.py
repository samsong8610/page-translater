# -*- coding: utf-8 -*-
import unittest
import urllib
import urllib2
import json

import bing

class BingTranslatorApiAuthTest(unittest.TestCase):
    def test_auth(self):
        """Test get access_token"""
        params = {
            'client_id': 'webtranslator8601',
            'client_secret': '38tnkL0LkSI5DjHq3mhFU0f7DKsm1/rizwEmMylZxtc=',
            'scope': 'http://api.microsofttranslator.com',
            'grant_type': 'client_credentials'
        }
        auth_url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13/'

        req = urllib2.Request(auth_url, urllib.urlencode(params))
        resp = urllib2.urlopen(req)
        self.assertEqual(200, resp.getcode())
        body = resp.read()
        resp_obj = json.loads(body)
        self.assertNotEqual(None, resp_obj['access_token'])

class BingTranslatorApiTest(unittest.TestCase):
    """Test Bing translator Api"""

    # api url
    api_url = 'http://api.microsofttranslator.com/v2/Http.svc/Translate'

    def setUp(self):
        params = {
            'client_id': 'webtranslator8601',
            'client_secret': '38tnkL0LkSI5DjHq3mhFU0f7DKsm1/rizwEmMylZxtc=',
            'scope': 'http://api.microsofttranslator.com',
            'grant_type': 'client_credentials'
        }
        auth_url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13/'

        req = urllib2.Request(auth_url, urllib.urlencode(params))
        resp = urllib2.urlopen(req)
        body = resp.read()
        resp_obj = json.loads(body)
        self.access_token = resp_obj['access_token']

    def test_translate(self):
        text = 'Use pixels to express measurements for padding and margins.'
        lang = 'en'
        to = 'zh-CHS'
        params = {'text': text, 'from': lang, 'to': to}
        auth_token = 'Bearer %s' % self.access_token
        url = '%(api)s?%(params)s' % {'api':self.api_url, 'params': urllib.urlencode(params)}
        req = urllib2.Request(url, None, {'Authorization': auth_token})
        resp = urllib2.urlopen(req)
        self.assertEqual(200, resp.getcode())

class BingTranslatorTest(unittest.TestCase):
    def setUp(self):
        self.translator = bing.Translator({'client_id': 'webtranslator8601', 'client_secret': '38tnkL0LkSI5DjHq3mhFU0f7DKsm1/rizwEmMylZxtc='})

    def test_translate(self):
        text = 'Use pixels to express measurements for padding and margins.'
        lang = 'en'
        to = 'zh-CHS'
        actual = self.translator.translate(text, to, lang)
        chinese = ''.join([ch for ch in actual if is_chinese_char(ch)])
        self.assertTrue(chinese != '')

    def test_translate_from_zh_to_en(self):
        text = u'中文'
        lang = 'zh-CHS'
        to = 'en'
        actual = self.translator.translate(text, to, lang)
        self.assertEqual('Chinese', actual)

    def test_group_translate(self):
        texts = [u'中', u'文']
        lang = 'zh-CHS'
        to = 'en'
        actual = self.translator.group_translate(texts, to, lang)
        self.assertEqual(2, len(actual))
        lang = None
        actual = self.translator.group_translate(texts, to, lang)
        print(actual)
        self.assertEqual(2, len(actual))

def is_chinese_char(ch):
    return u'\u4e00' <= ch <= u'\u9fff'

if __name__ == '__main__':
    unittest.main()
