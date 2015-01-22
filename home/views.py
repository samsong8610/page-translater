# Create your views here.
import bs4
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, redirect
import urllib
import urllib2
from urllib2 import urlparse
from lxml import etree
from lxml import html

from translator import bing

def index(request):
    url = request.GET.get('url', '')
    to = request.GET.get('to', 'en')
    context = {'url': url, 'to': to}
    return render(request, 'index.html', context)

def fetch(request):
    target = request.GET.get('url', None)
    if target is None:
        response = HttpResponse()
        response.status_code = 400
        return response
    to = request.GET.get('to', 'en')
    print('Translate %s to %s' % (target, to))
    page = ''
    if target:
        if not target.startswith('http'):
            target = 'http://' + target
        page = _fetch_link(target)
        parts = list(urlparse.urlsplit(target))
        # clean path fragement and params
        parts[2] = '/'
        parts[3] = ''
        parts[4] = ''
        base = urlparse.urlunsplit(parts)
        translated = _translate(page, to, 'zh-CHS', base)
    return HttpResponse(translated)

def _fetch_link(link):
    req = urllib2.Request(link)
    resp = urllib2.urlopen(req)
    page =  resp.read()
    return page

def _translate(page, to, lang=None, base_url=None):
    if not page:
        return ''
    #print(page)
    translator = _get_translator()
    doc = bs4.UnicodeDammit(page, is_html=True)
    parser = html.HTMLParser(encoding=doc.original_encoding)
    root = html.document_fromstring(page, parser=parser)
    def is_not_empty_and_whitespace(str):
        return str and str.strip()

    def html_escape(str):
        entity = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}
        if str:
            for k, v in entity.iteritems():
                str = str.replace(k, v)
        return str

#   def visitor(element, tr, to):
#       if element is None:
#           return
#       # ignore elements which's tag is not str/unicode
#       # such as comment, pi, entity
#       if not isinstance(element.tag, basestring):
#           return
#       name = element.tag.lower()
#       print('Visiting element %s' % name)
#       # do not translate script and style element
#       if name in ('script', 'style'):
#           return
#       # only translate title, h1-h4, p, a element
#       if name in ('title', 'h1', 'h2', 'h3', 'h4', 'p', 'a'):
#           src = element.text
#           if is_not_empty_and_whitespace(src):
#               element.text = html_escape(tr.translate(src, to))
#               print('Translate text %s to %s' % (src, element.text))
#           src = element.tail
#           if is_not_empty_and_whitespace(src):
#               element.tail = html_escape(tr.translate(src, to))
#               print('Translate tail text %s to %s' % (src, element.tail))

#       for sub in element:
#           visitor(sub, tr, to)
#
#    visitor(root, translator, to)
    elements = []
    # dict like {'0': 'text', '0t': 'tail'}
    texts = {}
    i = -1
    for e in root.iter():
        if not isinstance(e.tag, basestring):
            continue
        name = e.tag.lower()
        if name in ('script', 'style'):
            continue
        if name in ('span', 'li', 'label', 'caption', 'td', 'th', 'b', 'blockquote', 'q', 'dt', 'dd', 'figcaption', 'legend', 'br', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'input', 'option', 'p', 'a'):
            src = e.text
            e_saved = False
            if is_not_empty_and_whitespace(src):
                #print('Translate tag %s text %s' % (name, src))
                elements.append(e)
                i += 1
                texts[str(i)] = unicode(src)
                e_saved = True
            src = e.tail
            if is_not_empty_and_whitespace(src):
                #print('Translate tag %s tail %s' % (name, src))
                if not e_saved:
                    elements.append(e)
                    i += 1
                texts[str(i)+'t'] = unicode(src)

    # group translate
    sorted_keys = texts.keys()
    sorted_keys.sort()
    need_trans = [texts[k] for k in sorted_keys]
    #print(need_trans)
    trans = translator.group_translate(need_trans, to, lang)
    #print(trans)
    for i,k in enumerate(sorted_keys):
        if k[-1] == 't':
            index = int(k[:-1])
            elements[index].tail = html_escape(trans[i])
        else:
            index = int(k)
            elements[index].text = html_escape(trans[i])

    if base_url:
        # set <base> in <head> to support relative href in the document
        e_head = root.find('head')
        if e_head is None:
            e_head = etree.SubElement(root, 'head')
        e_base = e_head.find('base')
        if e_base is None:
            e_base = etree.Element('base')
            e_head.insert(0, e_base)
        e_base.attrib['href'] = base_url

    translated = etree.tostring(root, method='html', encoding='utf-8', pretty_print=True)
    #print(translated)
    return translated.decode('utf-8')

def _get_translator():
    return bing.Translator({'client_id': 'webtranslator8601', 'client_secret': '38tnkL0LkSI5DjHq3mhFU0f7DKsm1/rizwEmMylZxtc='})
