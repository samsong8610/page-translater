"""
Translator module define translator service interface.
"""
class Translator(object):
    """
    Initialize the translator.
    :param: config a dict of settings.
    """
    def __init__(self, config):
        pass

    """
    Return languages the translator supports.
    :return: tuple of supported languages.
    """
    def get_support_langs(self):
        pass

    """
    Translate the text from source language into target language.
    :param: text the string to translate.
    :param: target the desired language.
    :param: source the source language of the text. If None, auto detect.
    :return: the translated text.
    """
    def translate(self, text, target, source=None):
        pass
    """
    Translate a group of texts from source into target language.
    :param: texts a tuple or list of texts
    :param: target the desired language.
    :param: source the source language of the text. If None, auto detect.
    :return: the slice of the translated texts in the order provided.
    """
    def group_translate(self, texts, target, source=None):
        pass

class TranslateException(Exception):
    pass
