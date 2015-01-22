import json
import time
import urllib
import urllib2
from lxml import etree
import logging

import base

# api url
API_TRANSLATE = 'http://api.microsofttranslator.com/v2/Http.svc/Translate'
API_TRANSLATE_ARRAY = 'http://api.microsofttranslator.com/v2/Http.svc/TranslateArray'
# authorize url
AUTH_URL = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13/'
# parameters keys
P_CLIENT_ID = 'client_id'
P_CLIENT_SECRET = 'client_secret'
P_SCOPE = 'scope'
P_GRANT_TYPE = 'grant_type'
P_TEXT = 'text'
P_FROM = 'from'
P_TO = 'to'
P_CONTENTTYPE = 'contentType'
# response keys
RESP_ACCESS_TOKEN = 'access_token'
RESP_EXPIRES_IN = 'expires_in'
MAX_CHARS_PER_REQUEST = 1000
MAX_TEXTS_PER_REQUEST = 500

class Translator(base.Translator):
    """Translation service based on Bing api"""

    def __init__(self, config):
        super(Translator, self).__init__(config)
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.access_token = None
        self.expires_at = 0
        pass

    def get_support_langs(self):
        pass

    def translate(self, text, target, source=None):
        if not self._check_authorization():
            raise TranslateException('Unauthorized')

        if isinstance(text, unicode):
            text = text.encode('utf-8')
        params = {P_TEXT: text, P_TO: target, P_CONTENTTYPE: 'text/plain'}
        if source is not None:
            params[P_FROM] = source
        token = self._get_token()
        url = '%(api)s?%(params)s' % {'api':API_TRANSLATE, 'params': urllib.urlencode(params)}
        req = urllib2.Request(url, None, {'Authorization': token})
        resp = urllib2.urlopen(req)
        if resp.getcode() != 200:
            raise TranslateException(resp.msg())
        data = resp.read()
        return self._parse_response(data)

    def group_translate(self, texts, target, source=None):
        if not self._check_authorization():
            raise TranslateException('Unauthorized')

        total_chars = 0
        total_texts = 0
        parts = []
        results = []
        for each in texts:
            if total_chars + len(each) > MAX_CHARS_PER_REQUEST or total_texts + 1 > MAX_TEXTS_PER_REQUEST:
                logging.info('group translate %d lines %d chars' % (total_texts, total_chars))
                results += self._do_group_translate(parts, target, source)
                parts[:] = []
                total_chars = 0
                total_texts = 0
            parts.append(each)
            total_chars += len(each)
            total_texts += 1

        if total_texts and total_chars:
            logging.info('group translate %d lines %d chars' % (total_texts, total_chars))
            results += self._do_group_translate(parts, target, source)
        return results

    def _do_group_translate(self, texts, target, source=None):
        xml_body = self._generate_translate_array_request(texts, target, source)
        token = self._get_token()
        url = API_TRANSLATE_ARRAY
        req = urllib2.Request(url, xml_body, {'Authorization': token, 'Content-Type': 'text/xml'})
        resp = urllib2.urlopen(req)
        if resp.getcode() != 200:
            raise TranslateException(resp.msg())
        data = resp.read()
        return self._parse_translate_array_response(data)

    def _generate_translate_array_request(self, texts, target, source):
        root = etree.Element('TranslateArrayRequest')
        etree.SubElement(root, 'AppId')
        e_from = etree.SubElement(root, 'From')
        if source:
            e_from.text = source
        ns_opt = 'http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2'
        nsmap_opt = {None: ns_opt}
        get_qualified_name = lambda ns, name: '{%s}%s' % (ns, name)
        e_opt = etree.SubElement(root, 'Options')
        etree.SubElement(e_opt, get_qualified_name(ns_opt, 'Category'), nsmap=nsmap_opt)
        e_ctype = etree.SubElement(e_opt, get_qualified_name(ns_opt, 'ContentType'), nsmap=nsmap_opt)
        e_ctype.text = 'text/plain'
        etree.SubElement(e_opt, get_qualified_name(ns_opt, 'ReservedFlags'), nsmap=nsmap_opt)
        etree.SubElement(e_opt, get_qualified_name(ns_opt, 'State'), nsmap=nsmap_opt)
        etree.SubElement(e_opt, get_qualified_name(ns_opt, 'Uri'), nsmap=nsmap_opt)
        etree.SubElement(e_opt, get_qualified_name(ns_opt, 'User'), nsmap=nsmap_opt)
        e_texts = etree.SubElement(root, 'Texts')
        ns_array = 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'
        nsmap_array = {None: ns_array}
        for text in texts:
            t = etree.SubElement(e_texts, get_qualified_name(ns_array, 'string'), nsmap=nsmap_array)
            t.text = unicode(text)
        e_to = etree.SubElement(root, 'To')
        e_to.text = target
        return etree.tostring(root, method='html')

    def _parse_translate_array_response(self, data):
        root = etree.fromstring(data)
        tree = etree.ElementTree(root)
        result = []
        # tree.xpath does not support empty prefix namespace, so make a fake
        # ref: http://stackoverflow.com/questions/8053568/how-do-i-use-empty-namespaces-in-an-lxml-xpath-query
        ns = {'ns0': 'http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2'}
        translateds = tree.xpath('//ns0:TranslatedText', namespaces=ns)
        for each in translateds:
            result.append(each.text)
        return result

    def _parse_response(self, text):
        root = etree.fromstring(text)
        #return etree.tostring(root, encoding='utf-8', method='text')
        return root.text

    def _authorize(self):
        params = {
            P_CLIENT_ID: self.client_id,
            P_CLIENT_SECRET: self.client_secret,
            P_SCOPE: 'http://api.microsofttranslator.com',
            P_GRANT_TYPE: 'client_credentials'
        }

        req = urllib2.Request(AUTH_URL, urllib.urlencode(params))
        resp = urllib2.urlopen(req)
        body = resp.read()
        resp_obj = json.loads(body)
        self.access_token = resp_obj[RESP_ACCESS_TOKEN]
        age = int(resp_obj[RESP_EXPIRES_IN])
        self.expires_at = time.time() + age

    def _get_token(self):
        return 'Bearer %s' % self.access_token

    def _check_authorization(self):
        now = time.time()
        if not self.access_token or self.expires_at < now:
            self._authorize()
        return (self.access_token and self.expires_at > now)
